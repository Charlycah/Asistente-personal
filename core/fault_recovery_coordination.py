from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256

from core.cognitive_runtime_orchestration import (
    CognitiveRuntimeContribution,
    CognitiveRuntimeStageStatus,
)
from core.graceful_degradation_engine import (
    CognitiveCapabilityDisposition,
    CognitiveDegradationDecision,
    CognitiveDegradationMode,
    GracefulDegradationEngine,
)
from core.llm_provider import LLMRequest
from core.unified_cognitive_blackboard import (
    CognitiveBlackboardDomain,
    CognitiveBlackboardEntry,
    CognitiveBlackboardEntryKind,
    UnifiedCognitiveBlackboard,
)


class FaultRecoveryState(str, Enum):
    STABLE = "stable"
    OBSERVING = "observing"
    STABILIZING = "stabilizing"
    RESTORING = "restoring"
    HELD = "held"


class FaultRecoveryDisposition(str, Enum):
    VERIFY = "verify"
    RETRY = "retry"
    RESTORE = "restore"
    HOLD = "hold"


@dataclass(frozen=True)
class FaultRecoveryStep:
    sequence: int
    target: str
    disposition: FaultRecoveryDisposition | str
    rationale: tuple[str, ...]

    def __post_init__(self) -> None:
        target = self.target.strip()
        disposition = FaultRecoveryDisposition(self.disposition)
        rationale = tuple(item.strip() for item in self.rationale if item.strip())
        if self.sequence < 1:
            raise ValueError("fault recovery sequence must be positive")
        if not target:
            raise ValueError("fault recovery target must not be blank")
        if not rationale:
            raise ValueError("fault recovery rationale must not be empty")
        if len(set(rationale)) != len(rationale):
            raise ValueError("fault recovery rationale must be unique")
        object.__setattr__(self, "target", target)
        object.__setattr__(self, "disposition", disposition)
        object.__setattr__(self, "rationale", rationale)


