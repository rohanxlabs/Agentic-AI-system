"""FastAPI application for the Agentic AI System."""
import asyncio
import logging
import json
import time
import os
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Any, Dict
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from llm.groq_llm import GroqLLM
from agents.planner_agent import PlannerAgent
from agents.executor_agent import ExecutorAgent
from agents.critic_agent import CriticAgent
from agents.manager_agent import ManagerAgent
from config.config import LOG_LEVEL, LOG_FILE, API_AUTH_KEY, RATE_LIMIT_PER_MINUTE
from session.session_manager import session_store
from tools.tool_registry import TOOL_SCHEMAS

# Setup logging
log_path = Path(LOG_FILE)
log_path.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    cleanup_task = asyncio.create_task(cleanup_stale_sessions())
    app.state.cleanup_task = cleanup_task
    logger.info("Application startup complete - session cleanup task started")
    yield
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass


app = FastAPI(title="Agentic AI System API", version="1.0.0", lifespan=lifespan)
# Provide a standard `application` ASGI variable for WSGI/hosting compatibility
application = app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# API Key verification dependency
async def verify_api_key(request: Request):
    """Verify the X-API-Key header if auth is enabled."""
    if not API_AUTH_KEY:
        return
    api_key = request.headers.get("X-API-Key")
    if not api_key or api_key != API_AUTH_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


class RunRequest(BaseModel):
    goal: str
    session_id: Optional[str] = None
    enable_tools: bool = True


class RunResponse(BaseModel):
    results: List[str]
    session_id: str


@app.post("/run", response_model=RunResponse)
@limiter.limit(f"{RATE_LIMIT_PER_MINUTE}/minute")
def run_system(request: Request, run_request: RunRequest, _: Any = Depends(verify_api_key)):
    """Run the Agentic AI System with the given goal."""
    try:
        if not run_request.goal.strip():
            raise HTTPException(status_code=400, detail="Goal cannot be empty")

        session_id, session = session_store.get_or_create(run_request.session_id)
        stm = session["stm"]
        ltm = session["ltm"]

        if run_request.session_id and session["last_used"] != session["created_at"]:
            logger.info(f"Reusing session {session_id} with existing STM content: {stm.get()}")

        llm = GroqLLM()
        planner = PlannerAgent("Planner", llm, stm, ltm)
        executor = ExecutorAgent("Executor", llm, stm, ltm)
        critic = CriticAgent("Critic", llm, stm, ltm)

        manager = ManagerAgent(planner, executor, critic, ltm, enable_tools=run_request.enable_tools)

        logger.info(f"Starting system with goal: {run_request.goal}")
        results = manager.run(run_request.goal)
        logger.info("System completed successfully")

        return RunResponse(results=results, session_id=session_id)

    except Exception as e:
        logger.exception("Unexpected error occurred")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/run/stream")
@limiter.limit(f"{RATE_LIMIT_PER_MINUTE}/minute")
async def run_system_stream(request: Request, run_request: RunRequest, _: Any = Depends(verify_api_key)):
    """Run the Agentic AI System with streaming progress updates via SSE."""
    try:
        if not run_request.goal.strip():
            raise HTTPException(status_code=400, detail="Goal cannot be empty")

        session_id, session = session_store.get_or_create(run_request.session_id)
        stm = session["stm"]
        ltm = session["ltm"]

        if run_request.session_id and session["last_used"] != session["created_at"]:
            logger.info(f"Reusing streaming session {session_id} with existing STM content: {stm.get()}")

        llm = GroqLLM()
        planner = PlannerAgent("Planner", llm, stm, ltm)
        executor = ExecutorAgent("Executor", llm, stm, ltm)
        critic = CriticAgent("Critic", llm, stm, ltm)

        manager = ManagerAgent(planner, executor, critic, ltm, enable_tools=run_request.enable_tools)

        async def event_generator():
            try:
                for event in manager.run_streaming(run_request.goal):
                    yield f"data: {json.dumps(event)}\n\n"
                    await asyncio.sleep(0)
            except Exception as e:
                logger.exception("Error in streaming event generator")
                yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"

        logger.info(f"Starting streaming system with goal: {run_request.goal}")
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream"
        )

    except Exception as e:
        logger.exception("Unexpected error occurred in streaming endpoint")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Agentic AI System API","status": "OK"}


