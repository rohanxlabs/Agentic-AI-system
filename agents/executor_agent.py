"""Executor agent — runs planned tasks, calling tools when appropriate."""
import json
import logging
from typing import Any, List, Dict, Tuple

from agents.base_agent import BaseAgent
from tools.tool_registry import TOOL_SCHEMAS, execute_tool
from config.config import MAX_TOOL_CALLS

logger = logging.getLogger(__name__)

# Maximum tool-call rounds per task execution (prevents runaway loops)
_MAX_TOOL_ROUNDS = MAX_TOOL_CALLS


class ExecutorAgent(BaseAgent):
    """Agent responsible for executing individual planned tasks.

    Supports two execution modes:

    * ``execute_task``           – plain LLM call, no tools.
    * ``execute_task_with_tools`` – LLM function-calling loop following the
                                    OpenAI / Groq tool-calling protocol exactly:
                                    assistant message carries ``tool_calls``;
                                    each tool result is returned as a separate
                                    ``role="tool"`` message with the matching
                                    ``tool_call_id``.
    """

    # ------------------------------------------------------------------
    # Plain execution (no tools)
    # ------------------------------------------------------------------

    def execute_task(self, task: str) -> str:
        """Execute a task using the LLM without tools.

        Args:
            task: Task description.

        Returns:
            LLM-generated result.
        """
        relevant_memories = self.ltm.recall_relevant(task)
        memory_section = _format_memory_section(relevant_memories)

        prompt = (
            f"{memory_section}"
            "Execute the task below with maximum quality.\n"
            "Be precise and actionable.\n\n"
            f"Task:\n{task}"
        )
        return self.think(prompt)

    # ------------------------------------------------------------------
    # Tool-augmented execution
    # ------------------------------------------------------------------

    def execute_task_with_tools(self, task: str) -> Tuple[str, List[Dict[str, Any]]]:
        """Execute a task with LLM function-calling support.

        Follows the Groq / OpenAI tool-calling protocol precisely:

        1. Send messages to the LLM with tool schemas.
        2. If the LLM requests tool calls, execute each tool and return a
           ``role="tool"`` message per call (with matching ``tool_call_id``).
        3. Repeat up to ``MAX_TOOL_CALLS`` rounds.
        4. When the LLM stops requesting tools, return the final answer.

        Args:
            task: Task description.

        Returns:
            Tuple of (result_text, tool_events) where tool_events is a list of
            dicts describing each tool invocation for observability::

                {"tool": str, "input": str, "output": str, "status": str}
        """
        relevant_memories = self.ltm.recall_relevant(task)
        memory_section = _format_memory_section(relevant_memories)

        user_content = (
            f"{memory_section}"
            "Execute the task below with maximum quality.\n"
            "Be precise and actionable. Use the available tools when needed.\n\n"
            f"Task:\n{task}"
        )

        messages: List[Dict[str, Any]] = [{"role": "user", "content": user_content}]
        tool_events: List[Dict[str, Any]] = []

        for round_num in range(_MAX_TOOL_ROUNDS):
            logger.debug("Tool round %d/%d for task: %s", round_num + 1, _MAX_TOOL_ROUNDS, task[:60])

            response = self.llm.call_with_tools(messages, TOOL_SCHEMAS)

            # No more tool calls → final answer
            if not response["tool_calls"]:
                final_content = response["content"] or "No response generated"
                self.stm.add(f"Executor: {final_content}")
                return final_content, tool_events

            # ---- Build assistant message (must include tool_calls with id) ----
            tool_calls_for_message = [
                {
                    "id": tc["id"],
                    "type": "function",
                    "function": {
                        "name": tc["name"],
                        "arguments": json.dumps(tc["arguments"]),
                    },
                }
                for tc in response["tool_calls"]
            ]
            assistant_message: Dict[str, Any] = {
                "role": "assistant",
                "content": response["content"],   # may be None — that is valid
                "tool_calls": tool_calls_for_message,
            }
            messages.append(assistant_message)

            # ---- Execute each tool and append role="tool" result messages ----
            for tc in response["tool_calls"]:
                tool_name = tc["name"]
                tool_args = tc["arguments"]
                tool_call_id = tc["id"]

                logger.info("Executing tool '%s' with args: %s", tool_name, tool_args)
                result = execute_tool(tool_name, tool_args)
                status = "error" if str(result).startswith("Error") else "ok"

                tool_events.append(
                    {
                        "tool": tool_name,
                        "input": json.dumps(tool_args),
                        "output": result,
                        "status": status,
                    }
                )
                logger.info("Tool '%s' result (%s): %s", tool_name, status, result[:200])

                # role="tool" is required by the Groq/OpenAI protocol
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "content": result,
                    }
                )

        # Exhausted max rounds — ask the LLM to summarise from what it has
        logger.warning("Tool round limit (%d) reached for task: %s", _MAX_TOOL_ROUNDS, task[:60])
        summary_messages = messages + [
            {
                "role": "user",
                "content": "Provide your final answer based on the tool results above.",
            }
        ]
        # Plain call to avoid another tool loop
        final_result = self.llm.call(
            "\n".join(
                m["content"]
                for m in summary_messages
                if m.get("content") and m["role"] in ("user", "tool")
            )
        )
        self.stm.add(f"Executor: {final_result}")
        return final_result, tool_events


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _format_memory_section(relevant_memories: List[str]) -> str:
    if not relevant_memories:
        return ""
    lines = "\n".join(relevant_memories)
    return (
        "Relevant past experience (context only — do not simply repeat it):\n"
        f"{lines}\n\n"
    )
