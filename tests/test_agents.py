"""Tests for agent classes — LLM is fully mocked, no API calls."""
import pytest
from unittest.mock import MagicMock, patch, call

from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory
from agents.base_agent import BaseAgent
from agents.planner_agent import PlannerAgent
from agents.executor_agent import ExecutorAgent
from agents.critic_agent import CriticAgent
from agents.manager_agent import ManagerAgent


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_llm():
    llm = MagicMock()
    llm.call.return_value = "mocked LLM response"
    llm.call_with_tools.return_value = {"content": "mocked answer", "tool_calls": []}
    return llm


@pytest.fixture
def mock_stm():
    stm = MagicMock(spec=ShortTermMemory)
    stm.get.return_value = ""
    return stm


@pytest.fixture
def mock_ltm():
    ltm = MagicMock(spec=LongTermMemory)
    ltm.recall_relevant.return_value = []
    ltm.save.return_value = None
    return ltm


# ── BaseAgent ─────────────────────────────────────────────────────────────────

class TestBaseAgent:
    def test_think_calls_llm(self, mock_llm, mock_stm, mock_ltm):
        agent = BaseAgent("TestAgent", mock_llm, mock_stm, mock_ltm)
        result = agent.think("do something", use_memory=False)
        mock_llm.call.assert_called_once()
        assert result == "mocked LLM response"

    def test_think_stores_response_in_stm(self, mock_llm, mock_stm, mock_ltm):
        agent = BaseAgent("TestAgent", mock_llm, mock_stm, mock_ltm)
        agent.think("do something", use_memory=False)
        mock_stm.add.assert_called_once()
        stored = mock_stm.add.call_args[0][0]
        assert "TestAgent" in stored
        assert "mocked LLM response" in stored

    def test_think_prepends_stm_context_when_use_memory_true(
        self, mock_llm, mock_stm, mock_ltm
    ):
        mock_stm.get.return_value = "recent context"
        agent = BaseAgent("TestAgent", mock_llm, mock_stm, mock_ltm)
        agent.think("user prompt", use_memory=True)
        prompt_used = mock_llm.call.call_args[0][0]
        assert "recent context" in prompt_used
        assert "user prompt" in prompt_used

    def test_think_no_context_when_stm_empty(self, mock_llm, mock_stm, mock_ltm):
        mock_stm.get.return_value = ""
        agent = BaseAgent("TestAgent", mock_llm, mock_stm, mock_ltm)
        agent.think("plain prompt", use_memory=True)
        prompt_used = mock_llm.call.call_args[0][0]
        assert "recent context" not in prompt_used


# ── PlannerAgent ──────────────────────────────────────────────────────────────

class TestPlannerAgent:
    def test_create_plan_returns_llm_output(self, mock_llm, mock_stm, mock_ltm):
        mock_llm.call.return_value = "1. Step one\n2. Step two"
        planner = PlannerAgent("Planner", mock_llm, mock_stm, mock_ltm)
        plan = planner.create_plan("build a website")
        assert "Step one" in plan or "1." in plan

    def test_create_plan_includes_goal_in_prompt(self, mock_llm, mock_stm, mock_ltm):
        planner = PlannerAgent("Planner", mock_llm, mock_stm, mock_ltm)
        planner.create_plan("my unique goal 12345")
        prompt = mock_llm.call.call_args[0][0]
        assert "my unique goal 12345" in prompt

    def test_create_plan_includes_relevant_memories(self, mock_llm, mock_stm, mock_ltm):
        mock_ltm.recall_relevant.return_value = ["Past: solved similar problem"]
        planner = PlannerAgent("Planner", mock_llm, mock_stm, mock_ltm)
        planner.create_plan("build something")
        prompt = mock_llm.call.call_args[0][0]
        assert "Past: solved similar problem" in prompt

    def test_create_plan_handles_ltm_failure(self, mock_llm, mock_stm, mock_ltm):
        mock_ltm.recall_relevant.side_effect = Exception("LTM failure")
        planner = PlannerAgent("Planner", mock_llm, mock_stm, mock_ltm)
        # Should not raise — LTM failure is handled gracefully
        plan = planner.create_plan("some goal")
        assert isinstance(plan, str)


