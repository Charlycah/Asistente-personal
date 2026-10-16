from pathlib import Path


def test_m376_historical_archive_is_retired_without_memory_authority_transfer() -> None:
    root = Path(__file__).resolve().parents[2]
    assert not (root / "core/long_term_conversation.py").exists()
    assert not (root / "tests/test_m376_long_term_conversations.py").exists()
    assert not (root / "docs/M376_LONG_TERM_CONVERSATIONS.md").exists()
    archive = root / "docs/history/legacy-conversation/M376_LONG_TERM_CONVERSATIONS.md"
    assert archive.exists()

    rules = (root / "architecture_rules.md").read_text(encoding="utf-8")
    heading = "M376 Historical Unrealized Conversation Archive Retirement Boundary"
    assert heading in rules
    assert "does not authorize automatic Memory admission" in rules
    assert "Living Conversation remains longitudinal topic/thread continuity" in rules

    conversation_root = root / "core/end_to_end_local_conversation"
    runtime = (conversation_root / "runtime.py").read_text(encoding="utf-8")
    journal = (conversation_root / "journal.py").read_text(encoding="utf-8")
    memory = (root / "app/memory_consolidation.py").read_text(encoding="utf-8")
    assert "JsonLinesLocalConversationJournal" in runtime
    assert "class JsonLinesLocalConversationJournal" in journal
    assert "class OfficialMemoryGateway" in memory
