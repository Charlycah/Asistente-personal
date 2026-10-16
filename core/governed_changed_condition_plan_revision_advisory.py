from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Mapping

from domain.governed_objective_memory import (
    GovernedObjective,
    GovernedObjectiveState,
)
from domain.governed_plan import GovernedPlan


class ChangedConditionImpact(StrEnum):
    ASSUMPTION_INVALIDATED = "assumption_invalidated"
    DEPENDENCY_CHANGED = "dependency_changed"
    CURRENT_STATE_CHANGED = "current_state_changed"
    MISSING_INFORMATION_RESOLVED = "missing_information_resolved"


class PlanRevisionAdvisoryStatus(StrEnum):
    NO_REVISION_NEEDED = "no_revision_needed"
    REVIEW_REQUIRED = "review_required"


@dataclass(frozen=True)
class ChangedConditionEvidence:
    condition_id: str
    owner: str
    scope: str
    subject: str
    predicate: str
    previous_value: str
    observed_value: str
    provenance: str
    confidence: float
    impact: ChangedConditionImpact
    target_text: str
    impacted_step_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for name in (
            "condition_id",
            "owner",
            "scope",
            "subject",
            "predicate",
            "previous_value",
            "observed_value",
            "provenance",
            "target_text",
        ):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between zero and one")
        if not isinstance(self.impact, ChangedConditionImpact):
            raise ValueError("impact must be a ChangedConditionImpact")
        normalized = tuple(dict.fromkeys(self.impacted_step_ids))
        if any(not item.strip() for item in normalized):
            raise ValueError("impacted step ids must not be blank")
        object.__setattr__(self, "impacted_step_ids", normalized)


@dataclass(frozen=True)
class PlanRevisionAdvisory:
    status: PlanRevisionAdvisoryStatus
    source_plan_id: str
    source_plan_revision: int
    condition_id: str
    impact: ChangedConditionImpact
    reason: str
    proposed_changes: Mapping[str, object]
    impacted_step_ids: tuple[str, ...]
    provenance: str
    application_authorized: bool = False
    automatic_replanning: bool = False
    autonomous_revision_enabled: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "proposed_changes", MappingProxyType(dict(self.proposed_changes))
        )
        if self.application_authorized:
            raise ValueError("plan revision advisory cannot authorize application")
        if self.automatic_replanning or self.autonomous_revision_enabled:
            raise ValueError("plan revision advisory must remain non-autonomous")


class GovernedChangedConditionPlanRevisionAdvisory:
    """Advises bounded review of an existing plan; never applies a revision."""

    CANONICAL_AUTHORITY = "governed_plan_continuity"
    MIN_CONFIDENCE = 0.60

    def assess(
        self,
        *,
        objective: GovernedObjective,
        plan: GovernedPlan,
        evidence: ChangedConditionEvidence,
        scope: str,
    ) -> PlanRevisionAdvisory:
        self._validate_context(objective, plan, evidence, scope)
        if evidence.previous_value == evidence.observed_value:
            return self._no_revision(plan, evidence, "condition value is unchanged")
        changes = self._project_changes(plan, evidence)
        if not changes:
            return self._no_revision(
                plan, evidence, "changed condition is not relevant to this plan"
            )
        return PlanRevisionAdvisory(
            status=PlanRevisionAdvisoryStatus.REVIEW_REQUIRED,
            source_plan_id=plan.plan_id,
            source_plan_revision=plan.revision,
            condition_id=evidence.condition_id,
            impact=evidence.impact,
            reason=(
                "Changed condition conflicts with explicit governed plan context; "
                "human review is required before any revision."
            ),
            proposed_changes=changes,
            impacted_step_ids=evidence.impacted_step_ids,
            provenance=evidence.provenance,
        )

    def _validate_context(
        self,
        objective: GovernedObjective,
        plan: GovernedPlan,
        evidence: ChangedConditionEvidence,
        scope: str,
    ) -> None:
        if objective.state is GovernedObjectiveState.COMPLETED:
            raise ValueError("completed objectives cannot receive replanning advisory")
        if plan.plan_id not in objective.plan_ids:
            raise ValueError("objective does not link the assessed plan")
        if evidence.owner != objective.owner:
            raise ValueError("changed-condition owner does not match objective owner")
        if evidence.scope != scope:
            raise ValueError("changed-condition scope is incompatible")
        if evidence.confidence < self.MIN_CONFIDENCE:
            raise ValueError("changed-condition confidence is insufficient")
        known_steps = {step.step_id for step in plan.steps}
        if set(evidence.impacted_step_ids) - known_steps:
            raise ValueError("changed condition references unknown plan steps")

    def _project_changes(
        self,
        plan: GovernedPlan,
        evidence: ChangedConditionEvidence,
    ) -> dict[str, object]:
        target = evidence.target_text.casefold()
        if evidence.impact is ChangedConditionImpact.ASSUMPTION_INVALIDATED:
            matches = [item for item in plan.assumptions if item.casefold() == target]
            if not matches:
                return {}
            return {
                "assumptions": tuple(
                    item for item in plan.assumptions if item not in matches
                ),
                "missing_information": tuple(
                    dict.fromkeys((*plan.missing_information, f"Revisar: {matches[0]}"))
                ),
            }
        if evidence.impact is ChangedConditionImpact.DEPENDENCY_CHANGED:
            if not any(item.casefold() == target for item in plan.dependencies):
                return {}
            return {
                "current_state": (
                    f"{plan.current_state} Cambio observado: "
                    f"{evidence.subject} {evidence.predicate}="
                    f"{evidence.observed_value}."
                )
            }
        if evidence.impact is ChangedConditionImpact.CURRENT_STATE_CHANGED:
            if target not in plan.current_state.casefold():
                return {}
            return {
                "current_state": (
                    f"{evidence.subject} {evidence.predicate}="
                    f"{evidence.observed_value}."
                )
            }
        if evidence.impact is ChangedConditionImpact.MISSING_INFORMATION_RESOLVED:
            matches = [
                item for item in plan.missing_information if item.casefold() == target
            ]
            if not matches:
                return {}
            return {
                "missing_information": tuple(
                    item for item in plan.missing_information if item not in matches
                )
            }
        return {}

    @staticmethod
    def _no_revision(
        plan: GovernedPlan,
        evidence: ChangedConditionEvidence,
        reason: str,
    ) -> PlanRevisionAdvisory:
        return PlanRevisionAdvisory(
            status=PlanRevisionAdvisoryStatus.NO_REVISION_NEEDED,
            source_plan_id=plan.plan_id,
            source_plan_revision=plan.revision,
            condition_id=evidence.condition_id,
            impact=evidence.impact,
            reason=reason,
            proposed_changes={},
            impacted_step_ids=(),
            provenance=evidence.provenance,
        )
