"""Tool registry for LLM function calling."""
from typing import List, Dict, Any

from tools.web_search import search
from tools.calculator import calculate


# OpenAI/Groq compatible tool schemas
TOOL_SCHEMAS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for current information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to execute"
                    }
                },
                "required": ["query"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Evaluate a basic arithmetic expression safely.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The arithmetic expression to evaluate (supports numbers, +, -, *, /, **, parentheses)"
                    }
                },
                "required": ["expression"],
                "additionalProperties": False
            }
        }
    }
]


def execute_tool(name: str, arguments: Dict[str, Any]) -> str:
    """Execute a tool by name with the provided arguments.
    
    Args:
        name: Name of the tool to execute
        arguments: Dictionary of arguments to pass to the tool
        
    Returns:
        String result from tool execution, or error message if tool not found
    """
    tool_dispatch = {
        "web_search": lambda args: search(args.get("query", "")),
        "calculator": lambda args: calculate(args.get("expression", ""))
    }
    
    if name not in tool_dispatch:
        return f"Error: Tool '{name}' not found"
    
    try:
        return tool_dispatch[name](arguments)
    except Exception as e:
        return f"Error executing tool '{name}': {str(e)}"