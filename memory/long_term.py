"""Long-term memory module with persistence and semantic retrieval."""
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

import numpy as np

from config.config import EMBEDDING_MODEL, MEMORY_TOP_K


logger = logging.getLogger(__name__)


class LongTermMemory:
    """Persistent memory storage with file persistence and semantic retrieval."""

    def __init__(self, storage_file: str = "logs/memory.json") -> None:
        """Initialize long-term memory with file persistence.
        
        Args:
            storage_file: Path to store memory data
        """
        self.store: List[Dict[str, Any]] = []
        self.storage_file = Path(storage_file)
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)
        self._embedder: Optional[Any] = None  # Lazy loaded
        self._load()

    def _load_embedder(self) -> None:
        """Lazily load the sentence transformer model only when first needed."""
        if self._embedder is None:
            logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
            from sentence_transformers import SentenceTransformer
            self._embedder = SentenceTransformer(EMBEDDING_MODEL)

    def save(self, text: str) -> None:
        """Save text to memory and persist to file.
        
        Args:
            text: Text to save
        """
        self._load_embedder()  # Load model only when saving first memory
        embedding = self._embedder.encode(text).tolist() if self._embedder else []
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "content": text,
            "embedding": embedding
        }
        self.store.append(entry)
        self._persist()

    def recall(self) -> str:
        """Retrieve all stored content.
        
        Returns:
            Joined text from all entries
        """
        return "\n".join([entry["content"] for entry in self.store])

    def recall_recent(self, n: int = 5) -> str:
        """Retrieve the last n stored entries.

        Args:
            n: Number of recent entries to return

        Returns:
            Joined text from the last n entries
        """
        return "\n".join([entry["content"] for entry in self.store[-n:]])

    def recall_relevant(self, query: str, k: int = None) -> List[str]:
        """Retrieve top-k most semantically relevant memories for the query.
        
        Args:
            query: Text to find relevant memories for
            k: Number of results to return (defaults to MEMORY_TOP_K)
            
        Returns:
            List of relevant memory contents, ordered by similarity descending
        """
        k = MEMORY_TOP_K if k is None else k
        
        # Handle empty memory case
        if not self.store:
            return []
        
        # Load embedder if not already loaded
        self._load_embedder()
        
        # Filter entries that have valid embeddings
        valid_entries = []
        for entry in self.store:
            if "embedding" in entry and len(entry["embedding"]) > 0:
                valid_entries.append(entry)
        
        if not valid_entries:
            return []
        
        # Embed the query
        query_embedding = self._embedder.encode(query)
        
        # Convert embeddings to numpy array for efficient computation
        embeddings = np.array([entry["embedding"] for entry in valid_entries])
        
        # Compute cosine similarity
        norm_query = np.linalg.norm(query_embedding)
        norm_entries = np.linalg.norm(embeddings, axis=1)
        cosine_similarities = np.dot(embeddings, query_embedding) / (norm_entries * norm_query)
        
        # Get indices of top-k similarities
        top_indices = cosine_similarities.argsort()[-k:][::-1]
        
        # Collect the results
        results = []
        timestamps = []
        for idx in top_indices:
            results.append(valid_entries[idx]["content"])
            timestamps.append(valid_entries[idx]["timestamp"])
        
        if results:
            logger.info(f"Retrieved {len(results)} relevant memories with timestamps: {', '.join(timestamps)}")
            
        return results

    def _persist(self) -> None:
        """Write memory to file."""
        try:
            with open(self.storage_file, "w") as f:
                json.dump(self.store, f, indent=2)
        except IOError as e:
            logger.error(f"Error persisting memory: {e}")

    def _load(self) -> None:
        """Load memory from file if it exists."""
        if self.storage_file.exists():
            try:
                with open(self.storage_file, "r") as f:
                    loaded = json.load(f)
                    # Handle both old format (list of strings) and new format
                    self.store = []
                    for entry in loaded:
                        if isinstance(entry, str):
                            # Convert old string entries to new format without embedding
                            self.store.append({
                                "timestamp": datetime.now().isoformat(),
                                "content": entry,
                                "embedding": []
                            })
                        else:
                            # Already in dict format, keep as-is
                            self.store.append(entry)
            except (IOError, json.JSONDecodeError) as e:
                logger.error(f"Error loading memory: {e}")
                self.store = []