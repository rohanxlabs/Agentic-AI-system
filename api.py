"""FastAPI application for the Agentic AI System."""
import asyncio
import logging
import json
from pathlib import Path
from typing import List, Optional, Any
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse
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
app = FastAPI(title="Agentic AI System API", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# API Key verification dependency
async def verify_api_key(request: Request):
    """Verify the X-API-Key header if auth is enabled."""
    if not API_AUTH_KEY:
        # Auth is disabled, skip verification
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
async def run_system(request: Request, run_request: RunRequest, _: Any = Depends(verify_api_key)):
    """Run the Agentic AI System with the given goal."""
    try:
        if not run_request.goal.strip():
            raise HTTPException(status_code=400, detail="Goal cannot be empty")

        # Get or create session from session store
        session_id, session = session_store.get_or_create(run_request.session_id)
        stm = session["stm"]
        ltm = session["ltm"]

        # Log existing STM content if reusing a session
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

        # Get or create session from session store
        session_id, session = session_store.get_or_create(run_request.session_id)
        stm = session["stm"]
        ltm = session["ltm"]

        # Log existing STM content if reusing a session
        if run_request.session_id and session["last_used"] != session["created_at"]:
            logger.info(f"Reusing streaming session {session_id} with existing STM content: {stm.get()}")

        llm = GroqLLM()
        planner = PlannerAgent("Planner", llm, stm, ltm)
        executor = ExecutorAgent("Executor", llm, stm, ltm)
        critic = CriticAgent("Critic", llm, stm, ltm)

        manager = ManagerAgent(planner, executor, critic, ltm, enable_tools=run_request.enable_tools)

        async def event_generator():
            """Generate SSE events from the manager's streaming execution."""
            for event in manager.run_streaming(run_request.goal):
                yield f"data: {json.dumps(event)}\n\n"
                # Add a small yield to ensure async flushing
                await asyncio.sleep(0)

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


# Background task for cleaning up stale sessions
async def cleanup_stale_sessions():
    """Periodically clean up stale sessions every 10 minutes."""
    while True:
        await asyncio.sleep(600)  # 10 minutes in seconds
        cleaned = session_store.cleanup_stale()
        logger.info(f"Session cleanup completed: removed {cleaned} stale sessions")


@app.on_event("startup")
async def startup_event():
    """Start background tasks on application startup."""
    asyncio.create_task(cleanup_stale_sessions())
    logger.info("Application startup complete - session cleanup task started")