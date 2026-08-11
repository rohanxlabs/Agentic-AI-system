"""Tests for short-term and long-term memory — no LLM, no embeddings required."""
import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory


# ── Short-term memory ─────────────────────────────────────────────────────────

class TestShortTermMemory:
    def test_add_and_get(self):
        stm = ShortTermMemory(buffer_size=5)
        stm.add("hello")
        assert "hello" in stm.get()

    def test_multiple_entries(self):
        stm = ShortTermMemory(buffer_size=5)
        stm.add("first")
        stm.add("second")
        content = stm.get()
        assert "first" in content
        assert "second" in content

    def test_buffer_overflow_drops_oldest(self):
        stm = ShortTermMemory(buffer_size=3)
        stm.add("a")
        stm.add("b")
        stm.add("c")
        stm.add("d")  # "a" should be dropped
        content = stm.get()
        assert "a" not in content
        assert "b" in content
        assert "c" in content
        assert "d" in content

    def test_clear(self):
        stm = ShortTermMemory(buffer_size=5)
        stm.add("something")
        stm.clear()
        assert stm.get() == ""

    def test_empty_get(self):
        stm = ShortTermMemory()
        assert stm.get() == ""

    def test_isolation_between_instances(self):
        stm1 = ShortTermMemory()
        stm2 = ShortTermMemory()
        stm1.add("stm1 secret")
        assert "stm1 secret" not in stm2.get()


# ── Long-term memory ──────────────────────────────────────────────────────────

class TestLongTermMemory:
    """These tests mock out sentence-transformers so they run without the model."""

    def _make_ltm(self, tmp_path: Path) -> LongTermMemory:
        storage = str(tmp_path / "memory.json")
        ltm = LongTermMemory(storage_file=storage)
        return ltm

    def test_save_and_recall(self, tmp_path):
        ltm = self._make_ltm(tmp_path)
        # Mock the embedder to return a numpy array (as the real model does)
        import numpy as np
        mock_embedder = MagicMock()
        mock_embedder.encode.return_value = np.array([0.1, 0.2, 0.3])
        ltm._embedder = mock_embedder

        ltm.save("Important fact about Python")
        content = ltm.recall()
        assert "Important fact about Python" in content

    def test_persistence_to_file(self, tmp_path):
        import numpy as np
        storage = str(tmp_path / "memory.json")
        ltm = LongTermMemory(storage_file=storage)
        mock_embedder = MagicMock()
        mock_embedder.encode.return_value = np.array([0.1, 0.2, 0.3])
        ltm._embedder = mock_embedder

        ltm.save("Persistent memory entry")

        # Reload from file
        ltm2 = LongTermMemory(storage_file=storage)
        content = ltm2.recall()
        assert "Persistent memory entry" in content

    def test_recall_recent(self, tmp_path):
        import numpy as np
        ltm = self._make_ltm(tmp_path)
        mock_embedder = MagicMock()
        mock_embedder.encode.return_value = np.array([0.1, 0.2, 0.3])
        ltm._embedder = mock_embedder

        for i in range(10):
            ltm.save(f"Entry {i}")

        recent = ltm.recall_recent(n=3)
        assert "Entry 9" in recent
        assert "Entry 8" in recent
        assert "Entry 7" in recent
        # Oldest entries should not appear
        assert "Entry 0" not in recent

    def test_empty_recall(self, tmp_path):
        ltm = self._make_ltm(tmp_path)
        assert ltm.recall() == ""

    def test_recall_relevant_empty_store(self, tmp_path):
        ltm = self._make_ltm(tmp_path)
        results = ltm.recall_relevant("anything")
        assert results == []

    def test_isolation_between_files(self, tmp_path):
        """Two LTM instances with different storage paths must not share data."""
        import numpy as np
        ltm1 = LongTermMemory(storage_file=str(tmp_path / "a.json"))
        ltm2 = LongTermMemory(storage_file=str(tmp_path / "b.json"))

        mock = MagicMock()
        mock.encode.return_value = np.array([0.1, 0.2, 0.3])
        ltm1._embedder = mock
        ltm2._embedder = mock

        ltm1.save("session A secret")
        assert "session A secret" not in ltm2.recall()

    def test_corrupt_file_handled_gracefully(self, tmp_path):
        storage = str(tmp_path / "corrupt.json")
        # Write garbage to the file
        Path(storage).write_text("not valid json {{{")
        # Should not raise — should start with empty store
        ltm = LongTermMemory(storage_file=storage)
        assert ltm.store == []

    def test_persist_creates_file(self, tmp_path):
        import numpy as np
        storage = str(tmp_path / "new.json")
        ltm = LongTermMemory(storage_file=storage)
        mock = MagicMock()
        mock.encode.return_value = np.array([0.1])
        ltm._embedder = mock
        ltm.save("test entry")
        assert Path(storage).exists()
        data = json.loads(Path(storage).read_text())
        assert len(data) == 1
        assert data[0]["content"] == "test entry"