# ── ExecutorAgent ─────────────────────────────────────────────────────────────

class TestExecutorAgent:
    def test_execute_task_returns_llm_output(self, mock_llm, mock_stm, mock_ltm):
        executor = ExecutorAgent("Executor", mock_llm, mock_stm, mock_ltm)
        result = executor.execute_task("write hello world")
        assert result == "mocked LLM response"

    def test_execute_task_with_tools_no_tool_calls(self, mock_llm, mock_stm, mock_ltm):
        mock_llm.call_with_tools.return_value = {
            "content": "42 is the answer",
            "tool_calls": [],
        }
        executor = ExecutorAgent("Executor", mock_llm, mock_stm, mock_ltm)
        result, tool_events = executor.execute_task_with_tools("what is 6*7?")
        assert result == "42 is the answer"
        assert tool_events == []

    def test_execute_task_with_tools_calls_tool(self, mock_llm, mock_stm, mock_ltm):
        """Executor should call execute_tool when LLM requests a tool."""
        mock_llm.call_with_tools.side_effect = [
            # Round 1: LLM requests calculator
            {
                "content": None,
                "tool_calls": [
                    {"id": "call_abc", "name": "calculator", "arguments": {"expression": "6*7"}}
                ],
            },
            # Round 2: LLM gives final answer
            {"content": "The answer is 42", "tool_calls": []},
        ]
        executor = ExecutorAgent("Executor", mock_llm, mock_stm, mock_ltm)

        with patch("agents.executor_agent.execute_tool", return_value="42") as mock_exec:
            result, tool_events = executor.execute_task_with_tools("what is 6*7?")

        mock_exec.assert_called_once_with("calculator", {"expression": "6*7"})
        assert result == "The answer is 42"
        assert len(tool_events) == 1
        assert tool_events[0]["tool"] == "calculator"
        assert tool_events[0]["output"] == "42"
        assert tool_events[0]["status"] == "ok"

    def test_execute_task_with_tools_correct_protocol(self, mock_llm, mock_stm, mock_ltm):
        """Second LLM call must include role='tool' message with tool_call_id."""
        tool_call_id = "call_xyz_123"
        mock_llm.call_with_tools.side_effect = [
            {
                "content": None,
                "tool_calls": [
                    {"id": tool_call_id, "name": "calculator", "arguments": {"expression": "1+1"}}
                ],
            },
            {"content": "Result is 2", "tool_calls": []},
        ]
        executor = ExecutorAgent("Executor", mock_llm, mock_stm, mock_ltm)

        with patch("agents.executor_agent.execute_tool", return_value="2"):
            executor.execute_task_with_tools("1+1")

        # Inspect the second call's messages
        second_call_messages = mock_llm.call_with_tools.call_args_list[1][0][0]
        tool_result_messages = [m for m in second_call_messages if m.get("role") == "tool"]
        assert len(tool_result_messages) == 1
        assert tool_result_messages[0]["tool_call_id"] == tool_call_id
        assert tool_result_messages[0]["content"] == "2"

    def test_execute_task_with_tools_error_tool_result(self, mock_llm, mock_stm, mock_ltm):
        """A tool returning an error string should mark event status='error'."""
        mock_llm.call_with_tools.side_effect = [
            {
                "content": None,
                "tool_calls": [
                    {"id": "call_1", "name": "calculator", "arguments": {"expression": "1/0"}}
                ],
            },
            {"content": "Cannot divide by zero", "tool_calls": []},
        ]
        executor = ExecutorAgent("Executor", mock_llm, mock_stm, mock_ltm)

        with patch("agents.executor_agent.execute_tool", return_value="Error: Division by zero"):
            _, tool_events = executor.execute_task_with_tools("compute 1/0")

        assert tool_events[0]["status"] == "error"

    def test_execute_task_with_tools_max_rounds_respected(
        self, mock_llm, mock_stm, mock_ltm
    ):
        """Executor must stop after MAX_TOOL_CALLS rounds even if LLM keeps requesting tools."""
        # Each call returns a new tool request — use a counter to generate unique IDs
        call_counter = [0]

        def always_calls_tool(*args, **kwargs):
            call_counter[0] += 1
            return {
                "content": None,
                "tool_calls": [
                    {
                        "id": f"call_{call_counter[0]}",
                        "name": "calculator",
                        "arguments": {"expression": "1+1"},
                    }
                ],
            }

        mock_llm.call_with_tools.side_effect = always_calls_tool
        mock_llm.call.return_value = "fallback answer"

        executor = ExecutorAgent("Executor", mock_llm, mock_stm, mock_ltm)

        with patch("agents.executor_agent.execute_tool", return_value="2"):
            result, tool_events = executor.execute_task_with_tools("infinite tools")

        from config.config import MAX_TOOL_CALLS
        assert mock_llm.call_with_tools.call_count <= MAX_TOOL_CALLS


