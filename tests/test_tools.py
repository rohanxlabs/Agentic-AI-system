"""Tests for the tool system — no LLM calls, no network calls."""
import pytest
from tools.calculator import calculate
from tools.tool_registry import execute_tool, TOOL_ALLOWLIST, MAX_ARG_LENGTH, MAX_RESULT_LENGTH


# ── Calculator ────────────────────────────────────────────────────────────────

class TestCalculator:
    def test_addition(self):
        assert calculate("2 + 2") == "4"

    def test_subtraction(self):
        assert calculate("10 - 3") == "7"

    def test_multiplication(self):
        assert calculate("6 * 7") == "42"

    def test_division(self):
        assert calculate("10 / 4") == "2.5"

    def test_integer_result(self):
        assert calculate("9 / 3") == "3"

    def test_power(self):
        assert calculate("2 ** 10") == "1024"

    def test_parentheses(self):
        assert calculate("(3 + 5) * 2") == "16"

    def test_unary_minus(self):
        assert calculate("-5 + 10") == "5"

    def test_chained(self):
        result = calculate("1 + 2 * 3 - 4 / 2")
        # Python evaluates: 1 + 6 - 2 = 5 (whole number)
        assert result == "5"

    def test_division_by_zero(self):
        result = calculate("1 / 0")
        assert "Error" in result
        assert "zero" in result.lower()

    def test_empty_expression(self):
        result = calculate("")
        assert "Error" in result

    def test_whitespace_only(self):
        result = calculate("   ")
        assert "Error" in result

    def test_invalid_syntax(self):
        result = calculate("2 ++ 2")
        assert "Error" in result

    def test_no_function_calls(self):
        """AST evaluator must reject function calls."""
        result = calculate("abs(-5)")
        assert "Error" in result

    def test_no_attribute_access(self):
        result = calculate("(1).__class__")
        assert "Error" in result

    def test_no_import_injection(self):
        result = calculate('__import__("os").system("whoami")')
        assert "Error" in result

    def test_string_constants_rejected(self):
        result = calculate('"hello"')
        assert "Error" in result

    def test_large_number(self):
        result = calculate("999999 * 999999")
        assert result == "999998000001"


# ── Tool registry ─────────────────────────────────────────────────────────────

class TestToolRegistry:
    def test_allowlist_blocks_unknown_tool(self):
        result = execute_tool("shell_exec", {"cmd": "whoami"})
        assert "not available" in result

    def test_allowlist_blocks_exec(self):
        result = execute_tool("exec", {"code": "import os"})
        assert "not available" in result

    def test_calculator_dispatched(self):
        result = execute_tool("calculator", {"expression": "2 + 2"})
        assert result == "4"

    def test_calculator_empty_expression(self):
        result = execute_tool("calculator", {"expression": ""})
        assert "Error" in result

    def test_calculator_non_string_expression(self):
        result = execute_tool("calculator", {"expression": 42})
        assert "Error" in result

    def test_calculator_missing_expression_key(self):
        result = execute_tool("calculator", {})
        assert "Error" in result

    def test_web_search_empty_query(self):
        result = execute_tool("web_search", {"query": ""})
        assert "Error" in result

    def test_web_search_non_string_query(self):
        result = execute_tool("web_search", {"query": 123})
        assert "Error" in result

    def test_web_search_missing_query_key(self):
        result = execute_tool("web_search", {})
        assert "Error" in result

    def test_arg_length_cap(self):
        """Arguments over MAX_ARG_LENGTH should be truncated, not raise."""
        long_input = "x" * (MAX_ARG_LENGTH + 100)
        # calculator will fail on non-numeric input but must not raise an exception
        result = execute_tool("calculator", {"expression": long_input})
        assert isinstance(result, str)

    def test_result_length_cap(self):
        """A pathologically large result must be truncated."""
        # The calculator won't produce huge output, so patch the handler
        from unittest.mock import patch
        huge_str = "A" * (MAX_RESULT_LENGTH + 500)
        with patch("tools.tool_registry._DISPATCH", {
            "calculator": (
                lambda args: args.get("expression", ""),
                lambda e: huge_str,
            )
        }):
            # Must be capped
            result = execute_tool("calculator", {"expression": "test"})
            assert len(result) <= MAX_RESULT_LENGTH + len("\n[result truncated]") + 5

    def test_all_schema_tools_in_allowlist(self):
        """Every tool with a schema must be in the allowlist."""
        from tools.tool_registry import TOOL_SCHEMAS
        for schema in TOOL_SCHEMAS:
            name = schema["function"]["name"]
            assert name in TOOL_ALLOWLIST, f"Tool '{name}' has schema but is not in allowlist"


# ── Web search sanitiser ──────────────────────────────────────────────────────

class TestWebSearchSanitiser:
    def test_empty_query(self):
        from tools.web_search import search
        result = search("")
        assert "Error" in result

    def test_whitespace_query(self):
        from tools.web_search import search
        result = search("   ")
        assert "Error" in result

    def test_sanitise_helper_strips_control_chars(self):
        from tools.web_search import _sanitise
        dirty = "Hello\x00\x07World\x1f"
        clean = _sanitise(dirty, 100)
        assert "\x00" not in clean
        assert "\x07" not in clean
        assert "Hello" in clean
        assert "World" in clean

    def test_sanitise_helper_caps_length(self):
        from tools.web_search import _sanitise
        long_text = "A" * 300
        result = _sanitise(long_text, 50)
        assert len(result) <= 53  # 50 + "..."

    def test_sanitise_url_rejects_non_http(self):
        from tools.web_search import _sanitise_url
        assert _sanitise_url("javascript:alert(1)") == ""
        assert _sanitise_url("file:///etc/passwd") == ""
        assert _sanitise_url("ftp://example.com") == ""

    def test_sanitise_url_accepts_https(self):
        from tools.web_search import _sanitise_url
        url = "https://example.com/path"
        assert _sanitise_url(url) == url

    def test_sanitise_url_accepts_http(self):
        from tools.web_search import _sanitise_url
        url = "http://example.com"
        assert _sanitise_url(url) == url
