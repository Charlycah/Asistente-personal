from pathlib import Path

REMOVED_ORPHAN_MODULES = (
    "core/orchestrator.py",
    "domain/config.py",
    "domain/events.py",
    "domain/intents.py",
    "domain/memory.py",
    "domain/responses.py",
    "domain/reminders/events.py",
    "domain/reminders/policies.py",
    "engines/conversation_engine.py",
    "engines/habit_engine.py",
    "engines/proactive_engine.py",
    "engines/reminder_engine.py",
    "engines/voice_engine.py",
    "engines/weather_engine.py",
    "handlers/chat_handler.py",
    "handlers/email_handler.py",
    "handlers/reminder_handler.py",
    "handlers/system_handler.py",
    "handlers/weather_handler.py",
    "infrastructure/db/sqlite.py",
    "infrastructure/email/gmail_client.py",
    "infrastructure/repositories/habit_repository.py",
    "infrastructure/repositories/memory_repository.py",
    "infrastructure/repositories/reminder_repository.py",
    "infrastructure/voice/speech_to_text.py",
    "infrastructure/voice/text_to_speech.py",
    "infrastructure/weather/extended_weather_client.py",
    "interfaces/cli/cli_interface.py",
    "interfaces/notifier/notifier.py",
    "interfaces/voice/voice_interface.py",
    "m3/intent_parser/normalizer.py",
    "m3/intent_parser/prompts.py",
    "m6/response/templates.py",
)


def test_demonstrably_orphan_modules_were_physically_removed() -> None:
    remaining = [path for path in REMOVED_ORPHAN_MODULES if Path(path).exists()]
    assert remaining == []


def test_official_runtime_does_not_reference_removed_legacy_orchestrator() -> None:
    for root_name in ("app", "application", "core", "infrastructure"):
        for path in Path(root_name).rglob("*.py"):
            source = path.read_text(encoding="utf-8")
            assert "from core.orchestrator import" not in source
            assert "import core.orchestrator" not in source


def test_maintained_compatibility_layers_remain_available() -> None:
    assert Path("m6/response/models.py").is_file()
