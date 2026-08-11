"""Tool registry — schema definitions, argument validation, and safe dispatch.

Security model
--------------
* Only tools on the TOOL_ALLOWLIST can be invoked — the LLM cannot call
  arbitrary functions.
* Each tool's arguments are validated against a per-tool spec before dispatch.
* String arguments are capped at MAX_ARG_LENGTH characters to prevent
  prompt-injection payloads from being forwarded to external services.
* All tool results are capped at MAX_RESULT_LENGTH characters so that a
  pathological external result cannot overflow the LLM context.
* Exceptions are caught and returned as error strings — they never propagate
  to the agent loop as unhandled exceptions.
"""
import logging
from typing import Any, Dict, List

from tools.calculator import calculate
from tools.web_search import search

logger = logging.getLogger(__name__)

# Hard limits applied to all tool I/O
MAX_ARG_LENGTH = 512      # characters — per string argument
MAX_RESULT_LENGTH = 2000  # characters — per tool result


# ── Tool allowlist ────────────────────────────────────────────────────────────
# Only names in this set can be dispatched.  Adding a new tool requires
# an explicit entry here AND a schema entry in TOOL_SCHEMAS.
TOOL_ALLOWLIST = {"web_search", "calculator"}


# ── OpenAI / Groq compatible schemas ─────────────────────────────────────────
TOOL_SCHEMAS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": (
                "Search the web for current, factual information. "
                "Use for questions about recent events, current data, or "
                "topics that require up-to-date knowledge."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Concise search query (max 200 characters)",
                        "maxLength": 200,
                    }
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": (
                "Evaluate a basic arithmetic expression safely. "
                "Supports: numbers, +, -, *, /, ** (power), parentheses, "
                "and unary minus. Does NOT support function calls or variables."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Arithmetic expression to evaluate (e.g. '(3 + 5) * 2')",
                        "maxLength": 200,
                    }
                },
                "required": ["expression"],
                "additionalProperties": False,
            },
        },
    },
]


# ── Per-tool argument validators ──────────────────────────────────────────────

def _validate_web_search_args(arguments: Dict[str, Any]) -> str:
    """Return the validated query string or raise ValueError."""
    query = arguments.get("query", "")
    if not isinstance(query, str):
        raise ValueError("'query' must be a string")
    query = query.strip()
    if not query:
        raise ValueError("'query' cannot be empty")
    return query[:MAX_ARG_LENGTH]  # hard cap


def _validate_calculator_args(arguments: Dict[str, Any]) -> str:
    """Return the validated expression string or raise ValueError."""
    expression = arguments.get("expression", "")
    if not isinstance(expression, str):
        raise ValueError("'expression' must be a string")
    expression = expression.strip()
    if not expression:
        raise ValueError("'expression' cannot be empty")
    return expression[:MAX_ARG_LENGTH]  # hard cap


# ── Dispatch table ────────────────────────────────────────────────────────────

_DISPATCH = {
    "web_search": (
        _validate_web_search_args,
        lambda q: search(q),
    ),
    "calculator": (
        _validate_calculator_args,
        lambda e: calculate(e),
    ),
}


# ── Public entry point ────────────────────────────────────────────────────────

def execute_tool(name: str, arguments: Dict[str, Any]) -> str:
    """Execute a tool by name with validated arguments.

    Args:
        name:      Tool name — must be in TOOL_ALLOWLIST.
        arguments: Argument dict from the LLM's tool call.

    Returns:
        Tool result string (capped at MAX_RESULT_LENGTH), or an
        ``"Error: ..."`` string if anything goes wrong.  Never raises.
    """
    # Allowlist check
    if name not in TOOL_ALLOWLIST:
        logger.warning("Blocked unknown tool: %r", name)
        return f"Error: Tool '{name}' is not available"

    if name not in _DISPATCH:
        return f"Error: Tool '{name}' is registered but has no handler"

    validator, handler = _DISPATCH[name]

    # Validate arguments
    try:
        validated_arg = validator(arguments)
    except ValueError as exc:
        logger.warning("Tool '%s' argument validation failed: %s", name, exc)
        return f"Error: Invalid arguments for tool '{name}': {exc}"

    # Execute with a hard result length cap
    try:
        result = handler(validated_arg)
        if len(result) > MAX_RESULT_LENGTH:
            result = result[:MAX_RESULT_LENGTH] + "\n[result truncated]"
        return result
    except Exception as exc:
        logger.error("Tool '%s' raised an unexpected exception: %s", name, exc)
        return f"Error: Tool '{name}' failed unexpectedly: {exc}"
