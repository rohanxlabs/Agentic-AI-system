"""Groq LLM integration module."""
import os
import logging
import time
from typing import Optional

from groq import Groq
from dotenv import load_dotenv

from config.config import MODEL_NAME, RETRY_ATTEMPTS, API_TIMEOUT

load_dotenv()
logger = logging.getLogger(__name__)


class GroqLLM:
    """Interface to Groq language model API."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        """Initialize Groq LLM client.

        Args:
            api_key: Groq API key (uses env var if not provided)

        Raises:
            ValueError: If API key is not available
        """
        key = api_key or os.getenv("GROQ_API_KEY")
        if not key:
            raise ValueError("GROQ_API_KEY not found in environment variables")

        self.client = Groq(api_key=key)

    def call(self, prompt: str, temperature: float = 0.3, max_tokens: int = 2048) -> str:
        """Call the Groq API with a prompt.

        Args:
            prompt: Input prompt for the model
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum response length

        Returns:
            Model response text

        Raises:
            Exception: If API call fails after retries
        """
        max_retries = RETRY_ATTEMPTS
        last_exception = None

        for attempt in range(1, max_retries + 1):
            try:
                response = self.client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=API_TIMEOUT,
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                is_rate_limit = (
                    getattr(e, "__class__", None).__name__ == "RateLimitError"
                    or getattr(e, "status_code", None) == 429
                    or "rate limit" in str(e).lower()
                )
                if not is_rate_limit:
                    raise
                last_exception = e
                if attempt < max_retries:
                    wait = 2 ** (attempt - 1)
                    logger.warning(
                        f"Rate limit hit (attempt {attempt}/{max_retries}), retrying in {wait}s"
                    )
                    time.sleep(wait)

        logger.error(f"Rate limit exceeded after {max_retries} attempts")
        raise last_exception

    def call_with_tools(self, prompt: str, tools: list, temperature: float = 0.3, max_tokens: int = 2048) -> dict:
        """Call the Groq API with tool support.
        
        Args:
            prompt: Input prompt for the model
            tools: List of tool schemas in OpenAI format
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum response length
            
        Returns:
            Dictionary with content and tool_calls from the API response
        """
        messages = [{"role": "user", "content": prompt}]
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
            message = response.choices[0].message
            return {
                "content": message.content.strip() if message.content else None,
                "tool_calls": [
                    {
                        "name": tc.function.name,
                        "arguments": __import__("json").loads(tc.function.arguments)
                    } for tc in message.tool_calls
                ] if message.tool_calls else []
            }
        except Exception as e:
            logger.error(f"Tool call failed: {str(e)}")
            return {"content": None, "tool_calls": []}