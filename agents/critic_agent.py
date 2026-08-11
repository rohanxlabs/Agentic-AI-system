"""Critic agent — evaluates execution results and identifies improvements."""
from agents.base_agent import BaseAgent


class CriticAgent(BaseAgent):
    """Evaluates an Executor result and returns structured feedback.

    If the result is satisfactory the critique will explicitly say so
    (e.g. "No issues — looks good") so the Manager can skip refinement.
    """

    def critique(self, output: str) -> str:
        """Critically evaluate an output.

        Args:
            output: The text produced by the Executor.

        Returns:
            A short critique: either confirmation that the result is
            acceptable, or a list of specific, actionable improvements.
        """
        prompt = (
            "You are a critical reviewer.\n"
            "Evaluate the output below briefly and objectively.\n\n"
            "If the output is complete and correct, respond ONLY with:\n"
            "  'No issues — looks good.'\n\n"
            "Otherwise list specific flaws and concrete improvements "
            "(3 bullet points maximum).\n\n"
            f"Output:\n{output}"
        )
        return self.think(prompt, use_memory=False)
