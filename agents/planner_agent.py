"""Planner agent for breaking down goals into executable steps."""
from typing import Any
from agents.base_agent import BaseAgent


class PlannerAgent(BaseAgent):
    """Agent responsible for creating plans from goals."""

    def create_plan(self, goal: str) -> str:
        """Create a detailed plan from a goal.
        
        Args:
            goal: The objective to plan for
            
        Returns:
            Numbered steps as a string
        """
        # Retrieve relevant past memories
        relevant_memories = self.ltm.recall_relevant(goal)
        memory_section = ""
        
        if relevant_memories:
            memory_section = "Relevant past experience (for context only, don't just repeat it):\n"
            memory_section += "\n".join(relevant_memories) + "\n\n"
        
        prompt = f"""{memory_section}You are a strategic planning agent.
Break this goal into clear, executable steps.
Be concise and actionable.

Goal:
{goal}

Return numbered steps with brief descriptions.
"""
        return self.think(prompt)