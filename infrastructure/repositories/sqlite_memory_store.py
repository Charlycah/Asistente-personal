import json
import sqlite3
from pathlib import Path
from typing import Any

from core.memory import MemoryItem, MemoryQuery


class SQLiteMemoryStore:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_schema()

    def remember(self, item: MemoryItem) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO memories (content, metadata_json)
                VALUES (?, ?)
                """,
                (item.content, json.dumps(item.metadata, sort_keys=True)),
            )

    def recall(self, query: MemoryQuery) -> list[MemoryItem]:
        query_text = query.text.strip()
        with self._connect() as connection:
            if query_text:
                rows = connection.execute(
                    """
                    SELECT content, metadata_json
                    FROM memories
                    WHERE lower(content) LIKE ?
                    ORDER BY id ASC
                    """,
                    (f"%{query_text.lower()}%",),
                ).fetchall()
            else:
                rows = connection.execute(
                    """
                    SELECT content, metadata_json
                    FROM memories
                    ORDER BY id ASC
                    """
                ).fetchall()

        return [self._row_to_item(row) for row in rows]

    def _initialize_schema(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    metadata_json TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _row_to_item(self, row: tuple[str, str]) -> MemoryItem:
        content, metadata_json = row
        metadata = self._load_metadata(metadata_json)
        return MemoryItem(content=content, metadata=metadata)

    def _load_metadata(self, metadata_json: str) -> dict[str, Any]:
        metadata = json.loads(metadata_json)
        if not isinstance(metadata, dict):
            return {}
        return metadata
