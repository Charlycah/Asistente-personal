from datetime import datetime, timedelta, timezone

import pytest

from core.supervised_autonomy import (
    AutonomyEventType,
    AutonomyRisk,
    AutonomyStatus,
    SupervisedAutonomyPolicy,
    SupervisedAutonomyService,
)

NOW = datetime(2026, 7, 20, 20, 0, tzinfo=timezone.utc)


def proposal(service, action="create_calendar_event"):
    return service.propose(
        action,
        "Preparar una acción útil y verificable",
        requested_by="Carlos",
        now=NOW,
    )


def test_medium_risk_proposal_requires_human_approval():
    service = SupervisedAutonomyService()
    item = proposal(service)
    assert item.normalized_risk is AutonomyRisk.MEDIUM
    assert item.normalized_status is AutonomyStatus.AWAITING_APPROVAL
    assert service.snapshot.events[-1].event_type is AutonomyEventType.APPROVAL_REQUIRED


def test_prohibited_action_is_blocked_and_never_authorized():
    service = SupervisedAutonomyService()
    item = proposal(service, "run_shell")
    assert item.normalized_status is AutonomyStatus.BLOCKED
    with pytest.raises(ValueError, match="terminal"):
        service.approve(item.proposal_id, approved_by="Carlos", now=NOW)


def test_explicit_approval_issues_bounded_execution_token():
    service = SupervisedAutonomyService()
    item = proposal(service)
    approved = service.approve(
        item.proposal_id,
        approved_by="Carlos",
        now=NOW + timedelta(seconds=1),
    )
    token = service.authorize_execution(
        item.proposal_id,
        now=NOW + timedelta(seconds=2),
    )
    assert approved.normalized_status is AutonomyStatus.APPROVED
    assert len(token.authorization_id) == 64
    assert service.get(item.proposal_id).normalized_status is AutonomyStatus.EXECUTING


def test_unapproved_proposal_cannot_execute():
    service = SupervisedAutonomyService()
    item = proposal(service)
    with pytest.raises(PermissionError, match="not approved"):
        service.authorize_execution(item.proposal_id, now=NOW)


def test_execution_can_complete_or_fail_with_audit():
    service = SupervisedAutonomyService()
    first = proposal(service)
    service.approve(first.proposal_id, approved_by="Carlos", now=NOW)
    service.authorize_execution(first.proposal_id, now=NOW)
    completed = service.complete(
        first.proposal_id,
        result_summary="Evento creado correctamente",
        now=NOW,
    )
    second = service.propose(
        "modify_reminder",
        "Modificar un recordatorio",
        requested_by="Carlos",
        now=NOW + timedelta(seconds=1),
    )
    service.approve(
        second.proposal_id,
        approved_by="Carlos",
        now=NOW + timedelta(seconds=1),
    )
    service.authorize_execution(second.proposal_id, now=NOW + timedelta(seconds=1))
    failed = service.fail(
        second.proposal_id,
        error_summary="El adaptador rechazó la modificación",
        now=NOW + timedelta(seconds=1),
    )
    assert completed.normalized_status is AutonomyStatus.COMPLETED
    assert failed.normalized_status is AutonomyStatus.FAILED


def test_rejection_and_cancellation_are_terminal():
    service = SupervisedAutonomyService()
    rejected = proposal(service)
    service.reject(
        rejected.proposal_id,
        rejected_by="Carlos",
        reason="No corresponde hacerlo ahora",
        now=NOW,
    )
    cancelled = service.propose(
        "sync_preferences",
        "Sincronizar preferencias",
        requested_by="Carlos",
        now=NOW + timedelta(seconds=1),
    )
    result = service.cancel(
        cancelled.proposal_id,
        cancelled_by="Carlos",
        reason="Operación cancelada por el usuario",
        now=NOW + timedelta(seconds=1),
    )
    assert result.normalized_status is AutonomyStatus.CANCELLED
    with pytest.raises(ValueError, match="terminal"):
        service.approve(rejected.proposal_id, approved_by="Carlos", now=NOW)


def test_proposals_and_execution_authorizations_expire():
    policy = SupervisedAutonomyPolicy(
        proposal_ttl=timedelta(seconds=10),
        execution_ttl=timedelta(seconds=5),
    )
    service = SupervisedAutonomyService(policy)
    old = proposal(service)
    assert service.expire_pending(now=NOW + timedelta(seconds=10)) == (
        old.proposal_id,
    )
    current = service.propose(
        "modify_reminder",
        "Modificar otro recordatorio",
        requested_by="Carlos",
        now=NOW + timedelta(seconds=11),
    )
    service.approve(
        current.proposal_id,
        approved_by="Carlos",
        now=NOW + timedelta(seconds=11),
    )
    with pytest.raises(PermissionError, match="expired"):
        service.authorize_execution(
            current.proposal_id,
            now=NOW + timedelta(seconds=16),
        )


def test_low_risk_auto_approval_is_explicit_policy_only():
    default_service = SupervisedAutonomyService()
    default = proposal(default_service, "request_status")
    assert default.normalized_status is AutonomyStatus.AWAITING_APPROVAL
    enabled = SupervisedAutonomyService(
        SupervisedAutonomyPolicy(allow_low_risk_automatic_approval=True)
    )
    automatic = proposal(enabled, "request_status")
    assert automatic.normalized_status is AutonomyStatus.APPROVED


def test_pending_limit_and_duplicate_proposals_are_enforced():
    service = SupervisedAutonomyService(
        SupervisedAutonomyPolicy(maximum_pending=1)
    )
    proposal(service)
    with pytest.raises(RuntimeError, match="maximum pending"):
        service.propose(
            "request_status",
            "Consultar estado",
            requested_by="Carlos",
            now=NOW + timedelta(seconds=1),
        )


def test_audit_events_have_stable_sha256_identifiers():
    service = SupervisedAutonomyService()
    proposal(service)
    assert all(len(event.event_id) == 64 for event in service.snapshot.events)


def test_invalid_configuration_and_naive_times_are_rejected():
    with pytest.raises(ValueError, match="positive"):
        SupervisedAutonomyPolicy(proposal_ttl=timedelta(0))
    service = SupervisedAutonomyService()
    with pytest.raises(ValueError, match="timezone-aware"):
        service.propose(
            "request_status",
            "Consultar estado",
            requested_by="Carlos",
            now=datetime(2026, 7, 20, 20, 0),
        )
