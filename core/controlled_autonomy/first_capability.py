from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Callable, Protocol, runtime_checkable
from uuid import uuid4

from core.executive_recovery_health import ComponentHealth, ComponentHealthState

from .action_candidates import (
    ActionTemplate,
    CandidateRule,
    DeterministicActionCandidateGenerator,
)
from .audio_diagnostic import (
    AudioDiagnosticReader,
    DiagnoseAudioRuntimeCapability,
)
from .autonomy_gate import DeterministicAutonomyGate
from .contracts import (
    ActionCandidate,
    AutonomyDecision,
    DecisionDisposition,
    DecisionJournal,
    DecisionOutcome,
    DecisionPolicy,
    OutcomeStatus,
    Reversibility,
    RiskLevel,
)
from .decision_journal import InMemoryDecisionJournal
from .decision_policy import DeterministicDecisionPolicyEngine
from .dynamic_priority import (
    ExperienceAwareDynamicPriorityProvider,
    ExperienceMemoryReader,
)
from .orchestrator import (
    ControlledAutonomyOrchestrator,
    ControlledAutonomyResult,
    DeterministicControlledAutonomyOrchestrator,
    OrchestrationStatus,
)
from .outcome_supervisor import (
    DeterministicOutcomeSupervisor,
    OutcomeSupervisionResult,
    OutcomeSupervisor,
)
from .risk_confidence import (
    DeterministicRiskConfidenceEvaluator,
    RiskProfile,
    default_risk_profiles,
)
from .situation_assessment import (
    DeterministicSituationAssessor,
    RuntimeObservation,
    default_situation_rules,
)


class CapabilityRunStatus(str, Enum):
    NO_SITUATION = "no_situation"
    NOT_AUTHORIZED = "not_authorized"
    UNSUPPORTED_ACTION = "unsupported_action"
    EXECUTED = "executed"


@dataclass(frozen=True)
class CapabilityRunResult:
    status: CapabilityRunStatus | str
    orchestration: ControlledAutonomyResult
    candidate: ActionCandidate | None
    outcome: DecisionOutcome | None
    supervision: OutcomeSupervisionResult | None
    rationale: tuple[str, ...]
    run_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", CapabilityRunStatus(self.status))
        _require_text(self.run_id, "capability run id")
        _require_items(self.rationale, "capability run rationale")
        if self.status is CapabilityRunStatus.EXECUTED:
            if self.candidate is None or self.outcome is None:
                raise ValueError("executed capability requires candidate and outcome")
            if self.supervision is None:
                raise ValueError("executed capability requires supervision")
            if self.outcome.decision_id != self._decision().decision_id:
                raise ValueError("outcome must reference the governed decision")
            return
        if self.outcome is not None or self.supervision is not None:
            raise ValueError("non-executed capability must not contain an outcome")

    def _decision(self) -> AutonomyDecision:
        gate = self.orchestration.gate_evaluation
        if gate is None:
            raise ValueError("capability result requires a governed decision")
        return gate.gated_decision


@runtime_checkable
class ComponentHealthReader(Protocol):
    def get(self, component_id: str) -> ComponentHealth: ...


@runtime_checkable
class AutonomousCapabilityRunner(Protocol):
    def run(
        self,
        observation: RuntimeObservation,
        policy: DecisionPolicy,
    ) -> CapabilityRunResult: ...


