from __future__ import annotations

from datetime import datetime, timezone

import pytest

from core.governed_changed_condition_plan_revision_advisory import (
    ChangedConditionEvidence,
    ChangedConditionImpact,
    GovernedChangedConditionPlanRevisionAdvisory,
    PlanRevisionAdvisoryStatus,
)
from domain.governed_objective_memory import GovernedObjective
from domain.governed_plan import GovernedPlan, GovernedPlanStep

NOW = datetime(2026, 8, 21, 12, 0, tzinfo=timezone.utc)


def _objective(*, owner: str = "Carlos y Cristina", completed: bool = False):
    from domain.governed_objective_memory import GovernedObjectiveState

    return GovernedObjective(
        objective_id="travel",
        owner=owner,
        description="Preparar el viaje.",
        state=(
            GovernedObjectiveState.COMPLETED
            if completed
            else GovernedObjectiveState.ACTIVE
        ),
        created_at=NOW,
        updated_at=NOW,
        plan_ids=("travel-plan",),
    )


def _plan():
    return GovernedPlan(
        plan_id="travel-plan",
        objective="Preparar el viaje.",
        current_state="Tenemos vehículo disponible.",
        steps=(
            GovernedPlanStep("route", 1, "Confirmar transporte."),
            GovernedPlanStep("packing", 2, "Preparar equipaje."),
        ),
        expected_outcome="Viaje preparado.",
        confidence=80,
        assumptions=("El vehículo estará disponible.",),
        missing_information=("Fecha definitiva.",),
        dependencies=("Vehículo disponible.",),
    )


def _evidence(**changes):
    values = {
        "condition_id": "vehicle-availability",
        "owner": "Carlos y Cristina",
        "scope": "travel",
        "subject": "vehículo",
        "predicate": "availability",
        "previous_value": "available",
        "observed_value": "unavailable",
        "provenance": "observation:vehicle-status",
        "confidence": 0.95,
        "impact": ChangedConditionImpact.ASSUMPTION_INVALIDATED,
        "target_text": "El vehículo estará disponible.",
        "impacted_step_ids": ("route",),
    }
    values.update(changes)
    return ChangedConditionEvidence(**values)


def test_changed_condition_produces_review_only_advisory():
    advisory = GovernedChangedConditionPlanRevisionAdvisory().assess(
        objective=_objective(), plan=_plan(), evidence=_evidence(), scope="travel"
    )
    assert advisory.status is PlanRevisionAdvisoryStatus.REVIEW_REQUIRED
    assert advisory.source_plan_revision == 1
    assert advisory.impacted_step_ids == ("route",)
    assert advisory.proposed_changes["assumptions"] == ()
    assert advisory.application_authorized is False
    assert advisory.automatic_replanning is False
    assert advisory.autonomous_revision_enabled is False


def test_unchanged_condition_does_not_request_revision():
    evidence = _evidence(observed_value="available")
    advisory = GovernedChangedConditionPlanRevisionAdvisory().assess(
        objective=_objective(), plan=_plan(), evidence=evidence, scope="travel"
    )
    assert advisory.status is PlanRevisionAdvisoryStatus.NO_REVISION_NEEDED
    assert not advisory.proposed_changes


def test_irrelevant_changed_condition_does_not_request_revision():
    evidence = _evidence(target_text="Otra assumption.")
    advisory = GovernedChangedConditionPlanRevisionAdvisory().assess(
        objective=_objective(), plan=_plan(), evidence=evidence, scope="travel"
    )
    assert advisory.status is PlanRevisionAdvisoryStatus.NO_REVISION_NEEDED


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"owner": "otro"}, "owner"),
        ({"scope": "home"}, "scope"),
        ({"confidence": 0.20}, "confidence"),
        ({"impacted_step_ids": ("missing",)}, "unknown plan steps"),
    ],
)
def test_incompatible_evidence_fails_closed(changes, message):
    with pytest.raises(ValueError, match=message):
        GovernedChangedConditionPlanRevisionAdvisory().assess(
            objective=_objective(),
            plan=_plan(),
            evidence=_evidence(**changes),
            scope="travel",
        )


def test_completed_objective_cannot_receive_replanning_advisory():
    with pytest.raises(ValueError, match="completed"):
        GovernedChangedConditionPlanRevisionAdvisory().assess(
            objective=_objective(completed=True),
            plan=_plan(),
            evidence=_evidence(),
            scope="travel",
        )


def test_advisory_never_mutates_plan():
    plan = _plan()
    before = plan
    GovernedChangedConditionPlanRevisionAdvisory().assess(
        objective=_objective(), plan=plan, evidence=_evidence(), scope="travel"
    )
    assert plan is before
    assert plan.revision == 1
    assert plan.supersedes_revision is None
