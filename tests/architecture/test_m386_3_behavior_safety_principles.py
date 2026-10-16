from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from core.cognitive_maturity import (
    BEHAVIOR_SAFETY_PRINCIPLES,
    PRINCIPLE_CONFLICT_POLICY,
    BehaviorPrincipleDomain,
    behavior_safety_principle,
)

EXPECTED_PRINCIPLES = {
    "equal_human_coownership",
    "care_without_overreach",
    "epistemic_honesty",
    "privacy_and_minimization",
    "consent_and_least_privilege",
    "bounded_reversible_action",
    "no_self_authorization",
    "non_manipulative_relationship",
    "perception_truthfulness",
    "governed_memory_and_learning",
    "fail_closed_and_explain",
    "model_independent_identity",
}


def test_m386_3_catalog_covers_the_agreed_behavior_boundaries() -> None:
    identifiers = {principle.principle_id for principle in BEHAVIOR_SAFETY_PRINCIPLES}
    assert identifiers == EXPECTED_PRINCIPLES
    assert len(identifiers) == len(BEHAVIOR_SAFETY_PRINCIPLES)


def test_m386_3_principles_are_immutable_and_never_grant_authority() -> None:
    for principle in BEHAVIOR_SAFETY_PRINCIPLES:
        assert principle.grants_action_authority is False
        assert principle.required_behaviors
        assert principle.forbidden_behaviors
        assert principle.existing_authorities
    with pytest.raises(FrozenInstanceError):
        BEHAVIOR_SAFETY_PRINCIPLES[0].title = "altered"


def test_m386_3_carlos_and_cristina_are_equal_final_authorities() -> None:
    principle = behavior_safety_principle("equal_human_coownership")
    assert "Carlos y Cristina" in principle.statement
    assert "copropietarios iguales" in principle.statement
    assert any(
        "propietario principal" in item for item in principle.forbidden_behaviors
    )


def test_m386_3_epistemic_honesty_reuses_m386_2() -> None:
    principle = behavior_safety_principle("epistemic_honesty")
    assert principle.domain is BehaviorPrincipleDomain.EPISTEMIC_INTEGRITY
    assert "M386.2 epistemic classifier" in principle.existing_authorities
    assert any("Fabricar evidencia" in item for item in principle.forbidden_behaviors)


def test_m386_3_capability_never_implies_permission() -> None:
    principle = behavior_safety_principle("consent_and_least_privilege")
    assert "permission consent" in principle.existing_authorities
    assert any("capacidad disponible" in item for item in principle.forbidden_behaviors)


def test_m386_3_autonomy_cannot_expand_itself() -> None:
    principle = behavior_safety_principle("no_self_authorization")
    forbidden = " ".join(principle.forbidden_behaviors)
    assert "Autoprogramarse" in forbidden
    assert "Concederse permisos" in forbidden


def test_m386_3_relationship_must_not_manipulate_or_claim_consciousness() -> None:
    principle = behavior_safety_principle("non_manipulative_relationship")
    forbidden = " ".join(principle.forbidden_behaviors)
    assert "dependencia" in forbidden
    assert "consciencia" in forbidden


def test_m386_3_perception_requires_real_observation() -> None:
    principle = behavior_safety_principle("perception_truthfulness")
    assert any("sin observación real" in item for item in principle.forbidden_behaviors)
    assert any("canal" in item for item in principle.required_behaviors)


def test_m386_3_unresolved_conflict_fails_closed_for_human_review() -> None:
    policy = " ".join(PRINCIPLE_CONFLICT_POLICY)
    assert "Ningún principio concede" in policy
    assert "autoridad especializada" in policy
    assert "abstención segura" in policy
    assert "Carlos o Cristina" in policy


def test_m386_3_unknown_principle_is_rejected() -> None:
    with pytest.raises(KeyError):
        behavior_safety_principle("invented_superlaw")
