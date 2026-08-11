"""Tests for session management — no LLM, no embeddings required."""
import pytest
import time
from unittest.mock import patch, MagicMock

from session.session_manager import SessionStore
from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory


class TestSessionStore:
    def _make_store(self, tmp_path) -> SessionStore:
        """Return a fresh SessionStore that writes LTM files to tmp_path."""
        store = SessionStore.__new__(SessionStore)
        store._sessions = {}
        # Patch the LTM dir so tests don't pollute logs/sessions/
        with patch("session.session_manager._SESSION_LTM_DIR", tmp_path):
            store.__init__()
        return store

    def test_creates_new_session(self, tmp_path):
        with patch("session.session_manager._SESSION_LTM_DIR", tmp_path):
            store = SessionStore()
        sid, session = store.get_or_create()
        assert isinstance(sid, str)
        assert len(sid) == 36  # UUID4
        assert "stm" in session
        assert "ltm" in session
        assert session["status"] == "idle"

    def test_reuses_existing_session(self, tmp_path):
        with patch("session.session_manager._SESSION_LTM_DIR", tmp_path):
            store = SessionStore()
        sid, _ = store.get_or_create()
        sid2, session2 = store.get_or_create(sid)
        assert sid == sid2

    def test_session_isolation_stm(self, tmp_path):
        with patch("session.session_manager._SESSION_LTM_DIR", tmp_path):
            store = SessionStore()
        _, s1 = store.get_or_create()
        _, s2 = store.get_or_create()
        s1["stm"].add("session 1 secret")
        assert "session 1 secret" not in s2["stm"].get()

    def test_session_isolation_ltm(self, tmp_path):
        with patch("session.session_manager._SESSION_LTM_DIR", tmp_path):
            store = SessionStore()
        _, s1 = store.get_or_create()
        _, s2 = store.get_or_create()
        assert id(s1["ltm"]) != id(s2["ltm"]), "LTM instances must be different objects"

    def test_session_isolation_ltm_files(self, tmp_path):
        with patch("session.session_manager._SESSION_LTM_DIR", tmp_path):
            store = SessionStore()
        sid1, s1 = store.get_or_create()
        sid2, s2 = store.get_or_create()
        # LTM storage files must be different
        assert s1["ltm"].storage_file != s2["ltm"].storage_file

    def test_goal_stored_on_create(self, tmp_path):
        with patch("session.session_manager._SESSION_LTM_DIR", tmp_path):
            store = SessionStore()
        sid, session = store.get_or_create(goal="solve climate change")
        assert session["goal"] == "solve climate change"

    def test_list_sessions_empty(self, tmp_path):
        with patch("session.session_manager._SESSION_LTM_DIR", tmp_path):
            store = SessionStore()
        assert store.list_sessions() == []

    def test_list_sessions_returns_metadata(self, tmp_path):
        with patch("session.session_manager._SESSION_LTM_DIR", tmp_path):
            store = SessionStore()
        sid, _ = store.get_or_create(goal="test goal")
        sessions = store.list_sessions()
        assert len(sessions) == 1
        assert sessions[0]["id"] == sid
        assert sessions[0]["goal"] == "test goal"
        assert "created_at" in sessions[0]
        assert "last_used" in sessions[0]

    def test_list_sessions_sorted_newest_first(self, tmp_path):
        with patch("session.session_manager._SESSION_LTM_DIR", tmp_path):
            store = SessionStore()
        sid1, _ = store.get_or_create()
        time.sleep(0.01)
        sid2, _ = store.get_or_create()
        sessions = store.list_sessions()
        assert sessions[0]["id"] == sid2  # newest first

    def test_delete_existing_session(self, tmp_path):
        with patch("session.session_manager._SESSION_LTM_DIR", tmp_path):
            store = SessionStore()
        sid, _ = store.get_or_create()
        assert store.delete_session(sid) is True
        assert store.get_session(sid) is None

    def test_delete_nonexistent_session(self, tmp_path):
        with patch("session.session_manager._SESSION_LTM_DIR", tmp_path):
            store = SessionStore()
        assert store.delete_session("does-not-exist") is False

    def test_get_nonexistent_session(self, tmp_path):
        with patch("session.session_manager._SESSION_LTM_DIR", tmp_path):
            store = SessionStore()
        assert store.get_session("nonexistent") is None

    def test_cleanup_stale_sessions(self, tmp_path):
        with patch("session.session_manager._SESSION_LTM_DIR", tmp_path):
            store = SessionStore()
        sid, session = store.get_or_create()
        # Artificially age the session
        session["last_used"] = time.time() - 7200  # 2 hours ago
        removed = store.cleanup_stale(max_age_seconds=3600)
        assert removed == 1
        assert store.get_session(sid) is None

    def test_cleanup_does_not_remove_active_session(self, tmp_path):
        with patch("session.session_manager._SESSION_LTM_DIR", tmp_path):
            store = SessionStore()
        sid, _ = store.get_or_create()
        removed = store.cleanup_stale(max_age_seconds=3600)
        assert removed == 0
        assert store.get_session(sid) is not None

    def test_session_count(self, tmp_path):
        with patch("session.session_manager._SESSION_LTM_DIR", tmp_path):
            store = SessionStore()
        assert store.get_session_count() == 0
        store.get_or_create()
        store.get_or_create()
        assert store.get_session_count() == 2
