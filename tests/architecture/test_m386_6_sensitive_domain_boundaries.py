from __future__ import annotations

from dataclasses import FrozenInstanceError, replace

import pytest

from core.cognitive_maturity import (
    SENSITIVE_BOUNDARY_CONFLICT_POLICY,
    SENSITIVE_DOMAIN_BOUNDARIES,
    GovernedAutonomyStage,
    PermissionMode,
    SensitiveDomain,
    sensitive_domain_boundary,
)

EXPECTED_DOMAINS = {
    SensitiveDomain.HEALTH,
    SensitiveDomain.PSYCHOLOGY,
    SensitiveDomain.PRIVACY,
    SensitiveDomain.EXTERNAL_ACTION,
}


def test_m386_6_defines_exactly_the_four_sensitive_domains() -> None:
    domains = {boundary.domain for boundary in SENSITIVE_DOMAIN_BOUNDARIES}
    assert domains == EXPECTED_DOMAINS
    assert len(domains) == len(SENSITIVE_DOMAIN_BOUNDARIES)


def test_m386_6_boundaries_never_grant_action_authority() -> None:
    assert all(not item.grants_action_authority for item in SENSITIVE_DOMAIN_BOUNDARIES)
    assert all(item.existing_authorities for item in SENSITIVE_DOMAIN_BOUNDARIES)


def test_m386_6_health_and_psychology_stop_at_recommendation() -> None:
    for domain in (SensitiveDomain.HEALTH, SensitiveDomain.PSYCHOLOGY):
        boundary = sensitive_domain_boundary(domain)
        assert boundary.maximum_autonomy_stage is GovernedAutonomyStage.RECOMMEND
        assert PermissionMode.DELEGABLE not in boundary.permitted_permission_modes
        assert PermissionMode.PROPOSE_ONLY in boundary.permitted_permission_modes


def test_m386_6_health_never_diagnoses_prescribes_or_fakes_emergency_contact() -> None:
    boundary = sensitive_domain_boundary(SensitiveDomain.HEALTH)
    forbidden = " ".join(boundary.forbidden_behaviors)
    safeguards = " ".join(boundary.mandatory_safeguards)
    assert "Diagnosticar, prescribir o cambiar medicación" in forbidden
    assert "sin fingir contacto" in safeguards
    assert "ayuda profesional" in safeguards


def test_m386_6_psychology_requires_hypotheses_without_manipulation() -> None:
    boundary = sensitive_domain_boundary(SensitiveDomain.PSYCHOLOGY)
    allowed = " ".join(boundary.allowed_behaviors)
    forbidden = " ".join(boundary.forbidden_behaviors)
    assert "hipótesis corregibles" in allowed
    assert "perfiles psicológicos secretos" in forbidden
    assert "dependencia" in forbidden


def test_m386_6_privacy_stops_at_preparation_and_requires_confirmation() -> None:
    boundary = sensitive_domain_boundary(SensitiveDomain.PRIVACY)
    assert boundary.maximum_autonomy_stage is GovernedAutonomyStage.PREPARE
    assert PermissionMode.DELEGABLE not in boundary.permitted_permission_modes
    assert (
        PermissionMode.CONFIRMATION_REQUIRED
        in boundary.permitted_permission_modes
    )
    assert any("credenciales" in item for item in boundary.forbidden_behaviors)


def test_m386_6_external_actions_stop_before_minor_exception_autonomy() -> None:
    boundary = sensitive_domain_boundary(SensitiveDomain.EXTERNAL_ACTION)
    assert (
        boundary.maximum_autonomy_stage
        is GovernedAutonomyStage.EXECUTE_PREVALIDATED
    )
    assert PermissionMode.DELEGABLE in boundary.permitted_permission_modes
    assert PermissionMode.CONFIRMATION_REQUIRED in (
        boundary.permitted_permission_modes
    )


def test_m386_6_external_actions_reuse_gateways_and_block_finance() -> None:
    boundary = sensitive_domain_boundary(SensitiveDomain.EXTERNAL_ACTION)
    authorities = set(boundary.existing_authorities)
    forbidden = " ".join(boundary.forbidden_behaviors)
    assert {"permission consent", "capability registry", "tool gateway"} <= authorities
    assert "bancos, billeteras, pagos, compras o finanzas" in forbidden


def test_m386_6_more_restrictive_boundary_wins_without_emergency_override() -> None:
    policy = " ".join(SENSITIVE_BOUNDARY_CONFLICT_POLICY)
    assert "aplican todos los límites" in policy
    assert "más restrictiva prevalece" in policy
    assert "no inventar contacto o permiso" in policy
    assert "Carlos o Cristina" in policy


def test_m386_6_invalid_health_expansion_is_rejected_by_construction() -> None:
    health = sensitive_domain_boundary(SensitiveDomain.HEALTH)
    with pytest.raises(ValueError, match="cannot exceed recommendation"):
        replace(
            health,
            maximum_autonomy_stage=GovernedAutonomyStage.PREPARE,
        )


def test_m386_6_boundaries_are_immutable_and_unknown_domain_is_rejected() -> None:
    boundary = sensitive_domain_boundary(SensitiveDomain.PRIVACY)
    with pytest.raises(FrozenInstanceError):
        boundary.title = "altered"
    with pytest.raises(ValueError):
        sensitive_domain_boundary("invented_sensitive_domain")

