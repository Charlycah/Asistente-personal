from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from inspect import getsource
from pathlib import Path

import pytest

from app.official_conversation_gateway import OfficialConversationGateway
from app.unified_brain import UnifiedBrain, UnifiedBrainDiagnosticSnapshot

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Turn:
    response_text = "respuesta"
    status = "completed"
    session_id = "familia"
    provider_call_performed = False
    retrieval_performed = False
    network_access_performed = False


class ConversationRuntimeStub:
    def converse(self, text: str) -> Turn:
        return Turn()


def _brain() -> UnifiedBrain:
    return UnifiedBrain(OfficialConversationGateway(ConversationRuntimeStub()))


def test_diagnostics_unifies_the_existing_conversation_and_reflection_views() -> None:
    brain = _brain()
    brain.process("contenido privado", session_id="familia")

    diagnostics = brain.diagnostics

    assert isinstance(diagnostics, UnifiedBrainDiagnosticSnapshot)
    assert diagnostics.conversation == brain.snapshot
    assert diagnostics.reflection == brain.reflection_snapshot
    assert diagnostics.fully_observed is True
    assert diagnostics.observation_gap == 0


def test_diagnostics_starts_consistent_without_inventing_activity() -> None:
    diagnostics = _brain().diagnostics

    assert diagnostics.conversation.processed_messages == 0
    assert diagnostics.reflection.observed_turns == 0
    assert diagnostics.fully_observed is True
    assert diagnostics.observation_gap == 0


def test_diagnostic_view_is_immutable_and_contains_no_message_content() -> None:
    brain = _brain()
    brain.process("información familiar reservada")
    diagnostics = brain.diagnostics

    assert {item.name for item in fields(diagnostics)} == {
        "conversation",
        "reflection",
        "fully_observed",
        "observation_gap",
    }
    assert "información familiar reservada" not in repr(diagnostics)
    with pytest.raises(FrozenInstanceError):
        diagnostics.observation_gap = 99


def test_diagnostics_has_no_memory_decision_or_operational_authority() -> None:
    source = getsource(UnifiedBrain.diagnostics.fget)
    forbidden_calls = (
        "alert(",
        "decide(",
        "execute(",
        "persist(",
        "recall(",
        "remember(",
        "retry(",
    )

    assert all(call not in source for call in forbidden_calls)


def test_m382_closure_documents_one_boundary_without_absorbing_domains() -> None:
    document = (
        PROJECT_ROOT / "docs" / "M382_UNIFIED_BRAIN_STABILIZATION.md"
    ).read_text(encoding="utf-8")

    assert "single application integration boundary" in document
    assert "does not absorb" in document
    for authority in ("Memory", "decision", "agenda", "reminders", "notes"):
        assert authority in document
