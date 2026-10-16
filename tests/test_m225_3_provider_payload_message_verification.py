from __future__ import annotations

from datetime import datetime, timezone

from core.development_console_observability import (
    DevelopmentConsoleObserver,
    DevelopmentConsoleRenderer,
)
from tests.test_m178_runtime_composition_root import RecordingProvider
from tests.test_m224_2_conversational_context_continuity import runtime

NOW = datetime(2026, 7, 14, 17, 0, tzinfo=timezone.utc)


def test_observer_reports_provider_endpoint_and_role_sequence(tmp_path):
    item = runtime(tmp_path, provider=RecordingProvider())
    item.bootstrap.start(now=NOW)
    item.converse("Mi nombre es Carlos.", now=NOW)
    turn = item.converse("¿Cómo me llamo?", now=NOW)

    observation = DevelopmentConsoleObserver(item).turn_observation(turn.sequence)

    assert observation is not None
    assert observation.provider_endpoint_path == "/chat/completions"
    assert observation.provider_message_roles == (
        "user",
        "assistant",
        "user",
    )


def test_renderer_places_verified_provider_messages_at_end(tmp_path):
    item = runtime(tmp_path, provider=RecordingProvider())
    item.bootstrap.start(now=NOW)
    turn = item.converse("Hola", now=NOW)
    observation = DevelopmentConsoleObserver(item).turn_observation(turn.sequence)
    assert observation is not None

    rendered = DevelopmentConsoleRenderer().render_turn(
        observation,
        reveal_prompt=True,
    )

    assert "endpoint=/chat/completions" in next(
        line for line in rendered if line.startswith("provider_payload ")
    )
    assert "provider_message_roles=user" in rendered
    assert rendered[-4:] == (
        "llm_message| user: Hola",
        "llm_messages_end",
        "provider_messages_end",
        "provider_transport_verified",
    )


def test_non_revealing_render_keeps_message_contents_redacted(tmp_path):
    item = runtime(tmp_path, provider=RecordingProvider())
    item.bootstrap.start(now=NOW)
    turn = item.converse("dato privado", now=NOW)
    observation = DevelopmentConsoleObserver(item).turn_observation(turn.sequence)
    assert observation is not None

    rendered = DevelopmentConsoleRenderer().render_turn(observation)

    assert "provider_messages_begin" not in rendered
    assert all("dato privado" not in line for line in rendered)
