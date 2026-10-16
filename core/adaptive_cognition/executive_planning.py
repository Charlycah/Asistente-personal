from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.adaptive_cognition.knowledge_evolution import KnowledgeEvolutionProposal
from core.adaptive_cognition.mental_models import MentalModel
from core.adaptive_cognition.reflection_engine import ReflectionRecord


class ExecutivePlanHorizon(str, Enum):
    NEAR = "near"
    MID = "mid"
    LONG = "long"


class ExecutivePlanStatus(str, Enum):
    DRAFT = "draft"
    REVIEW_REQUIRED = "review_required"
    APPROVED = "approved"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ExecutivePriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class ExecutiveObjective:
    title: str
    success_criteria: tuple[str, ...]
    priority: ExecutivePriority | str = ExecutivePriority.MEDIUM
    objective_id: str = ""

    def __post_init__(self) -> None:
        priority = ExecutivePriority(self.priority)
        if not self.title.strip() or not self.success_criteria:
            raise ValueError("executive objective requires title and criteria")
        if any(not item.strip() for item in self.success_criteria):
            raise ValueError("executive success criteria must not be blank")
        if len(set(self.success_criteria)) != len(self.success_criteria):
            raise ValueError("executive success criteria must be unique")
        expected = sha256(
            "|".join((self.title, priority.value, *self.success_criteria)).encode()
        ).hexdigest()
        if self.objective_id and self.objective_id != expected:
            raise ValueError("executive objective id is inconsistent")
        object.__setattr__(self, "objective_id", expected)

    @property
    def normalized_priority(self) -> ExecutivePriority:
        return ExecutivePriority(self.priority)


@dataclass(frozen=True)
class ExecutiveMilestone:
    title: str
    objective_ids: tuple[str, ...]
    sequence: int
    dependencies: tuple[str, ...] = ()
    milestone_id: str = ""

    def __post_init__(self) -> None:
        if not self.title.strip() or not self.objective_ids:
            raise ValueError("executive milestone requires title and objectives")
        if self.sequence <= 0:
            raise ValueError("executive milestone sequence must be positive")
        collections = (self.objective_ids, self.dependencies)
        if any(len(set(items)) != len(items) for items in collections):
            raise ValueError("executive milestone references must be unique")
        if any(not item.strip() for items in collections for item in items):
            raise ValueError("executive milestone references must not be blank")
        expected = sha256(
            "|".join(
                (
                    self.title,
                    str(self.sequence),
                    ";".join(self.objective_ids),
                    ";".join(self.dependencies),
                )
            ).encode()
        ).hexdigest()
        if self.milestone_id and self.milestone_id != expected:
            raise ValueError("executive milestone id is inconsistent")
        object.__setattr__(self, "milestone_id", expected)


@dataclass(frozen=True)
class ExecutivePlan:
    owner: str
    title: str
    purpose: str
    horizon: ExecutivePlanHorizon | str
    objectives: tuple[ExecutiveObjective, ...]
    milestones: tuple[ExecutiveMilestone, ...]
    status: ExecutivePlanStatus | str = ExecutivePlanStatus.DRAFT
    revision: int = 1
    domains: tuple[str, ...] = ()
    reflection_ids: tuple[str, ...] = ()
    mental_model_ids: tuple[str, ...] = ()
    knowledge_proposal_ids: tuple[str, ...] = ()
    constraints: tuple[str, ...] = ()
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    plan_id: str = ""

    def __post_init__(self) -> None:
        horizon = ExecutivePlanHorizon(self.horizon)
        status = ExecutivePlanStatus(self.status)
        if not self.owner.strip() or not self.title.strip() or not self.purpose.strip():
            raise ValueError("executive plan requires owner, title and purpose")
        if not self.objectives or not self.milestones:
            raise ValueError("executive plan requires objectives and milestones")
        if self.revision <= 0:
            raise ValueError("executive plan revision must be positive")
        if self.created_at.tzinfo is None:
            raise ValueError("executive plan timestamp must be timezone-aware")
        objective_ids = tuple(item.objective_id for item in self.objectives)
        if len(set(objective_ids)) != len(objective_ids):
            raise ValueError("executive plan objectives must be unique")
        milestone_ids = tuple(item.milestone_id for item in self.milestones)
        if len(set(milestone_ids)) != len(milestone_ids):
            raise ValueError("executive plan milestones must be unique")
        sequences = tuple(item.sequence for item in self.milestones)
        if sequences != tuple(range(1, len(self.milestones) + 1)):
            raise ValueError("executive milestone sequence must be contiguous")
        known_objectives = set(objective_ids)
        known_milestones = set(milestone_ids)
        for milestone in self.milestones:
            if not set(milestone.objective_ids) <= known_objectives:
                raise ValueError("executive milestone references unknown objective")
            if not set(milestone.dependencies) <= known_milestones:
                raise ValueError("executive milestone dependency is unknown")
            if milestone.milestone_id in milestone.dependencies:
                raise ValueError("executive milestone cannot depend on itself")
        references = (
            self.domains,
            self.reflection_ids,
            self.mental_model_ids,
            self.knowledge_proposal_ids,
            self.constraints,
        )
        if any(len(set(items)) != len(items) for items in references):
            raise ValueError("executive plan references must be unique")
        if any(not item.strip() for items in references for item in items):
            raise ValueError("executive plan references must not be blank")
        expected = sha256(
            "|".join(
                (
                    self.owner,
                    self.title,
                    self.purpose,
                    horizon.value,
                    status.value,
                    str(self.revision),
                    ";".join(objective_ids),
                    ";".join(milestone_ids),
                    ";".join(self.domains),
                    ";".join(self.reflection_ids),
                    ";".join(self.mental_model_ids),
                    ";".join(self.knowledge_proposal_ids),
                    ";".join(self.constraints),
                    self.created_at.isoformat(),
                )
            ).encode()
        ).hexdigest()
        if self.plan_id and self.plan_id != expected:
            raise ValueError("executive plan id is inconsistent")
        object.__setattr__(self, "plan_id", expected)

    @property
    def normalized_status(self) -> ExecutivePlanStatus:
        return ExecutivePlanStatus(self.status)

    @property
    def normalized_horizon(self) -> ExecutivePlanHorizon:
        return ExecutivePlanHorizon(self.horizon)

    @property
    def requires_review(self) -> bool:
        critical = any(
            item.normalized_priority is ExecutivePriority.CRITICAL
            for item in self.objectives
        )
        return critical or self.normalized_horizon is ExecutivePlanHorizon.LONG

    def to_dict(self) -> dict[str, object]:
        return {
            "plan_id": self.plan_id,
            "owner": self.owner,
            "title": self.title,
            "purpose": self.purpose,
            "horizon": self.normalized_horizon.value,
            "status": self.normalized_status.value,
            "revision": self.revision,
            "domains": list(self.domains),
            "reflection_ids": list(self.reflection_ids),
            "mental_model_ids": list(self.mental_model_ids),
            "knowledge_proposal_ids": list(self.knowledge_proposal_ids),
            "constraints": list(self.constraints),
            "requires_review": self.requires_review,
            "created_at": self.created_at.isoformat(),
        }


