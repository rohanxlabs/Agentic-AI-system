"""Executor agent for performing tasks."""
from typing import Any, List, Dict
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
        relevant_memories = self.ltm.recall_relevant(task)
        memory_section = ""
        
        if relevant_memories:
            memory_section = "Relevant past experience (for context only, don't just repeat it):\n"
            memory_section += "\n".join(relevant_memories) + "\n\n"
        
        prompt = f"""{memory_section}Execute the task below with maximum quality.
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
        relevant_memories = self.ltm.recall_relevant(task)
        memory_section = ""
        
        if relevant_memories:
            memory_section = "Relevant past experience (for context only, don't just repeat it):\n"
            memory_section += "\n".join(relevant_memories) + "\n\n"
            
        user_content = f"""{memory_section}Execute the task below with maximum quality.
Be precise and actionable. Use tools if necessary.

Task:
{task}
"""
        messages: List[Dict[str, Any]] = [{"role": "user", "content": user_content}]
        
        for round_num in range(max_rounds):
            response = self.llm.call_with_tools(messages, TOOL_SCHEMAS)
            
            if not response["tool_calls"]:
                final_content = response["content"] or "No response generated"
                self.stm.add(f"Executor: {final_content}")
                return final_content
            
            tool_calls = response["tool_calls"]
            assistant_message: Dict[str, Any] = {
                "role": "assistant",
                "content": response["content"],
                "tool_calls": [
                    {
                        "type": "function",
                        "function": {
                            "name": tc["name"],
                            "arguments": __import__("json").dumps(tc["arguments"])
                        }
                    }
                    for tc in tool_calls
                ]
            }
            messages.append(assistant_message)
            
            tool_results: List[str] = []
            for tool_call in tool_calls:
                result = execute_tool(tool_call["name"], tool_call["arguments"])
                tool_results.append(f"Tool {tool_call['name']} result:\n{result}")
            
            messages.append({
                "role": "user",
                "content": "\n\n".join(tool_results)
            })
        
        final_prompt = messages[-1]["content"] + "\n\nProvide your final answer based on the information above."
        final_result = self.think(final_prompt)
        self.stm.add(f"Executor: {final_result}")
        return final_result