from pathlib import Path

from core.memory import MemoryItem, MemoryQuery
from infrastructure.repositories.sqlite_memory_store import SQLiteMemoryStore


def test_sqlite_memory_store_persists_items_between_instances(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "memory.db"
    first_store = SQLiteMemoryStore(db_path)

    first_store.remember(
        MemoryItem(
            content="Carlos prefers architectural milestones",
            metadata={"kind": "user_input", "session_id": "s1"},
        )
    )

    second_store = SQLiteMemoryStore(db_path)

    assert second_store.recall(MemoryQuery(text="architectural")) == [
        MemoryItem(
            content="Carlos prefers architectural milestones",
            metadata={"kind": "user_input", "session_id": "s1"},
        )
    ]


def test_sqlite_memory_store_recall_filters_by_query_text(
    tmp_path: Path,
) -> None:
    store = SQLiteMemoryStore(tmp_path / "memory.db")
    store.remember(MemoryItem(content="ROBY remembers reminders"))
    store.remember(MemoryItem(content="ROBY executes tools"))

    results = store.recall(MemoryQuery(text="reminders"))

    assert results == [MemoryItem(content="ROBY remembers reminders")]


def test_sqlite_memory_store_recall_is_case_insensitive(
    tmp_path: Path,
) -> None:
    store = SQLiteMemoryStore(tmp_path / "memory.db")
    store.remember(MemoryItem(content="Persistent Memory is enabled"))

    results = store.recall(MemoryQuery(text="persistent memory"))

    assert results == [MemoryItem(content="Persistent Memory is enabled")]


def test_sqlite_memory_store_empty_query_returns_all_items_in_insert_order(
    tmp_path: Path,
) -> None:
    store = SQLiteMemoryStore(tmp_path / "memory.db")
    first = MemoryItem(content="first", metadata={"index": 1})
    second = MemoryItem(content="second", metadata={"index": 2})

    store.remember(first)
    store.remember(second)

    assert store.recall(MemoryQuery(text="")) == [first, second]
