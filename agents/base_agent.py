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

    def think(self, prompt: str, use_memory: bool = True) -> str:
        """Process a prompt and store response in memory.
        
        Args:
            prompt: Input prompt for the LLM
            use_memory: If True, prepend recent short-term memory as context
            
        Returns:
            LLM response
        """
        if use_memory:
            context = self.stm.get()
            if context:
                prompt = f"Recent context:\n{context}\n\n{prompt}"
        response = self.llm.call(prompt)
        self.stm.add(f"{self.name}: {response}")
        return response