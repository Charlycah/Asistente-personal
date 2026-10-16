from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Callable, Protocol, runtime_checkable
from uuid import uuid4

from .contracts import (
    ActionCandidate,
    AutonomyDecision,
    AutonomyLevel,
    DecisionDisposition,
    DecisionPolicy,
    DecisionSituation,
    Reversibility,
    RiskAssessment,
    RiskLevel,
)
from .dynamic_priority import (
    DynamicPriorityProvider,
    NeutralDynamicPriorityProvider,
)


class PolicyEvaluationStatus(str, Enum):
    DECISION_PRODUCED = "decision_produced"
    NO_CANDIDATES = "no_candidates"
    INVALID_INPUT = "invalid_input"


@dataclass(frozen=True)
class CandidatePolicyScore:
    """Auditable deterministic score for one assessed candidate."""

    candidate_id: str
    eligible: bool
    score: float
    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_text(self.candidate_id, "policy score candidate id")
        _require_items(self.reasons, "policy score reasons")
        _require_unit_interval(self.score, "policy score")


@dataclass(frozen=True)
class PolicyEvaluationResult:
    status: PolicyEvaluationStatus | str
    situation: DecisionSituation
    candidates: tuple[ActionCandidate, ...]
    assessments: tuple[RiskAssessment, ...]
    policy: DecisionPolicy
    scores: tuple[CandidatePolicyScore, ...]
    decision: AutonomyDecision
    rationale: tuple[str, ...]
    evaluation_id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        _require_text(self.evaluation_id, "policy evaluation id")
        _require_items(self.rationale, "policy evaluation rationale")
        status = PolicyEvaluationStatus(self.status)
        object.__setattr__(self, "status", status)
        candidate_ids = tuple(item.candidate_id for item in self.candidates)
        assessment_ids = tuple(item.candidate_id for item in self.assessments)
        score_ids = tuple(item.candidate_id for item in self.scores)
        if len(set(candidate_ids)) != len(candidate_ids):
            raise ValueError("policy candidates must have unique ids")
        if len(set(assessment_ids)) != len(assessment_ids):
            raise ValueError("policy assessments must be unique per candidate")
        if len(set(score_ids)) != len(score_ids):
            raise ValueError("policy scores must be unique per candidate")
        if set(assessment_ids) != set(candidate_ids):
            raise ValueError("policy requires one assessment per candidate")
        if set(score_ids) != set(candidate_ids):
            raise ValueError("policy requires one score per candidate")
        if self.decision.situation_id != self.situation.situation_id:
            raise ValueError("policy decision must reference its situation")
        if self.decision.candidate_id is not None:
            if self.decision.candidate_id not in set(candidate_ids):
                raise ValueError("policy decision references unknown candidate")
        if self.decision.disposition in {
            DecisionDisposition.AUTHORIZE,
            DecisionDisposition.REQUEST_CONFIRMATION,
        }:
            raise ValueError("policy engine must not perform autonomy gating")
        if status is PolicyEvaluationStatus.NO_CANDIDATES and self.candidates:
            raise ValueError("no-candidates status requires an empty candidate set")
        if status is PolicyEvaluationStatus.DECISION_PRODUCED:
            if not self.candidates:
                raise ValueError("produced decision requires candidates")


@runtime_checkable
class DecisionPolicyEngine(Protocol):
    def decide(
        self,
        situation: DecisionSituation,
        candidates: tuple[ActionCandidate, ...],
        assessments: tuple[RiskAssessment, ...],
        policy: DecisionPolicy,
    ) -> PolicyEvaluationResult: ...