@dataclass(frozen=True)
class FaultRecoveryPlan:
    owner: str
    session_id: str
    state: FaultRecoveryState | str
    steps: tuple[FaultRecoveryStep, ...]
    restored_capabilities: tuple[str, ...]
    held_capabilities: tuple[str, ...]
    source_reference_ids: tuple[str, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    plan_id: str = ""

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        session_id = self.session_id.strip()
        state = FaultRecoveryState(self.state)
        restored = tuple(
            item.strip() for item in self.restored_capabilities if item.strip()
        )
        held = tuple(item.strip() for item in self.held_capabilities if item.strip())
        references = tuple(
            item.strip() for item in self.source_reference_ids if item.strip()
        )
        if not owner or not session_id:
            raise ValueError("fault recovery identity must be complete")
        if self.created_at.tzinfo is None:
            raise ValueError("fault recovery time must be timezone-aware")
        sequences = tuple(item.sequence for item in self.steps)
        if sequences != tuple(range(1, len(self.steps) + 1)):
            raise ValueError("fault recovery steps must be contiguous")
        if len(set(restored)) != len(restored):
            raise ValueError("restored capabilities must be unique")
        if len(set(held)) != len(held):
            raise ValueError("held capabilities must be unique")
        if set(restored) & set(held):
            raise ValueError("restored and held capabilities must not overlap")
        if len(set(references)) != len(references):
            raise ValueError("fault recovery references must be unique")
        expected = sha256(
            "|".join(
                (
                    owner.casefold(),
                    session_id,
                    state.value,
                    *(
                        f"{item.sequence}:{item.target}:{item.disposition.value}:{','.join(item.rationale)}"
                        for item in self.steps
                    ),
                    *restored,
                    *held,
                    *references,
                    self.created_at.isoformat(),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.plan_id and self.plan_id != expected:
            raise ValueError("fault recovery plan id is inconsistent")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "session_id", session_id)
        object.__setattr__(self, "state", state)
        object.__setattr__(self, "restored_capabilities", restored)
        object.__setattr__(self, "held_capabilities", held)
        object.__setattr__(self, "source_reference_ids", references)
        object.__setattr__(self, "plan_id", expected)


class FaultRecoveryCoordinator:
    """Coordinate bounded recovery sequencing without mutating external systems."""

    def __init__(self, degradation_engine: GracefulDegradationEngine) -> None:
        self.degradation_engine = degradation_engine
        self.last_plan: FaultRecoveryPlan | None = None

    def coordinate(
        self, *, owner: str, session_id: str, now: datetime | None = None
    ) -> FaultRecoveryPlan:
        decision = self.degradation_engine.activate(
            owner=owner, session_id=session_id, now=now
        )
        plan = self.coordinate_decision(decision)
        self.last_plan = plan
        return plan

    def coordinate_decision(
        self, decision: CognitiveDegradationDecision
    ) -> FaultRecoveryPlan:
        state = self._state(decision.mode)
        restricted = tuple(
            item.capability
            for item in decision.policies
            if item.disposition is not CognitiveCapabilityDisposition.PRESERVE
        )
        restored = restricted if state is FaultRecoveryState.RESTORING else ()
        held = (
            restricted
            if state in {FaultRecoveryState.STABILIZING, FaultRecoveryState.HELD}
            else ()
        )
        steps = self._steps(state, restricted)
        return FaultRecoveryPlan(
            owner=decision.owner,
            session_id=decision.session_id,
            state=state,
            steps=steps,
            restored_capabilities=restored,
            held_capabilities=held,
            source_reference_ids=(decision.decision_id, *decision.source_reference_ids),
            created_at=decision.created_at,
        )

    @staticmethod
    def _state(mode: CognitiveDegradationMode) -> FaultRecoveryState:
        return {
            CognitiveDegradationMode.FULL: FaultRecoveryState.STABLE,
            CognitiveDegradationMode.CONSERVATIVE: FaultRecoveryState.OBSERVING,
            CognitiveDegradationMode.ESSENTIAL: FaultRecoveryState.STABILIZING,
            CognitiveDegradationMode.CONTAINED: FaultRecoveryState.HELD,
        }[mode]

    @staticmethod
    def _steps(
        state: FaultRecoveryState, restricted: tuple[str, ...]
    ) -> tuple[FaultRecoveryStep, ...]:
        if state is FaultRecoveryState.STABLE:
            return (
                FaultRecoveryStep(
                    1, "cognitive_baseline", "verify", ("service_mode:full",)
                ),
            )
        if state is FaultRecoveryState.OBSERVING:
            return tuple(
                FaultRecoveryStep(index, capability, "verify", ("bounded_observation",))
                for index, capability in enumerate(
                    restricted or ("cognitive_baseline",), 1
                )
            )
        disposition = (
            FaultRecoveryDisposition.RETRY
            if state is FaultRecoveryState.STABILIZING
            else FaultRecoveryDisposition.HOLD
        )
        return tuple(
            FaultRecoveryStep(
                index,
                capability,
                disposition,
                (f"recovery_state:{state.value}", "conversation_continuity_preserved"),
            )
            for index, capability in enumerate(restricted or ("cognitive_baseline",), 1)
        )


@dataclass
class FaultRecoveryRuntimeContributor:
    coordinator: FaultRecoveryCoordinator
    blackboard: UnifiedCognitiveBlackboard
    name: str = "fault_recovery_coordination"

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
        plan = self.coordinator.coordinate(owner=owner, session_id=session_id, now=now)
        entry = self.blackboard.publish(
            CognitiveBlackboardEntry(
                owner=owner,
                session_id=session_id,
                domain=CognitiveBlackboardDomain.SYSTEM,
                kind=CognitiveBlackboardEntryKind.CONSTRAINT,
                key="fault_recovery_state",
                value=plan.state.value,
                confidence=1.0,
                source_reference_ids=(plan.plan_id, *plan.source_reference_ids),
                created_at=now,
            )
        )
        return CognitiveRuntimeContribution(
            stage=self.name,
            status=CognitiveRuntimeStageStatus.APPLIED,
            prompt_lines=(
                f"Recuperación cognitiva: {plan.state.value}; pasos={len(plan.steps)}.",
            ),
            reference_ids=(entry.entry_id, plan.plan_id, *plan.source_reference_ids),
            rationale=(
                "degradation_mode_translated_to_recovery_sequence",
                "recovery_actions_remain_bounded_and_traceable",
                "no_external_system_mutation_authority_acquired",
            ),
        )
