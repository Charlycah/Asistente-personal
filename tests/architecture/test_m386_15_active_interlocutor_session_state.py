from __future__ import annotations

from dataclasses import FrozenInstanceError
from inspect import getsource

import pytest

from core.cognitive_maturity import (
    ActiveInterlocutorSessionState,
    CoownerIdentity,
    InterlocutorResolutionAction,
    InterlocutorResolutionRequest,
    InterlocutorResolutionSource,
    InterlocutorResolutionStatus,
)


def _declare(
    person: str = "Carlos",
    *,
    session_id: str = "coowners-main",
    confirmed: bool = True,
    replace_existing: bool = False,
    current: str | None = None,
    source: InterlocutorResolutionSource = (
        InterlocutorResolutionSource.EXPLICIT_DECLARATION
    ),
) -> InterlocutorResolutionRequest:
    return InterlocutorResolutionRequest(
        session_id=session_id,
        action=InterlocutorResolutionAction.DECLARE,
        source=source,
        declared_interlocutor=person,
        current_interlocutor=current,
        confirmed=confirmed,
        replace_existing=replace_existing,
    )


def _revoke(session_id: str = "coowners-main") -> InterlocutorResolutionRequest:
    return InterlocutorResolutionRequest(
        session_id=session_id,
        action=InterlocutorResolutionAction.REVOKE,
        source=InterlocutorResolutionSource.EXPLICIT_RECONFIRMATION,
        confirmed=True,
    )


def test_m386_15_unknown_session_starts_without_an_interlocutor() -> None:
    state = ActiveInterlocutorSessionState()
    current = state.current("coowners-main")
    assert current.status is InterlocutorResolutionStatus.UNKNOWN
    assert current.interlocutor is None
    assert current.may_use_private_context is False
    assert state.snapshot.retained_sessions == 0


def test_m386_15_confirmed_declaration_becomes_active_for_session() -> None:
    state = ActiveInterlocutorSessionState()
    result = state.apply(_declare("Carlos"))
    assert result.status is InterlocutorResolutionStatus.RESOLVED
    assert state.current("coowners-main") == result
    assert result.interlocutor is CoownerIdentity.CARLOS
    assert result.may_use_private_context is True


def test_m386_15_sessions_are_strictly_isolated() -> None:
    state = ActiveInterlocutorSessionState()
    state.apply(_declare("Carlos", session_id="session-carlos"))
    state.apply(_declare("Cristina", session_id="session-cristina"))
    assert state.current("session-carlos").interlocutor is (
        CoownerIdentity.CARLOS
    )
    assert state.current("session-cristina").interlocutor is (
        CoownerIdentity.CRISTINA
    )


def test_m386_15_pending_declaration_suspends_private_context() -> None:
    state = ActiveInterlocutorSessionState()
    state.apply(_declare("Carlos"))
    pending = state.apply(_declare("Cristina", confirmed=False))
    assert pending.status is InterlocutorResolutionStatus.PENDING_CONFIRMATION
    assert state.current("coowners-main") == pending
    assert state.current("coowners-main").may_use_private_context is False


def test_m386_15_switch_without_reconfirmation_remains_conflict() -> None:
    state = ActiveInterlocutorSessionState()
    state.apply(_declare("Carlos"))
    conflict = state.apply(_declare("Cristina"))
    assert conflict.status is InterlocutorResolutionStatus.CONFLICT
    assert conflict.interlocutor is None
    assert conflict.may_use_private_context is False


def test_m386_15_explicit_reconfirmation_switches_interlocutor() -> None:
    state = ActiveInterlocutorSessionState()
    state.apply(_declare("Carlos"))
    changed = state.apply(
        _declare(
            "Cristina",
            replace_existing=True,
            source=InterlocutorResolutionSource.EXPLICIT_RECONFIRMATION,
        )
    )
    assert changed.status is InterlocutorResolutionStatus.RESOLVED
    assert changed.interlocutor is CoownerIdentity.CRISTINA
    assert state.current("coowners-main") == changed


def test_m386_15_revocation_closes_private_context() -> None:
    state = ActiveInterlocutorSessionState()
    state.apply(_declare("Carlos"))
    revoked = state.revoke(_revoke())
    assert revoked.status is InterlocutorResolutionStatus.REVOKED
    assert revoked.interlocutor is None
    assert revoked.may_use_private_context is False
    assert state.current("coowners-main") == revoked


def test_m386_15_caller_cannot_spoof_authoritative_current_identity() -> None:
    state = ActiveInterlocutorSessionState()
    state.apply(_declare("Carlos"))
    conflict = state.apply(_declare("Cristina", current="Cristina"))
    assert conflict.status is InterlocutorResolutionStatus.CONFLICT
    assert conflict.reason_code == (
        "interlocutor:replacement_confirmation_required"
    )


def test_m386_15_snapshot_is_immutable_temporary_and_non_authoritative() -> None:
    state = ActiveInterlocutorSessionState()
    state.apply(_declare("Carlos"))
    snapshot = state.snapshot
    assert snapshot.persisted is False
    assert snapshot.grants_action_authority is False
    assert snapshot.retained_sessions == 1
    assert snapshot.resolved_sessions == 1
    with pytest.raises(FrozenInstanceError):
        snapshot.resolved_sessions = 99


def test_m386_15_retention_is_bounded_and_evicts_identity_together() -> None:
    state = ActiveInterlocutorSessionState(max_sessions=2)
    state.apply(_declare("Carlos", session_id="session-1"))
    state.apply(_declare("Cristina", session_id="session-2"))
    state.apply(_declare("Carlos", session_id="session-3"))
    assert state.snapshot.retained_sessions == 2
    assert state.current("session-1").status is (
        InterlocutorResolutionStatus.UNKNOWN
    )
    assert tuple(item.session_id for item in state.snapshot.states) == (
        "session-2",
        "session-3",
    )


def test_m386_15_state_performs_no_io_or_operational_actions() -> None:
    source = getsource(ActiveInterlocutorSessionState)
    forbidden_calls = (
        "open(",
        "write(",
        "save(",
        "persist(",
        "converse(",
        "execute(",
        "recall(",
        "remember(",
    )
    assert all(call not in source for call in forbidden_calls)


def test_m386_15_state_is_not_yet_wired_to_productive_runtime() -> None:
    source = getsource(ActiveInterlocutorSessionState)
    assert "UnifiedBrain" not in source
    assert "OfficialConversationGateway" not in source
    assert "EndToEndLocalConversation" not in source