class DeterministicDecisionPolicyEngine:
    """Pure policy engine that ranks candidates without authorizing actions."""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime] | None = None,
        priority_provider: DynamicPriorityProvider | None = None,
    ) -> None:
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._priority_provider = (
            priority_provider or NeutralDynamicPriorityProvider()
        )

    def decide(
        self,
        situation: DecisionSituation,
        candidates: tuple[ActionCandidate, ...],
        assessments: tuple[RiskAssessment, ...],
        policy: DecisionPolicy,
    ) -> PolicyEvaluationResult:
        _validate_candidate_assessment_alignment(candidates, assessments)
        if not candidates:
            decision = self._decision(
                situation=situation,
                candidate_id=None,
                disposition=DecisionDisposition.OBSERVE,
                confidence=0.0,
                risk=RiskLevel.LOW,
                policy=policy,
                rationale=("no_candidates_available",),
            )
            return PolicyEvaluationResult(
                status=PolicyEvaluationStatus.NO_CANDIDATES,
                situation=situation,
                candidates=(),
                assessments=(),
                policy=policy,
                scores=(),
                decision=decision,
                rationale=("no_candidates_available",),
            )

        assessment_by_id = {item.candidate_id: item for item in assessments}
        scores = tuple(
            self._score(
                situation,
                candidate,
                assessment_by_id[candidate.candidate_id],
                policy,
            )
            for candidate in candidates
        )
        eligible = tuple(item for item in scores if item.eligible)
        if not eligible:
            candidate, assessment = _blocked_reference(candidates, assessments)
            rationale = (
                "no_candidate_satisfied_policy",
                *scores[_candidate_index(candidates, candidate.candidate_id)].reasons,
            )
            decision = self._decision(
                situation=situation,
                candidate_id=candidate.candidate_id,
                disposition=DecisionDisposition.BLOCK,
                confidence=assessment.confidence,
                risk=assessment.risk,
                policy=policy,
                rationale=rationale,
            )
        else:
            selected_score = max(
                eligible,
                key=lambda item: (
                    item.score,
                    -_candidate_index(candidates, item.candidate_id),
                ),
            )
            candidate = candidates[
                _candidate_index(candidates, selected_score.candidate_id)
            ]
            assessment = assessment_by_id[candidate.candidate_id]
            disposition = _selection_disposition(policy)
            rationale = (
                "highest_eligible_policy_score",
                f"selected_score={selected_score.score:.6f}",
                *selected_score.reasons,
            )
            decision = self._decision(
                situation=situation,
                candidate_id=candidate.candidate_id,
                disposition=disposition,
                confidence=assessment.confidence,
                risk=assessment.risk,
                policy=policy,
                rationale=rationale,
            )
        return PolicyEvaluationResult(
            status=PolicyEvaluationStatus.DECISION_PRODUCED,
            situation=situation,
            candidates=candidates,
            assessments=assessments,
            policy=policy,
            scores=scores,
            decision=decision,
            rationale=(
                "deterministic_policy_ranking_complete",
                f"candidate_count={len(candidates)}",
            ),
        )

    def _score(
        self,
        situation: DecisionSituation,
        candidate: ActionCandidate,
        assessment: RiskAssessment,
        policy: DecisionPolicy,
    ) -> CandidatePolicyScore:
        reasons: list[str] = []
        eligible = True
        if candidate.action in policy.prohibited_actions:
            eligible = False
            reasons.append("action_prohibited_by_policy")
        if assessment.risk is RiskLevel.PROHIBITED:
            eligible = False
            reasons.append("assessment_risk_prohibited")
        if assessment.confidence < policy.minimum_confidence:
            eligible = False
            reasons.append("confidence_below_policy_minimum")
        if policy.autonomy_level is AutonomyLevel.PROHIBITED:
            eligible = False
            reasons.append("policy_level_prohibited")
        base_score = _candidate_score(candidate, assessment)
        priority = self._priority_provider.prioritize(
            situation, candidate, assessment
        )
        if priority.candidate_id != candidate.candidate_id:
            raise ValueError("priority adjustment must reference its candidate")
        score = round(_clamp(base_score + priority.adjustment), 6)
        reasons.extend(
            (
                f"confidence={assessment.confidence:.6f}",
                f"impact={assessment.impact:.6f}",
                f"risk={assessment.risk.value}",
                f"reversibility={assessment.reversibility.value}",
                f"estimated_cost={candidate.estimated_cost:.6f}",
                f"base_score={base_score:.6f}",
                *priority.reasons,
            )
        )
        return CandidatePolicyScore(
            candidate_id=candidate.candidate_id,
            eligible=eligible,
            score=score,
            reasons=tuple(reasons),
        )

    def _decision(
        self,
        *,
        situation: DecisionSituation,
        candidate_id: str | None,
        disposition: DecisionDisposition,
        confidence: float,
        risk: RiskLevel,
        policy: DecisionPolicy,
        rationale: tuple[str, ...],
    ) -> AutonomyDecision:
        return AutonomyDecision(
            situation_id=situation.situation_id,
            candidate_id=candidate_id,
            disposition=disposition,
            confidence=confidence,
            risk=risk,
            rationale=rationale,
            decided_at=self._clock(),
            policy_level=policy.autonomy_level,
        )


