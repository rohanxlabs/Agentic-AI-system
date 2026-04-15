"""Manager agent orchestrating the agentic system workflow."""
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
        steps = plan.split("\n")

        final_results = []

        for iteration in range(MAX_ITERATIONS):
            iteration_results = []
            for step in steps:
                if not step.strip():
                    continue
                result = self.executor.execute_task(step)
                critique = self.critic.critique(result)

                improved_prompt = f"""
Improve the result using this critique.

Result:
{result}

Critique:
{critique}
"""
                improved = self.executor.think(improved_prompt)
                iteration_results.append(improved)

            # Save results from this iteration
            final_results.extend(iteration_results)
            self.ltm.save(f"Iteration {iteration}: " + "\n".join(iteration_results))

        return final_results