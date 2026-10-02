import asyncio
import logging
from collections.abc import Callable
from typing import Any

logger = logging.getLogger("mirofish.brain.blackboard")

class NoticeBoard:
    """
    The Blackboard Architecture implementation for zero-chatter token saving.
    Agents pin results, state diffs, and facts here instead of conversing.
    """
    def __init__(self) -> None:
        self._board: dict[str, list[Any]] = {}
        self._subscribers: dict[str, list[Callable[..., Any]]] = {}
        self._lock = asyncio.Lock()

    async def pin(self, topic: str, content: Any) -> None:
        """Agents post facts or artifacts to a specific topic."""
        async with self._lock:
            if topic not in self._board:
                self._board[topic] = []
            self._board[topic].append(content)
            logger.debug(f"Pinned to {topic}: {content}")
        
        # Notify subscribers (fire and forget to decouple producers)
        if topic in self._subscribers:
            for cb in self._subscribers[topic]:
                asyncio.create_task(self._safe_invoke(cb, topic, content))

    async def read(self, topic: str) -> list[Any]:
        """Read all pinned artifacts for a topic."""
        async with self._lock:
            return self._board.get(topic, []).copy()

    def subscribe(self, topic: str, callback: Callable[..., Any]) -> None:
        """Subscribe an agent to reactive updates on a topic."""
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(callback)

    async def _safe_invoke(self, cb: Callable[..., Any], topic: str, content: Any) -> None:
        try:
            if asyncio.iscoroutinefunction(cb):
                await cb(topic, content)
            else:
                cb(topic, content)
        except Exception as e:
            logger.error(f"Error in Blackboard subscriber on topic {topic}: {e}")

global_blackboard = NoticeBoard()