def _candidate_score(
    candidate: ActionCandidate,
    assessment: RiskAssessment,
) -> float:
    risk_penalty = {
        RiskLevel.LOW: 0.0,
        RiskLevel.MEDIUM: 0.18,
        RiskLevel.HIGH: 0.38,
        RiskLevel.PROHIBITED: 1.0,
    }[assessment.risk]
    reversibility_bonus = {
        Reversibility.FULL: 0.08,
        Reversibility.PARTIAL: 0.03,
        Reversibility.NONE: 0.0,
    }[assessment.reversibility]
    cost_penalty = min(candidate.estimated_cost, 1.0) * 0.12
    raw = (
        assessment.confidence * 0.62
        + (1.0 - assessment.impact) * 0.18
        + reversibility_bonus
        - risk_penalty
        - cost_penalty
    )
    return round(_clamp(raw), 6)


def _selection_disposition(policy: DecisionPolicy) -> DecisionDisposition:
    if policy.simulation_mode:
        return DecisionDisposition.SIMULATE
    if policy.autonomy_level is AutonomyLevel.OBSERVE_ONLY:
        return DecisionDisposition.OBSERVE
    return DecisionDisposition.RECOMMEND


def _blocked_reference(
    candidates: tuple[ActionCandidate, ...],
    assessments: tuple[RiskAssessment, ...],
) -> tuple[ActionCandidate, RiskAssessment]:
    assessment_by_id = {item.candidate_id: item for item in assessments}
    candidate = candidates[0]
    return candidate, assessment_by_id[candidate.candidate_id]


def _candidate_index(
    candidates: tuple[ActionCandidate, ...],
    candidate_id: str,
) -> int:
    return next(
        index
        for index, candidate in enumerate(candidates)
        if candidate.candidate_id == candidate_id
    )


def _validate_candidate_assessment_alignment(
    candidates: tuple[ActionCandidate, ...],
    assessments: tuple[RiskAssessment, ...],
) -> None:
    candidate_ids = tuple(item.candidate_id for item in candidates)
    assessment_ids = tuple(item.candidate_id for item in assessments)
    if len(set(candidate_ids)) != len(candidate_ids):
        raise ValueError("decision candidates must have unique ids")
    if len(set(assessment_ids)) != len(assessment_ids):
        raise ValueError("decision assessments must be unique per candidate")
    if set(candidate_ids) != set(assessment_ids):
        raise ValueError("decision requires one assessment per candidate")


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def _has_text(value: str | None) -> bool:
    return value is not None and bool(value.strip())


def _require_text(value: str | None, label: str) -> None:
    if not _has_text(value):
        raise ValueError(f"{label} must not be blank")


def _require_items(values: tuple[str, ...], label: str) -> None:
    if not values or any(not item.strip() for item in values):
        raise ValueError(f"{label} must contain non-blank items")


def _require_unit_interval(value: float, label: str) -> None:
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{label} must be between 0.0 and 1.0")
