"""Quick import and isolation verification — run after fixes."""
import sys
sys.path.insert(0, ".")

from config.config import MAX_ITERATIONS, MAX_TOOL_CALLS
print(f"MAX_ITERATIONS = {MAX_ITERATIONS}")
print(f"MAX_TOOL_CALLS = {MAX_TOOL_CALLS}")

from llm.groq_llm import GroqLLM, LLMError
print(f"LLMError importable: {LLMError}")

from agents.executor_agent import ExecutorAgent
from agents.planner_agent import PlannerAgent
from agents.critic_agent import CriticAgent
from agents.manager_agent import ManagerAgent
print("All agent imports OK")

from session.session_manager import session_store, _SESSION_LTM_DIR
print(f"Session LTM dir: {_SESSION_LTM_DIR}")

sid1, s1 = session_store.get_or_create()
sid2, s2 = session_store.get_or_create()
assert id(s1["ltm"]) != id(s2["ltm"]), "LTM not isolated!"
assert id(s1["stm"]) != id(s2["stm"]), "STM not isolated!"
print("LTM isolated: True")
print("STM isolated: True")

from tools.tool_registry import execute_tool, TOOL_SCHEMAS
result = execute_tool("calculator", {"expression": "2+2"})
assert result == "4", f"Calculator returned: {result}"
print(f"calculator(2+2) = {result}")

print("\nAll verification checks passed.")
