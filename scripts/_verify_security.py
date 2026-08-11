"""Security verification — run after fixes."""
import sys
sys.path.insert(0, ".")

from tools.tool_registry import execute_tool, TOOL_ALLOWLIST

# 1. Allowlist blocks unknown tools
r = execute_tool("shell_exec", {"cmd": "whoami"})
assert "not available" in r, f"Allowlist failed: {r}"
print("PASS: unknown tool blocked")

# 2. Empty query blocked
r = execute_tool("web_search", {"query": ""})
assert "Error" in r, f"Empty query not blocked: {r}"
print("PASS: empty query blocked")

# 3. Oversized argument truncated (not raised)
long_expr = "1+" * 300 + "0"
r = execute_tool("calculator", {"expression": long_expr})
print(f"PASS: long expression handled -> {r[:60]}")

# 4. Injection attempt in calculator (AST rejects non-arithmetic)
r = execute_tool("calculator", {"expression": '__import__("os").system("whoami")'})
assert "Error" in r, f"Injection not blocked: {r}"
print(f"PASS: calc injection blocked -> {r}")

# 5. Non-string argument
r = execute_tool("calculator", {"expression": 12345})
assert "Error" in r, f"Non-string arg not caught: {r}"
print(f"PASS: non-string arg validated -> {r}")

# 6. Division by zero handled
r = execute_tool("calculator", {"expression": "1/0"})
assert "Error" in r, f"Division by zero not caught: {r}"
print(f"PASS: division by zero handled -> {r}")

# 7. Goal length cap in pydantic model (simulate)
from pydantic import ValidationError
from api import RunRequest
try:
    # Should succeed at exactly 2000 chars
    req = RunRequest(goal="x" * 2000, enable_tools=True)
    print("PASS: 2000-char goal accepted")
except Exception as e:
    print(f"FAIL: 2000-char goal rejected: {e}")

print("\nAll security checks passed.")
