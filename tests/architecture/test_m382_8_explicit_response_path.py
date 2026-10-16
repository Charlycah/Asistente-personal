from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

from core.end_to_end_local_conversation import LocalConversationTurn
from core.governed_operational_conversation_pipeline import (
    ConversationResponsePath,
    GovernedConversationPipelineStatus,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 8, 4, 12, 0, tzinfo=timezone.utc)


def _pipeline_result(path: ConversationResponsePath):
    return SimpleNamespace(
        request=SimpleNamespace(
            owner="Carlos",
            session_id="familia",
            text="mensaje",
        ),
        status=GovernedConversationPipelineStatus.COMPLETED,
        operational_response=SimpleNamespace(
            response_text="respuesta",
            response_id="response-id",
        ),
        result_id="pipeline-id",
        provider_call_performed=path is ConversationResponsePath.PROVIDER,
        retrieval_performed=False,
        network_access_performed=False,
        rationale=("completed",),
        response_path=path,
        created_at=NOW,
    )


def test_pipeline_response_path_is_propagated_to_the_local_turn() -> None:
    for path in ConversationResponsePath:
        turn = LocalConversationTurn.from_pipeline_result(
            sequence=1,
            result=_pipeline_result(path),
        )

        assert turn.response_path is path


def test_response_path_is_persisted_without_changing_historical_turn_identity() -> None:
    model_source = (
        PROJECT_ROOT / "core" / "end_to_end_local_conversation" / "models.py"
    ).read_text(encoding="utf-8")
    journal_source = (
        PROJECT_ROOT / "core" / "end_to_end_local_conversation" / "journal.py"
    ).read_text(encoding="utf-8")

    identity_payload = model_source.split("def _identity_payload", maxsplit=1)[1]
    assert "response_path" not in identity_payload
    assert '"response_path": turn.response_path.value' in journal_source


def test_historical_turns_default_to_conservative_degraded_path() -> None:
    turn = LocalConversationTurn(
        owner="Carlos",
        session_id="familia",
        sequence=1,
        user_text="mensaje",
        response_text="respuesta",
        status="completed",
        pipeline_result_id="pipeline-id",
        operational_response_id="response-id",
        provider_call_performed=False,
        retrieval_performed=False,
        network_access_performed=False,
        rationale=("historical_turn",),
        created_at=NOW,
    )

    assert turn.response_path is ConversationResponsePath.DEGRADED


def test_pipeline_assigns_each_response_path_without_text_heuristics() -> None:
    source = (
        PROJECT_ROOT
        / "core"
        / "governed_operational_conversation_pipeline"
        / "pipeline.py"
    ).read_text(encoding="utf-8")

    assert "ConversationResponsePath.PROVIDER" in source
    assert "ConversationResponsePath.INTERCEPTOR" in source
    assert "ConversationResponsePath.DEGRADED" in source
    assert "response_text.casefold" not in source
