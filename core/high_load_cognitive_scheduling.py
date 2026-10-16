from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256

from core.cognitive_runtime_orchestration import (
    CognitiveRuntimeContribution,
    CognitiveRuntimeStageStatus,
)
from core.fault_recovery_coordination import (
    FaultRecoveryCoordinator,
    FaultRecoveryPlan,
    FaultRecoveryState,
)
from core.llm_provider import LLMRequest
from core.unified_cognitive_blackboard import (
    CognitiveBlackboardDomain,
    CognitiveBlackboardEntry,
    CognitiveBlackboardEntryKind,
    UnifiedCognitiveBlackboard,
)
from core.unified_cognitive_scheduler import (
    UnifiedCognitiveSchedule,
    UnifiedCognitiveScheduler,
)


class CognitiveLoadBand(str, Enum):
    NOMINAL = "nominal"
    ELEVATED = "elevated"
    HIGH = "high"
    SATURATED = "saturated"


class CognitiveAdmissionDisposition(str, Enum):
    ADMIT = "admit"
    DEFER = "defer"
    SHED = "shed"


@dataclass(frozen=True)
class HighLoadScheduleItem:
    sequence: int
    action: str
    disposition: CognitiveAdmissionDisposition | str
    priority: int
    rationale: tuple[str, ...]

    def __post_init__(self) -> None:
        action = self.action.strip()
        disposition = CognitiveAdmissionDisposition(self.disposition)
        rationale = tuple(item.strip() for item in self.rationale if item.strip())
        if self.sequence < 1:
            raise ValueError("high-load schedule sequence must be positive")
        if not action:
            raise ValueError("high-load schedule action must not be blank")
        if not 0 <= self.priority <= 100:
            raise ValueError(
                "high-load schedule priority must be between zero and one hundred"
            )
        if not rationale or len(set(rationale)) != len(rationale):
            raise ValueError(
                "high-load schedule rationale must be non-empty and unique"
            )
        object.__setattr__(self, "action", action)
        object.__setattr__(self, "disposition", disposition)
        object.__setattr__(self, "rationale", rationale)


@dataclass(frozen=True)
class HighLoadCognitiveSchedule:
    owner: str
    session_id: str
    load_band: CognitiveLoadBand | str
    demand_units: int
    capacity_units: int
    items: tuple[HighLoadScheduleItem, ...]
    source_reference_ids: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    schedule_id: str = ""

    def __post_init__(self) -> None:
        owner, session_id = self.owner.strip(), self.session_id.strip()
        load_band = CognitiveLoadBand(self.load_band)
        references = tuple(
            item.strip() for item in self.source_reference_ids if item.strip()
        )
        if not owner or not session_id:
            raise ValueError("high-load schedule identity must be complete")
        if self.demand_units < 0 or self.capacity_units < 1:
            raise ValueError("high-load schedule demand and capacity are invalid")
        if self.created_at.tzinfo is None:
            raise ValueError("high-load schedule time must be timezone-aware")
        if tuple(item.sequence for item in self.items) != tuple(
            range(1, len(self.items) + 1)
        ):
            raise ValueError("high-load schedule items must be contiguous")
        if len(set(references)) != len(references):
            raise ValueError("high-load schedule references must be unique")
        expected = sha256(
            "|".join(
                (
                    owner.casefold(),
                    session_id,
                    load_band.value,
                    str(self.demand_units),
                    str(self.capacity_units),
                    *(
                        f"{i.sequence}:{i.action}:{i.disposition.value}:{i.priority}:{','.join(i.rationale)}"
                        for i in self.items
                    ),
                    *references,
                    self.created_at.isoformat(),
                )
            ).encode()
        ).hexdigest()
        if self.schedule_id and self.schedule_id != expected:
            raise ValueError("high-load schedule id is inconsistent")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "load_band", load_band)
        object.__setattr__(self, "source_reference_ids", references)
        object.__setattr__(self, "schedule_id", expected)


