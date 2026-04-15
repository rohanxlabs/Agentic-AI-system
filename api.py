"""FastAPI application for the Agentic AI System."""
import logging
from pathlib import Path
from typing import List

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

# Components will be initialized lazily
_manager = None

def get_manager():
    """Get or initialize the manager instance."""
    global _manager
    if _manager is None:
        llm = GroqLLM()
        stm = ShortTermMemory()
        ltm = LongTermMemory()

        planner = PlannerAgent("Planner", llm, stm, ltm)
        executor = ExecutorAgent("Executor", llm, stm, ltm)
        critic = CriticAgent("Critic", llm, stm, ltm)

        _manager = ManagerAgent(planner, executor, critic, ltm)
    return _manager

app = FastAPI(title="Agentic AI System API", version="1.0.0")

class RunRequest(BaseModel):
    goal: str

class RunResponse(BaseModel):
    results: List[str]

@app.post("/run", response_model=RunResponse)
async def run_system(request: RunRequest):
    """Run the Agentic AI System with the given goal."""
    try:
        if not request.goal.strip():
            raise HTTPException(status_code=400, detail="Goal cannot be empty")

        logger.info(f"Starting system with goal: {request.goal}")
        manager = get_manager()
        results = manager.run(request.goal)
        logger.info("System completed successfully")

        return RunResponse(results=results)

    except Exception as e:
        logger.exception("Unexpected error occurred")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Agentic AI System API","status": "OK"}