"""Planner agent — breaks a goal into numbered, executable steps."""
import logging
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class PlannerAgent(BaseAgent):
    """Creates a step-by-step plan from a high-level goal.

    The plan is a numbered list of concise, actionable items that the
    Executor will work through one by one.
    """

    def create_plan(self, goal: str) -> str:
        """Produce a numbered execution plan for the given goal.

        Args:
            goal: High-level objective to plan for.

        Returns:
            A numbered-list plan as a string.
        """
        memory_section = self._relevant_memory(goal)

        prompt = (
            f"{memory_section}"
            "You are a strategic planning agent.\n"
            "Break the goal below into clear, concise, executable steps.\n"
            "Each step should be a single, self-contained action.\n"
            "Return ONLY a numbered list — no prose before or after.\n\n"
            f"Goal:\n{goal}"
        )
        return self.think(prompt)

    # ---- private ------------------------------------------------------------

    def _relevant_memory(self, goal: str) -> str:
        try:
            memories = self.ltm.recall_relevant(goal)
        except Exception:
            logger.warning("LTM recall failed during planning — skipping memory context.")
            return ""
        if not memories:
            return ""
        joined = "\n".join(memories)
        return (
            "Relevant past experience (context only — do not simply repeat):\n"
            f"{joined}\n\n"
        )