@dataclass(frozen=True)
class ExecutivePlanningPolicy:
    max_objectives: int = 12
    max_milestones: int = 24
    long_horizon_requires_review: bool = True
    allow_direct_execution: bool = False

    def __post_init__(self) -> None:
        if self.max_objectives <= 0 or self.max_milestones <= 0:
            raise ValueError("executive planning limits must be positive")
        if self.allow_direct_execution:
            raise ValueError("M90 must not allow direct execution")


@runtime_checkable
class ExecutivePlanRepository(Protocol):
    def add(self, plan: ExecutivePlan) -> None: ...
    def get(self, plan_id: str) -> ExecutivePlan | None: ...
    def history(self, owner: str, title: str) -> tuple[ExecutivePlan, ...]: ...
    def list_all(self) -> tuple[ExecutivePlan, ...]: ...


class InMemoryExecutivePlanRepository:
    def __init__(self) -> None:
        self._plans: dict[str, ExecutivePlan] = {}

    def add(self, plan: ExecutivePlan) -> None:
        if plan.plan_id in self._plans:
            raise ValueError("executive plan already exists")
        history = self.history(plan.owner, plan.title)
        if history and plan.revision != history[-1].revision + 1:
            raise ValueError("executive plan revision must be contiguous")
        if not history and plan.revision != 1:
            raise ValueError("first executive plan revision must be one")
        self._plans[plan.plan_id] = plan

    def get(self, plan_id: str) -> ExecutivePlan | None:
        return self._plans.get(plan_id)

    def history(self, owner: str, title: str) -> tuple[ExecutivePlan, ...]:
        items = (
            plan
            for plan in self._plans.values()
            if plan.owner == owner and plan.title == title
        )
        return tuple(sorted(items, key=lambda item: item.revision))

    def list_all(self) -> tuple[ExecutivePlan, ...]:
        return tuple(sorted(self._plans.values(), key=lambda item: item.created_at))


