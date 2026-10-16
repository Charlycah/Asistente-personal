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
from core.llm_provider import LLMRequest
from core.unified_cognitive_blackboard import (
    CognitiveBlackboardDomain,
    CognitiveBlackboardEntry,
    CognitiveBlackboardEntryKind,
    UnifiedCognitiveBlackboard,
)
from core.unified_cognitive_scheduler import (
    CognitiveScheduleItem,
    UnifiedCognitiveSchedule,
    UnifiedCognitiveScheduler,
    UnifiedCognitiveScheduleStatus,
)


class ExecutiveArbitrationStatus(str, Enum):
    IDLE = "idle"
    AUTHORIZED = "authorized"
    PARTIALLY_AUTHORIZED = "partially_authorized"
    DEFERRED = "deferred"
    REJECTED = "rejected"


class ExecutiveTaskDisposition(str, Enum):
    AUTHORIZE = "authorize"
    DEFER = "defer"
    REJECT = "reject"


@dataclass(frozen=True)
class ExecutiveTaskDecision:
    sequence: int
    domain: CognitiveBlackboardDomain | str
    action: str
    disposition: ExecutiveTaskDisposition | str
    rationale: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        domain = CognitiveBlackboardDomain(self.domain)
        disposition = ExecutiveTaskDisposition(self.disposition)
        action = self.action.strip()
        rationale = tuple(item.strip() for item in self.rationale if item.strip())
        if self.sequence < 1:
            raise ValueError("executive task decision sequence must be positive")
        if not action:
            raise ValueError("executive task decision action must be present")
        if len(set(rationale)) != len(rationale):
            raise ValueError("executive task decision rationale must be unique")
        object.__setattr__(self, "domain", domain)
        object.__setattr__(self, "disposition", disposition)
        object.__setattr__(self, "action", action)
        object.__setattr__(self, "rationale", rationale)


