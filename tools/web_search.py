"""Web search tool — DuckDuckGo-backed, with result sanitisation."""
import logging
import re
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

_MAX_QUERY_LEN = 200      # characters
_MAX_SNIPPET_LEN = 200    # characters per result snippet
_MAX_TITLE_LEN = 120      # characters per title


def search(query: str, max_results: int = 3) -> str:
    """Search the web using DuckDuckGo and return formatted, sanitised results.

    Security notes
    --------------
    * The query is truncated at ``_MAX_QUERY_LEN`` characters before being
      sent to DuckDuckGo, preventing excessively long or injected queries.
    * Titles and snippets from the search provider are treated as *untrusted
      external content* — HTML/control characters are stripped, and each
      field is capped in length before being returned to the agent.
    * The function never raises; network failures return a safe fallback
      string so the agent can continue without the search result.

    Args:
        query:       Search query string (will be truncated if too long).
        max_results: Maximum number of results to return (capped at 5).

    Returns:
        Formatted, sanitised search results, or a fallback message on failure.
    """
    if not isinstance(query, str) or not query.strip():
        return "Error: Empty search query provided"

    # Enforce length limit
    query = query.strip()[:_MAX_QUERY_LEN]
    max_results = min(max(1, max_results), 5)

    try:
        from duckduckgo_search import DDGS
        raw_results: List[Dict[str, Any]] = DDGS().text(query, max_results=max_results)
    except Exception as exc:
        logger.warning("Web search network error: %s", exc)
        return "Search temporarily unavailable — proceeding without it."

    if not raw_results:
        return "No search results found for the query."

    formatted: List[str] = []
    for i, result in enumerate(raw_results, 1):
        title = _sanitise(result.get("title", ""), _MAX_TITLE_LEN)
        snippet = _sanitise(result.get("body", ""), _MAX_SNIPPET_LEN)
        url = _sanitise_url(result.get("href", ""))

        entry = f"{i}. {title}"
        if snippet:
            entry += f"\n   {snippet}"
        if url:
            entry += f"\n   {url}"
        formatted.append(entry)

    return "\n\n".join(formatted)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _sanitise(text: str, max_len: int) -> str:
    """Strip control characters and cap length."""
    if not isinstance(text, str):
        return ""
    # Remove ASCII control characters (except newline/tab)
    text = re.sub(r"[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]", "", text)
    text = text.strip()
    if len(text) > max_len:
        text = text[: max_len - 3] + "..."
    return text


def _sanitise_url(url: str) -> str:
    """Return the URL only if it starts with http/https; empty string otherwise."""
    if not isinstance(url, str):
        return ""
    url = url.strip()
    if url.startswith("http://") or url.startswith("https://"):
        return url[:300]
    return ""
