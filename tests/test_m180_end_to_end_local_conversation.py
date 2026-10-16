from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest

from app.official_conversation_gateway import ConversationOrigin
from app.runtime_ui_adapter import LocalConversationUIAdapter
from core.end_to_end_local_conversation import (
    EndToEndLocalConversation,
    EndToEndLocalConversationConfig,
    JsonLinesLocalConversationJournal,
    LocalConversationTurnStatus,
)
from core.local_runtime_bootstrap import (
    LocalRuntimeBootstrap,
    LocalRuntimeBootstrapConfig,
)
from core.platform_runtime_compatibility import private_file_is_protected
from core.runtime_composition_root import RuntimeCompositionRoot
from tests.test_m178_runtime_composition_root import RecordingProvider, dependencies

NOW = datetime(2026, 7, 12, 23, 30, tzinfo=timezone.utc)


def runtime(tmp_path, *, provider=None, persist=True):
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
            persist_turns=persist,
        ),
    )


def test_real_turn_runs_m179_m178_m177_end_to_end(tmp_path):
    item = runtime(tmp_path)
    item.bootstrap.start(now=NOW)
    turn = item.converse("Explica ROBY", now=NOW)
    assert turn.status is LocalConversationTurnStatus.COMPLETED
    assert turn.response_text == "Hola desde el proveedor local."


def test_runtime_must_be_started(tmp_path):
    with pytest.raises(RuntimeError, match="running"):
        runtime(tmp_path).converse("Hola", now=NOW)


def test_blank_text_is_rejected(tmp_path):
    item = runtime(tmp_path)
    item.bootstrap.start(now=NOW)
    with pytest.raises(ValueError, match="blank"):
        item.converse("  ", now=NOW)


def test_exact_owner_and_session_reach_pipeline(tmp_path):
    item = runtime(tmp_path)
    item.bootstrap.start(now=NOW)
    turn = item.converse("Hola", now=NOW)
    assert turn.owner == "Carlos"
    assert turn.session_id == "desktop-main"


def test_turn_preserves_exact_m177_and_m175_lineage(tmp_path):
    item = runtime(tmp_path)
    composition = item.bootstrap.start(now=NOW)
    turn = item.converse("Hola", now=NOW)
    result = composition.conversation_pipeline.last_result
    assert turn.pipeline_result_id == result.result_id
    assert turn.operational_response_id == result.operational_response.response_id


def test_execution_flags_are_preserved(tmp_path):
    item = runtime(tmp_path)
    item.bootstrap.start(now=NOW)
    turn = item.converse("Hola", now=NOW)
    assert turn.provider_call_performed
    assert turn.retrieval_performed
    assert not turn.network_access_performed


def test_turn_is_persisted_as_local_jsonl(tmp_path):
    item = runtime(tmp_path)
    item.bootstrap.start(now=NOW)
    turn = item.converse("Hola", now=NOW)
    payload = json.loads((tmp_path / "turns.jsonl").read_text().strip())
    assert payload["turn_id"] == turn.turn_id
    assert payload["user_text"] == "Hola"


def test_journal_file_is_private(tmp_path):
    item = runtime(tmp_path)
    item.bootstrap.start(now=NOW)
    item.converse("Hola", now=NOW)
    assert private_file_is_protected(tmp_path / "turns.jsonl")


def test_history_survives_runtime_recreation(tmp_path):
    first = runtime(tmp_path)
    first.bootstrap.start(now=NOW)
    first.converse("Hola", now=NOW)
    second = runtime(tmp_path)
    assert len(second.history) == 1
    assert second.history[0].user_text == "Hola"


def test_sequence_continues_after_restart(tmp_path):
    first = runtime(tmp_path)
    first.bootstrap.start(now=NOW)
    first.converse("Uno", now=NOW)
    first.bootstrap.stop(now=NOW)
    second = runtime(tmp_path)
    second.bootstrap.start(now=NOW)
    assert second.converse("Dos", now=NOW).sequence == 2


def test_history_is_scoped_to_owner_and_session(tmp_path):
    item = runtime(tmp_path)
    item.bootstrap.start(now=NOW)
    item.converse("Hola", now=NOW)
    journal = JsonLinesLocalConversationJournal(tmp_path / "turns.jsonl")
    assert journal.list_for_session("Ana", "desktop-main") == ()
    assert journal.list_for_session("Carlos", "other") == ()


def test_persistence_can_be_disabled(tmp_path):
    item = runtime(tmp_path, persist=False)
    item.bootstrap.start(now=NOW)
    turn = item.converse("Hola", now=NOW)
    assert turn.sequence == 1
    assert item.history == ()
    assert not (tmp_path / "turns.jsonl").exists()


def test_multiple_turns_use_same_composed_runtime(tmp_path):
    provider = RecordingProvider()
    item = runtime(tmp_path, provider=provider)
    composition = item.bootstrap.start(now=NOW)
    item.converse("Uno", now=NOW)
    item.converse("Dos", now=NOW)
    assert item.bootstrap.composition is composition
    assert len(provider.calls) == 2


def test_desktop_adapter_submits_completed_turn_through_official_gateway(tmp_path):
    item = runtime(tmp_path)
    item.bootstrap.start(now=NOW)
    adapter = LocalConversationUIAdapter(item)

    response = adapter.submit_text("Hola")

    assert response.text == "Hola desde el proveedor local."
    assert response.status == "completed"
    assert adapter.runtime.snapshot.last_origin is ConversationOrigin.DESKTOP_TEXT
    item.bootstrap.stop(now=NOW)


def test_desktop_adapter_rejects_blank_text_without_starting_runtime(tmp_path):
    item = runtime(tmp_path)
    response = LocalConversationUIAdapter(item).submit_text(" ")

    assert response.needs_input
    assert response.status == "needs_information"
    assert item.history == ()
    assert not item.bootstrap.is_running


def test_provider_failure_is_contained_as_failed_turn(tmp_path):
    class BrokenProvider(RecordingProvider):
        def generate(self, request):
            raise RuntimeError("offline")

    item = runtime(tmp_path, provider=BrokenProvider())
    item.bootstrap.start(now=NOW)
    turn = item.converse("Hola", now=NOW)
    assert turn.status is LocalConversationTurnStatus.FAILED
    assert turn.response_text == ""


def test_non_deliverable_desktop_output_is_explicit(tmp_path):
    class BrokenProvider(RecordingProvider):
        def generate(self, request):
            raise RuntimeError("offline")

    item = runtime(tmp_path, provider=BrokenProvider())
    item.bootstrap.start(now=NOW)
    response = LocalConversationUIAdapter(item).submit_text("Hola")

    assert response.text == "[failed]"
    assert response.status == "failed"
    item.bootstrap.stop(now=NOW)


def test_turn_id_is_deterministic_for_exact_lineage(tmp_path):
    item = runtime(tmp_path)
    item.bootstrap.start(now=NOW)
    turn = item.converse("Hola", now=NOW)
    loaded = item.history[0]
    assert loaded.turn_id == turn.turn_id


def test_m180_does_not_authorize_platform_mutation(tmp_path):
    item = runtime(tmp_path)
    composition = item.bootstrap.start(now=NOW)
    item.converse("Hola", now=NOW)
    assert not composition.conversation_pipeline.last_result.platform_mutation_performed
