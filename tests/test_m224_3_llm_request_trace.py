from __future__ import annotations

from datetime import datetime, timezone

from core.development_console_observability import (
    DevelopmentConsoleObserver,
    DevelopmentConsoleRenderer,
)
from tests.test_m178_runtime_composition_root import RecordingProvider
from tests.test_m224_2_conversational_context_continuity import runtime

NOW = datetime(2026, 7, 14, 13, 0, tzinfo=timezone.utc)


def test_observer_exposes_exact_context_enriched_llm_request(tmp_path):
    provider = RecordingProvider()
    item = runtime(tmp_path, provider=provider)
    item.bootstrap.start(now=NOW)
    item.converse("Mi nombre es Carlos.", now=NOW)
    second = item.converse("¿Cómo me llamo?", now=NOW)

    observation = DevelopmentConsoleObserver(item).turn_observation(second.sequence)

    assert observation is not None
    assert observation.context_turns == 1
    assert observation.context_from_journal
    assert not observation.context_from_persistent_memory
    assert observation.current_message_characters == len("¿Cómo me llamo?")
    assert observation.inference_prompt == provider.calls[1].prompt
    assert "Usuario: Mi nombre es Carlos." in observation.inference_prompt
    assert observation.prompt_characters == len(provider.calls[1].prompt)


def test_observer_reports_provider_payload_identity(tmp_path):
    provider = RecordingProvider()
    item = runtime(tmp_path, provider=provider)
    item.bootstrap.start(now=NOW)
    turn = item.converse("Hola", now=NOW)

    observation = DevelopmentConsoleObserver(item).turn_observation(turn.sequence)

    assert observation is not None
    assert observation.provider_name == provider.name
    assert observation.model_name
    assert observation.inference_prompt == "Hola"
    assert observation.context_turns == 0
    assert not observation.context_from_journal


def test_renderer_delimits_full_llm_prompt_for_observe_mode(tmp_path):
    provider = RecordingProvider()
    item = runtime(tmp_path, provider=provider)
    item.bootstrap.start(now=NOW)
    item.converse("Mi nombre es Carlos.", now=NOW)
    turn = item.converse("¿Cómo me llamo?", now=NOW)
    observation = DevelopmentConsoleObserver(item).turn_observation(turn.sequence)
    assert observation is not None

    lines = DevelopmentConsoleRenderer().render_turn(observation, reveal_prompt=True)

    assert "llm_prompt_begin" in lines
    assert "llm_prompt| Usuario: Mi nombre es Carlos." in lines
    assert "llm_prompt| Usuario: ¿Cómo me llamo?" in lines
    assert "llm_prompt_end" in lines
    assert any(line.startswith("context turns=1 ") for line in lines)
    assert any("journal=yes" in line for line in lines)
    assert any(line.startswith("provider_payload provider=") for line in lines)


def test_historical_turn_without_live_pipeline_result_remains_observable(tmp_path):
    first_provider = RecordingProvider()
    first = runtime(tmp_path, provider=first_provider)
    first.bootstrap.start(now=NOW)
    first.converse("Persistime", now=NOW)
    first.bootstrap.stop(now=NOW)

    second_provider = RecordingProvider()
    second = runtime(tmp_path, provider=second_provider)
    second.bootstrap.start(now=NOW)

    observation = DevelopmentConsoleObserver(second).turn_observation(1)

    assert observation is not None
    assert observation.inference_prompt == ""
    assert observation.prompt_characters == 0
    assert observation.provider_name == ""