@app.get("/sessions")
@limiter.limit(f"{RATE_LIMIT_PER_MINUTE}/minute")
def list_sessions(request: Request, _: Any = Depends(verify_api_key)):
    """List all active sessions."""
    sessions = session_store.list_sessions()
    return {"sessions": sessions}


@app.post("/sessions")
@limiter.limit(f"{RATE_LIMIT_PER_MINUTE}/minute")
def create_session_endpoint(request: Request, _: Any = Depends(verify_api_key)):
    """Create a new session with optional initial goal."""
    session_id, session = session_store.get_or_create()
    session_data = {
        "id": session_id,
        "created_at": datetime.fromtimestamp(session["created_at"]).isoformat(),
        "last_used": datetime.fromtimestamp(session["last_used"]).isoformat(),
        "status": session.get("status", "idle"),
        "goal": None,
    }
    return JSONResponse(status_code=201, content=session_data)


@app.get("/sessions/{session_id}")
@limiter.limit(f"{RATE_LIMIT_PER_MINUTE}/minute")
def get_session_endpoint(request: Request, session_id: str, _: Any = Depends(verify_api_key)):
    """Get session details."""
    session = session_store.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_data = {
        "id": session_id,
        "created_at": datetime.fromtimestamp(session["created_at"]).isoformat(),
        "last_used": datetime.fromtimestamp(session["last_used"]).isoformat(),
        "status": session.get("status", "idle"),
        "goal": session.get("goal"),
    }
    return session_data


