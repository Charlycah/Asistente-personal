from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from typing import Mapping, Sequence

from .exceptions import DomainError
from .governed_objective_memory import GovernedObjective, GovernedObjectiveState
from .governed_plan import GovernedPlan


@dataclass(frozen=True)
class GovernedPlanReview:
    """Immutable evidence explaining one governed plan revision."""

    objective_id: str
    plan_id: str
    revision: int
    previous_revision: int
    reason: str
    changed_fields: tuple[str, ...]
    impacted_step_ids: tuple[str, ...]
    observed_at: datetime

    def __post_init__(self) -> None:
        for field_name in ("objective_id", "plan_id", "reason"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise DomainError(f"{field_name} must be a non-empty string")
        if self.revision != self.previous_revision + 1:
            raise DomainError(
                "review revision must immediately follow previous_revision"
            )
        if self.observed_at.tzinfo is None:
            raise DomainError("observed_at must be timezone-aware")
        object.__setattr__(
            self,
            "changed_fields",
            _normalized_strings("changed_fields", self.changed_fields),
        )
        object.__setattr__(
            self,
            "impacted_step_ids",
            _normalized_strings("impacted_step_ids", self.impacted_step_ids),
        )


@dataclass(frozen=True)
class GovernedPlanContinuitySnapshot:
    schema_version: str
    authority: str
    persistence_enabled: bool
    execution_enabled: bool
    autonomous_revision_enabled: bool
    conversation_authority: bool
    tracked_plans: int
    recorded_reviews: int


class GovernedPlanContinuity:
    """Gateway-owned revision history for existing objectives and plans."""

    SCHEMA_VERSION = "m346.8"
    AUTHORITY = "domain.governed_plan_continuity:GovernedPlanContinuity"

    def __init__(self) -> None:
        self._histories: dict[tuple[str, str], list[GovernedPlan]] = {}
        self._reviews: dict[tuple[str, str], list[GovernedPlanReview]] = {}

    @property
    def snapshot(self) -> GovernedPlanContinuitySnapshot:
        return GovernedPlanContinuitySnapshot(
            schema_version=self.SCHEMA_VERSION,
            authority=self.AUTHORITY,
            persistence_enabled=False,
            execution_enabled=False,
            autonomous_revision_enabled=False,
            conversation_authority=False,
            tracked_plans=len(self._histories),
            recorded_reviews=sum(len(items) for items in self._reviews.values()),
        )

    def track(
        self,
        objective: GovernedObjective,
        plan: GovernedPlan,
    ) -> GovernedPlan:
        _validate_relationship(objective, plan)
        key = (objective.objective_id, plan.plan_id)
        if key in self._histories:
            raise DomainError("plan is already tracked for objective")
        if plan.revision != 1 or plan.supersedes_revision is not None:
            raise DomainError("a newly tracked plan must begin at revision 1")
        self._histories[key] = [plan]
        self._reviews[key] = []
        return plan

    def current(self, objective_id: str, plan_id: str) -> GovernedPlan | None:
        history = self._histories.get((objective_id, plan_id), ())
        return history[-1] if history else None

    def history(self, objective_id: str, plan_id: str) -> tuple[GovernedPlan, ...]:
        return tuple(self._histories.get((objective_id, plan_id), ()))

    def reviews(
        self, objective_id: str, plan_id: str
    ) -> tuple[GovernedPlanReview, ...]:
        return tuple(self._reviews.get((objective_id, plan_id), ()))

    def review(
        self,
        objective: GovernedObjective,
        plan_id: str,
        *,
        reason: str,
        changes: Mapping[str, object],
        impacted_step_ids: Sequence[str] = (),
        observed_at: datetime | None = None,
    ) -> GovernedPlan:
        if objective.state is GovernedObjectiveState.COMPLETED:
            raise DomainError("completed objectives cannot be reviewed")
        key = (objective.objective_id, plan_id)
        current = self.current(*key)
        if current is None:
            raise DomainError("unknown tracked plan for objective")
        if not isinstance(reason, str) or not reason.strip():
            raise DomainError("reason must be a non-empty string")
        if not changes:
            return current
        allowed = {
            "objective",
            "current_state",
            "steps",
            "expected_outcome",
            "confidence",
            "assumptions",
            "missing_information",
            "dependencies",
            "risks",
            "required_authorizations",
            "state",
            "metadata",
        }
        unknown = set(changes) - allowed
        if unknown:
            raise DomainError("changes contain unsupported plan fields")
        effective_changes = {
            field_name: value
            for field_name, value in changes.items()
            if getattr(current, field_name) != value
        }
        if not effective_changes:
            return current
        changed_fields = tuple(effective_changes)
        candidate = replace(
            current,
            **effective_changes,
            revision=current.revision + 1,
            supersedes_revision=current.revision,
        )
        known_steps = {step.step_id for step in candidate.steps}
        impacted = _normalized_strings("impacted_step_ids", impacted_step_ids)
        if set(impacted) - known_steps:
            raise DomainError("impacted_step_ids must reference current plan steps")
        timestamp = _observed_at(observed_at)
        review = GovernedPlanReview(
            objective_id=objective.objective_id,
            plan_id=plan_id,
            revision=candidate.revision,
            previous_revision=current.revision,
            reason=reason,
            changed_fields=changed_fields,
            impacted_step_ids=impacted,
            observed_at=timestamp,
        )
        self._histories[key].append(candidate)
        self._reviews[key].append(review)
        return candidate


def _validate_relationship(
    objective: GovernedObjective,
    plan: GovernedPlan,
) -> None:
    if plan.plan_id not in objective.plan_ids:
        raise DomainError("objective must link the plan before continuity tracking")


def _observed_at(value: datetime | None) -> datetime:
    timestamp = value or datetime.now(timezone.utc)
    if timestamp.tzinfo is None:
        raise DomainError("observed_at must be timezone-aware")
    return timestamp


def _normalized_strings(field_name: str, values: Sequence[str]) -> tuple[str, ...]:
    normalized = tuple(values)
    if not all(isinstance(value, str) and value.strip() for value in normalized):
        raise DomainError(f"{field_name} must contain only non-empty strings")
    if len(normalized) != len(set(normalized)):
        raise DomainError(f"{field_name} cannot contain duplicates")
    return normalized
