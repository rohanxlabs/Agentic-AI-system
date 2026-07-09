"""Session management for persisting user sessions across requests."""
import uuid
import time
import logging
from typing import Tuple, Dict, Any, Optional, List
from datetime import datetime

from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory
from config.config import MEMORY_FILE

logger = logging.getLogger(__name__)


class SessionStore:
    """In-memory session store that maintains STM and LTM for each session."""
    
    def __init__(self):
        """Initialize the session store."""
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._shared_ltm = LongTermMemory()
    
    def get_or_create(self, session_id: Optional[str] = None, ltm_path: Optional[str] = None, goal: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
        """Get an existing session or create a new one if it doesn't exist.
        
        Args:
            session_id: Optional session ID. If None, a new UUID will be generated.
            ltm_path: Optional path for per-session LTM storage. If None, uses shared LTM.
            
        Returns:
            Tuple of (session_id, session_data) containing stm, ltm, created_at, last_used
        """
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        if session_id in self._sessions:
            session = self._sessions[session_id]
            session["last_used"] = time.time()
            logger.info(f"Reusing existing session: {session_id}")
            return session_id, session
        
        now = time.time()
        if ltm_path:
            ltm = LongTermMemory(storage_file=ltm_path)
        else:
            ltm = self._shared_ltm
            
        stm = ShortTermMemory()
        session = {
            "stm": stm,
            "ltm": ltm,
            "created_at": now,
            "last_used": now,
            "goal": goal,
            "status": "idle",
        }
        
        self._sessions[session_id] = session
        logger.info(f"Created new session: {session_id}")
        return session_id, session
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a session by ID."""
        return self._sessions.get(session_id)
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all sessions with metadata."""
        sessions = []
        for sid, data in self._sessions.items():
            sessions.append({
                "id": sid,
                "created_at": datetime.fromtimestamp(data["created_at"]).isoformat(),
                "last_used": datetime.fromtimestamp(data["last_used"]).isoformat(),
                "goal": data.get("goal"),
                "status": data.get("status", "idle"),
            })
        sessions.sort(key=lambda s: s["last_used"], reverse=True)
        return sessions
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session by ID."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.info(f"Deleted session: {session_id}")
            return True
        return False
    
    def cleanup_stale(self, max_age_seconds: int = 3600) -> int:
        """Remove sessions that haven't been used in max_age_seconds.
        
        Args:
            max_age_seconds: Maximum time in seconds since last use to keep a session.
            
        Returns:
            Number of sessions that were cleaned up
        """
        now = time.time()
        stale_session_ids = []
        
        for session_id, session in self._sessions.items():
            if now - session["last_used"] > max_age_seconds:
                stale_session_ids.append(session_id)
        
        for session_id in stale_session_ids:
            del self._sessions[session_id]
            logger.info(f"Cleaned up stale session: {session_id}")
            
        return len(stale_session_ids)
    
    def get_session_count(self) -> int:
        """Get the current number of active sessions."""
        return len(self._sessions)


# Global session store instance
session_store = SessionStore()