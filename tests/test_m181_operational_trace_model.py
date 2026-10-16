from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import pytest

from core.end_to_end_local_conversation import (
    EndToEndLocalConversation,
    EndToEndLocalConversationConfig,
)
from core.local_runtime_bootstrap import (
    LocalRuntimeBootstrap,
    LocalRuntimeBootstrapConfig,
)
from core.operational_trace_model import (
    JsonLinesOperationalTraceStore,
    OperationalTraceEvent,
    OperationalTraceEventType,
    OperationalTraceRecorder,
    OperationalTraceStatus,
    OperationalTurnTrace,
)
from core.platform_runtime_compatibility import private_file_is_protected
from core.runtime_composition_root import RuntimeCompositionRoot
from tests.test_m178_runtime_composition_root import RecordingProvider, dependencies

NOW = datetime(2026, 7, 13, 1, 0, tzinfo=timezone.utc)


def runtime(tmp_path, *, provider=None, persist_turns=True, persist_traces=True):
    bootstrap = LocalRuntimeBootstrap(
        root=RuntimeCompositionRoot(dependencies(provider=provider)),
        config=LocalRuntimeBootstrapConfig(
            owner="Carlos",
            session_id="desktop-main",
            state_path=tmp_path / "runtime.json",
        ),
    )
    return EndToEndLocalConversation(
        bootstrap=bootstrap,
        config=EndToEndLocalConversationConfig(
            journal_path=tmp_path / "turns.jsonl",
            persist_turns=persist_turns,
            trace_path=tmp_path / "traces.jsonl",
            persist_traces=persist_traces,
        ),
    )


def test_turn_emits_formal_three_event_trace(tmp_path):
    item = runtime(tmp_path)
    item.bootstrap.start(now=NOW)
    item.converse("Hola", now=NOW)
    trace = item.traces[0]
    assert [event.event_type for event in trace.events] == [
        OperationalTraceEventType.TURN_STARTED,
        OperationalTraceEventType.PIPELINE_FINISHED,
        OperationalTraceEventType.TURN_PERSISTED,
    ]


def test_trace_preserves_owner_session_and_turn_sequence(tmp_path):
    item = runtime(tmp_path)
    item.bootstrap.start(now=NOW)
    item.converse("Hola", now=NOW)
    for event in item.traces[0].events:
        assert (event.owner, event.session_id, event.turn_sequence) == (
            "Carlos",
            "desktop-main",
            1,
        )


def test_event_sequence_is_contiguous_and_causal(tmp_path):
    item = runtime(tmp_path)
    item.bootstrap.start(now=NOW)
    item.converse("Hola", now=NOW)
    events = item.traces[0].events
    assert [event.event_sequence for event in events] == [1, 2, 3]
    assert events[1].parent_event_id == events[0].event_id
    assert events[2].parent_event_id == events[1].event_id


def test_pipeline_event_preserves_exact_m180_lineage(tmp_path):
    item = runtime(tmp_path)
    item.bootstrap.start(now=NOW)
    turn = item.converse("Hola", now=NOW)
    event = item.traces[0].events[1]
    assert event.turn_id == turn.turn_id
    assert event.pipeline_result_id == turn.pipeline_result_id
    assert event.operational_response_id == turn.operational_response_id


def test_execution_flags_are_formally_traced(tmp_path):
    item = runtime(tmp_path)
    item.bootstrap.start(now=NOW)
    item.converse("Hola", now=NOW)
    event = item.traces[0].events[1]
    assert event.provider_call_performed
    assert event.retrieval_performed
    assert not event.network_access_performed
    assert not event.platform_mutation_performed


def test_trace_does_not_duplicate_conversation_content(tmp_path):
    item = runtime(tmp_path)
    item.bootstrap.start(now=NOW)
    item.converse("secreto familiar", now=NOW)
    text = (tmp_path / "traces.jsonl").read_text(encoding="utf-8")
    assert "secreto familiar" not in text
    assert "Hola desde el proveedor local" not in text


def test_trace_file_is_private(tmp_path):
    item = runtime(tmp_path)
    item.bootstrap.start(now=NOW)
    item.converse("Hola", now=NOW)
    assert private_file_is_protected(tmp_path / "traces.jsonl")


def test_trace_survives_runtime_recreation(tmp_path):
    first = runtime(tmp_path)
    first.bootstrap.start(now=NOW)
    first.converse("Hola", now=NOW)
    second = runtime(tmp_path)
    assert len(second.traces) == 1
    assert second.traces[0].events[1].status is OperationalTraceStatus.COMPLETED


