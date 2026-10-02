import json
import logging
from typing import Any

import aiosqlite

from ..config.settings import settings

logger = logging.getLogger("mirofish.brain.memory")

class SQLiteMemory:
    """
    Long-term Context Memory using Async SQLite (WAL mode, FTS5).
    Memory limit enforced by aggressive caching boundaries.
    """
    def __init__(self, db_path: str = settings.DB_PATH):
        self.db_path = db_path
        self._conn: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        self._conn = await aiosqlite.connect(self.db_path)
        # Apply hardware-specific memory-leak mitigation PRAGMAs
        await self._conn.execute("PRAGMA journal_mode=WAL;")
        await self._conn.execute("PRAGMA synchronous=NORMAL;")
        await self._conn.execute("PRAGMA cache_size=-64000;") # Limit cache to ~64MB
        
        # Initialize schema
        await self._conn.execute('''
            CREATE TABLE IF NOT EXISTS semantic_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,
                content TEXT,
                metadata TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Create FTS5 virtual table for lightning fast semantic retrieval
        await self._conn.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
                content, session_id UNINDEXED, role UNINDEXED
            )
        ''')
        await self._conn.commit()
        logger.info(f"SQLite Long-term Memory initialized at {self.db_path}")

    async def store(self, session_id: str, role: str, content: str, metadata: dict[str, Any] | None = None) -> None:
        meta_str = json.dumps(metadata) if metadata else "{}"
        
        # Insert into main table and FTS index concurrently via trigger (or manually)
        await self._conn.execute(
            "INSERT INTO semantic_memory (session_id, role, content, metadata) VALUES (?, ?, ?, ?)",
            (session_id, role, content, meta_str)
        )
        await self._conn.execute(
            "INSERT INTO memory_fts (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, role, content)
        )
        await self._conn.commit()

    async def search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """Full-Text Search across historical memories."""
        cursor = await self._conn.execute(
            "SELECT session_id, role, content FROM memory_fts WHERE memory_fts MATCH ? ORDER BY rank LIMIT ?",
            (query, limit)
        )
        rows = await cursor.fetchall()
        return [{"session_id": r[0], "role": r[1], "content": r[2]} for r in rows]

    async def close(self) -> None:
        if self._conn:
            await self._conn.close()
