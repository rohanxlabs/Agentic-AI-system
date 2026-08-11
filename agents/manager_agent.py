"""Manager agent — orchestrates the Plan → Execute → Critique → Refine loop."""
import re
import time
import logging
from typing import Any, List, Generator, Dict, Optional

from config.config import MAX_ITERATIONS

logger = logging.getLogger(__name__)

# Hard upper bound on wall-clock time per run (seconds).
# Prevents a single request from blocking the server indefinitely.
_MAX_RUN_SECONDS = 300


class ManagerAgent:
    """Orchestrates planning, execution, critique, and optional refinement.

    Architecture
    ------------
    * ``MAX_ITERATIONS == 1`` → *simple mode*: a single, comprehensive LLM
      call via the Executor.  Useful when API rate limits are tight.
    * ``MAX_ITERATIONS >= 2`` → *agentic mode*: Planner creates a plan,
      Executor works through each step (with optional tool use), Critic
      evaluates each result, and the Manager refines the plan if needed.

    Observability events (yielded by ``run_streaming``)
    ---------------------------------------------------
    ``plan``         – Planner produced / revised a plan.
    ``step_start``   – About to execute a step.
    ``tool_call``    – A tool was invoked (name, input, output, status).
    ``step_result``  – Step execution finished.
    ``critique``     – Critic evaluated a step result.
    ``complete``     – Final result ready.
    ``error``        – An error occurred.
    """

    def __init__(
        self,
        planner: Any,
        executor: Any,
        critic: Any,
        ltm: Any,
        enable_tools: bool = True,
    ) -> None:
        self.planner = planner
        self.executor = executor
        self.critic = critic
        self.ltm = ltm
        self.enable_tools = enable_tools

    # ── Public API ────────────────────────────────────────────────────────────

    def run(self, goal: str) -> List[str]:
        """Run synchronously; collect and return all result strings."""
        results: List[str] = []
        deadline = time.time() + _MAX_RUN_SECONDS

        for event in self.run_streaming(goal):
            if time.time() > deadline:
                logger.error("Run exceeded maximum allowed time (%ds).", _MAX_RUN_SECONDS)
                break
            if event["type"] == "complete":
                results.append(event["result"])
            elif event["type"] == "step_result":
                results.append(event["content"])

        # Deduplicate — complete already contains an aggregated result
        if len(results) > 1 and results[-1] == "\n\n".join(results[:-1]):
            return [results[-1]]
        return results

    def run_streaming(
        self, goal: str
    ) -> Generator[Dict[str, Any], None, None]:
        """Execute the goal and yield structured observability events."""
        deadline = time.time() + _MAX_RUN_SECONDS

        if MAX_ITERATIONS <= 1:
            yield from self._run_simple_mode_streaming(goal, deadline)
        else:
            yield from self._run_full_mode_streaming(goal, deadline)

    # ── Simple mode (MAX_ITERATIONS == 1) ────────────────────────────────────

    def _run_simple_mode_streaming(
        self, goal: str, deadline: float
    ) -> Generator[Dict[str, Any], None, None]:
        prompt = (
            "You are an expert AI assistant. Complete this task comprehensively:\n\n"
            f"Goal: {goal}\n\n"
            "Provide a complete, high-quality solution with:\n"
            "1. Clear steps or implementation\n"
            "2. Best practices and considerations\n"
            "3. Any relevant examples or code\n\n"
            "Be thorough but concise."
        )

        yield {"type": "step_start", "step": goal, "agent": "Executor"}
        result = self.executor.think(prompt)
        try:
            self.ltm.save(f"Goal: {goal}\nResult: {result}")
        except Exception:
            logger.warning("LTM save failed in simple mode — continuing.")
        yield {"type": "step_result", "content": result, "agent": "Executor"}
        yield {"type": "complete", "result": result}

    # ── Full agentic mode (MAX_ITERATIONS >= 2) ───────────────────────────────

    def _run_full_mode_streaming(
        self, goal: str, deadline: float
    ) -> Generator[Dict[str, Any], None, None]:
        # ---- Planning -------------------------------------------------------
        yield {"type": "plan", "content": "Creating execution plan…"}
        plan_text = self.planner.create_plan(goal)
        yield {"type": "plan", "content": plan_text}

        steps = self._parse_steps(plan_text) or [plan_text]
        final_results: List[str] = []
        accumulated_critiques: List[str] = []

        for iteration in range(MAX_ITERATIONS):
            if time.time() > deadline:
                logger.error("Deadline exceeded at iteration %d.", iteration)
                yield {"type": "error", "message": "Execution time limit reached."}
                break

            iter_results: List[str] = []
            iter_critiques: List[str] = []

            for step_idx, step in enumerate(steps):
                if time.time() > deadline:
                    break

                yield {
                    "type": "step_start",
                    "step": step,
                    "agent": "Executor",
                    "iteration": iteration + 1,
                    "step_number": step_idx + 1,
                    "total_steps": len(steps),
                }

                # ---- Execute ------------------------------------------------
                try:
                    if self.enable_tools:
                        result, tool_events = self.executor.execute_task_with_tools(step)
                        # Surface tool invocations individually
                        for ev in tool_events:
                            yield {
                                "type": "tool_call",
                                "tool": ev["tool"],
                                "input": ev["input"],
                                "output": ev["output"],
                                "status": ev["status"],
                            }
                    else:
                        result = self.executor.execute_task(step)
                        tool_events = []
                except Exception as exc:
                    logger.exception("Executor raised an error on step: %s", step)
                    result = f"Error executing step: {exc}"
                    tool_events = []

                yield {"type": "step_result", "content": result, "agent": "Executor"}

                # ---- Critique -----------------------------------------------
                try:
                    critique = self.critic.critique(result)
                except Exception as exc:
                    logger.exception("Critic raised an error.")
                    critique = f"Critique unavailable: {exc}"

                yield {"type": "critique", "content": critique}

                # ---- Refine if critique identifies issues --------------------
                if not self._is_acceptable(critique):
                    try:
                        improved = self.executor.think(
                            f"Improve the result using this critique.\n\n"
                            f"Result:\n{result}\n\nCritique:\n{critique}"
                        )
                        iter_results.append(improved)
                    except Exception:
                        iter_results.append(result)
                    iter_critiques.append(f"Step: {step}\nCritique: {critique}")
                else:
                    iter_results.append(result)

            final_results.extend(iter_results)

            try:
                self.ltm.save(
                    f"Goal: {goal} | Iteration {iteration + 1}\n"
                    + "\n".join(iter_results)
                )
            except Exception:
                logger.warning("LTM save failed — continuing.")

            # ---- Re-plan if there are critiques and more iterations left -----
            if iter_critiques and iteration < MAX_ITERATIONS - 1:
                accumulated_critiques.extend(iter_critiques)
                yield {"type": "plan", "content": "Refining plan based on feedback…"}
                try:
                    new_plan = self.planner.think(
                        self._plan_prompt(goal, "\n".join(accumulated_critiques))
                    )
                    yield {"type": "plan", "content": new_plan}
                    new_steps = self._parse_steps(new_plan)
                    if new_steps:
                        steps = new_steps
                except Exception:
                    logger.warning("Re-planning failed — keeping current steps.")

        final_output = "\n\n".join(final_results)
        yield {"type": "complete", "result": final_output}

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _parse_steps(plan: str) -> List[str]:
        """Extract numbered / bulleted items from a plan string."""
        steps: List[str] = []
        for line in plan.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            match = re.match(r"^(?:\d+[\.\)]\s*|[-*•]\s*)(.*)", stripped)
            if match:
                text = match.group(1).strip()
                if text:
                    steps.append(text)
        return steps

    @staticmethod
    def _plan_prompt(goal: str, accumulated_critiques: str) -> str:
        return (
            "You are a strategic planning agent.\n"
            "Break this goal into clear, executable steps.\n"
            "Be concise and actionable.\n\n"
            f"Goal:\n{goal}\n\n"
            f"Previous iteration feedback:\n{accumulated_critiques}\n\n"
            "Incorporate this feedback into your revised plan.\n\n"
            "Return numbered steps with brief descriptions."
        )

    @staticmethod
    def _is_acceptable(critique: str) -> bool:
        """Return True when the critique signals no significant issues."""
        lowered = critique.lower()
        no_issue_phrases = [
            "no issues",
            "looks good",
            "acceptable",
            "sufficient",
            "satisfactory",
            "no problems",
            "no problem",
            "well done",
            "excellent",
        ]
        if any(phrase in lowered for phrase in no_issue_phrases):
            return True
        return len(critique.strip()) < 30