class VerifyComponentHealthCapability:
    """Executes the first read-only autonomous capability."""

    action = "verify_component_health"

    def __init__(
        self,
        health_reader: ComponentHealthReader,
        *,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._health_reader = health_reader
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def execute(
        self,
        decision: AutonomyDecision,
        candidate: ActionCandidate,
        component_id: str,
    ) -> DecisionOutcome:
        if decision.disposition is not DecisionDisposition.AUTHORIZE:
            raise ValueError("capability execution requires authorization")
        if candidate.candidate_id != decision.candidate_id:
            raise ValueError("candidate must match the authorized decision")
        if candidate.action != self.action:
            raise ValueError("unsupported capability action")
        _require_text(component_id, "component id")
        try:
            health = self._health_reader.get(component_id)
        except Exception as exc:  # boundary converts adapter failure to outcome
            return DecisionOutcome(
                decision_id=decision.decision_id,
                status=OutcomeStatus.FAILED,
                observed_at=self._clock(),
                summary="Component health verification failed",
                evidence=(
                    f"component_id={component_id}",
                    f"error={type(exc).__name__}: {exc}",
                ),
            )
        status = _outcome_status(health.state)
        return DecisionOutcome(
            decision_id=decision.decision_id,
            status=status,
            observed_at=self._clock(),
            summary=f"Component health verified as {health.state.value}",
            evidence=(
                f"component_id={health.component_id}",
                f"health_state={health.state.value}",
                f"consecutive_failures={health.consecutive_failures}",
                f"recovery_attempts={health.recovery_attempts}",
            ),
        )


class DeterministicFirstAutonomousCapabilityRunner:
    """Runs only the authorized read-only health verification capability."""

    def __init__(
        self,
        *,
        orchestrator: ControlledAutonomyOrchestrator,
        capability: VerifyComponentHealthCapability,
        audio_capability: DiagnoseAudioRuntimeCapability | None = None,
        outcome_supervisor: OutcomeSupervisor | None = None,
    ) -> None:
        self._orchestrator = orchestrator
        self._capability = capability
        self._audio_capability = audio_capability
        self._outcome_supervisor = (
            outcome_supervisor or DeterministicOutcomeSupervisor()
        )

    def run(
        self,
        observation: RuntimeObservation,
        policy: DecisionPolicy,
    ) -> CapabilityRunResult:
        orchestration = self._orchestrator.orchestrate(observation, policy)
        if orchestration.status is OrchestrationStatus.NO_SITUATION:
            return CapabilityRunResult(
                status=CapabilityRunStatus.NO_SITUATION,
                orchestration=orchestration,
                candidate=None,
                outcome=None,
                supervision=None,
                rationale=("pipeline_stopped_without_situation",),
            )
        gate = orchestration.gate_evaluation
        generation = orchestration.generation
        if gate is None or generation is None:
            raise ValueError("completed orchestration requires gate and candidates")
        decision = gate.gated_decision
        candidate = _selected_candidate(decision, generation.candidates)
        if decision.disposition is not DecisionDisposition.AUTHORIZE:
            return CapabilityRunResult(
                status=CapabilityRunStatus.NOT_AUTHORIZED,
                orchestration=orchestration,
                candidate=candidate,
                outcome=None,
                supervision=None,
                rationale=("governed_decision_did_not_authorize_execution",),
            )
        if candidate is None:
            return CapabilityRunResult(
                status=CapabilityRunStatus.UNSUPPORTED_ACTION,
                orchestration=orchestration,
                candidate=None,
                outcome=None,
                supervision=None,
                rationale=("authorized_action_has_no_registered_capability",),
            )
        if candidate.action == self._capability.action:
            component_id = observation.attributes.get("component_id", "")
            _require_text(component_id, "component id observation attribute")
            outcome = self._capability.execute(decision, candidate, component_id)
        elif (
            self._audio_capability is not None
            and candidate.action == self._audio_capability.action
        ):
            outcome = self._audio_capability.execute(decision, candidate)
        else:
            return CapabilityRunResult(
                status=CapabilityRunStatus.UNSUPPORTED_ACTION,
                orchestration=orchestration,
                candidate=candidate,
                outcome=None,
                supervision=None,
                rationale=("authorized_action_has_no_registered_capability",),
            )
        supervision = self._outcome_supervisor.supervise(
            decision,
            outcome,
            policy,
            candidate,
            attempts_used=1,
        )
        return CapabilityRunResult(
            status=CapabilityRunStatus.EXECUTED,
            orchestration=orchestration,
            candidate=candidate,
            outcome=outcome,
            supervision=supervision,
            rationale=(
                "authorized_read_only_capability_executed",
                "outcome_supervised",
            ),
        )



def default_first_autonomous_capability_runner(
    health_reader: ComponentHealthReader,
    *,
    journal: DecisionJournal | None = None,
    audio_reader: AudioDiagnosticReader | None = None,
    experience_memory: ExperienceMemoryReader | None = None,
) -> DeterministicFirstAutonomousCapabilityRunner:
    """Compose the first capability with an intentionally narrow candidate set."""

    candidate_generator = DeterministicActionCandidateGenerator(
        (
            CandidateRule(
                situation_kind="audio_runtime_requires_diagnosis",
                templates=(
                    ActionTemplate(
                        action="diagnose_audio_runtime",
                        description="Inspect the local audio runtime state",
                        rationale=("diagnosis_before_audio_intervention",),
                        reversible=Reversibility.FULL,
                        estimated_cost=0.1,
                    ),
                ),
                rule_id="second-capability-audio-runtime-diagnosis",
            ),
            CandidateRule(
                situation_kind="runtime_component_degraded",
                templates=(
                    ActionTemplate(
                        action="verify_component_health",
                        description=(
                            "Verify whether the degraded component has recovered"
                        ),
                        rationale=("verification_before_intervention",),
                        reversible=Reversibility.FULL,
                        estimated_cost=0.1,
                    ),
                ),
                rule_id="first-capability-component-health-verification",
            ),
        )
    )
    orchestrator = DeterministicControlledAutonomyOrchestrator(
        assessor=DeterministicSituationAssessor(default_situation_rules()),
        candidate_generator=candidate_generator,
        risk_evaluator=DeterministicRiskConfidenceEvaluator(
            default_risk_profiles()
            + (
                RiskProfile(
                    action="diagnose_audio_runtime",
                    base_risk=RiskLevel.LOW,
                    base_confidence=0.96,
                    base_impact=0.12,
                    reasons=("read_only_audio_diagnosis",),
                    profile_id="risk-profile-diagnose-audio-runtime",
                ),
            )
        ),
        policy_engine=DeterministicDecisionPolicyEngine(
            priority_provider=(
                ExperienceAwareDynamicPriorityProvider(experience_memory)
                if experience_memory is not None
                else None
            )
        ),
        autonomy_gate=DeterministicAutonomyGate(),
        journal=journal or InMemoryDecisionJournal(),
    )
    return DeterministicFirstAutonomousCapabilityRunner(
        orchestrator=orchestrator,
        capability=VerifyComponentHealthCapability(health_reader),
        audio_capability=(
            DiagnoseAudioRuntimeCapability(audio_reader)
            if audio_reader is not None
            else None
        ),
    )


def _selected_candidate(
    decision: AutonomyDecision,
    candidates: tuple[ActionCandidate, ...],
) -> ActionCandidate | None:
    if decision.candidate_id is None:
        return None
    candidate = next(
        (item for item in candidates if item.candidate_id == decision.candidate_id),
        None,
    )
    if candidate is None:
        raise ValueError("governed decision references an unknown candidate")
    return candidate


def _outcome_status(state: ComponentHealthState) -> OutcomeStatus:
    if state is ComponentHealthState.HEALTHY:
        return OutcomeStatus.SUCCEEDED
    if state is ComponentHealthState.UNKNOWN:
        return OutcomeStatus.UNKNOWN
    return OutcomeStatus.DEGRADED


def _require_text(value: str, label: str) -> None:
    if not value.strip():
        raise ValueError(f"{label} must not be blank")


def _require_items(values: tuple[str, ...], label: str) -> None:
    if not values or any(not value.strip() for value in values):
        raise ValueError(f"{label} must contain non-blank items")


__all__ = [
    "AutonomousCapabilityRunner",
    "CapabilityRunResult",
    "CapabilityRunStatus",
    "ComponentHealthReader",
    "DeterministicFirstAutonomousCapabilityRunner",
    "VerifyComponentHealthCapability",
    "default_first_autonomous_capability_runner",
]
