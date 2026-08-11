"""FastAPI application for the Agentic AI System."""
import asyncio
import json
import logging
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from agents.critic_agent import CriticAgent
from agents.executor_agent import ExecutorAgent
from agents.manager_agent import ManagerAgent
from agents.planner_agent import PlannerAgent
from config.config import (
    API_AUTH_KEY,
    LOG_FILE,
    LOG_LEVEL,
    RATE_LIMIT_PER_MINUTE,
)
from llm.groq_llm import GroqLLM, LLMError
from session.session_manager import session_store
from tools.tool_registry import TOOL_SCHEMAS

# ── Logging ───────────────────────────────────────────────────────────────────
log_path = Path(LOG_FILE)
log_path.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# ── Rate limiter ──────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.start_time = time.time()
    cleanup_task = asyncio.create_task(_cleanup_loop())
    logger.info("Agentic AI System API started.")
    yield
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="Agentic AI System API",
    version="1.0.0",
    description=(
        "A goal-driven agentic AI system: Plan → Execute (with tools) → "
        "Critique → Refine, with session-isolated memory."
    ),
    lifespan=lifespan,
)
application = app  # ASGI alias for hosting compatibility

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

_CORS_ORIGINS = [
    o.strip()
    for o in os.getenv(
        "CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")
    if o.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Auth dependency ───────────────────────────────────────────────────────────

async def verify_api_key(request: Request) -> None:
    """Verify X-API-Key header when API_AUTH_KEY is configured."""
    if not API_AUTH_KEY:
        return
    api_key = request.headers.get("X-API-Key", "")
    if api_key != API_AUTH_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


# ── Request / Response models ─────────────────────────────────────────────────

class RunRequest(BaseModel):
    goal: str
    session_id: Optional[str] = None
    enable_tools: bool = True


class RunResponse(BaseModel):
    results: List[str]
    session_id: str


class SessionData(BaseModel):
    id: str
    created_at: str
    last_used: str
    status: str = "idle"
    goal: Optional[str] = None


class CreateSessionRequest(BaseModel):
    goal: Optional[str] = None


# ── Agent factory ─────────────────────────────────────────────────────────────

def _build_manager(stm: Any, ltm: Any, enable_tools: bool) -> ManagerAgent:
    llm = GroqLLM()
    planner = PlannerAgent("Planner", llm, stm, ltm)
    executor = ExecutorAgent("Executor", llm, stm, ltm)
    critic = CriticAgent("Critic", llm, stm, ltm)
    return ManagerAgent(planner, executor, critic, ltm, enable_tools=enable_tools)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
async def root() -> Dict[str, str]:
    return {"message": "Agentic AI System API", "status": "OK"}


@app.post("/run", response_model=RunResponse, tags=["Agent"])
@limiter.limit(f"{RATE_LIMIT_PER_MINUTE}/minute")
def run_system(
    request: Request,
    run_request: RunRequest,
    _: Any = Depends(verify_api_key),
) -> RunResponse:
    """Run the agent synchronously and return all results."""
    goal = run_request.goal.strip()
    if not goal:
        raise HTTPException(status_code=400, detail="Goal cannot be empty")
    if len(goal) > 2000:
        raise HTTPException(status_code=400, detail="Goal exceeds 2000 character limit")

    session_id, session = session_store.get_or_create(
        run_request.session_id, goal=goal
    )
    session["status"] = "running"

    try:
        manager = _build_manager(
            session["stm"], session["ltm"], run_request.enable_tools
        )
        logger.info("run  session=%s goal=%r", session_id, goal[:80])
        results = manager.run(goal)
        session["status"] = "completed"
        logger.info("run  completed  session=%s", session_id)
        return RunResponse(results=results, session_id=session_id)
    except LLMError as exc:
        session["status"] = "error"
        logger.error("LLM error in /run: %s", exc)
        raise HTTPException(status_code=502, detail=f"LLM error: {exc}")
    except Exception as exc:
        session["status"] = "error"
        logger.exception("Unexpected error in /run")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/run/stream", tags=["Agent"])
@limiter.limit(f"{RATE_LIMIT_PER_MINUTE}/minute")
async def run_system_stream(
    request: Request,
    run_request: RunRequest,
    _: Any = Depends(verify_api_key),
) -> StreamingResponse:
    """Run the agent and stream structured SSE progress events.

    Event types:

    * ``plan``       – Planner produced or revised a plan.
    * ``step_start`` – About to execute a step.
    * ``tool_call``  – A tool was invoked (name / input / output / status).
    * ``step_result``– Step execution finished.
    * ``critique``   – Critic evaluated a step result.
    * ``complete``   – Final answer ready (also carries ``session_id``).
    * ``error``      – Something went wrong.
    """
    goal = run_request.goal.strip()
    if not goal:
        raise HTTPException(status_code=400, detail="Goal cannot be empty")
    if len(goal) > 2000:
        raise HTTPException(status_code=400, detail="Goal exceeds 2000 character limit")

    session_id, session = session_store.get_or_create(
        run_request.session_id, goal=goal
    )

    async def event_generator():
        session["status"] = "running"
        try:
            manager = _build_manager(
                session["stm"], session["ltm"], run_request.enable_tools
            )
            logger.info(
                "stream  session=%s goal=%r", session_id, goal[:80]
            )
            for event in manager.run_streaming(goal):
                if event.get("type") == "complete":
                    event = {**event, "session_id": session_id}
                    session["status"] = "completed"
                yield f"data: {json.dumps(event)}\n\n"
                await asyncio.sleep(0)  # yield to event loop
        except LLMError as exc:
            session["status"] = "error"
            logger.error("LLM error in /run/stream: %s", exc)
            yield f"data: {json.dumps({'type': 'error', 'message': f'LLM error: {exc}'})}\n\n"
        except Exception as exc:
            session["status"] = "error"
            logger.exception("Unexpected error in /run/stream")
            yield f"data: {json.dumps({'type': 'error', 'message': str(exc)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ── Sessions ──────────────────────────────────────────────────────────────────

@app.get("/sessions", tags=["Sessions"])
@limiter.limit(f"{RATE_LIMIT_PER_MINUTE}/minute")
def list_sessions(
    request: Request, _: Any = Depends(verify_api_key)
) -> List[SessionData]:
    """List all active sessions."""
    return [SessionData(**s) for s in session_store.list_sessions()]


@app.post("/sessions", response_model=SessionData, tags=["Sessions"])
@limiter.limit(f"{RATE_LIMIT_PER_MINUTE}/minute")
def create_session_endpoint(
    request: Request,
    body: CreateSessionRequest,
    _: Any = Depends(verify_api_key),
) -> SessionData:
    """Create a new isolated session."""
    session_id, session = session_store.get_or_create(goal=body.goal)
    return SessionData(
        id=session_id,
        created_at=datetime.fromtimestamp(session["created_at"]).isoformat(),
        last_used=datetime.fromtimestamp(session["last_used"]).isoformat(),
        status=session.get("status", "idle"),
        goal=session.get("goal"),
    )


@app.get("/sessions/{session_id}", response_model=SessionData, tags=["Sessions"])
@limiter.limit(f"{RATE_LIMIT_PER_MINUTE}/minute")
def get_session_endpoint(
    request: Request,
    session_id: str,
    _: Any = Depends(verify_api_key),
) -> SessionData:
    session = session_store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionData(
        id=session_id,
        created_at=datetime.fromtimestamp(session["created_at"]).isoformat(),
        last_used=datetime.fromtimestamp(session["last_used"]).isoformat(),
        status=session.get("status", "idle"),
        goal=session.get("goal"),
    )


@app.delete("/sessions/{session_id}", status_code=204, tags=["Sessions"])
@limiter.limit(f"{RATE_LIMIT_PER_MINUTE}/minute")
def delete_session_endpoint(
    request: Request,
    session_id: str,
    _: Any = Depends(verify_api_key),
) -> None:
    if not session_store.delete_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found")


# ── Memory ────────────────────────────────────────────────────────────────────

@app.get("/memory/stats", tags=["Memory"])
@limiter.limit(f"{RATE_LIMIT_PER_MINUTE}/minute")
def get_memory_stats(
    request: Request, _: Any = Depends(verify_api_key)
) -> Dict[str, Any]:
    """Aggregate memory statistics across all active sessions."""
    sessions = session_store.list_sessions()

    stm_count = 0
    stm_max_size = 0
    ltm_count = 0
    growth_rate = 0.0

    for s in sessions:
        data = session_store.get_session(s["id"])
        if not data:
            continue
        stm = data.get("stm")
        if stm:
            stm_count += len(stm.buffer)
            stm_max_size = max(stm_max_size, stm.buffer_size)
        ltm = data.get("ltm")
        if ltm:
            ltm_count += len(ltm.store)
            if ltm.store:
                oldest = ltm.store[0].get("timestamp")
                if oldest:
                    try:
                        from datetime import datetime as _dt
                        days = max(
                            (_dt.now() - _dt.fromisoformat(oldest)).total_seconds()
                            / 86400,
                            1,
                        )
                        growth_rate += round(len(ltm.store) / days, 2)
                    except Exception:
                        pass

    effective_max = stm_max_size or 10
    return {
        "short_term": {
            "count": stm_count,
            "max_size": effective_max,
            "usage_percent": round(stm_count / effective_max * 100, 1),
        },
        "long_term": {
            "count": ltm_count,
            "growth_rate": round(growth_rate, 2),
        },
    }


# ── Agents ────────────────────────────────────────────────────────────────────

@app.get("/agents/status", tags=["Agents"])
@limiter.limit(f"{RATE_LIMIT_PER_MINUTE}/minute")
def get_agent_statuses(
    request: Request, _: Any = Depends(verify_api_key)
) -> List[Dict[str, Any]]:
    """Return current inferred status of each agent role."""
    running_sessions = [
        s for s in session_store.list_sessions() if s.get("status") == "running"
    ]
    agent_status = "busy" if running_sessions else "idle"
    current_task = running_sessions[0].get("goal") if running_sessions else None

    agents = []
    for name in ("Planner", "Executor", "Critic", "Manager"):
        agents.append(
            {
                "name": name,
                "status": agent_status,
                "current_task": current_task,
                "last_activity": datetime.now().isoformat(),
                "task_count": getattr(app.state, "successful_requests", 0),
                "avg_response_time": getattr(app.state, "avg_response_time", 0.0),
            }
        )
    return agents


# ── Tools ─────────────────────────────────────────────────────────────────────

@app.get("/tools", tags=["Tools"])
@limiter.limit(f"{RATE_LIMIT_PER_MINUTE}/minute")
def get_tools(
    request: Request, _: Any = Depends(verify_api_key)
) -> List[Dict[str, Any]]:
    """Return the available tool schemas."""
    return [
        {
            "name": schema["function"]["name"],
            "description": schema["function"]["description"],
            "parameters": schema["function"]["parameters"],
            "is_enabled": True,
            "usage_count": 0,
        }
        for schema in TOOL_SCHEMAS
    ]


# ── Metrics ───────────────────────────────────────────────────────────────────

@app.get("/metrics", tags=["Metrics"])
@limiter.limit(f"{RATE_LIMIT_PER_MINUTE}/minute")
def get_metrics(
    request: Request, _: Any = Depends(verify_api_key)
) -> Dict[str, Any]:
    """Return basic system metrics."""
    uptime_s = time.time() - getattr(app.state, "start_time", time.time())
    h = int(uptime_s // 3600)
    m = int((uptime_s % 3600) // 60)
    s = int(uptime_s % 60)

    memory_used = 0
    memory_total = 0
    try:
        import psutil, os as _os
        proc = psutil.Process(_os.getpid())
        memory_used = proc.memory_info().rss
        memory_total = psutil.virtual_memory().total
    except Exception:
        pass

    return {
        "uptime": f"{h}h {m}m {s}s",
        "total_requests": getattr(app.state, "total_requests", 0),
        "successful_requests": getattr(app.state, "successful_requests", 0),
        "failed_requests": getattr(app.state, "failed_requests", 0),
        "avg_response_time": round(
            getattr(app.state, "avg_response_time", 0.0), 3
        ),
        "active_sessions": session_store.get_session_count(),
        "memory_usage": {
            "used": memory_used,
            "total": memory_total,
            "unit": "bytes",
        },
    }


# ── Middleware ────────────────────────────────────────────────────────────────

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.time()
    try:
        response = await call_next(request)
        app.state.successful_requests = (
            getattr(app.state, "successful_requests", 0) + 1
        )
        return response
    except Exception:
        app.state.failed_requests = getattr(app.state, "failed_requests", 0) + 1
        raise
    finally:
        app.state.total_requests = getattr(app.state, "total_requests", 0) + 1
        elapsed = time.time() - start
        count = app.state.total_requests
        prev_avg = getattr(app.state, "avg_response_time", 0.0)
        app.state.avg_response_time = (
            (prev_avg * (count - 1) + elapsed) / count if count else elapsed
        )


# ── Background helpers ────────────────────────────────────────────────────────

async def _cleanup_loop() -> None:
    """Periodically evict sessions idle for more than 1 hour."""
    while True:
        await asyncio.sleep(600)
        removed = session_store.cleanup_stale(max_age_seconds=3600)
        if removed:
            logger.info("Session cleanup removed %d stale session(s).", removed)
