from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from app.learning_foundation import LearningFoundation
from app.preference_learning import PreferenceLearning
from app.safe_learning_policies import SafeLearningPolicies
from core.cognitive_maturity.curiosity_human_answer_evidence import (
    CuriosityKnowledgeCandidate,
)
from core.learning_foundation import LearningObservation
from core.preference_learning import PreferenceCandidate, PreferenceEvidence
from core.safe_learning_policies import SafeLearningDecision, SafeLearningDisposition


class CuriosityLearningKind(StrEnum):
    NOT_LEARNING_RELEVANT = "not_learning_relevant"
    PREFERENCE = "preference"
    STABLE_KNOWLEDGE = "stable_knowledge"


class CuriosityM369EvaluationOutcome(StrEnum):
    NOT_LEARNING_RELEVANT = "not_learning_relevant"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    REVIEW_REQUIRED = "review_required"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass(frozen=True)
class CuriosityM369EvaluationContext:
    learning_kind: CuriosityLearningKind
    confidence: float
    age_days: int
    contradiction_count: int = 0
    sensitive: bool = False
    consent_present: bool = False

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                "curiosity learning confidence must be between zero and one"
            )
        if self.age_days < 0 or self.contradiction_count < 0:
            raise ValueError("curiosity learning counters must not be negative")


@dataclass(frozen=True)
class CuriosityM369LearningEvaluationReport:
    report_id: str
    outcome: CuriosityM369EvaluationOutcome
    candidate_id: str
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    learning_candidate_id: str | None = None
    preference_candidate: PreferenceCandidate | None = None
    safe_learning_decision: SafeLearningDecision | None = None
    schema_version: str = "post-m409.1-curiosity-m369-evaluation-v1"
    read_only: bool = True
    uses_existing_m369: bool = True
    persists_results: bool = False
    accepts_learning: bool = False
    applies_adaptation: bool = False
    writes_memory: bool = False
    writes_knowledge: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if not self.report_id.startswith("curiosity-m369-evaluation-"):
            raise ValueError("curiosity M369 evaluation identifier is invalid")
        if not self.rationale_codes:
            raise ValueError("curiosity M369 evaluation requires rationale")
        if not self.read_only or not self.uses_existing_m369:
            raise ValueError("curiosity M369 evaluation must reuse read-only M369")
        if any(
            (
                self.persists_results,
                self.accepts_learning,
                self.applies_adaptation,
                self.writes_memory,
                self.writes_knowledge,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("curiosity M369 evaluation violates governed v1 limits")


class CuriosityM369LearningEvaluationFoundation:
    """Bridge curiosity evidence into existing read-only M369 evaluation."""

    def __init__(self) -> None:
        self._learning = LearningFoundation()
        self._preference = PreferenceLearning()
        self._safe_policy = SafeLearningPolicies()

    def evaluate(
        self,
        candidate: CuriosityKnowledgeCandidate,
        context: CuriosityM369EvaluationContext,
        *,
        prior_preference_evidence: tuple[PreferenceEvidence, ...] = (),
    ) -> CuriosityM369LearningEvaluationReport:
        if context.learning_kind is CuriosityLearningKind.NOT_LEARNING_RELEVANT:
            return self._report(
                candidate,
                CuriosityM369EvaluationOutcome.NOT_LEARNING_RELEVANT,
                ("explicitly_not_learning_relevant",),
                context,
            )

        observation = LearningObservation(
            observation_id=f"curiosity-observation-{candidate.candidate_id[-16:]}",
            statement=candidate.statement,
            source="curiosity_human_answer",
            source_reference=candidate.human_answer_reference,
            confidence=context.confidence,
        )
        learning_candidate = self._learning.structure_candidate(
            subject=candidate.subject,
            proposed_value=candidate.statement,
            observations=(observation,),
            confidence=context.confidence,
        )
        current_evidence = PreferenceEvidence.from_learning_candidate(
            learning_candidate
        )
        preference_candidate = self._preference.evaluate(
            evidence=(*prior_preference_evidence, current_evidence),
        )
        policy_candidate = self._policy_candidate(
            preference_candidate,
            context,
        )
        decision = self._safe_policy.evaluate(policy_candidate)
        outcome = self._outcome(decision.disposition)
        return self._report(
            candidate,
            outcome,
            (
                "curiosity_adapted_to_m369_learning_observation",
                "existing_m369_1_candidate_structured",
                "existing_m369_2_preference_evaluated",
                "existing_m369_6_safe_policy_evaluated",
                *decision.explanation_codes,
            ),
            context,
            learning_candidate_id=learning_candidate.candidate_id,
            preference_candidate=preference_candidate,
            safe_learning_decision=decision,
        )

    @staticmethod
    def _policy_candidate(
        preference: PreferenceCandidate,
        context: CuriosityM369EvaluationContext,
    ):
        from core.safe_learning_policies import LearningPolicyCandidate

        return LearningPolicyCandidate(
            candidate_id=preference.preference_id,
            subject=preference.subject,
            evidence_ids=preference.evidence_ids,
            confidence=preference.confidence,
            age_days=context.age_days,
            contradiction_count=context.contradiction_count,
            sensitive=context.sensitive,
            consent_present=context.consent_present,
        )

    @staticmethod
    def _outcome(
        disposition: SafeLearningDisposition,
    ) -> CuriosityM369EvaluationOutcome:
        return CuriosityM369EvaluationOutcome(disposition.value)

    @staticmethod
    def _report(
        candidate: CuriosityKnowledgeCandidate,
        outcome: CuriosityM369EvaluationOutcome,
        rationale_codes: tuple[str, ...],
        context: CuriosityM369EvaluationContext,
        *,
        learning_candidate_id: str | None = None,
        preference_candidate: PreferenceCandidate | None = None,
        safe_learning_decision: SafeLearningDecision | None = None,
    ) -> CuriosityM369LearningEvaluationReport:
        fingerprint = sha256(
            repr(
                (
                    candidate.source_fingerprint,
                    candidate.candidate_id,
                    context,
                    outcome.value,
                    rationale_codes,
                    learning_candidate_id,
                    preference_candidate,
                    safe_learning_decision,
                )
            ).encode("utf-8")
        ).hexdigest()
        return CuriosityM369LearningEvaluationReport(
            report_id=f"curiosity-m369-evaluation-{fingerprint[:16]}",
            outcome=outcome,
            candidate_id=candidate.candidate_id,
            rationale_codes=rationale_codes,
            source_fingerprint=fingerprint,
            learning_candidate_id=learning_candidate_id,
            preference_candidate=preference_candidate,
            safe_learning_decision=safe_learning_decision,
        )
