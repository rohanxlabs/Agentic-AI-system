"""Groq LLM integration module."""
import os
import logging
import time
from typing import Optional, List, Dict, Any

from groq import Groq
from dotenv import load_dotenv

from config.config import MODEL_NAME, RETRY_ATTEMPTS, API_TIMEOUT

load_dotenv()
logger = logging.getLogger(__name__)


class LLMError(Exception):
    """Raised when the LLM call fails after all retries."""


class GroqLLM:
    """Interface to the Groq language model API."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        """Initialise the Groq client.

        Args:
            api_key: Groq API key (reads GROQ_API_KEY env-var if omitted).

        Raises:
            ValueError: If no API key is available.
        """
        key = api_key or os.getenv("GROQ_API_KEY")
        if not key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        self.client = Groq(api_key=key)

    # ------------------------------------------------------------------
    # Simple text call
    # ------------------------------------------------------------------

    def call(
        self,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> str:
        """Call Groq with a plain text prompt.

        Retries on rate-limit errors with exponential back-off.

        Args:
            prompt: Input text for the model.
            temperature: Sampling temperature (0.0–2.0).
            max_tokens: Maximum tokens in the response.

        Returns:
            Model response text (never empty — raises on failure).

        Raises:
            LLMError: If the API call fails after all retries.
        """
        last_exception: Optional[Exception] = None

        for attempt in range(1, RETRY_ATTEMPTS + 1):
            try:
                response = self.client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=API_TIMEOUT,
                )
                content = response.choices[0].message.content
                if not content:
                    raise LLMError("LLM returned an empty response")
                return content.strip()
            except Exception as exc:
                is_rate_limit = (
                    type(exc).__name__ == "RateLimitError"
                    or getattr(exc, "status_code", None) == 429
                    or "rate limit" in str(exc).lower()
                )
                if not is_rate_limit:
                    raise LLMError(f"LLM call failed: {exc}") from exc

                last_exception = exc
                if attempt < RETRY_ATTEMPTS:
                    wait = 2 ** (attempt - 1)
                    logger.warning(
                        "Rate limit hit (attempt %d/%d), retrying in %ds",
                        attempt,
                        RETRY_ATTEMPTS,
                        wait,
                    )
                    time.sleep(wait)

        raise LLMError(
            f"Rate limit exceeded after {RETRY_ATTEMPTS} attempts"
        ) from last_exception

    # ------------------------------------------------------------------
    # Tool-calling  (OpenAI / Groq function-calling protocol)
    # ------------------------------------------------------------------

    def call_with_tools(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> Dict[str, Any]:
        """Call Groq with tool-calling support.

        Returns a dict that preserves the ``id`` field on every tool-call
        so callers can build correctly formatted ``role="tool"`` result
        messages (required by the Groq / OpenAI protocol).

        Args:
            messages: Conversation history in OpenAI message format.
            tools: Tool schemas in OpenAI function-calling format.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens in the response.

        Returns:
            ``{"content": str | None, "tool_calls": [...]}``

            Each tool-call entry has the shape::

                {
                    "id":        str,          # call ID — MUST be echoed back
                    "name":      str,
                    "arguments": dict,
                }

        Raises:
            LLMError: If the API call fails (never silently swallowed).
        """
        try:
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=API_TIMEOUT,
            )
        except Exception as exc:
            raise LLMError(f"Tool call failed: {exc}") from exc

        message = response.choices[0].message
        content: Optional[str] = message.content.strip() if message.content else None

        tool_calls: List[Dict[str, Any]] = []
        if message.tool_calls:
            for tc in message.tool_calls:
                try:
                    import json
                    arguments = json.loads(tc.function.arguments)
                except (ValueError, TypeError):
                    arguments = {}
                tool_calls.append(
                    {
                        "id": tc.id,          # preserved — needed for role="tool" messages
                        "name": tc.function.name,
                        "arguments": arguments,
                    }
                )

        return {"content": content, "tool_calls": tool_calls}