class ExecutivePlanningEngine:
    def __init__(self, policy: ExecutivePlanningPolicy | None = None) -> None:
        self.policy = policy or ExecutivePlanningPolicy()

    def create_plan(
        self,
        *,
        owner: str,
        title: str,
        purpose: str,
        horizon: ExecutivePlanHorizon | str,
        objectives: tuple[ExecutiveObjective, ...],
        milestones: tuple[ExecutiveMilestone, ...],
        domains: tuple[str, ...] = (),
        reflections: tuple[ReflectionRecord, ...] = (),
        mental_models: tuple[MentalModel, ...] = (),
        knowledge_proposals: tuple[KnowledgeEvolutionProposal, ...] = (),
        constraints: tuple[str, ...] = (),
        now: datetime | None = None,
    ) -> ExecutivePlan:
        if len(objectives) > self.policy.max_objectives:
            raise ValueError("executive plan has too many objectives")
        if len(milestones) > self.policy.max_milestones:
            raise ValueError("executive plan has too many milestones")
        timestamp = now or datetime.now(timezone.utc)
        status = ExecutivePlanStatus.DRAFT
        normalized_horizon = ExecutivePlanHorizon(horizon)
        if (
            self.policy.long_horizon_requires_review
            and normalized_horizon is ExecutivePlanHorizon.LONG
        ) or any(
            item.normalized_priority is ExecutivePriority.CRITICAL
            for item in objectives
        ):
            status = ExecutivePlanStatus.REVIEW_REQUIRED
        return ExecutivePlan(
            owner=owner,
            title=title,
            purpose=purpose,
            horizon=normalized_horizon,
            objectives=objectives,
            milestones=milestones,
            status=status,
            domains=domains,
            reflection_ids=tuple(item.reflection_id for item in reflections),
            mental_model_ids=tuple(item.model_id for item in mental_models),
            knowledge_proposal_ids=tuple(
                item.proposal_id for item in knowledge_proposals
            ),
            constraints=constraints,
            created_at=timestamp,
        )

    def revise(
        self,
        plan: ExecutivePlan,
        *,
        purpose: str | None = None,
        objectives: tuple[ExecutiveObjective, ...] | None = None,
        milestones: tuple[ExecutiveMilestone, ...] | None = None,
        constraints: tuple[str, ...] | None = None,
        now: datetime | None = None,
    ) -> ExecutivePlan:
        return replace(
            plan,
            purpose=purpose if purpose is not None else plan.purpose,
            objectives=objectives if objectives is not None else plan.objectives,
            milestones=milestones if milestones is not None else plan.milestones,
            constraints=constraints if constraints is not None else plan.constraints,
            status=ExecutivePlanStatus.REVIEW_REQUIRED,
            revision=plan.revision + 1,
            created_at=now or datetime.now(timezone.utc),
            plan_id="",
        )

    def transition(
        self,
        plan: ExecutivePlan,
        status: ExecutivePlanStatus | str,
        *,
        now: datetime | None = None,
    ) -> ExecutivePlan:
        target = ExecutivePlanStatus(status)
        allowed = {
            ExecutivePlanStatus.DRAFT: {
                ExecutivePlanStatus.REVIEW_REQUIRED,
                ExecutivePlanStatus.APPROVED,
                ExecutivePlanStatus.CANCELLED,
            },
            ExecutivePlanStatus.REVIEW_REQUIRED: {
                ExecutivePlanStatus.APPROVED,
                ExecutivePlanStatus.CANCELLED,
            },
            ExecutivePlanStatus.APPROVED: {
                ExecutivePlanStatus.ACTIVE,
                ExecutivePlanStatus.CANCELLED,
            },
            ExecutivePlanStatus.ACTIVE: {
                ExecutivePlanStatus.PAUSED,
                ExecutivePlanStatus.COMPLETED,
                ExecutivePlanStatus.CANCELLED,
            },
            ExecutivePlanStatus.PAUSED: {
                ExecutivePlanStatus.ACTIVE,
                ExecutivePlanStatus.CANCELLED,
            },
        }
        if target not in allowed.get(plan.normalized_status, set()):
            raise ValueError("executive plan transition is not allowed")
        return replace(
            plan,
            status=target,
            revision=plan.revision + 1,
            created_at=now or datetime.now(timezone.utc),
            plan_id="",
        )


class ExecutivePlanningManager:
    def __init__(
        self,
        repository: ExecutivePlanRepository | None = None,
        engine: ExecutivePlanningEngine | None = None,
    ) -> None:
        self.repository = repository or InMemoryExecutivePlanRepository()
        self.engine = engine or ExecutivePlanningEngine()

    def create(self, **kwargs: object) -> ExecutivePlan:
        plan = self.engine.create_plan(**kwargs)  # type: ignore[arg-type]
        self.repository.add(plan)
        return plan

    def revise(self, plan: ExecutivePlan, **kwargs: object) -> ExecutivePlan:
        revised = self.engine.revise(plan, **kwargs)  # type: ignore[arg-type]
        self.repository.add(revised)
        return revised

    def transition(
        self,
        plan: ExecutivePlan,
        status: ExecutivePlanStatus | str,
        *,
        now: datetime | None = None,
    ) -> ExecutivePlan:
        updated = self.engine.transition(plan, status, now=now)
        self.repository.add(updated)
        return updated

    def system_prompt_lines(self) -> tuple[str, ...]:
        return (
            "Executive Planning M90:",
            "- Los planes ejecutivos son estrategias, no acciones.",
            "- No calendarices, ejecutes ni autorices herramientas desde M90.",
            "- Conserva objetivos, hitos, dependencias y restricciones.",
            "- Todo plan de largo plazo o crítico requiere revisión explícita.",
            "- La activación de un plan no implica ejecutar sus hitos.",
        )
