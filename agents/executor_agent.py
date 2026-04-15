"""Executor agent for performing tasks."""
from typing import Any
from agents.base_agent import BaseAgent


class ExecutorAgent(BaseAgent):
    """Agent responsible for executing planned tasks."""

    def execute_task(self, task: str) -> str:
        """Execute a single task.
        
        Args:
            task: Task description to execute
            
        Returns:
            Task execution result
        """
        prompt = f"""
Execute the task below with maximum quality.
Be precise and actionable.

Task:
{task}
"""
        return self.think(prompt)