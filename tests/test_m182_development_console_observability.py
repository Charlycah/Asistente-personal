from __future__ import annotations

from datetime import datetime, timezone

from core.development_console_observability import (
    DevelopmentConsoleObserver,
    DevelopmentConsoleRenderer,
)
from tests.test_m181_operational_trace_model import runtime

NOW = datetime(2026, 7, 13, 2, 0, tzinfo=timezone.utc)


def started_runtime(tmp_path, **kwargs):
    item = runtime(tmp_path, **kwargs)
    item.bootstrap.start(now=NOW)
    return item


def test_runtime_observation_reports_identity_and_status(tmp_path):
    item = started_runtime(tmp_path)
    observed = DevelopmentConsoleObserver(item).runtime_observation()
    assert (observed.owner, observed.session_id, observed.status) == (
        "Carlos",
        "desktop-main",
        "running",
    )


def test_runtime_observation_reports_counts(tmp_path):
    item = started_runtime(tmp_path)
    item.converse("Hola", now=NOW)
    observed = DevelopmentConsoleObserver(item).runtime_observation()
    assert (observed.turn_count, observed.trace_count) == (1, 1)


def test_runtime_observation_lists_composed_modules(tmp_path):
    item = started_runtime(tmp_path)
    modules = DevelopmentConsoleObserver(item).runtime_observation().composed_modules
    assert "conversation_pipeline" in modules
    assert "provider_router" in modules
    assert "response_assembler" in modules


def test_last_turn_is_none_without_history(tmp_path):
    item = started_runtime(tmp_path)
    assert DevelopmentConsoleObserver(item).last_turn() is None


def test_last_turn_projects_trace_and_lineage(tmp_path):
    item = started_runtime(tmp_path)
    turn = item.converse("Hola", now=NOW)
    observed = DevelopmentConsoleObserver(item).last_turn()
    assert observed is not None
    assert observed.turn_id == turn.turn_id
    assert observed.pipeline_result_id == turn.pipeline_result_id
    assert observed.operational_response_id == turn.operational_response_id
    assert observed.trace_id


def test_turn_observation_reports_activated_modules(tmp_path):
    item = started_runtime(tmp_path)
    item.converse("Hola", now=NOW)
    observed = DevelopmentConsoleObserver(item).turn_observation(1)
    assert observed is not None
    assert observed.modules == (
        "end_to_end_local_conversation",
        "governed_operational_conversation_pipeline",
        "local_conversation_journal",
    )


def test_turn_observation_reports_execution_flags(tmp_path):
    item = started_runtime(tmp_path)
    item.converse("Hola", now=NOW)
    observed = DevelopmentConsoleObserver(item).turn_observation(1)
    assert observed is not None
    assert observed.provider_call_performed
    assert observed.retrieval_performed
    assert not observed.network_access_performed
    assert not observed.platform_mutation_performed


def test_turn_observation_reports_terminal_event(tmp_path):
    item = started_runtime(tmp_path)
    item.converse("Hola", now=NOW)
    observed = DevelopmentConsoleObserver(item).turn_observation(1)
    assert observed is not None
    assert observed.event_count == 3
    assert observed.terminal_event == "turn_persisted"


def test_turn_observation_handles_disabled_traces(tmp_path):
    item = started_runtime(tmp_path, persist_traces=False)
    item.converse("Hola", now=NOW)
    observed = DevelopmentConsoleObserver(item).turn_observation(1)
    assert observed is not None
    assert observed.trace_id == ""
    assert observed.modules == ()
    assert observed.terminal_event == "untraced"


def test_unknown_turn_returns_none(tmp_path):
    item = started_runtime(tmp_path)
    assert DevelopmentConsoleObserver(item).turn_observation(7) is None


def test_observation_does_not_call_provider_again(tmp_path):
    from tests.test_m178_runtime_composition_root import RecordingProvider

    provider = RecordingProvider()
    item = started_runtime(tmp_path, provider=provider)
    item.converse("Hola", now=NOW)
    observer = DevelopmentConsoleObserver(item)
    observer.runtime_observation()
    observer.last_turn()
    observer.turn_observation(1)
    assert len(provider.calls) == 1


def test_runtime_renderer_is_stable_and_content_free(tmp_path):
    item = started_runtime(tmp_path)
    rendered = DevelopmentConsoleRenderer().render_runtime(
        DevelopmentConsoleObserver(item).runtime_observation()
    )
    assert rendered[0].startswith("runtime status=running")
    assert "Carlos" in rendered[0]


def test_turn_renderer_does_not_render_conversation_text(tmp_path):
    item = started_runtime(tmp_path)
    item.converse("secreto familiar", now=NOW)
    observed = DevelopmentConsoleObserver(item).last_turn()
    assert observed is not None
    text = "\n".join(DevelopmentConsoleRenderer().render_turn(observed))
    assert "secreto familiar" not in text
    assert "Hola desde el proveedor local" not in text

