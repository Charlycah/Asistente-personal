from __future__ import annotations

from datetime import datetime, timezone

from core.development_console_observability import (
    DevelopmentConsoleObserver,
    DevelopmentConsoleRenderer,
)
from tests.test_m178_runtime_composition_root import RecordingProvider
from tests.test_m224_2_conversational_context_continuity import runtime

NOW = datetime(2026, 7, 14, 16, 0, tzinfo=timezone.utc)


def test_observer_reports_structured_message_roles(tmp_path):
    provider = RecordingProvider()
    item = runtime(tmp_path, provider=provider)
    item.bootstrap.start(now=NOW)
    item.converse("Mi nombre es Carlos.", now=NOW)
    turn = item.converse("¿Cómo me llamo?", now=NOW)

    observation = DevelopmentConsoleObserver(item).turn_observation(turn.sequence)

    assert observation is not None
    assert observation.message_transport == "messages"
    assert observation.system_message_count == 0
    assert observation.user_message_count == 2
    assert observation.assistant_message_count == 1
    assert observation.inference_messages[0] == (
        "user",
        "Mi nombre es Carlos.",
    )
    assert observation.inference_messages[-1] == (
        "user",
        "¿Cómo me llamo?",
    )


def test_renderer_reveals_structured_messages_only_when_requested(tmp_path):
    provider = RecordingProvider()
    item = runtime(tmp_path, provider=provider)
    item.bootstrap.start(now=NOW)
    turn = item.converse("Hola", now=NOW)
    observation = DevelopmentConsoleObserver(item).turn_observation(turn.sequence)
    assert observation is not None

    hidden = DevelopmentConsoleRenderer().render_turn(observation)
    revealed = DevelopmentConsoleRenderer().render_turn(observation, reveal_prompt=True)

    assert "llm_messages_begin" not in hidden
    assert "llm_messages_begin" in revealed
    assert "llm_message| user: Hola" in revealed
    assert "llm_messages_end" in revealed
    assert any("transport=messages" in line for line in revealed)


def test_historical_turn_uses_prompt_fallback_observation(tmp_path):
    first = runtime(tmp_path, provider=RecordingProvider())
    first.bootstrap.start(now=NOW)
    first.converse("Persistime", now=NOW)
    first.bootstrap.stop(now=NOW)

    second = runtime(tmp_path, provider=RecordingProvider())
    second.bootstrap.start(now=NOW)
    observation = DevelopmentConsoleObserver(second).turn_observation(1)

    assert observation is not None
    assert observation.message_transport == "prompt"
    assert observation.inference_messages == ()
