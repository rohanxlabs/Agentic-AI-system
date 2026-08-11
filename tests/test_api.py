"""Tests for the FastAPI endpoints — no LLM calls, no network required.

Uses FastAPI's TestClient with the ManagerAgent fully mocked so these
tests run fast and free.
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_client():
    """Return a TestClient with a fresh import of the app."""
    from api import app
    return TestClient(app, raise_server_exceptions=False)


def _mock_manager_run(results=None, stream_events=None):
    """Return a context-manager patch that replaces ManagerAgent.

    * run()          → returns ``results`` (default: ["mocked result"])
    * run_streaming() → yields from ``stream_events``
    """
    if results is None:
        results = ["mocked result"]
    if stream_events is None:
        stream_events = [
            {"type": "step_result", "content": "step done", "agent": "Executor"},
            {"type": "complete", "result": "mocked result"},
        ]

    mock_mgr = MagicMock()
    mock_mgr.run.return_value = results
    mock_mgr.run_streaming.return_value = iter(stream_events)

    return patch("api._build_manager", return_value=mock_mgr)


# ── Health ────────────────────────────────────────────────────────────────────

class TestHealth:
    def test_root_returns_ok(self):
        client = _make_client()
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "OK"


# ── /run ──────────────────────────────────────────────────────────────────────

class TestRunEndpoint:
    def test_valid_request(self):
        client = _make_client()
        with _mock_manager_run():
            resp = client.post("/run", json={"goal": "say hello"})
        assert resp.status_code == 200
        data = resp.json()
        assert "results" in data
        assert "session_id" in data
        assert isinstance(data["results"], list)

    def test_empty_goal_rejected(self):
        client = _make_client()
        resp = client.post("/run", json={"goal": ""})
        assert resp.status_code == 400

    def test_whitespace_goal_rejected(self):
        client = _make_client()
        resp = client.post("/run", json={"goal": "   "})
        assert resp.status_code == 400

    def test_goal_too_long_rejected(self):
        client = _make_client()
        resp = client.post("/run", json={"goal": "x" * 2001})
        assert resp.status_code == 400

    def test_goal_at_limit_accepted(self):
        client = _make_client()
        with _mock_manager_run():
            resp = client.post("/run", json={"goal": "x" * 2000})
        assert resp.status_code == 200

    def test_reuses_existing_session(self):
        client = _make_client()
        with _mock_manager_run():
            resp1 = client.post("/run", json={"goal": "first task"})
        sid = resp1.json()["session_id"]

        with _mock_manager_run():
            resp2 = client.post("/run", json={"goal": "second task", "session_id": sid})
        assert resp2.json()["session_id"] == sid

    def test_llm_error_returns_502(self):
        from llm.groq_llm import LLMError

        mock_mgr = MagicMock()
        mock_mgr.run.side_effect = LLMError("rate limit")

        client = _make_client()
        with patch("api._build_manager", return_value=mock_mgr):
            resp = client.post("/run", json={"goal": "trigger error"})
        assert resp.status_code == 502
        assert "LLM error" in resp.json()["detail"]

    def test_missing_goal_field(self):
        client = _make_client()
        resp = client.post("/run", json={})
        assert resp.status_code == 422  # Pydantic validation error


# ── /run/stream ───────────────────────────────────────────────────────────────

class TestStreamEndpoint:
    def _collect_events(self, response_text: str):
        """Parse SSE data lines from a response body."""
        import json
        events = []
        for line in response_text.splitlines():
            if line.startswith("data: "):
                try:
                    events.append(json.loads(line[6:]))
                except Exception:
                    pass
        return events

    def test_stream_returns_200(self):
        client = _make_client()
        with _mock_manager_run():
            resp = client.post(
                "/run/stream",
                json={"goal": "stream test"},
            )
        assert resp.status_code == 200

    def test_stream_returns_event_stream_content_type(self):
        client = _make_client()
        with _mock_manager_run():
            resp = client.post("/run/stream", json={"goal": "stream"})
        assert "text/event-stream" in resp.headers.get("content-type", "")

    def test_stream_contains_complete_event(self):
        client = _make_client()
        with _mock_manager_run():
            resp = client.post("/run/stream", json={"goal": "stream test"})
        events = self._collect_events(resp.text)
        types = [e.get("type") for e in events]
        assert "complete" in types

    def test_stream_complete_event_has_session_id(self):
        client = _make_client()
        with _mock_manager_run():
            resp = client.post("/run/stream", json={"goal": "stream test"})
        events = self._collect_events(resp.text)
        complete = next(e for e in events if e.get("type") == "complete")
        assert "session_id" in complete

    def test_stream_empty_goal_rejected(self):
        client = _make_client()
        resp = client.post("/run/stream", json={"goal": ""})
        assert resp.status_code == 400


# ── /sessions ─────────────────────────────────────────────────────────────────

class TestSessionsEndpoints:
    def test_list_sessions_empty(self):
        from api import app
        # Use a fresh session store snapshot
        client = TestClient(app, raise_server_exceptions=False)
        resp = client.get("/sessions")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_create_session(self):
        client = _make_client()
        resp = client.post("/sessions", json={"goal": "test goal"})
        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data
        assert data["goal"] == "test goal"
        assert data["status"] == "idle"

    def test_get_existing_session(self):
        client = _make_client()
        create = client.post("/sessions", json={"goal": "find me"})
        sid = create.json()["id"]
        resp = client.get(f"/sessions/{sid}")
        assert resp.status_code == 200
        assert resp.json()["id"] == sid

    def test_get_nonexistent_session_returns_404(self):
        client = _make_client()
        resp = client.get("/sessions/does-not-exist")
        assert resp.status_code == 404

    def test_delete_existing_session(self):
        client = _make_client()
        create = client.post("/sessions", json={})
        sid = create.json()["id"]
        resp = client.delete(f"/sessions/{sid}")
        assert resp.status_code == 204

    def test_delete_nonexistent_session_returns_404(self):
        client = _make_client()
        resp = client.delete("/sessions/ghost-session")
        assert resp.status_code == 404


# ── /tools ────────────────────────────────────────────────────────────────────

class TestToolsEndpoint:
    def test_tools_returns_list(self):
        client = _make_client()
        resp = client.get("/tools")
        assert resp.status_code == 200
        tools = resp.json()
        assert isinstance(tools, list)
        assert len(tools) >= 1

    def test_tools_have_required_fields(self):
        client = _make_client()
        resp = client.get("/tools")
        for tool in resp.json():
            assert "name" in tool
            assert "description" in tool
            assert "parameters" in tool

    def test_known_tools_present(self):
        client = _make_client()
        resp = client.get("/tools")
        names = {t["name"] for t in resp.json()}
        assert "calculator" in names
        assert "web_search" in names


# ── /memory/stats ─────────────────────────────────────────────────────────────

class TestMemoryStatsEndpoint:
    def test_memory_stats_returns_expected_shape(self):
        client = _make_client()
        resp = client.get("/memory/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert "short_term" in data
        assert "long_term" in data
        assert "count" in data["short_term"]
        assert "count" in data["long_term"]


# ── /metrics ──────────────────────────────────────────────────────────────────

class TestMetricsEndpoint:
    def test_metrics_returns_expected_shape(self):
        client = _make_client()
        resp = client.get("/metrics")
        assert resp.status_code == 200
        data = resp.json()
        assert "uptime" in data
        assert "total_requests" in data
        assert "active_sessions" in data

    def test_total_requests_increments(self):
        client = _make_client()
        before = client.get("/metrics").json()["total_requests"]
        client.get("/metrics")
        after = client.get("/metrics").json()["total_requests"]
        assert after > before
