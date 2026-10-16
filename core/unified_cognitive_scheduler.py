# ruff: noqa: E501
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256

from core.cognitive_runtime_orchestration import (
    CognitiveRuntimeContribution,
    CognitiveRuntimeStageStatus,
)
from core.cross_domain_coordination import (
    CrossDomainCoordinationDirective,
    CrossDomainCoordinationStatus,
    CrossDomainCoordinator,
)
from core.llm_provider import LLMRequest
from core.unified_cognitive_blackboard import (
    CognitiveBlackboardDomain,
    CognitiveBlackboardEntry,
    CognitiveBlackboardEntryKind,
    UnifiedCognitiveBlackboard,
)


class UnifiedCognitiveScheduleStatus(str, Enum):
    IDLE = "idle"
    SCHEDULED = "scheduled"
    ATTENTION_REQUIRED = "attention_required"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class CognitiveScheduleItem:
    sequence: int
    domain: CognitiveBlackboardDomain | str
    action: str
    priority: int
    depends_on: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        domain = CognitiveBlackboardDomain(self.domain)
        action = self.action.strip()
        dependencies = tuple(item.strip() for item in self.depends_on if item.strip())
        if self.sequence < 1:
            raise ValueError("cognitive schedule sequence must be positive")
        if not action:
            raise ValueError("cognitive schedule action must be present")
        if not 0 <= self.priority <= 100:
            raise ValueError(
                "cognitive schedule priority must be between zero and one hundred"
            )
        if len(set(dependencies)) != len(dependencies):
            raise ValueError("cognitive schedule dependencies must be unique")
        object.__setattr__(self, "domain", domain)
        object.__setattr__(self, "action", action)
        object.__setattr__(self, "depends_on", dependencies)