# ── CriticAgent ───────────────────────────────────────────────────────────────

class TestCriticAgent:
    def test_critique_returns_llm_output(self, mock_llm, mock_stm, mock_ltm):
        critic = CriticAgent("Critic", mock_llm, mock_stm, mock_ltm)
        result = critic.critique("some output")
        assert isinstance(result, str)

    def test_critique_includes_output_in_prompt(self, mock_llm, mock_stm, mock_ltm):
        critic = CriticAgent("Critic", mock_llm, mock_stm, mock_ltm)
        critic.critique("specific output to review")
        prompt = mock_llm.call.call_args[0][0]
        assert "specific output to review" in prompt

    def test_critique_does_not_use_stm(self, mock_llm, mock_stm, mock_ltm):
        """Critic always reviews in isolation — no STM context."""
        mock_stm.get.return_value = "some prior context"
        critic = CriticAgent("Critic", mock_llm, mock_stm, mock_ltm)
        critic.critique("output")
        prompt = mock_llm.call.call_args[0][0]
        # STM context should not appear in the prompt
        assert "some prior context" not in prompt


# ── ManagerAgent ──────────────────────────────────────────────────────────────

class TestManagerAgent:
    def _make_manager(self, mock_llm, mock_stm, mock_ltm, max_iters=1):
        planner = PlannerAgent("Planner", mock_llm, mock_stm, mock_ltm)
        executor = ExecutorAgent("Executor", mock_llm, mock_stm, mock_ltm)
        critic = CriticAgent("Critic", mock_llm, mock_stm, mock_ltm)
        with patch("agents.manager_agent.MAX_ITERATIONS", max_iters):
            manager = ManagerAgent(planner, executor, critic, mock_ltm, enable_tools=False)
        return manager

    def test_run_simple_mode_returns_result(self, mock_llm, mock_stm, mock_ltm):
        mock_llm.call.return_value = "simple mode result"
        with patch("agents.manager_agent.MAX_ITERATIONS", 1):
            manager = ManagerAgent(
                PlannerAgent("P", mock_llm, mock_stm, mock_ltm),
                ExecutorAgent("E", mock_llm, mock_stm, mock_ltm),
                CriticAgent("C", mock_llm, mock_stm, mock_ltm),
                mock_ltm,
                enable_tools=False,
            )
            results = manager.run("simple task")
        assert any("simple mode result" in r for r in results)

    def test_run_streaming_yields_complete_event(self, mock_llm, mock_stm, mock_ltm):
        mock_llm.call.return_value = "streaming result"
        with patch("agents.manager_agent.MAX_ITERATIONS", 1):
            manager = ManagerAgent(
                PlannerAgent("P", mock_llm, mock_stm, mock_ltm),
                ExecutorAgent("E", mock_llm, mock_stm, mock_ltm),
                CriticAgent("C", mock_llm, mock_stm, mock_ltm),
                mock_ltm,
                enable_tools=False,
            )
            events = list(manager.run_streaming("test goal"))

        event_types = [e["type"] for e in events]
        assert "complete" in event_types

    def test_run_streaming_yields_step_result(self, mock_llm, mock_stm, mock_ltm):
        mock_llm.call.return_value = "step output"
        with patch("agents.manager_agent.MAX_ITERATIONS", 1):
            manager = ManagerAgent(
                PlannerAgent("P", mock_llm, mock_stm, mock_ltm),
                ExecutorAgent("E", mock_llm, mock_stm, mock_ltm),
                CriticAgent("C", mock_llm, mock_stm, mock_ltm),
                mock_ltm,
                enable_tools=False,
            )
            events = list(manager.run_streaming("test goal"))

        step_results = [e for e in events if e["type"] == "step_result"]
        assert len(step_results) >= 1

    def test_full_mode_plan_step_critique_cycle(self, mock_llm, mock_stm, mock_ltm):
        """Full agentic mode (MAX_ITERATIONS>=2) must emit step_start, step_result, critique, complete."""
        # Responses: planner plan, executor x1, critic x1
        call_responses = [
            "1. Do the thing",            # planner create_plan → think()
            "thing done",                  # executor execute_task → think()
            "No issues — looks good.",    # critic critique → think()
        ]
        mock_llm.call.side_effect = call_responses

        with patch("agents.manager_agent.MAX_ITERATIONS", 2):  # Full mode needs >=2
            manager = ManagerAgent(
                PlannerAgent("P", mock_llm, mock_stm, mock_ltm),
                ExecutorAgent("E", mock_llm, mock_stm, mock_ltm),
                CriticAgent("C", mock_llm, mock_stm, mock_ltm),
                mock_ltm,
                enable_tools=False,
            )
            events = list(manager.run_streaming("build a thing"))

        types = [e["type"] for e in events]
        assert "step_start" in types
        assert "step_result" in types
        assert "critique" in types
        assert "complete" in types

    def test_parse_steps_numbered_list(self):
        plan = "1. First step\n2. Second step\n3. Third step"
        steps = ManagerAgent._parse_steps(plan)
        assert steps == ["First step", "Second step", "Third step"]

    def test_parse_steps_bullet_list(self):
        plan = "- Alpha\n- Beta\n* Gamma"
        steps = ManagerAgent._parse_steps(plan)
        assert steps == ["Alpha", "Beta", "Gamma"]

    def test_parse_steps_empty_plan(self):
        assert ManagerAgent._parse_steps("") == []

    def test_parse_steps_no_bullets(self):
        assert ManagerAgent._parse_steps("just prose") == []

    def test_is_acceptable_no_issues_phrase(self):
        assert ManagerAgent._is_acceptable("No issues — looks good.") is True

    def test_is_acceptable_looks_good(self):
        assert ManagerAgent._is_acceptable("Looks good to me.") is True

    def test_is_acceptable_has_critique(self):
        assert ManagerAgent._is_acceptable(
            "The answer is missing error handling and edge cases."
        ) is False

    def test_is_acceptable_short_critique(self):
        # Less than 30 chars → treated as acceptable (no real issue)
        assert ManagerAgent._is_acceptable("ok") is True

    def test_ltm_save_failure_does_not_crash_run(self, mock_llm, mock_stm, mock_ltm):
        mock_ltm.save.side_effect = Exception("disk full")
        mock_llm.call.return_value = "result despite ltm failure"
        with patch("agents.manager_agent.MAX_ITERATIONS", 1):
            manager = ManagerAgent(
                PlannerAgent("P", mock_llm, mock_stm, mock_ltm),
                ExecutorAgent("E", mock_llm, mock_stm, mock_ltm),
                CriticAgent("C", mock_llm, mock_stm, mock_ltm),
                mock_ltm,
                enable_tools=False,
            )
            results = manager.run("task")
        assert len(results) >= 1
