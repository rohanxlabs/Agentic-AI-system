"""Web search tool implementation using DuckDuckGo."""
import logging
from ddgs import DDGS
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def search(query: str, max_results: int = 3) -> str:
    """Search the web using DuckDuckGo and return formatted results.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return (default: 3)
        
    Returns:
        Formatted string of search results, or error message if search fails
    """
    if not query.strip():
        return "Error: Empty search query provided"
    
    try:
        from duckduckgo_search import DDGS
        results: List[Dict[str, Any]] = DDGS().text(query, max_results=max_results)
        
        if not results:
            return "No search results found for the query"
        
        formatted = []
        for i, result in enumerate(results, 1):
            title = result.get("title", "No title").strip()
            snippet = result.get("body", "No snippet available").strip()
            url = result.get("href", "No URL").strip()
            
            # Cap snippet at ~200 characters
            if len(snippet) > 200:
                snippet = snippet[:197] + "..."
            
            formatted.append(f"{i}. {title}\n   {snippet}\n   {url}")
        
        return "\n".join(formatted)
        
    except Exception as e:
        logger.warning(f"Web search failed: {str(e)}")
        return "Search temporarily unavailable, proceeding without it"