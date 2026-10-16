from __future__ import annotations

from dataclasses import FrozenInstanceError, replace

import pytest

from core.cognitive_maturity import (
    COOWNER_PERMISSION_CONFLICT_POLICY,
    COOWNER_PERMISSION_MATRIX,
    EQUAL_COOWNERS,
    CoownerIdentity,
    PermissionMode,
    PermissionRisk,
    coowner_permission_rule,
)

EXPECTED_ACTIONS = {
    "conversation_response",
    "read_only_analysis",
    "memory_recall",
    "memory_write_correct_archive",
    "learning_activation",
    "planning_and_recommendation",
    "external_information_read",
    "sensor_observation",
    "external_message_or_write",
    "physical_device_control",
    "health_or_psychological_decision",
    "permanent_personal_data_deletion",
    "credential_secret_exposure",
    "unbounded_destructive_action",
    "self_modification_or_permission_expansion",
}


def test_m386_4_matrix_covers_the_agreed_action_families() -> None:
    action_ids = {rule.action_id for rule in COOWNER_PERMISSION_MATRIX}
    assert action_ids == EXPECTED_ACTIONS
    assert len(action_ids) == len(COOWNER_PERMISSION_MATRIX)


def test_m386_4_carlos_and_cristina_have_identical_authority() -> None:
    assert EQUAL_COOWNERS == {
        CoownerIdentity.CARLOS,
        CoownerIdentity.CRISTINA,
    }
    assert all(
        rule.authorized_coowners == EQUAL_COOWNERS
        for rule in COOWNER_PERMISSION_MATRIX
    )


def test_m386_4_unequal_authority_is_rejected_by_construction() -> None:
    rule = coowner_permission_rule("conversation_response")
    with pytest.raises(ValueError, match="equal permission authority"):
        replace(
            rule,
            authorized_coowners=frozenset({CoownerIdentity.CARLOS}),
        )


def test_m386_4_matrix_never_grants_runtime_action_authority() -> None:
    assert all(not rule.grants_action_authority for rule in COOWNER_PERMISSION_MATRIX)
    assert all(rule.existing_authorities for rule in COOWNER_PERMISSION_MATRIX)


def test_m386_4_internal_actions_have_no_external_or_persistent_effect() -> None:
    internal = [
        rule
        for rule in COOWNER_PERMISSION_MATRIX
        if rule.mode is PermissionMode.INTERNAL
    ]
    assert internal
    assert all(not rule.external_effect for rule in internal)
    assert all(not rule.persistent_effect for rule in internal)


def test_m386_4_standing_delegation_is_limited_to_medium_risk() -> None:
    delegated = [
        rule
        for rule in COOWNER_PERMISSION_MATRIX
        if rule.mode is PermissionMode.DELEGABLE
    ]
    assert delegated
    assert all(rule.risk is PermissionRisk.MEDIUM for rule in delegated)
    assert all(rule.audit_required for rule in delegated)


def test_m386_4_memory_mutation_and_learning_require_confirmation() -> None:
    for action_id in ("memory_write_correct_archive", "learning_activation"):
        rule = coowner_permission_rule(action_id)
        assert rule.mode is PermissionMode.CONFIRMATION_REQUIRED
        assert rule.persistent_effect is True
        assert rule.audit_required is True


def test_m386_4_health_decisions_remain_proposals() -> None:
    rule = coowner_permission_rule("health_or_psychological_decision")
    assert rule.mode is PermissionMode.PROPOSE_ONLY
    assert rule.risk is PermissionRisk.HIGH


def test_m386_4_critical_self_expansion_and_secret_exposure_are_forbidden() -> None:
    for action_id in (
        "credential_secret_exposure",
        "self_modification_or_permission_expansion",
    ):
        rule = coowner_permission_rule(action_id)
        assert rule.risk is PermissionRisk.CRITICAL
        assert rule.mode is PermissionMode.FORBIDDEN


def test_m386_4_conflict_or_revocation_fails_closed() -> None:
    policy = " ".join(COOWNER_PERMISSION_CONFLICT_POLICY)
    assert "idéntica autoridad" in policy
    assert "revocación vigente bloquea" in policy
    assert "requieren aclaración" in policy
    assert "no reemplaza la autoridad de dominio" in policy


def test_m386_4_rules_are_immutable_and_unknown_actions_are_rejected() -> None:
    rule = coowner_permission_rule("sensor_observation")
    with pytest.raises(FrozenInstanceError):
        rule.mode = PermissionMode.INTERNAL
    with pytest.raises(KeyError):
        coowner_permission_rule("invented_permission")