@app.delete("/sessions/{session_id}")
@limiter.limit(f"{RATE_LIMIT_PER_MINUTE}/minute")
def delete_session_endpoint(request: Request, session_id: str, _: Any = Depends(verify_api_key)):
    """Delete a session."""
    deleted = session_store.delete_session(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return JSONResponse(status_code=204, content=None)


@app.get("/memory/stats")
@limiter.limit(f"{RATE_LIMIT_PER_MINUTE}/minute")
def get_memory_stats(request: Request, _: Any = Depends(verify_api_key)):
    """Get memory statistics across all sessions."""
    sessions = session_store.list_sessions()
    
    # Aggregate short-term memory stats from active sessions
    stm_count = 0
    stm_max_size = 0
    for s in sessions:
        session = session_store.get_session(s["id"])
        if session and "stm" in session:
            stm = session["stm"]
            stm_count += len(stm.buffer)
            stm_max_size = max(stm_max_size, stm.buffer_size)
    
    # Long-term memory stats from shared LTM
    shared_ltm = session_store._shared_ltm
    ltm_count = len(shared_ltm.store)
    
    # Estimate growth rate (entries per day since oldest entry)
    growth_rate = 0.0
    if shared_ltm.store:
        oldest = shared_ltm.store[0].get("timestamp")
        if oldest:
            try:
                oldest_dt = datetime.fromisoformat(oldest)
                days = max((datetime.now() - oldest_dt).total_seconds() / 86400, 1)
                growth_rate = round(ltm_count / days, 2)
            except Exception:
                growth_rate = 0.0
    
    return {
        "short_term": {
            "count": stm_count,
            "max_size": stm_max_size or 10,
            "usage_percent": round((stm_count / max(stm_max_size, 1)) * 100, 1) if stm_max_size else 0.0,
        },
        "long_term": {
            "count": ltm_count,
            "growth_rate": growth_rate,
        },
    }


@app.get("/agents/status")
@limiter.limit(f"{RATE_LIMIT_PER_MINUTE}/minute")
def get_agent_statuses(request: Request, _: Any = Depends(verify_api_key)):
    """Get current status of all agents."""
    # Since agents don't run continuously in this architecture,
    # return their current inferred state
    agents = [
        {
            "name": "Planner",
            "status": "idle",
            "current_task": None,
            "last_activity": datetime.now().isoformat(),
            "task_count": 0,
            "avg_response_time": 0.0,
        },
        {
            "name": "Executor",
            "status": "idle",
            "current_task": None,
            "last_activity": datetime.now().isoformat(),
            "task_count": 0,
            "avg_response_time": 0.0,
        },
        {
            "name": "Critic",
            "status": "idle",
            "current_task": None,
            "last_activity": datetime.now().isoformat(),
            "task_count": 0,
            "avg_response_time": 0.0,
        },
        {
            "name": "Manager",
            "status": "idle",
            "current_task": None,
            "last_activity": datetime.now().isoformat(),
            "task_count": session_store.get_session_count(),
            "avg_response_time": 0.0,
        },
    ]
    return agents


@app.get("/tools")
@limiter.limit(f"{RATE_LIMIT_PER_MINUTE}/minute")
def get_tools(request: Request, _: Any = Depends(verify_api_key)):
    """Get available tools and their schemas."""
    tools = []
    for schema in TOOL_SCHEMAS:
        tools.append({
            "name": schema["function"]["name"],
            "description": schema["function"]["description"],
            "parameters": schema["function"]["parameters"],
            "is_enabled": True,
            "usage_count": 0,
        })
    return tools


@app.get("/metrics")
@limiter.limit(f"{RATE_LIMIT_PER_MINUTE}/minute")
def get_metrics(request: Request, _: Any = Depends(verify_api_key)):
    """Get system metrics."""
    process_start = getattr(app.state, "start_time", time.time())
    if not hasattr(app.state, "start_time"):
        app.state.start_time = time.time()
        process_start = app.state.start_time
    
    uptime_seconds = time.time() - process_start
    hours = int(uptime_seconds // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    seconds = int(uptime_seconds % 60)
    uptime = f"{hours}h {minutes}m {seconds}s"
    
    # Approximate memory usage of process
    try:
        import psutil
        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()
        memory_used = mem_info.rss
        memory_total = psutil.virtual_memory().total
        memory_unit = "bytes"
    except Exception:
        memory_used = 0
        memory_total = 0
        memory_unit = "bytes"
    
    return {
        "uptime": uptime,
        "total_requests": getattr(app.state, "total_requests", 0),
        "successful_requests": getattr(app.state, "successful_requests", 0),
        "failed_requests": getattr(app.state, "failed_requests", 0),
        "avg_response_time": getattr(app.state, "avg_response_time", 0.0),
        "active_sessions": session_store.get_session_count(),
        "memory_usage": {
            "used": memory_used,
            "total": memory_total,
            "unit": memory_unit,
        },
    }


# Background task for cleaning up stale sessions
async def cleanup_stale_sessions():
    """Periodically clean up stale sessions every 10 minutes."""
    while True:
        await asyncio.sleep(600)
        cleaned = session_store.cleanup_stale()
        logger.info(f"Session cleanup completed: removed {cleaned} stale sessions")


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Middleware to track request metrics."""
    start = time.time()
    try:
        response = await call_next(request)
        app.state.successful_requests = getattr(app.state, "successful_requests", 0) + 1
        return response
    except Exception:
        app.state.failed_requests = getattr(app.state, "failed_requests", 0) + 1
        raise
    finally:
        app.state.total_requests = getattr(app.state, "total_requests", 0) + 1
        elapsed = time.time() - start
        avg = getattr(app.state, "avg_response_time", 0.0)
        count = app.state.total_requests
        app.state.avg_response_time = (avg * (count - 1) + elapsed) / count if count > 0 else elapsed