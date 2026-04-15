"""Short-term memory module for recent interactions."""
from typing import List


class ShortTermMemory:
    """Maintains recent context with limited buffer size."""

    def __init__(self, buffer_size: int = 10) -> None:
        """Initialize short-term memory.
        
        Args:
            buffer_size: Maximum number of entries to keep
        """
        self.buffer: List[str] = []
        self.buffer_size = buffer_size

    def add(self, text: str) -> None:
        """Add text to memory buffer.
        
        Args:
            text: Text to add
        """
        self.buffer.append(text)
        # Keep only the most recent entries
        if len(self.buffer) > self.buffer_size:
            self.buffer = self.buffer[-self.buffer_size:]

    def get(self) -> str:
        """Retrieve all buffered text.
        
        Returns:
            Joined text from recent entries
        """
        return "\n".join(self.buffer[-self.buffer_size:])

    def clear(self) -> None:
        """Clear the memory buffer."""
        self.buffer.clear()