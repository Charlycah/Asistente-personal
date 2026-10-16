from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256

from core.cognitive_runtime_orchestration import (
    CognitiveRuntimeContribution,
    CognitiveRuntimeStageStatus,
)
from core.high_load_cognitive_scheduling import (
    CognitiveAdmissionDisposition,
    CognitiveLoadBand,
    HighLoadCognitiveSchedule,
    HighLoadCognitiveScheduler,
)
from core.llm_provider import LLMRequest
from core.unified_cognitive_blackboard import (
    CognitiveBlackboardDomain,
    CognitiveBlackboardEntry,
    CognitiveBlackboardEntryKind,
    UnifiedCognitiveBlackboard,
)


class LongRunningStabilityState(str, Enum):
    STABLE = "stable"
    OBSERVING = "observing"
    CHECKPOINT_REQUIRED = "checkpoint_required"
    GUARDED = "guarded"


class StabilityDirective(str, Enum):
    CONTINUE = "continue"
    OBSERVE = "observe"
    CHECKPOINT = "checkpoint"
    STABILIZE = "stabilize"


@dataclass(frozen=True)
class StabilityObservation:
    sequence: int
    load_band: CognitiveLoadBand | str
    admitted: int
    deferred: int
    shed: int
    created_at: datetime

    def __post_init__(self) -> None:
        band = CognitiveLoadBand(self.load_band)
        if self.sequence < 1:
            raise ValueError("stability observation sequence must be positive")
        if min(self.admitted, self.deferred, self.shed) < 0:
            raise ValueError("stability observation counts must be non-negative")
        if self.created_at.tzinfo is None:
            raise ValueError("stability observation time must be timezone-aware")
        object.__setattr__(self, "load_band", band)


@dataclass(frozen=True)
class LongRunningStabilityAssessment:
    owner: str
    session_id: str
    state: LongRunningStabilityState | str
    directive: StabilityDirective | str
    cycle_count: int
    drift_score: int
    checkpoint_due: bool
    observations: tuple[StabilityObservation, ...]
    source_reference_ids: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    assessment_id: str = ""

    def __post_init__(self) -> None:
        owner, session_id = self.owner.strip(), self.session_id.strip()
        state = LongRunningStabilityState(self.state)
        directive = StabilityDirective(self.directive)
        references = tuple(
            item.strip() for item in self.source_reference_ids if item.strip()
        )
        if not owner or not session_id:
            raise ValueError("stability assessment identity must be complete")
        if self.cycle_count < 1:
            raise ValueError("stability assessment cycle count must be positive")
        if not 0 <= self.drift_score <= 100:
            raise ValueError("stability assessment drift score must be bounded")
        if self.created_at.tzinfo is None:
            raise ValueError("stability assessment time must be timezone-aware")
        sequences = tuple(item.sequence for item in self.observations)
        if sequences and sequences != tuple(range(sequences[0], sequences[-1] + 1)):
            raise ValueError("stability observations must be contiguous")
        if len(set(references)) != len(references):
            raise ValueError("stability assessment references must be unique")
        expected = sha256(
            "|".join(
                (
                    owner.casefold(),
                    session_id,
                    state.value,
                    directive.value,
                    str(self.cycle_count),
                    str(self.drift_score),
                    str(self.checkpoint_due),
                    *(
                        f"{item.sequence}:{item.load_band.value}:{item.admitted}:"
                        f"{item.deferred}:{item.shed}:{item.created_at.isoformat()}"
                        for item in self.observations
                    ),
                    *references,
                    self.created_at.isoformat(),
                )
            ).encode()
        ).hexdigest()
        if self.assessment_id and self.assessment_id != expected:
            raise ValueError("stability assessment id is inconsistent")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "state", state)
        object.__setattr__(self, "directive", directive)
        object.__setattr__(self, "source_reference_ids", references)
        object.__setattr__(self, "assessment_id", expected)


