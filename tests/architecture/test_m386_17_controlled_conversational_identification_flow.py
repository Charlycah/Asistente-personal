from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from inspect import getsource

import pytest

from core.cognitive_maturity import (
    ControlledConversationalIdentificationFlow,
    CoownerIdentity,
    InterlocutorResolutionStatus,
)


def test_m386_17_common_conversation_is_not_handled_or_stateful() -> None:
    flow = ControlledConversationalIdentificationFlow()
    result = flow.process("Carlos dijo que mañana llueve", session_id="main")
    assert result.handled is False
    assert result.resolution is None
    assert result.response_text is None
    assert flow.state.snapshot.retained_sessions == 0


def test_m386_17_declaration_creates_pending_state_and_fixed_prompt() -> None:
    flow = ControlledConversationalIdentificationFlow()
    result = flow.process("Soy Carlos", session_id="main")
    assert result.handled is True
    assert result.resolution is not None
    assert result.resolution.status is (
        InterlocutorResolutionStatus.PENDING_CONFIRMATION
    )
    assert result.response_text == (
        "Entendí que sos Carlos. Para confirmarlo, escribí exactamente: "
        "Confirmo que soy Carlos."
    )
    assert result.resolution.may_use_private_context is False


def test_m386_17_confirmation_activates_carlos_for_that_session() -> None:
    flow = ControlledConversationalIdentificationFlow()
    flow.process("Soy Carlos", session_id="main")
    result = flow.process("Confirmo que soy Carlos", session_id="main")
    assert result.resolution is not None
    assert result.resolution.status is InterlocutorResolutionStatus.RESOLVED
    assert result.resolution.interlocutor is CoownerIdentity.CARLOS
    assert result.resolution.may_use_private_context is True


def test_m386_17_cristina_follows_the_identical_flow() -> None:
    flow = ControlledConversationalIdentificationFlow()
    pending = flow.process("Soy Cristina", session_id="main")
    resolved = flow.process("Confirmo que soy Cristina", session_id="main")
    assert pending.resolution is not None
    assert pending.resolution.may_use_private_context is False
    assert resolved.resolution is not None
    assert resolved.resolution.interlocutor is CoownerIdentity.CRISTINA
    assert resolved.resolution.equal_coowner_authority is True


def test_m386_17_ordinary_confirmation_cannot_silently_switch_person() -> None:
    flow = ControlledConversationalIdentificationFlow()
    flow.process("Confirmo que soy Carlos", session_id="main")
    result = flow.process("Confirmo que soy Cristina", session_id="main")
    assert result.resolution is not None
    assert result.resolution.status is InterlocutorResolutionStatus.CONFLICT
    assert result.resolution.may_use_private_context is False
    assert "Confirmo cambiar interlocutor a Cristina" in result.response_text


def test_m386_17_explicit_replacement_changes_the_active_person() -> None:
    flow = ControlledConversationalIdentificationFlow()
    flow.process("Confirmo que soy Carlos", session_id="main")
    result = flow.process(
        "Confirmo cambiar interlocutor a Cristina",
        session_id="main",
    )
    assert result.resolution is not None
    assert result.resolution.status is InterlocutorResolutionStatus.RESOLVED
    assert result.resolution.interlocutor is CoownerIdentity.CRISTINA
    assert "autoridad de Carlos y Cristina sigue siendo idéntica" in (
        result.response_text
    )


def test_m386_17_revocation_closes_private_context() -> None:
    flow = ControlledConversationalIdentificationFlow()
    flow.process("Confirmo que soy Carlos", session_id="main")
    result = flow.process(
        "Confirmo revocar la identificación del interlocutor",
        session_id="main",
    )
    assert result.resolution is not None
    assert result.resolution.status is InterlocutorResolutionStatus.REVOKED
    assert result.resolution.may_use_private_context is False
    assert "contexto privado permanece cerrado" in result.response_text


def test_m386_17_identification_state_is_isolated_by_session() -> None:
    flow = ControlledConversationalIdentificationFlow()
    flow.process("Confirmo que soy Carlos", session_id="carlos-session")
    flow.process("Confirmo que soy Cristina", session_id="cristina-session")
    assert flow.state.current("carlos-session").interlocutor is (
        CoownerIdentity.CARLOS
    )
    assert flow.state.current("cristina-session").interlocutor is (
        CoownerIdentity.CRISTINA
    )


def test_m386_17_result_is_immutable_and_does_not_retain_input_text() -> None:
    flow = ControlledConversationalIdentificationFlow()
    private_text = "Carlos dijo un contenido reservado"
    result = flow.process(private_text, session_id="main")
    assert private_text not in repr(result)
    assert {item.name for item in fields(result)} == {
        "handled",
        "interpretation",
        "resolution",
        "response_text",
        "grants_action_authority",
    }
    with pytest.raises(FrozenInstanceError):
        result.handled = True


def test_m386_17_flow_grants_no_action_authority() -> None:
    result = ControlledConversationalIdentificationFlow().process(
        "Soy Carlos",
        session_id="main",
    )
    assert result.grants_action_authority is False
    assert result.resolution is not None
    assert result.resolution.grants_action_authority is False


def test_m386_17_flow_uses_no_model_io_memory_or_execution() -> None:
    source = getsource(ControlledConversationalIdentificationFlow).casefold()
    forbidden = (
        "llm",
        "provider",
        "open(",
        "write(",
        "save(",
        "persist(",
        "recall(",
        "remember(",
        "execute(",
    )
    assert all(item not in source for item in forbidden)


def test_m386_17_flow_is_not_wired_to_productive_runtime() -> None:
    source = getsource(ControlledConversationalIdentificationFlow)
    assert "UnifiedBrain" not in source
    assert "OfficialConversationGateway" not in source
    assert "EndToEndLocalConversation" not in source
