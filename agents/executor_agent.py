"""Executor agent for performing tasks."""
from typing import Any
from agents.base_agent import BaseAgent
from tools.tool_registry import TOOL_SCHEMAS, execute_tool


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

    def execute_task_with_tools(self, task: str) -> str:
        """Execute a task with tool calling capabilities.
        
        Args:
            task: Task description to execute
            
        Returns:
            Task execution result
        """
        max_rounds = 3
        messages = [{"role": "user", "content": f"""Execute the task below with maximum quality.
Be precise and actionable. Use tools if necessary.

Task:
{task}
"""}]
        
        for round_num in range(max_rounds):
            response = self.llm.call_with_tools(messages[-1]["content"], TOOL_SCHEMAS)
            
            if not response["tool_calls"]:
                final_content = response["content"] or "No response generated"
                self.stm.add(f"Executor: {final_content}")
                return final_content
            
            # Execute all tool calls
            tool_results = []
            for tool_call in response["tool_calls"]:
                result = execute_tool(tool_call["name"], tool_call["arguments"])
                tool_results.append(f"Tool {tool_call['name']} result:\n{result}")
            
            # Append tool results to the conversation
            messages.append({
                "role": "user",
                "content": messages[-1]["content"] + "\n\n" + "\n".join(tool_results)
            })
        
        # If we hit max rounds, generate final response with accumulated tool results
        final_prompt = messages[-1]["content"] + "\n\nProvide your final answer based on the information above."
        final_result = self.think(final_prompt)
        return final_result