class LongRunningStabilityMonitor:
    """Track bounded runtime drift and emit checkpoint guidance only."""

    def __init__(
        self,
        scheduler: HighLoadCognitiveScheduler,
        *,
        checkpoint_interval: int = 25,
        history_limit: int = 32,
    ) -> None:
        if checkpoint_interval < 2:
            raise ValueError("checkpoint interval must be at least two")
        if history_limit < 2:
            raise ValueError("stability history limit must be at least two")
        self.scheduler = scheduler
        self.checkpoint_interval = checkpoint_interval
        self.history_limit = history_limit
        self._history: dict[tuple[str, str], deque[StabilityObservation]] = {}
        self._cycles: dict[tuple[str, str], int] = {}
        self.last_assessment: LongRunningStabilityAssessment | None = None

    def assess(
        self,
        *,
        owner: str,
        session_id: str,
        demand_units: int | None = None,
        now: datetime | None = None,
    ) -> LongRunningStabilityAssessment:
        timestamp = now or datetime.now(timezone.utc)
        schedule = self.scheduler.schedule(
            owner=owner,
            session_id=session_id,
            demand_units=demand_units,
            now=timestamp,
        )
        result = self.assess_schedule(schedule)
        self.last_assessment = result
        return result

    def assess_schedule(
        self, schedule: HighLoadCognitiveSchedule
    ) -> LongRunningStabilityAssessment:
        key = (schedule.owner.casefold(), schedule.session_id)
        cycle = self._cycles.get(key, 0) + 1
        self._cycles[key] = cycle
        history = self._history.setdefault(key, deque(maxlen=self.history_limit))
        observation = StabilityObservation(
            cycle,
            schedule.load_band,
            sum(
                item.disposition is CognitiveAdmissionDisposition.ADMIT
                for item in schedule.items
            ),
            sum(
                item.disposition is CognitiveAdmissionDisposition.DEFER
                for item in schedule.items
            ),
            sum(
                item.disposition is CognitiveAdmissionDisposition.SHED
                for item in schedule.items
            ),
            schedule.created_at,
        )
        history.append(observation)
        drift = self._drift_score(tuple(history))
        checkpoint_due = cycle % self.checkpoint_interval == 0
        if (
            observation.load_band is CognitiveLoadBand.SATURATED
            or observation.shed > 0
            or drift >= 70
        ):
            state, directive = (
                LongRunningStabilityState.GUARDED,
                StabilityDirective.STABILIZE,
            )
        elif checkpoint_due:
            state, directive = (
                LongRunningStabilityState.CHECKPOINT_REQUIRED,
                StabilityDirective.CHECKPOINT,
            )
        elif (
            observation.load_band
            in {CognitiveLoadBand.ELEVATED, CognitiveLoadBand.HIGH}
            or drift >= 30
        ):
            state, directive = (
                LongRunningStabilityState.OBSERVING,
                StabilityDirective.OBSERVE,
            )
        else:
            state, directive = (
                LongRunningStabilityState.STABLE,
                StabilityDirective.CONTINUE,
            )
        return LongRunningStabilityAssessment(
            schedule.owner,
            schedule.session_id,
            state,
            directive,
            cycle,
            drift,
            checkpoint_due,
            tuple(history),
            (schedule.schedule_id, *schedule.source_reference_ids),
            schedule.created_at,
        )

    @staticmethod
    def _drift_score(observations: tuple[StabilityObservation, ...]) -> int:
        if len(observations) < 2:
            return 0
        previous, current = observations[-2:]
        band_weight = {
            CognitiveLoadBand.NOMINAL: 0,
            CognitiveLoadBand.ELEVATED: 20,
            CognitiveLoadBand.HIGH: 45,
            CognitiveLoadBand.SATURATED: 70,
        }
        band_delta = abs(
            band_weight[current.load_band] - band_weight[previous.load_band]
        )
        disposition_delta = (
            abs(current.admitted - previous.admitted) * 5
            + abs(current.deferred - previous.deferred) * 8
            + abs(current.shed - previous.shed) * 12
        )
        return min(100, band_delta + disposition_delta)


@dataclass
class LongRunningStabilityRuntimeContributor:
    monitor: LongRunningStabilityMonitor
    blackboard: UnifiedCognitiveBlackboard
    name: str = "long_running_stability"

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
        assessment = self.monitor.assess(
            owner=owner,
            session_id=session_id,
            now=now,
        )
        entry = self.blackboard.publish(
            CognitiveBlackboardEntry(
                owner=owner,
                session_id=session_id,
                domain=CognitiveBlackboardDomain.SYSTEM,
                kind=CognitiveBlackboardEntryKind.CONSTRAINT,
                key="long_running_stability",
                value=assessment.state.value,
                confidence=1.0,
                source_reference_ids=(
                    assessment.assessment_id,
                    *assessment.source_reference_ids,
                ),
                created_at=now,
            )
        )
        return CognitiveRuntimeContribution(
            stage=self.name,
            status=CognitiveRuntimeStageStatus.APPLIED,
            prompt_lines=(
                f"Estabilidad prolongada: {assessment.state.value}; "
                f"directiva={assessment.directive.value}; "
                f"deriva={assessment.drift_score}.",
            ),
            reference_ids=(
                entry.entry_id,
                assessment.assessment_id,
                *assessment.source_reference_ids,
            ),
            rationale=(
                "bounded_runtime_history_evaluated",
                "checkpoint_policy_applied",
                "concurrent_execution_authority_not_acquired",
            ),
        )
