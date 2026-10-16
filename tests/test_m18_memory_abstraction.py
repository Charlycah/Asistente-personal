from core.memory import MemoryItem, MemoryQuery, NullMemoryStore


def test_memory_item_has_content_and_metadata_defaults() -> None:
    item = MemoryItem(content="User prefers concise answers")

    assert item.content == "User prefers concise answers"
    assert item.metadata == {}


def test_memory_query_has_text_and_metadata_defaults() -> None:
    query = MemoryQuery(text="preferences")

    assert query.text == "preferences"
    assert query.metadata == {}


def test_null_memory_store_accepts_remember_without_side_effects() -> None:
    store = NullMemoryStore()
    item = MemoryItem(content="Remember this later")

    store.remember(item)

    assert store.recall(MemoryQuery(text="Remember")) == []


def test_null_memory_store_always_returns_empty_list() -> None:
    store = NullMemoryStore()

    assert store.recall(MemoryQuery(text="anything")) == []