class HighLoadCognitiveScheduler:
    """Apply bounded admission control without executing work concurrently."""

    def __init__(
        self,
        scheduler: UnifiedCognitiveScheduler,
        recovery: FaultRecoveryCoordinator,
        *,
        capacity_units: int = 4,
    ) -> None:
        if capacity_units < 1:
            raise ValueError("high-load scheduler capacity must be positive")
        self.scheduler, self.recovery, self.capacity_units = (
            scheduler,
            recovery,
            capacity_units,
        )
        self.last_schedule: HighLoadCognitiveSchedule | None = None

    def schedule(
        self,
        *,
        owner: str,
        session_id: str,
        demand_units: int | None = None,
        now: datetime | None = None,
    ) -> HighLoadCognitiveSchedule:
        timestamp = now or datetime.now(timezone.utc)
        base = self.scheduler.schedule(
            owner=owner, session_id=session_id, now=timestamp
        )
        recovery = self.recovery.coordinate(
            owner=owner, session_id=session_id, now=timestamp
        )
        demand = len(base.items) if demand_units is None else demand_units
        result = self.schedule_inputs(
            base, recovery, demand_units=demand, capacity_units=self.capacity_units
        )
        self.last_schedule = result
        return result

    @staticmethod
    def schedule_inputs(
        base: UnifiedCognitiveSchedule,
        recovery: FaultRecoveryPlan,
        *,
        demand_units: int,
        capacity_units: int,
    ) -> HighLoadCognitiveSchedule:
        if demand_units < 0 or capacity_units < 1:
            raise ValueError("high-load scheduler demand and capacity are invalid")
        ratio = demand_units / capacity_units
        band = (
            CognitiveLoadBand.NOMINAL
            if ratio <= 1
            else CognitiveLoadBand.ELEVATED
            if ratio <= 1.5
            else CognitiveLoadBand.HIGH
            if ratio <= 2
            else CognitiveLoadBand.SATURATED
        )
        actions = tuple(item.action for item in base.items) or (
            "maintain_cognitive_continuity",
        )
        admitted_limit = capacity_units
        if recovery.state in {FaultRecoveryState.STABILIZING, FaultRecoveryState.HELD}:
            admitted_limit = 1
        items = []
        for index, action in enumerate(actions, 1):
            if index <= admitted_limit:
                disposition = CognitiveAdmissionDisposition.ADMIT
            elif (
                band is CognitiveLoadBand.SATURATED
                or recovery.state is FaultRecoveryState.HELD
            ):
                disposition = CognitiveAdmissionDisposition.SHED
            else:
                disposition = CognitiveAdmissionDisposition.DEFER
            items.append(
                HighLoadScheduleItem(
                    index,
                    action,
                    disposition,
                    max(10, 100 - (index - 1) * 10),
                    (
                        f"load_band:{band.value}",
                        f"recovery_state:{recovery.state.value}",
                    ),
                )
            )
        return HighLoadCognitiveSchedule(
            base.owner,
            base.session_id,
            band,
            demand_units,
            capacity_units,
            tuple(items),
            tuple(
                dict.fromkeys(
                    (
                        base.schedule_id,
                        recovery.plan_id,
                        *base.source_reference_ids,
                        *recovery.source_reference_ids,
                    )
                )
            ),
            base.created_at,
        )


@dataclass
class HighLoadCognitiveSchedulingRuntimeContributor:
    scheduler: HighLoadCognitiveScheduler
    blackboard: UnifiedCognitiveBlackboard
    name: str = "high_load_cognitive_scheduling"

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
        schedule = self.scheduler.schedule(owner=owner, session_id=session_id, now=now)
        entry = self.blackboard.publish(
            CognitiveBlackboardEntry(
                owner=owner,
                session_id=session_id,
                domain=CognitiveBlackboardDomain.SYSTEM,
                kind=CognitiveBlackboardEntryKind.CONSTRAINT,
                key="high_load_cognitive_schedule",
                value=schedule.load_band.value,
                confidence=1.0,
                source_reference_ids=(
                    schedule.schedule_id,
                    *schedule.source_reference_ids,
                ),
                created_at=now,
            )
        )
        admitted = sum(
            item.disposition is CognitiveAdmissionDisposition.ADMIT
            for item in schedule.items
        )
        return CognitiveRuntimeContribution(
            stage=self.name,
            status=CognitiveRuntimeStageStatus.APPLIED,
            prompt_lines=(
                f"Carga cognitiva: {schedule.load_band.value}; "
                f"admitidas={admitted}/{len(schedule.items)}.",
            ),
            reference_ids=(
                entry.entry_id,
                schedule.schedule_id,
                *schedule.source_reference_ids,
            ),
            rationale=(
                "bounded_admission_control_applied",
                "recovery_constraints_preserved",
                "concurrent_execution_authority_not_acquired",
            ),
        )
