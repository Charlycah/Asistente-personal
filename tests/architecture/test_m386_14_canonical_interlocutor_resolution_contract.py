from __future__ import annotations

from dataclasses import FrozenInstanceError
from inspect import getsource

import pytest

from core.cognitive_maturity import (
    EQUAL_COOWNERS,
    CanonicalInterlocutorResolver,
    CoownerIdentity,
    InterlocutorResolutionAction,
    InterlocutorResolutionRequest,
    InterlocutorResolutionSource,
    InterlocutorResolutionStatus,
)


def _request(**overrides) -> InterlocutorResolutionRequest:
    values = {
        "session_id": "coowners-main",
        "action": InterlocutorResolutionAction.DECLARE,
        "source": InterlocutorResolutionSource.EXPLICIT_DECLARATION,
        "declared_interlocutor": CoownerIdentity.CARLOS,
        "confirmed": True,
    }
    values.update(overrides)
    return InterlocutorResolutionRequest(**values)


def test_m386_14_explicit_carlos_declaration_resolves_for_the_session() -> None:
    result = CanonicalInterlocutorResolver().resolve(_request())
    assert result.status is InterlocutorResolutionStatus.RESOLVED
    assert result.interlocutor is CoownerIdentity.CARLOS
    assert result.scope == "session"
    assert result.interlocutor_resolved is True
    assert result.may_use_private_context is True


def test_m386_14_explicit_cristina_has_exactly_equal_authority() -> None:
    resolver = CanonicalInterlocutorResolver()
    cristina = resolver.resolve(
        _request(declared_interlocutor="cristina")
    )
    assert cristina.interlocutor is CoownerIdentity.CRISTINA
    assert cristina.equal_coowner_authority is True
    assert cristina.grants_action_authority is False
    assert EQUAL_COOWNERS == {
        CoownerIdentity.CARLOS,
        CoownerIdentity.CRISTINA,
    }


def test_m386_14_unconfirmed_declaration_remains_pending() -> None:
    result = CanonicalInterlocutorResolver().resolve(
        _request(confirmed=False)
    )
    assert result.status is InterlocutorResolutionStatus.PENDING_CONFIRMATION
    assert result.interlocutor is None
    assert result.candidate is CoownerIdentity.CARLOS
    assert result.may_use_private_context is False


def test_m386_14_unknown_session_starts_without_guessing() -> None:
    result = CanonicalInterlocutorResolver.unresolved("coowners-main")
    assert result.status is InterlocutorResolutionStatus.UNKNOWN
    assert result.interlocutor is None
    assert result.candidate is None
    assert result.reason_code == "interlocutor:not_declared"


def test_m386_14_switching_people_requires_explicit_replacement() -> None:
    resolver = CanonicalInterlocutorResolver()
    conflict = resolver.resolve(
        _request(
            declared_interlocutor="Cristina",
            current_interlocutor="Carlos",
        )
    )
    assert conflict.status is InterlocutorResolutionStatus.CONFLICT
    assert conflict.interlocutor is None
    replaced = resolver.resolve(
        _request(
            source=InterlocutorResolutionSource.EXPLICIT_RECONFIRMATION,
            declared_interlocutor="Cristina",
            current_interlocutor="Carlos",
            replace_existing=True,
        )
    )
    assert replaced.status is InterlocutorResolutionStatus.RESOLVED
    assert replaced.interlocutor is CoownerIdentity.CRISTINA


def test_m386_14_explicit_revocation_removes_private_context_access() -> None:
    result = CanonicalInterlocutorResolver().resolve(
        _request(
            action=InterlocutorResolutionAction.REVOKE,
            source=InterlocutorResolutionSource.EXPLICIT_RECONFIRMATION,
            declared_interlocutor=None,
            current_interlocutor="Carlos",
        )
    )
    assert result.status is InterlocutorResolutionStatus.REVOKED
    assert result.interlocutor is None
    assert result.may_use_private_context is False


def test_m386_14_visitors_and_third_identities_are_rejected() -> None:
    with pytest.raises(ValueError, match="Carlos or Cristina"):
        _request(declared_interlocutor="Visitante")
    with pytest.raises(ValueError, match="Carlos or Cristina"):
        _request(declared_interlocutor="Familia")


def test_m386_14_resolution_uses_no_biometrics_or_inference() -> None:
    result = CanonicalInterlocutorResolver().resolve(_request())
    assert result.biometric_evidence_used is False
    assert result.inferred_identity_used is False
    source = getsource(CanonicalInterlocutorResolver)
    for forbidden in ("face", "voiceprint", "camera", "writing_style"):
        assert forbidden not in source.casefold()


def test_m386_14_resolution_is_immutable_and_deterministic() -> None:
    resolver = CanonicalInterlocutorResolver()
    first = resolver.resolve(_request())
    second = resolver.resolve(_request())
    assert first.resolution_id == second.resolution_id
    with pytest.raises(FrozenInstanceError):
        first.interlocutor = CoownerIdentity.CRISTINA


def test_m386_14_session_identifier_must_be_safe() -> None:
    with pytest.raises(ValueError, match="safe identifier"):
        _request(session_id="sesión con datos privados")


def test_m386_14_contract_does_not_execute_or_persist() -> None:
    source = getsource(CanonicalInterlocutorResolver)
    forbidden_calls = (
        "converse(",
        "execute(",
        "persist(",
        "save(",
        "recall(",
        "remember(",
        "request(",
    )
    assert all(call not in source for call in forbidden_calls)


def test_m386_14_contract_is_not_yet_wired_to_productive_runtime() -> None:
    source = getsource(CanonicalInterlocutorResolver)
    assert "UnifiedBrain" not in source
    assert "OfficialConversationGateway" not in source
    assert "EndToEndLocalConversation" not in source
