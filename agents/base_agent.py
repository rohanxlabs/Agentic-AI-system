"""Base agent class providing core thinking capabilities."""
from typing import Any


class BaseAgent:
    """Base class for all agents in the system."""

    def __init__(self, name: str, llm: Any, stm: Any, ltm: Any) -> None:
        """Initialize a base agent.
        
        Args:
            name: Agent identifier
            llm: Language model instance
            stm: Short-term memory instance
            ltm: Long-term memory instance
        """
        self.name = name
        self.llm = llm
        self.stm = stm
        self.ltm = ltm

    def think(self, prompt: str) -> str:
        """Process a prompt and store response in memory.
        
        Args:
            prompt: Input prompt for the LLM
            
        Returns:
            LLM response
        """
        response = self.llm.call(prompt)
        self.stm.add(f"{self.name}: {response}")
        return response