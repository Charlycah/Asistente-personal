from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol, runtime_checkable
from uuid import uuid4

from .action_candidates import (
    ActionCandidateGenerator,
    CandidateGenerationResult,
    DeterministicActionCandidateGenerator,
    default_candidate_rules,
)
from .autonomy_gate import (
    AutonomyGate,
    AutonomyGateResult,
    DeterministicAutonomyGate,
)
from .contracts import (
    ActionCandidate,
    DecisionJournal,
    DecisionJournalEntry,
    DecisionPolicy,
    RiskAssessment,
)
from .decision_journal import InMemoryDecisionJournal
from .decision_policy import (
    DecisionPolicyEngine,
    DeterministicDecisionPolicyEngine,
    PolicyEvaluationResult,
)
from .risk_confidence import (
    DeterministicRiskConfidenceEvaluator,
    RiskConfidenceEvaluator,
    RiskEvaluationResult,
    default_risk_profiles,
)
from .situation_assessment import (
    AssessmentStatus,
    DeterministicSituationAssessor,
    RuntimeObservation,
    SituationAssessmentResult,
    SituationAssessor,
    default_situation_rules,
)


class OrchestrationStatus(str, Enum):
    COMPLETED = "completed"
    NO_SITUATION = "no_situation"


@dataclass(frozen=True)
class ControlledAutonomyResult:
    """Immutable audit view of one complete controlled-autonomy cycle."""

    status: OrchestrationStatus | str
    observation: RuntimeObservation
    policy: DecisionPolicy
    assessment: SituationAssessmentResult
    generation: CandidateGenerationResult | None
    risk_evaluation: RiskEvaluationResult | None
    policy_evaluation: PolicyEvaluationResult | None
    gate_evaluation: AutonomyGateResult | None
    journal_entry: DecisionJournalEntry | None
    rationale: tuple[str, ...]
    orchestration_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", OrchestrationStatus(self.status))
        _require_text(self.orchestration_id, "orchestration id")
        _require_items(self.rationale, "orchestration rationale")
        if self.status is OrchestrationStatus.NO_SITUATION:
            if self.assessment.observation != self.observation:
                raise ValueError("assessment must reference the input observation")
            if self.assessment.status is AssessmentStatus.SITUATION_IDENTIFIED:
                raise ValueError("no-situation result cannot contain a situation")
            if any(
                item is not None
                for item in (
                    self.generation,
                    self.risk_evaluation,
                    self.policy_evaluation,
                    self.gate_evaluation,
                    self.journal_entry,
                )
            ):
                raise ValueError("no-situation result must stop after assessment")
            return
        if self.assessment.status is not AssessmentStatus.SITUATION_IDENTIFIED:
            raise ValueError("completed result requires an identified situation")
        if self.assessment.observation != self.observation:
            raise ValueError("assessment must reference the input observation")
        if any(
            item is None
            for item in (
                self.generation,
                self.risk_evaluation,
                self.policy_evaluation,
                self.gate_evaluation,
                self.journal_entry,
            )
        ):
            raise ValueError("completed result requires every pipeline stage")
        _validate_completed_result(self)


@runtime_checkable
class ControlledAutonomyOrchestrator(Protocol):
    def orchestrate(
        self,
        observation: RuntimeObservation,
        policy: DecisionPolicy,
    ) -> ControlledAutonomyResult: ...


class DeterministicControlledAutonomyOrchestrator:
    """Coordinates pure autonomy stages and journals the governed decision."""

    def __init__(
        self,
        *,
        assessor: SituationAssessor,
        candidate_generator: ActionCandidateGenerator,
        risk_evaluator: RiskConfidenceEvaluator,
        policy_engine: DecisionPolicyEngine,
        autonomy_gate: AutonomyGate,
        journal: DecisionJournal,
    ) -> None:
        self._assessor = assessor
        self._candidate_generator = candidate_generator
        self._risk_evaluator = risk_evaluator
        self._policy_engine = policy_engine
        self._autonomy_gate = autonomy_gate
        self._journal = journal

    @property
    def journal(self) -> DecisionJournal:
        return self._journal

    def orchestrate(
        self,
        observation: RuntimeObservation,
        policy: DecisionPolicy,
    ) -> ControlledAutonomyResult:
        assessment = self._assessor.assess(observation)
        if assessment.status is not AssessmentStatus.SITUATION_IDENTIFIED:
            return ControlledAutonomyResult(
                status=OrchestrationStatus.NO_SITUATION,
                observation=observation,
                policy=policy,
                assessment=assessment,
                generation=None,
                risk_evaluation=None,
                policy_evaluation=None,
                gate_evaluation=None,
                journal_entry=None,
                rationale=("pipeline_stopped_without_situation",),
            )

        situation = assessment.situation
        if situation is None:
            raise ValueError("identified assessment must contain a situation")
        generation = self._candidate_generator.generate(situation)
        risk_evaluation = self._risk_evaluator.evaluate(
            situation,
            generation.candidates,
        )
        policy_evaluation = self._policy_engine.decide(
            situation,
            generation.candidates,
            risk_evaluation.assessments,
            policy,
        )
        candidate, risk_assessment = _selected_inputs(
            policy_evaluation.decision.candidate_id,
            generation.candidates,
            risk_evaluation.assessments,
        )
        gate_evaluation = self._autonomy_gate.evaluate(
            policy_evaluation.decision,
            policy,
            candidate,
            risk_assessment,
        )
        journal_entry = DecisionJournalEntry(
            situation=situation,
            candidates=generation.candidates,
            assessments=risk_evaluation.assessments,
            decision=gate_evaluation.gated_decision,
        )
        self._journal.append(journal_entry)
        return ControlledAutonomyResult(
            status=OrchestrationStatus.COMPLETED,
            observation=observation,
            policy=policy,
            assessment=assessment,
            generation=generation,
            risk_evaluation=risk_evaluation,
            policy_evaluation=policy_evaluation,
            gate_evaluation=gate_evaluation,
            journal_entry=journal_entry,
            rationale=(
                "controlled_autonomy_pipeline_completed",
                "governed_decision_journaled",
            ),
        )


