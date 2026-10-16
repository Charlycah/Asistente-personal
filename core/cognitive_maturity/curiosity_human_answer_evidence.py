from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from .epistemic import EpistemicLevel
from .governed_epistemic_curiosity import (
    EpistemicCuriosityOutcome,
    GovernedEpistemicCuriosityReport,
)


class HumanAnswerKind(StrEnum):
    ANSWER = "answer"
    PARTIAL_ANSWER = "partial_answer"
    UNCERTAIN_ANSWER = "uncertain_answer"
    CORRECTION = "correction"
    NOT_AN_ANSWER = "not_an_answer"


class HumanAnswerOutcome(StrEnum):
    KNOWLEDGE_CANDIDATE = "knowledge_candidate"
    PARTIAL_KNOWLEDGE_CANDIDATE = "partial_knowledge_candidate"
    UNCERTAIN_KNOWLEDGE_CANDIDATE = "uncertain_knowledge_candidate"
    CORRECTION_CANDIDATE = "correction_candidate"
    NOT_AN_ANSWER = "not_an_answer"
    ABSTAIN = "abstain"


@dataclass(frozen=True)
class ExplicitHumanAnswerEvidence:
    """Explicit, exact linkage between a curiosity question and human answer."""

    curiosity_report_id: str
    question_id: str
    human_answer_reference: str
    answer_text: str
    answer_kind: HumanAnswerKind
    speaker: str
    evidence_codes: tuple[str, ...]
    exact_linkage: bool = True

    def __post_init__(self) -> None:
        if not self.curiosity_report_id.startswith("epistemic-curiosity-report-"):
            raise ValueError("human answer requires a curiosity report id")
        if not self.question_id.startswith("epistemic-question-"):
            raise ValueError("human answer requires a curiosity question id")
        if not self.human_answer_reference.strip():
            raise ValueError("human answer requires explicit answer provenance")
        if not self.answer_text.strip() or not self.speaker.strip():
            raise ValueError("human answer requires answer text and speaker")
        if not self.evidence_codes:
            raise ValueError("human answer requires explicit evidence codes")
        if any(not code.strip() for code in self.evidence_codes):
            raise ValueError("human answer evidence codes cannot be blank")


