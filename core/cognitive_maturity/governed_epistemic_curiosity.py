from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256


class EpistemicCuriositySourceKind(StrEnum):
    """Governed evidence origins; source ownership remains external."""

    CONVERSATION = "conversation"
    AUDIO = "audio"
    VISUAL = "visual"
    WORLD_MODEL = "world_model"
    MEMORY = "memory"
    ORGANIZATION = "organization"
    REASONING = "reasoning"
    EXTERNAL_EVIDENCE = "external_evidence"
    OTHER = "other"


class EpistemicCuriosityQuestionKind(StrEnum):
    CLARIFICATION = "clarification"
    LEARNING = "learning"
    HYPOTHESIS_CHECK = "hypothesis_check"


class EpistemicCuriosityRelevance(StrEnum):
    RELEVANT = "relevant"
    NOT_RELEVANT = "not_relevant"
    UNKNOWN = "unknown"


class EpistemicCuriosityOutcome(StrEnum):
    NO_GAP = "no_gap"
    GAP_NOT_RELEVANT = "gap_not_relevant"
    QUESTION_CANDIDATE = "question_candidate"
    ABSTAIN = "abstain"


@dataclass(frozen=True)
class MultisourceKnowledgeGapEvidence:
    """Structured evidence of something ROBY does not sufficiently understand."""

    subject: str
    source_kind: EpistemicCuriositySourceKind
    source_reference: str
    known_elements: tuple[str, ...]
    unknown_element: str | None
    evidence_codes: tuple[str, ...]
    relevance: EpistemicCuriosityRelevance
    target_person: str | None = None
    hypothesis: str | None = None
    prior_question_reference: str | None = None

    def __post_init__(self) -> None:
        if not self.subject.strip() or not self.source_reference.strip():
            raise ValueError(
                "curiosity evidence requires subject and source provenance"
            )
        if not self.evidence_codes:
            raise ValueError("curiosity evidence requires explicit evidence codes")
        if any(
            not value.strip() for value in self.known_elements + self.evidence_codes
        ):
            raise ValueError("curiosity evidence strings cannot be empty")
        if self.unknown_element is not None and not self.unknown_element.strip():
            raise ValueError("unknown element cannot be blank")
        if self.target_person is not None and not self.target_person.strip():
            raise ValueError("target person cannot be blank")
        if self.hypothesis is not None and not self.hypothesis.strip():
            raise ValueError("hypothesis cannot be blank")
        if (
            self.prior_question_reference is not None
            and not self.prior_question_reference.strip()
        ):
            raise ValueError("prior question reference cannot be blank")


