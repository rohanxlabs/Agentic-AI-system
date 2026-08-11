"""Base agent — thin wrapper that combines an LLM with short- and long-term memory."""
import logging
from typing import Any

logger = logging.getLogger(__name__)


class BaseAgent:
    """Shared foundation for all agents.

    Provides a single ``think(prompt)`` helper that:
    * Optionally prepends recent short-term memory as context.
    * Calls the LLM.
    * Stores the response back into short-term memory.

    All specialised agents (Planner, Executor, Critic) inherit from this
    class and add their own higher-level methods on top.
    """

    def __init__(self, name: str, llm: Any, stm: Any, ltm: Any) -> None:
        """Initialise a base agent.

        Args:
            name: Human-readable identifier (e.g. "Planner").
            llm:  Language-model instance (``GroqLLM``).
            stm:  Short-term memory instance (``ShortTermMemory``).
            ltm:  Long-term memory instance (``LongTermMemory``).
        """
        self.name = name
        self.llm = llm
        self.stm = stm
        self.ltm = ltm

    def think(self, prompt: str, use_memory: bool = True) -> str:
        """Send a prompt to the LLM, optionally enriched with recent context.

        Args:
            prompt:     The prompt to send.
            use_memory: If True, prepend the recent STM buffer as context.

        Returns:
            The LLM response text.

        Raises:
            LLMError: Propagated from ``GroqLLM`` — callers should handle it.
        """
        if use_memory:
            context = self.stm.get()
            if context:
                prompt = f"Recent context:\n{context}\n\n{prompt}"

        response = self.llm.call(prompt)
        self.stm.add(f"{self.name}: {response}")
        return response