def default_controlled_autonomy_orchestrator(
    *,
    journal: DecisionJournal | None = None,
) -> DeterministicControlledAutonomyOrchestrator:
    """Compose the validated deterministic stages with default rule sets."""

    return DeterministicControlledAutonomyOrchestrator(
        assessor=DeterministicSituationAssessor(default_situation_rules()),
        candidate_generator=DeterministicActionCandidateGenerator(
            default_candidate_rules()
        ),
        risk_evaluator=DeterministicRiskConfidenceEvaluator(
            default_risk_profiles()
        ),
        policy_engine=DeterministicDecisionPolicyEngine(),
        autonomy_gate=DeterministicAutonomyGate(),
        journal=journal or InMemoryDecisionJournal(),
    )


def _selected_inputs(
    candidate_id: str | None,
    candidates: tuple[ActionCandidate, ...],
    assessments: tuple[RiskAssessment, ...],
) -> tuple[ActionCandidate | None, RiskAssessment | None]:
    if candidate_id is None:
        return None, None
    candidate = next(
        (item for item in candidates if item.candidate_id == candidate_id),
        None,
    )
    assessment = next(
        (item for item in assessments if item.candidate_id == candidate_id),
        None,
    )
    if candidate is None or assessment is None:
        raise ValueError("selected decision must reference evaluated candidate data")
    return candidate, assessment


def _validate_completed_result(result: ControlledAutonomyResult) -> None:
    situation = result.assessment.situation
    generation = result.generation
    risk_evaluation = result.risk_evaluation
    policy_evaluation = result.policy_evaluation
    gate_evaluation = result.gate_evaluation
    journal_entry = result.journal_entry
    assert situation is not None
    assert generation is not None
    assert risk_evaluation is not None
    assert policy_evaluation is not None
    assert gate_evaluation is not None
    assert journal_entry is not None
    if generation.situation != situation:
        raise ValueError("candidate generation must reference the situation")
    if risk_evaluation.situation != situation:
        raise ValueError("risk evaluation must reference the situation")
    if risk_evaluation.candidates != generation.candidates:
        raise ValueError("risk evaluation must preserve generated candidates")
    if policy_evaluation.situation != situation:
        raise ValueError("policy evaluation must reference the situation")
    if policy_evaluation.candidates != generation.candidates:
        raise ValueError("policy evaluation must preserve generated candidates")
    if policy_evaluation.assessments != risk_evaluation.assessments:
        raise ValueError("policy evaluation must preserve risk assessments")
    if gate_evaluation.policy_decision != policy_evaluation.decision:
        raise ValueError("autonomy gate must receive the policy decision")
    if journal_entry.situation != situation:
        raise ValueError("journal entry must preserve the situation")
    if journal_entry.candidates != generation.candidates:
        raise ValueError("journal entry must preserve generated candidates")
    if journal_entry.assessments != risk_evaluation.assessments:
        raise ValueError("journal entry must preserve risk assessments")
    if journal_entry.decision != gate_evaluation.gated_decision:
        raise ValueError("journal entry must store the gated decision")


def _require_text(value: str, label: str) -> None:
    if not value.strip():
        raise ValueError(f"{label} must not be blank")


def _require_items(values: tuple[str, ...], label: str) -> None:
    if not values or any(not value.strip() for value in values):
        raise ValueError(f"{label} must contain non-blank items")


__all__ = [
    "ControlledAutonomyOrchestrator",
    "ControlledAutonomyResult",
    "DeterministicControlledAutonomyOrchestrator",
    "OrchestrationStatus",
    "default_controlled_autonomy_orchestrator",
]
