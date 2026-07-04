"""FastAPI application for the Agentic AI System."""
import logging
import uuid
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from llm.groq_llm import GroqLLM
from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory
from agents.planner_agent import PlannerAgent
from agents.executor_agent import ExecutorAgent
from agents.critic_agent import CriticAgent
from agents.manager_agent import ManagerAgent
from config.config import LOG_LEVEL, LOG_FILE

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

app = FastAPI(title="Agentic AI System API", version="1.0.0")

_shared_ltm = LongTermMemory()
_sessions: dict[str, ShortTermMemory] = {}


class RunRequest(BaseModel):
    goal: str
    session_id: Optional[str] = None
    enable_tools: bool = True


class RunResponse(BaseModel):
    results: List[str]
    session_id: str


@app.post("/run", response_model=RunResponse)
async def run_system(request: RunRequest):
    """Run the Agentic AI System with the given goal."""
    try:
        if not request.goal.strip():
            raise HTTPException(status_code=400, detail="Goal cannot be empty")

        session_id = request.session_id or str(uuid.uuid4())
        if session_id not in _sessions:
            _sessions[session_id] = ShortTermMemory()

        llm = GroqLLM()
        stm = _sessions[session_id]
        ltm = _shared_ltm

        planner = PlannerAgent("Planner", llm, stm, ltm)
        executor = ExecutorAgent("Executor", llm, stm, ltm)
        critic = CriticAgent("Critic", llm, stm, ltm)

        manager = ManagerAgent(planner, executor, critic, ltm, enable_tools=request.enable_tools)

        logger.info(f"Starting system with goal: {request.goal}")
        results = manager.run(request.goal)
        logger.info("System completed successfully")

        return RunResponse(results=results, session_id=session_id)

    except Exception as e:
        logger.exception("Unexpected error occurred")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Agentic AI System API","status": "OK"}