@dataclass(frozen=True)
class GovernedEpistemicQuestionCandidate:
    question_id: str
    subject: str
    question_kind: EpistemicCuriosityQuestionKind
    question: str
    target_person: str | None
    source_kind: EpistemicCuriositySourceKind
    source_reference: str
    unknown_element: str
    evidence_codes: tuple[str, ...]
    source_fingerprint: str
    read_only: bool = True
    persists_results: bool = False
    creates_memory: bool = False
    creates_learning_candidate: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if not self.question_id.startswith("epistemic-question-"):
            raise ValueError("question candidate identifier is invalid")
        if not self.question.strip() or not self.unknown_element.strip():
            raise ValueError("question candidate requires explicit missing knowledge")
        if not self.read_only or any(
            (
                self.persists_results,
                self.creates_memory,
                self.creates_learning_candidate,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError(
                "question candidate must remain read-only and non-authoritative"
            )


@dataclass(frozen=True)
class GovernedEpistemicCuriosityReport:
    report_id: str
    outcome: EpistemicCuriosityOutcome
    source_kind: EpistemicCuriositySourceKind
    source_reference: str
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    question_candidate: GovernedEpistemicQuestionCandidate | None = None
    schema_version: str = "post-m409.1-curiosity-v1"
    read_only: bool = True
    multisource: bool = True
    persists_results: bool = False
    creates_memory: bool = False
    creates_learning_candidate: bool = False
    modifies_knowledge: bool = False
    starts_background_process: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if not self.report_id.startswith("epistemic-curiosity-report-"):
            raise ValueError("curiosity report identifier is invalid")
        has_question = self.question_candidate is not None
        if has_question is not (
            self.outcome is EpistemicCuriosityOutcome.QUESTION_CANDIDATE
        ):
            raise ValueError("question candidate must match curiosity outcome")
        if (
            not self.read_only
            or not self.multisource
            or any(
                (
                    self.persists_results,
                    self.creates_memory,
                    self.creates_learning_candidate,
                    self.modifies_knowledge,
                    self.starts_background_process,
                    self.executes_actions,
                    self.grants_authority,
                )
            )
        ):
            raise ValueError("curiosity foundation violates governed v1 limits")


class GovernedEpistemicCuriosityFoundation:
    """Pure multisource knowledge-gap to question-candidate composition."""

    def evaluate(
        self,
        evidence: MultisourceKnowledgeGapEvidence,
    ) -> GovernedEpistemicCuriosityReport:
        fingerprint = self._fingerprint(evidence)

        if evidence.unknown_element is None:
            return self._report(
                evidence,
                fingerprint,
                EpistemicCuriosityOutcome.NO_GAP,
                ("no_explicit_knowledge_gap",),
            )
        if evidence.prior_question_reference is not None:
            return self._report(
                evidence,
                fingerprint,
                EpistemicCuriosityOutcome.ABSTAIN,
                ("repeat_question_suppressed",),
            )
        if evidence.relevance is EpistemicCuriosityRelevance.NOT_RELEVANT:
            return self._report(
                evidence,
                fingerprint,
                EpistemicCuriosityOutcome.GAP_NOT_RELEVANT,
                ("explicit_gap_not_relevant",),
            )
        if evidence.relevance is EpistemicCuriosityRelevance.UNKNOWN:
            return self._report(
                evidence,
                fingerprint,
                EpistemicCuriosityOutcome.ABSTAIN,
                ("relevance_not_yet_governed",),
            )

        kind = (
            EpistemicCuriosityQuestionKind.HYPOTHESIS_CHECK
            if evidence.hypothesis is not None
            else (
                EpistemicCuriosityQuestionKind.CLARIFICATION
                if not evidence.known_elements
                else EpistemicCuriosityQuestionKind.LEARNING
            )
        )
        question = self._question(evidence, kind)
        question_fingerprint = sha256(
            repr((fingerprint, kind.value, question)).encode("utf-8")
        ).hexdigest()
        candidate = GovernedEpistemicQuestionCandidate(
            question_id=f"epistemic-question-{question_fingerprint[:16]}",
            subject=evidence.subject,
            question_kind=kind,
            question=question,
            target_person=evidence.target_person,
            source_kind=evidence.source_kind,
            source_reference=evidence.source_reference,
            unknown_element=evidence.unknown_element,
            evidence_codes=evidence.evidence_codes,
            source_fingerprint=question_fingerprint,
        )
        return self._report(
            evidence,
            fingerprint,
            EpistemicCuriosityOutcome.QUESTION_CANDIDATE,
            ("explicit_gap", "explicit_relevance", "governed_question_candidate"),
            candidate,
        )

    @staticmethod
    def _question(
        evidence: MultisourceKnowledgeGapEvidence,
        kind: EpistemicCuriosityQuestionKind,
    ) -> str:
        target = f"{evidence.target_person}, " if evidence.target_person else ""
        if kind is EpistemicCuriosityQuestionKind.HYPOTHESIS_CHECK:
            return (
                f"{target}quiero comprobar una hipótesis sobre {evidence.subject}: "
                f"{evidence.hypothesis}. ¿Podés explicarme "
                f"{evidence.unknown_element}?"
            )
        if kind is EpistemicCuriosityQuestionKind.CLARIFICATION:
            return (
                f"{target}no entiendo suficientemente {evidence.subject}. "
                f"¿Podés explicarme {evidence.unknown_element}?"
            )
        return (
            f"{target}hay algo sobre {evidence.subject} que todavía no entiendo. "
            f"¿Podés explicarme {evidence.unknown_element}?"
        )

    @staticmethod
    def _fingerprint(evidence: MultisourceKnowledgeGapEvidence) -> str:
        return sha256(
            repr(
                (
                    evidence.subject,
                    evidence.source_kind.value,
                    evidence.source_reference,
                    evidence.known_elements,
                    evidence.unknown_element,
                    evidence.evidence_codes,
                    evidence.relevance.value,
                    evidence.target_person,
                    evidence.hypothesis,
                    evidence.prior_question_reference,
                )
            ).encode("utf-8")
        ).hexdigest()

    @staticmethod
    def _report(
        evidence: MultisourceKnowledgeGapEvidence,
        fingerprint: str,
        outcome: EpistemicCuriosityOutcome,
        rationale_codes: tuple[str, ...],
        candidate: GovernedEpistemicQuestionCandidate | None = None,
    ) -> GovernedEpistemicCuriosityReport:
        return GovernedEpistemicCuriosityReport(
            report_id=f"epistemic-curiosity-report-{fingerprint[:16]}",
            outcome=outcome,
            source_kind=evidence.source_kind,
            source_reference=evidence.source_reference,
            rationale_codes=rationale_codes,
            source_fingerprint=fingerprint,
            question_candidate=candidate,
        )