def test_multiple_turns_have_distinct_trace_ids(tmp_path):
    item = runtime(tmp_path)
    item.bootstrap.start(now=NOW)
    item.converse("Uno", now=NOW)
    item.converse("Dos", now=NOW + timedelta(seconds=1))
    assert len(item.traces) == 2
    assert item.traces[0].trace_id != item.traces[1].trace_id


def test_trace_query_is_scoped_to_owner_and_session(tmp_path):
    item = runtime(tmp_path)
    item.bootstrap.start(now=NOW)
    item.converse("Hola", now=NOW)
    store = JsonLinesOperationalTraceStore(tmp_path / "traces.jsonl")
    assert store.list_for_session("Ana", "desktop-main") == ()
    assert store.list_for_session("Carlos", "other") == ()


def test_failed_governed_turn_is_traced_without_exception(tmp_path):
    class BrokenProvider(RecordingProvider):
        def generate(self, request):
            raise RuntimeError("offline")

    item = runtime(tmp_path, provider=BrokenProvider())
    item.bootstrap.start(now=NOW)
    item.converse("Hola", now=NOW)
    assert item.traces[0].events[1].status is OperationalTraceStatus.FAILED


def test_trace_can_be_disabled(tmp_path):
    item = runtime(tmp_path, persist_traces=False)
    item.bootstrap.start(now=NOW)
    item.converse("Hola", now=NOW)
    assert item.traces == ()
    assert not (tmp_path / "traces.jsonl").exists()


def test_non_persisted_turn_has_two_event_trace(tmp_path):
    item = runtime(tmp_path, persist_turns=False)
    item.bootstrap.start(now=NOW)
    item.converse("Hola", now=NOW)
    assert len(item.traces[0].events) == 2


def test_trace_event_id_is_deterministic_on_reload(tmp_path):
    item = runtime(tmp_path)
    item.bootstrap.start(now=NOW)
    item.converse("Hola", now=NOW)
    original = item.traces[0].events[1]
    loaded = JsonLinesOperationalTraceStore(tmp_path / "traces.jsonl").get_trace(
        original.trace_id
    )
    assert loaded is not None
    assert loaded.events[1].event_id == original.event_id


def test_first_event_rejects_parent_lineage():
    with pytest.raises(ValueError, match="cannot have a parent"):
        OperationalTraceEvent(
            owner="Carlos",
            session_id="desktop-main",
            turn_sequence=1,
            event_sequence=1,
            event_type="turn_started",
            status="started",
            module="runtime",
            parent_event_id="invalid",
            created_at=NOW,
        )


def test_subsequent_event_requires_trace_and_parent():
    with pytest.raises(ValueError, match="trace lineage"):
        OperationalTraceEvent(
            owner="Carlos",
            session_id="desktop-main",
            turn_sequence=1,
            event_sequence=2,
            event_type="pipeline_finished",
            status="completed",
            module="pipeline",
            created_at=NOW,
        )


def test_turn_trace_rejects_non_contiguous_sequence():
    first = OperationalTraceEvent(
        owner="Carlos",
        session_id="desktop-main",
        turn_sequence=1,
        event_sequence=1,
        event_type="turn_started",
        status="started",
        module="runtime",
        created_at=NOW,
    )
    third = OperationalTraceEvent(
        owner="Carlos",
        session_id="desktop-main",
        turn_sequence=1,
        event_sequence=3,
        event_type="turn_persisted",
        status="persisted",
        module="journal",
        trace_id=first.trace_id,
        parent_event_id=first.event_id,
        created_at=NOW,
    )
    with pytest.raises(ValueError, match="contiguous"):
        OperationalTurnTrace((first, third))


def test_store_payload_is_structured_json(tmp_path):
    item = runtime(tmp_path)
    item.bootstrap.start(now=NOW)
    item.converse("Hola", now=NOW)
    lines = (tmp_path / "traces.jsonl").read_text(encoding="utf-8").splitlines()
    payload = json.loads(lines[1])
    assert payload["event_type"] == "pipeline_finished"
    assert payload["module"] == "governed_operational_conversation_pipeline"


def test_injected_trace_recorder_is_used(tmp_path):
    store = JsonLinesOperationalTraceStore(tmp_path / "custom.jsonl")
    recorder = OperationalTraceRecorder(store)
    item = runtime(tmp_path, persist_traces=False)
    item.trace_recorder = recorder
    item.bootstrap.start(now=NOW)
    item.converse("Hola", now=NOW)
    assert len(store.list_for_session("Carlos", "desktop-main")) == 3


def test_trace_model_does_not_authorize_new_execution(tmp_path):
    provider = RecordingProvider()
    item = runtime(tmp_path, provider=provider)
    item.bootstrap.start(now=NOW)
    item.converse("Hola", now=NOW)
    _ = item.traces
    _ = item.traces[0].terminal_event
    assert len(provider.calls) == 1