@dataclass(frozen=True)
class UnifiedCognitiveSchedule:
    owner: str
    session_id: str
    status: UnifiedCognitiveScheduleStatus | str
    items: tuple[CognitiveScheduleItem, ...]
    constraints: tuple[str, ...] = ()
    source_reference_ids: tuple[str, ...] = ()
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    schedule_id: str = ""

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        session_id = self.session_id.strip()
        status = UnifiedCognitiveScheduleStatus(self.status)
        constraints = tuple(item.strip() for item in self.constraints if item.strip())
        references = tuple(
            item.strip() for item in self.source_reference_ids if item.strip()
        )
        if not owner or not session_id:
            raise ValueError("cognitive schedule identity must be complete")
        if self.created_at.tzinfo is None:
            raise ValueError("cognitive schedule time must be timezone-aware")
        if len(set(item.sequence for item in self.items)) != len(self.items):
            raise ValueError("cognitive schedule sequences must be unique")
        if tuple(sorted(item.sequence for item in self.items)) != tuple(
            range(1, len(self.items) + 1)
        ):
            raise ValueError("cognitive schedule sequences must be contiguous")
        if len(set(constraints)) != len(constraints):
            raise ValueError("cognitive schedule constraints must be unique")
        if len(set(references)) != len(references):
            raise ValueError("cognitive schedule references must be unique")
        expected = sha256(
            "|".join(
                (
                    owner.casefold(),
                    session_id,
                    status.value,
                    *(
                        f"{item.sequence}:{item.domain.value}:{item.action}:{item.priority}:{','.join(item.depends_on)}"
                        for item in self.items
                    ),
                    *constraints,
                    *references,
                    self.created_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.schedule_id and self.schedule_id != expected:
            raise ValueError("cognitive schedule id is inconsistent")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "constraints", constraints)
        object.__setattr__(self, "source_reference_ids", references)
        object.__setattr__(self, "schedule_id", expected)


class UnifiedCognitiveScheduler:
    """Derive a governed, consultative execution order from M204 directives."""

    def __init__(self, coordinator: CrossDomainCoordinator | None = None) -> None:
        self.coordinator = coordinator
        self.last_schedule: UnifiedCognitiveSchedule | None = None

    def bind_coordinator(self, coordinator: CrossDomainCoordinator) -> None:
        self.coordinator = coordinator

    def schedule(
        self, *, owner: str, session_id: str, now: datetime | None = None
    ) -> UnifiedCognitiveSchedule:
        if self.coordinator is None:
            raise RuntimeError("unified cognitive scheduler coordinator is not bound")
        timestamp = now or datetime.now(timezone.utc)
        directive = self.coordinator.last_directive
        if (
            directive is None
            or directive.owner != owner.strip()
            or directive.session_id != session_id.strip()
        ):
            directive = self.coordinator.coordinate(
                owner=owner, session_id=session_id, now=timestamp
            )
        items = self._build_items(directive)
        constraints = tuple(
            dict.fromkeys(
                (
                    *directive.conflicts,
                    *(
                        priority
                        for priority in directive.priorities
                        if priority
                        in {"resolve_constraints", "preserve_blocking_boundary"}
                    ),
                )
            )
        )
        if directive.status is CrossDomainCoordinationStatus.IDLE:
            status = UnifiedCognitiveScheduleStatus.IDLE
        elif directive.status is CrossDomainCoordinationStatus.BLOCKED:
            status = UnifiedCognitiveScheduleStatus.BLOCKED
        elif directive.status is CrossDomainCoordinationStatus.ATTENTION_REQUIRED:
            status = UnifiedCognitiveScheduleStatus.ATTENTION_REQUIRED
        else:
            status = UnifiedCognitiveScheduleStatus.SCHEDULED
        schedule = UnifiedCognitiveSchedule(
            owner=owner,
            session_id=session_id,
            status=status,
            items=items,
            constraints=constraints,
            source_reference_ids=(
                directive.directive_id,
                *directive.source_reference_ids,
            ),
            created_at=timestamp,
        )
        self.last_schedule = schedule
        return schedule

    @staticmethod
    def _build_items(
        directive: CrossDomainCoordinationDirective,
    ) -> tuple[CognitiveScheduleItem, ...]:
        if directive.status is CrossDomainCoordinationStatus.IDLE:
            return ()
        actions = list(directive.priorities)
        if not actions:
            actions = ["maintain_cross_domain_alignment"]
        domains = directive.participating_domains or (CognitiveBlackboardDomain.SYSTEM,)
        items: list[CognitiveScheduleItem] = []
        for index, action in enumerate(actions, start=1):
            domain = domains[min(index - 1, len(domains) - 1)]
            priority = max(10, 100 - ((index - 1) * 10))
            dependencies = () if index == 1 else (actions[index - 2],)
            items.append(
                CognitiveScheduleItem(
                    sequence=index,
                    domain=domain,
                    action=action,
                    priority=priority,
                    depends_on=dependencies,
                )
            )
        return tuple(items)


@dataclass
class UnifiedCognitiveSchedulerRuntimeContributor:
    scheduler: UnifiedCognitiveScheduler
    coordinator: CrossDomainCoordinator
    blackboard: UnifiedCognitiveBlackboard
    name: str = "unified_cognitive_scheduler"

    def contribute(
        self,
        *,
        owner: str,
        session_id: str,
        text: str,
        request: LLMRequest,
        now: datetime,
    ) -> CognitiveRuntimeContribution:
        del text, request
        self.scheduler.bind_coordinator(self.coordinator)
        schedule = self.scheduler.schedule(owner=owner, session_id=session_id, now=now)
        entry = self.blackboard.publish(
            CognitiveBlackboardEntry(
                owner=owner,
                session_id=session_id,
                domain=CognitiveBlackboardDomain.SYSTEM,
                kind=CognitiveBlackboardEntryKind.CANDIDATE,
                key="unified_cognitive_schedule_status",
                value=schedule.status.value,
                confidence=1.0
                if schedule.status
                in {
                    UnifiedCognitiveScheduleStatus.IDLE,
                    UnifiedCognitiveScheduleStatus.SCHEDULED,
                }
                else 0.75,
                source_reference_ids=(
                    schedule.schedule_id,
                    *schedule.source_reference_ids,
                ),
                created_at=now,
            )
        )
        ordered = ", ".join(item.action for item in schedule.items) or "sin tareas"
        return CognitiveRuntimeContribution(
            stage=self.name,
            status=CognitiveRuntimeStageStatus.APPLIED,
            prompt_lines=(
                f"Agenda cognitiva: {schedule.status.value}; orden {ordered}.",
            ),
            reference_ids=(
                entry.entry_id,
                schedule.schedule_id,
                *schedule.source_reference_ids,
            ),
            rationale=(
                "m204_coordination_directive_consulted",
                "priority_order_derived",
                "governed_schedule_candidate_published",
                "execution_authority_not_acquired",
            ),
        )
