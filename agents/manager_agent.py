"""Manager agent orchestrating the agentic system workflow."""
import re
from typing import Any, List
from config.config import MAX_ITERATIONS


class ManagerAgent:
    """Orchestrates planning, execution, and criticism cycle."""

    def __init__(self, planner: Any, executor: Any, critic: Any, ltm: Any) -> None:
        """Initialize the manager agent.

        Args:
            planner: PlannerAgent instance
            executor: ExecutorAgent instance
            critic: CriticAgent instance
            ltm: Long-term memory instance
        """
        self.planner = planner
        self.executor = executor
        self.critic = critic
        self.ltm = ltm

    def run(self, goal: str) -> List[str]:
        """Execute the goal through planning, execution, and refinement cycles.

        Args:
            goal: The goal to accomplish

        Returns:
            List of final improved results
        """
        # For simple tasks, use a single comprehensive approach to avoid rate limits
        if MAX_ITERATIONS <= 1:
            return self._run_simple_mode(goal)

        # For complex tasks, use the full multi-step approach
        return self._run_full_mode(goal)

    def _run_simple_mode(self, goal: str) -> List[str]:
        """Run in simple mode with minimal API calls.

        Args:
            goal: The goal to accomplish

        Returns:
            List of results
        """
        prompt = f"""You are an expert AI assistant. Complete this task comprehensively:

Goal: {goal}

Provide a complete, high-quality solution with:
1. Clear steps or implementation
2. Best practices and considerations
3. Any relevant examples or code

Be thorough but concise."""

        result = self.executor.think(prompt)
        self.ltm.save(f"Simple execution: {result}")
        return [result]

    def _run_full_mode(self, goal: str) -> List[str]:
        """Run in full agentic mode with multiple iterations.

        Args:
            goal: The goal to accomplish

        Returns:
            List of final improved results
        """
        plan = self.planner.create_plan(goal)
        steps = self._parse_steps(plan)
        if not steps:
            steps = [plan]

        final_results: List[str] = []
        accumulated_critiques = ""

        for iteration in range(MAX_ITERATIONS):
            iteration_results: List[str] = []
            iteration_critiques: List[str] = []

            for step in steps:
                result = self.executor.execute_task(step)
                critique = self.critic.critique(result)

                if self._is_acceptable(critique):
                    iteration_results.append(result)
                else:
                    improved_prompt = f"""
Improve the result using this critique.

Result:
{result}

Critique:
{critique}
"""
                    improved = self.executor.think(improved_prompt)
                    iteration_results.append(improved)
                    iteration_critiques.append(f"Step: {step}\nCritique: {critique}")

            final_results.extend(iteration_results)
            self.ltm.save(f"Iteration {iteration}: " + "\n".join(iteration_results))

            if iteration < MAX_ITERATIONS - 1 and iteration_critiques:
                accumulated_critiques += "\n".join(iteration_critiques) + "\n"
                next_plan = self.planner.think(self._plan_prompt(goal, accumulated_critiques))
                next_steps = self._parse_steps(next_plan)
                if next_steps:
                    steps = next_steps

        return final_results

    def _parse_steps(self, plan: str) -> List[str]:
        """Extract numbered list items from a plan string.

        Args:
            plan: Raw plan text

        Returns:
            List of parsed step strings
        """
        steps: List[str] = []
        for line in plan.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            match = re.match(r'^(?:\d+[\.\)]\s*|[-*]\s*)(.*)', stripped)
            if match:
                steps.append(match.group(1).strip())
        return steps

    def _plan_prompt(self, goal: str, accumulated_critiques: str) -> str:
        """Build a prompt for the planner that incorporates prior feedback.

        Args:
            goal: The original goal
            accumulated_critiques: Collected critiques from previous iterations

        Returns:
            Planning prompt string
        """
        return f"""You are a strategic planning agent.
Break this goal into clear, executable steps.
Be concise and actionable.

Goal:
{goal}

Previous iteration feedback:
{accumulated_critiques}
Incorporate this feedback into your revised plan.

Return numbered steps with brief descriptions.
"""

    def _is_acceptable(self, critique: str) -> bool:
        """Heuristic check to skip improvement when critique indicates no issues.

        Args:
            critique: Critic output for a result

        Returns:
            True if the result should be kept as-is
        """
        lowered = critique.lower()
        no_issue_phrases = [
            "no issues",
            "looks good",
            "acceptable",
            "sufficient",
            "satisfactory",
            "no problems",
            "no problem",
        ]
        if any(phrase in lowered for phrase in no_issue_phrases):
            return True
        return len(critique.strip()) < 30