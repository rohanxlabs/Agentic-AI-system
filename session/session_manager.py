"""Session management — creates and tracks isolated per-session memory."""
import uuid
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory
from config.config import MEMORY_FILE

logger = logging.getLogger(__name__)

# Base directory for per-session LTM files.
# Each session gets its own JSON file: logs/sessions/<session_id>.json
_SESSION_LTM_DIR = Path("logs/sessions")


class SessionStore:
    """In-memory registry of active sessions.

    Each session has:
    * An isolated ``ShortTermMemory`` buffer.
    * An isolated ``LongTermMemory`` backed by its own JSON file under
      ``logs/sessions/<session_id>.json``.

    This prevents cross-session memory leakage that existed when all
    sessions shared a single LTM instance.
    """

    def __init__(self) -> None:
        self._sessions: Dict[str, Dict[str, Any]] = {}
        _SESSION_LTM_DIR.mkdir(parents=True, exist_ok=True)

    # ── Core operations ───────────────────────────────────────────────────────

    def get_or_create(
        self,
        session_id: Optional[str] = None,
        goal: Optional[str] = None,
    ) -> Tuple[str, Dict[str, Any]]:
        """Return an existing session or create a new one.

        Args:
            session_id: Reuse this ID if it already exists; generate a new
                        UUID if ``None``.
            goal:       Optional label for the session goal (stored on
                        creation only — not overwritten on reuse).

        Returns:
            ``(session_id, session_data)`` where ``session_data`` has keys
            ``stm``, ``ltm``, ``created_at``, ``last_used``, ``goal``,
            ``status``.
        """
        if session_id is None:
            session_id = str(uuid.uuid4())

        if session_id in self._sessions:
            session = self._sessions[session_id]
            session["last_used"] = time.time()
            logger.debug("Reusing session: %s", session_id)
            return session_id, session

        # New session — give it its own LTM file
        ltm_path = _SESSION_LTM_DIR / f"{session_id}.json"
        now = time.time()
        session: Dict[str, Any] = {
            "stm": ShortTermMemory(),
            "ltm": LongTermMemory(storage_file=str(ltm_path)),
            "created_at": now,
            "last_used": now,
            "goal": goal,
            "status": "idle",
        }
        self._sessions[session_id] = session
        logger.info("Created new session: %s (ltm=%s)", session_id, ltm_path)
        return session_id, session

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Return session data by ID, or ``None`` if not found."""
        return self._sessions.get(session_id)

    def list_sessions(self) -> List[Dict[str, Any]]:
        """Return summary metadata for all active sessions, newest-first."""
        summaries = []
        for sid, data in self._sessions.items():
            summaries.append(
                {
                    "id": sid,
                    "created_at": datetime.fromtimestamp(data["created_at"]).isoformat(),
                    "last_used": datetime.fromtimestamp(data["last_used"]).isoformat(),
                    "goal": data.get("goal"),
                    "status": data.get("status", "idle"),
                }
            )
        summaries.sort(key=lambda s: s["last_used"], reverse=True)
        return summaries

    def delete_session(self, session_id: str) -> bool:
        """Remove a session from the store.

        Does NOT delete the LTM file — history is preserved on disk.

        Returns:
            ``True`` if the session existed and was removed.
        """
        if session_id not in self._sessions:
            return False
        del self._sessions[session_id]
        logger.info("Deleted session: %s", session_id)
        return True

    def cleanup_stale(self, max_age_seconds: int = 3600) -> int:
        """Remove sessions idle for longer than *max_age_seconds*.

        Returns:
            Number of sessions removed.
        """
        cutoff = time.time() - max_age_seconds
        stale = [
            sid
            for sid, data in self._sessions.items()
            if data["last_used"] < cutoff
        ]
        for sid in stale:
            del self._sessions[sid]
            logger.info("Cleaned up stale session: %s", sid)
        return len(stale)

    def get_session_count(self) -> int:
        """Return the number of currently active (in-memory) sessions."""
        return len(self._sessions)


# Module-level singleton — shared across all request handlers
session_store = SessionStore()
