"""Configuration module for the Agentic AI System.

All values are read from environment variables (via .env) so nothing is
hard-coded.  Sensitive values such as API keys must NEVER be committed.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── LLM ──────────────────────────────────────────────────────────────────────
MODEL_NAME: str = os.getenv("MODEL_NAME", "llama-3.1-8b-instant")
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.3"))
MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "2048"))

# ── Agent loop ────────────────────────────────────────────────────────────────
# MAX_ITERATIONS=1 → simple (single LLM call) mode — useful for demos with
#   tight rate-limit budgets.
# MAX_ITERATIONS>=2 → full agentic mode: plan → execute → critique → refine.
MAX_ITERATIONS: int = int(os.getenv("MAX_ITERATIONS", "3"))

# Maximum number of tool-call rounds per executor task.
# Prevents runaway tool loops.
MAX_TOOL_CALLS: int = int(os.getenv("MAX_TOOL_CALLS", "5"))

# ── Memory ───────────────────────────────────────────────────────────────────
SHORT_TERM_MEMORY_SIZE: int = int(os.getenv("SHORT_TERM_MEMORY_SIZE", "10"))
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
MEMORY_TOP_K: int = int(os.getenv("MEMORY_TOP_K", "5"))

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE: str = os.getenv("LOG_FILE", "logs/agentic_system.log")
MEMORY_FILE: str = os.getenv("MEMORY_FILE", "logs/memory.json")

# ── Networking / timeouts ─────────────────────────────────────────────────────
API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "30"))
RETRY_ATTEMPTS: int = int(os.getenv("RETRY_ATTEMPTS", "3"))

# ── Security ─────────────────────────────────────────────────────────────────
# Set API_AUTH_KEY to a random secret to enable X-API-Key authentication on
# all backend endpoints.  Leave empty to disable auth (local dev only).
API_AUTH_KEY: str = os.getenv("API_AUTH_KEY", "")
RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))

# ── Start-up warnings ────────────────────────────────────────────────────────
# Use print() here because logging may not be configured yet when config.py
# is first imported.
import sys as _sys

if not GROQ_API_KEY:
    print(
        "Warning: GROQ_API_KEY is not set — LLM calls will fail.",
        file=_sys.stderr,
    )
if not API_AUTH_KEY:
    print(
        "Warning: API_AUTH_KEY is not set — the API is running without "
        "authentication. Set a strong random secret in .env for any "
        "non-local deployment.",
        file=_sys.stderr,
    )
