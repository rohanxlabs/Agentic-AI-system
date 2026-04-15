"""Long-term memory module with persistence."""
import json
from typing import List
from pathlib import Path
from datetime import datetime


class LongTermMemory:
    """Persistent memory storage with file persistence."""

    def __init__(self, storage_file: str = "logs/memory.json") -> None:
        """Initialize long-term memory with file persistence.
        
        Args:
            storage_file: Path to store memory data
        """
        self.store: List[str] = []
        self.storage_file = Path(storage_file)
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)
        self._load()

    def save(self, text: str) -> None:
        """Save text to memory and persist to file.
        
        Args:
            text: Text to save
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "content": text
        }
        self.store.append(entry)
        self._persist()

    def recall(self) -> str:
        """Retrieve all stored content.
        
        Returns:
            Joined text from all entries
        """
        return "\n".join([entry["content"] for entry in self.store])

    def _persist(self) -> None:
        """Write memory to file."""
        try:
            with open(self.storage_file, "w") as f:
                json.dump(self.store, f, indent=2)
        except IOError as e:
            print(f"Error persisting memory: {e}")

    def _load(self) -> None:
        """Load memory from file if it exists."""
        if self.storage_file.exists():
            try:
                with open(self.storage_file, "r") as f:
                    self.store = json.load(f)
            except (IOError, json.JSONDecodeError) as e:
                print(f"Error loading memory: {e}")
                self.store = []