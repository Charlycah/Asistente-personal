from __future__ import annotations

from dataclasses import FrozenInstanceError, fields
from inspect import getsource

import pytest

from core.cognitive_maturity import (
    CoownerIdentity,
    ExplicitInterlocutorDeclarationInterpreter,
    InterlocutorDeclarationKind,
    InterlocutorResolutionAction,
    InterlocutorResolutionSource,
)


def _interpret(text: str):
    return ExplicitInterlocutorDeclarationInterpreter().interpret(
        text,
        session_id="coowners-main",
    )


def test_m386_16_plain_carlos_declaration_requires_confirmation() -> None:
    result = _interpret("Soy Carlos")
    assert result.kind is InterlocutorDeclarationKind.DECLARATION
    assert result.candidate is CoownerIdentity.CARLOS
    assert result.request is not None
    assert result.request.confirmed is False
    assert result.response_code == "interlocutor:confirmation_required"


def test_m386_16_plain_cristina_has_the_same_contract() -> None:
    result = _interpret("Soy Cristina")
    assert result.kind is InterlocutorDeclarationKind.DECLARATION
    assert result.candidate is CoownerIdentity.CRISTINA
    assert result.request is not None
    assert result.request.confirmed is False


def test_m386_16_explicit_confirmation_creates_confirmed_request() -> None:
    result = _interpret("Confirmo que soy Carlos")
    assert result.kind is InterlocutorDeclarationKind.CONFIRMATION
    assert result.request is not None
    assert result.request.confirmed is True
    assert result.request.source is (
        InterlocutorResolutionSource.EXPLICIT_DECLARATION
    )


def test_m386_16_explicit_replacement_is_reconfirmation() -> None:
    result = _interpret("Confirmo cambiar interlocutor a Cristina")
    assert result.kind is InterlocutorDeclarationKind.REPLACEMENT
    assert result.candidate is CoownerIdentity.CRISTINA
    assert result.request is not None
    assert result.request.confirmed is True
    assert result.request.replace_existing is True
    assert result.request.source is (
        InterlocutorResolutionSource.EXPLICIT_RECONFIRMATION
    )


def test_m386_16_explicit_revocation_creates_no_identity_candidate() -> None:
    result = _interpret("Confirmo revocar la identificación del interlocutor")
    assert result.kind is InterlocutorDeclarationKind.REVOCATION
    assert result.candidate is None
    assert result.request is not None
    assert result.request.action is InterlocutorResolutionAction.REVOKE
    assert result.request.confirmed is True


def test_m386_16_casual_or_extended_mentions_do_not_match() -> None:
    texts = (
        "Carlos dijo que mañana llueve",
        "Quiero consultar algo para Cristina",
        "Soy amigo de Carlos",
        "¿Carlos o Cristina prefieren té?",
        "Hola, soy Carlos",
    )
    for text in texts:
        result = _interpret(text)
        assert result.kind is InterlocutorDeclarationKind.NO_MATCH
        assert result.matched is False
        assert result.candidate is None
        assert result.request is None


def test_m386_16_ambiguous_self_declaration_does_not_guess() -> None:
    result = _interpret("Soy Carlos o Cristina")
    assert result.kind is InterlocutorDeclarationKind.NO_MATCH
    assert result.request is None


def test_m386_16_normalization_is_bounded_and_deterministic() -> None:
    result = _interpret("  CONFIRMO   QUE SOY CRISTINA!!!  ")
    assert result.kind is InterlocutorDeclarationKind.CONFIRMATION
    assert result.candidate is CoownerIdentity.CRISTINA


def test_m386_16_interpretation_does_not_retain_input_text() -> None:
    private_text = "Carlos dijo un dato privado"
    result = _interpret(private_text)
    assert private_text not in repr(result)
    assert {item.name for item in fields(result)} == {
        "kind",
        "candidate",
        "request",
        "response_code",
        "matched",
        "grants_action_authority",
    }


def test_m386_16_result_is_immutable_and_non_authoritative() -> None:
    result = _interpret("Soy Carlos")
    assert result.grants_action_authority is False
    with pytest.raises(FrozenInstanceError):
        result.candidate = CoownerIdentity.CRISTINA


def test_m386_16_interpreter_uses_no_model_biometrics_or_memory() -> None:
    source = getsource(ExplicitInterlocutorDeclarationInterpreter).casefold()
    forbidden = (
        "llm",
        "provider",
        "camera",
        "face",
        "voiceprint",
        "recall(",
        "remember(",
    )
    assert all(item not in source for item in forbidden)


def test_m386_16_interpreter_does_not_apply_or_persist_state() -> None:
    source = getsource(ExplicitInterlocutorDeclarationInterpreter)
    forbidden_calls = (
        "apply(",
        "save(",
        "persist(",
        "execute(",
        "converse(",
    )
    assert all(call not in source for call in forbidden_calls)
    assert "UnifiedBrain" not in source
    assert "OfficialConversationGateway" not in source
    assert "EndToEndLocalConversation" not in source