@dataclass(frozen=True)
class ExecutiveArbitrationDecision:
    owner: str
    session_id: str
    status: ExecutiveArbitrationStatus | str
    task_decisions: tuple[ExecutiveTaskDecision, ...]
    constraints: tuple[str, ...] = ()
    source_reference_ids: tuple[str, ...] = ()
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    decision_id: str = ""

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        session_id = self.session_id.strip()
        status = ExecutiveArbitrationStatus(self.status)
        constraints = tuple(item.strip() for item in self.constraints if item.strip())
        references = tuple(
            item.strip() for item in self.source_reference_ids if item.strip()
        )
        if not owner or not session_id:
            raise ValueError("executive arbitration identity must be complete")
        if self.created_at.tzinfo is None:
            raise ValueError("executive arbitration time must be timezone-aware")
        if len(set(item.sequence for item in self.task_decisions)) != len(
            self.task_decisions
        ):
            raise ValueError("executive arbitration sequences must be unique")
        if tuple(sorted(item.sequence for item in self.task_decisions)) != tuple(
            range(1, len(self.task_decisions) + 1)
        ):
            raise ValueError("executive arbitration sequences must be contiguous")
        if len(set(constraints)) != len(constraints):
            raise ValueError("executive arbitration constraints must be unique")
        if len(set(references)) != len(references):
            raise ValueError("executive arbitration references must be unique")
        expected = sha256(
            "|".join(
                (
                    owner.casefold(),
                    session_id,
                    status.value,
                    *(
                        f"{item.sequence}:{item.domain.value}:{item.action}:{item.disposition.value}:{','.join(item.rationale)}"
                        for item in self.task_decisions
                    ),
                    *constraints,
                    *references,
                    self.created_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.decision_id and self.decision_id != expected:
            raise ValueError("executive arbitration id is inconsistent")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "constraints", constraints)
        object.__setattr__(self, "source_reference_ids", references)
        object.__setattr__(self, "decision_id", expected)


class ExecutiveArbitrator:
    """Apply governed executive disposition to M205 schedule candidates."""

    def __init__(self, scheduler: UnifiedCognitiveScheduler | None = None) -> None:
        self.scheduler = scheduler
        self.last_decision: ExecutiveArbitrationDecision | None = None

    def bind_scheduler(self, scheduler: UnifiedCognitiveScheduler) -> None:
        self.scheduler = scheduler

    def arbitrate(
        self, *, owner: str, session_id: str, now: datetime | None = None
    ) -> ExecutiveArbitrationDecision:
        if self.scheduler is None:
            raise RuntimeError("executive arbitrator scheduler is not bound")
        timestamp = now or datetime.now(timezone.utc)
        schedule = self.scheduler.last_schedule
        if (
            schedule is None
            or schedule.owner != owner.strip()
            or schedule.session_id != session_id.strip()
        ):
            schedule = self.scheduler.schedule(
                owner=owner, session_id=session_id, now=timestamp
            )
        task_decisions = self._decide_tasks(schedule)
        dispositions = {item.disposition for item in task_decisions}
        if schedule.status is UnifiedCognitiveScheduleStatus.IDLE:
            status = ExecutiveArbitrationStatus.IDLE
        elif dispositions == {ExecutiveTaskDisposition.REJECT}:
            status = ExecutiveArbitrationStatus.REJECTED
        elif dispositions == {ExecutiveTaskDisposition.DEFER}:
            status = ExecutiveArbitrationStatus.DEFERRED
        elif (
            ExecutiveTaskDisposition.AUTHORIZE in dispositions and len(dispositions) > 1
        ):
            status = ExecutiveArbitrationStatus.PARTIALLY_AUTHORIZED
        else:
            status = ExecutiveArbitrationStatus.AUTHORIZED
        decision = ExecutiveArbitrationDecision(
            owner=owner,
            session_id=session_id,
            status=status,
            task_decisions=task_decisions,
            constraints=schedule.constraints,
            source_reference_ids=(schedule.schedule_id, *schedule.source_reference_ids),
            created_at=timestamp,
        )
        self.last_decision = decision
        return decision

    @staticmethod
    def _decide_tasks(
        schedule: UnifiedCognitiveSchedule,
    ) -> tuple[ExecutiveTaskDecision, ...]:
        if schedule.status is UnifiedCognitiveScheduleStatus.IDLE:
            return ()
        decisions: list[ExecutiveTaskDecision] = []
        for item in schedule.items:
            disposition, rationale = ExecutiveArbitrator._disposition_for(
                schedule, item
            )
            decisions.append(
                ExecutiveTaskDecision(
                    sequence=item.sequence,
                    domain=item.domain,
                    action=item.action,
                    disposition=disposition,
                    rationale=rationale,
                )
            )
        return tuple(decisions)

    @staticmethod
    def _disposition_for(
        schedule: UnifiedCognitiveSchedule, item: CognitiveScheduleItem
    ) -> tuple[ExecutiveTaskDisposition, tuple[str, ...]]:
        if schedule.status is UnifiedCognitiveScheduleStatus.BLOCKED:
            return ExecutiveTaskDisposition.REJECT, (
                "blocking_constraint_preserved",
                "execution_not_authorized",
            )
        if schedule.status is UnifiedCognitiveScheduleStatus.ATTENTION_REQUIRED:
            if item.action in {
                "reconcile_conflicting_signals",
                "resolve_constraints",
                "preserve_blocking_boundary",
            }:
                return ExecutiveTaskDisposition.AUTHORIZE, (
                    "governance_repair_authorized",
                    "conflict_resolution_precedes_execution",
                )
            return ExecutiveTaskDisposition.DEFER, (
                "attention_required",
                "dependent_work_deferred",
            )
        return ExecutiveTaskDisposition.AUTHORIZE, (
            "schedule_candidate_governed",
            "task_authorized_for_downstream_execution",
        )


@dataclass
class ExecutiveArbitrationRuntimeContributor:
    arbitrator: ExecutiveArbitrator
    scheduler: UnifiedCognitiveScheduler
    blackboard: UnifiedCognitiveBlackboard
    name: str = "executive_arbitration"

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
        self.arbitrator.bind_scheduler(self.scheduler)
        decision = self.arbitrator.arbitrate(
            owner=owner, session_id=session_id, now=now
        )
        entry = self.blackboard.publish(
            CognitiveBlackboardEntry(
                owner=owner,
                session_id=session_id,
                domain=CognitiveBlackboardDomain.SYSTEM,
                kind=CognitiveBlackboardEntryKind.CANDIDATE,
                key="executive_arbitration_status",
                value=decision.status.value,
                confidence=1.0
                if decision.status
                in {
                    ExecutiveArbitrationStatus.IDLE,
                    ExecutiveArbitrationStatus.AUTHORIZED,
                }
                else 0.8,
                source_reference_ids=(
                    decision.decision_id,
                    *decision.source_reference_ids,
                ),
                created_at=now,
            )
        )
        summary = (
            ", ".join(
                f"{item.action}:{item.disposition.value}"
                for item in decision.task_decisions
            )
            or "sin tareas"
        )
        return CognitiveRuntimeContribution(
            stage=self.name,
            status=CognitiveRuntimeStageStatus.APPLIED,
            prompt_lines=(f"Arbitraje ejecutivo: {decision.status.value}; {summary}.",),
            reference_ids=(
                entry.entry_id,
                decision.decision_id,
                *decision.source_reference_ids,
            ),
            rationale=(
                "m205_schedule_consulted",
                "governed_task_dispositions_derived",
                "executive_decision_published",
                "tool_execution_not_performed",
            ),
        )