@dataclass(frozen=True)
class CuriosityKnowledgeCandidate:
    candidate_id: str
    statement: str
    subject: str
    speaker: str
    answer_kind: HumanAnswerKind
    epistemic_level: EpistemicLevel
    curiosity_report_id: str
    question_id: str
    human_answer_reference: str
    evidence_codes: tuple[str, ...]
    source_fingerprint: str
    read_only: bool = True
    requires_admission: bool = True
    persists_results: bool = False
    creates_memory: bool = False
    creates_learning_candidate: bool = False
    modifies_knowledge: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if not self.candidate_id.startswith("curiosity-knowledge-candidate-"):
            raise ValueError("knowledge candidate identifier is invalid")
        if not self.statement.strip() or not self.subject.strip():
            raise ValueError("knowledge candidate requires statement and subject")
        if not self.read_only or not self.requires_admission:
            raise ValueError("knowledge candidate must remain pending admission")
        if any(
            (
                self.persists_results,
                self.creates_memory,
                self.creates_learning_candidate,
                self.modifies_knowledge,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("knowledge candidate violates governed v1 limits")


@dataclass(frozen=True)
class CuriosityHumanAnswerReport:
    report_id: str
    outcome: HumanAnswerOutcome
    curiosity_report_id: str
    question_id: str
    human_answer_reference: str
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    knowledge_candidate: CuriosityKnowledgeCandidate | None = None
    schema_version: str = "post-m409.1-curiosity-human-answer-v1"
    read_only: bool = True
    persists_results: bool = False
    creates_memory: bool = False
    creates_learning_candidate: bool = False
    modifies_knowledge: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if not self.report_id.startswith("curiosity-human-answer-report-"):
            raise ValueError("human answer report identifier is invalid")
        has_candidate = self.knowledge_candidate is not None
        candidate_outcomes = {
            HumanAnswerOutcome.KNOWLEDGE_CANDIDATE,
            HumanAnswerOutcome.PARTIAL_KNOWLEDGE_CANDIDATE,
            HumanAnswerOutcome.UNCERTAIN_KNOWLEDGE_CANDIDATE,
            HumanAnswerOutcome.CORRECTION_CANDIDATE,
        }
        if has_candidate is not (self.outcome in candidate_outcomes):
            raise ValueError("candidate presence must match human answer outcome")
        if not self.read_only or any(
            (
                self.persists_results,
                self.creates_memory,
                self.creates_learning_candidate,
                self.modifies_knowledge,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("human answer report violates governed v1 limits")


class CuriosityHumanAnswerEvidenceFoundation:
    """Pure exact-link human-answer to knowledge-candidate composition."""

    def evaluate(
        self,
        curiosity_report: GovernedEpistemicCuriosityReport,
        evidence: ExplicitHumanAnswerEvidence,
    ) -> CuriosityHumanAnswerReport:
        fingerprint = self._fingerprint(curiosity_report, evidence)
        question = curiosity_report.question_candidate
        if (
            curiosity_report.outcome
            is not EpistemicCuriosityOutcome.QUESTION_CANDIDATE
            or question is None
        ):
            return self._report(
                evidence,
                fingerprint,
                HumanAnswerOutcome.ABSTAIN,
                ("source_is_not_question_candidate",),
            )
        if (
            evidence.curiosity_report_id != curiosity_report.report_id
            or evidence.question_id != question.question_id
            or not evidence.exact_linkage
        ):
            return self._report(
                evidence,
                fingerprint,
                HumanAnswerOutcome.ABSTAIN,
                ("exact_question_answer_linkage_required",),
            )
        if evidence.answer_kind is HumanAnswerKind.NOT_AN_ANSWER:
            return self._report(
                evidence,
                fingerprint,
                HumanAnswerOutcome.NOT_AN_ANSWER,
                ("explicitly_not_an_answer",),
            )

        outcome, level, rationale = self._classification(evidence.answer_kind)
        candidate_fingerprint = sha256(
            repr(
                (
                    fingerprint,
                    evidence.answer_text.strip(),
                    outcome.value,
                    level.value,
                )
            ).encode("utf-8")
        ).hexdigest()
        candidate = CuriosityKnowledgeCandidate(
            candidate_id=(
                f"curiosity-knowledge-candidate-{candidate_fingerprint[:16]}"
            ),
            statement=evidence.answer_text.strip(),
            subject=question.subject,
            speaker=evidence.speaker,
            answer_kind=evidence.answer_kind,
            epistemic_level=level,
            curiosity_report_id=curiosity_report.report_id,
            question_id=question.question_id,
            human_answer_reference=evidence.human_answer_reference,
            evidence_codes=evidence.evidence_codes,
            source_fingerprint=candidate_fingerprint,
        )
        return self._report(
            evidence,
            fingerprint,
            outcome,
            rationale,
            candidate,
        )

    @staticmethod
    def _classification(
        kind: HumanAnswerKind,
    ) -> tuple[HumanAnswerOutcome, EpistemicLevel, tuple[str, ...]]:
        if kind is HumanAnswerKind.ANSWER:
            return (
                HumanAnswerOutcome.KNOWLEDGE_CANDIDATE,
                EpistemicLevel.FACT,
                ("explicit_human_answer", "candidate_requires_admission"),
            )
        if kind is HumanAnswerKind.PARTIAL_ANSWER:
            return (
                HumanAnswerOutcome.PARTIAL_KNOWLEDGE_CANDIDATE,
                EpistemicLevel.UNKNOWN,
                ("explicit_partial_answer", "knowledge_gap_may_remain"),
            )
        if kind is HumanAnswerKind.UNCERTAIN_ANSWER:
            return (
                HumanAnswerOutcome.UNCERTAIN_KNOWLEDGE_CANDIDATE,
                EpistemicLevel.HYPOTHESIS,
                ("explicit_uncertain_answer", "fact_promotion_not_allowed"),
            )
        if kind is HumanAnswerKind.CORRECTION:
            return (
                HumanAnswerOutcome.CORRECTION_CANDIDATE,
                EpistemicLevel.UNKNOWN,
                ("explicit_human_correction", "existing_knowledge_review_required"),
            )
        raise ValueError("unsupported human answer kind")

    @staticmethod
    def _fingerprint(
        curiosity_report: GovernedEpistemicCuriosityReport,
        evidence: ExplicitHumanAnswerEvidence,
    ) -> str:
        return sha256(
            repr(
                (
                    curiosity_report.source_fingerprint,
                    evidence.curiosity_report_id,
                    evidence.question_id,
                    evidence.human_answer_reference,
                    evidence.answer_text,
                    evidence.answer_kind.value,
                    evidence.speaker,
                    evidence.evidence_codes,
                    evidence.exact_linkage,
                )
            ).encode("utf-8")
        ).hexdigest()

    @staticmethod
    def _report(
        evidence: ExplicitHumanAnswerEvidence,
        fingerprint: str,
        outcome: HumanAnswerOutcome,
        rationale: tuple[str, ...],
        candidate: CuriosityKnowledgeCandidate | None = None,
    ) -> CuriosityHumanAnswerReport:
        return CuriosityHumanAnswerReport(
            report_id=f"curiosity-human-answer-report-{fingerprint[:16]}",
            outcome=outcome,
            curiosity_report_id=evidence.curiosity_report_id,
            question_id=evidence.question_id,
            human_answer_reference=evidence.human_answer_reference,
            rationale_codes=rationale,
            source_fingerprint=fingerprint,
            knowledge_candidate=candidate,
        )
