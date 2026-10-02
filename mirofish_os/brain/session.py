import logging
from typing import Any

logger = logging.getLogger("mirofish.brain.session")

class SessionManager:
    """
    Multi-turn conversation context compaction engine.
    Truncates and summarizes context before it hits the LLM context window limits.
    """
    def __init__(self, max_tokens: int = 4000):
        self.max_tokens = max_tokens
        self.active_contexts: dict[str, list[dict[str, Any]]] = {}

    def add_message(self, session_id: str, role: str, content: str):
        if session_id not in self.active_contexts:
            self.active_contexts[session_id] = []
        self.active_contexts[session_id].append({"role": role, "content": content})
        self._compact(session_id)

    def _compact(self, session_id: str):
        # A simple placeholder for token-aware compaction
        # e.g., using tiktoken or simple character length heuristics
        history = self.active_contexts[session_id]
        if len(history) > 20: # Keep last 20 messages for real-time reactivity
            logger.debug(f"Compacting session {session_id} to prevent token bloat.")
            self.active_contexts[session_id] = history[-20:]

    def get_context(self, session_id: str) -> list[dict[str, Any]]:
        return self.active_contexts.get(session_id, [])
