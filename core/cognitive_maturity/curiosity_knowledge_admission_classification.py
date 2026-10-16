from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from .curiosity_human_answer_evidence import (
    CuriosityKnowledgeCandidate,
    HumanAnswerKind,
)
from .epistemic import EpistemicLevel


class CuriosityAdmissionTarget(StrEnum):
    KNOWLEDGE = "knowledge"
    MEMORY = "memory"
    KNOWLEDGE_AND_MEMORY = "knowledge_and_memory"
    REVIEW_REQUIRED = "review_required"
    REJECT = "reject"


@dataclass(frozen=True)
class CuriosityAdmissionContext:
    """Explicit routing hints supplied by existing governed context."""

    durable_generalizable: bool
    contextual_provenance_worth_remembering: bool
    sensitive_or_personal: bool = False
    conflicts_with_existing_knowledge: bool = False

    def __post_init__(self) -> None:
        if self.sensitive_or_personal and self.durable_generalizable:
            raise ValueError(
                "sensitive or personal evidence cannot be auto-routed "
                "as general knowledge"
            )


@dataclass(frozen=True)
class CuriosityKnowledgeAdmissionClassification:
    classification_id: str
    candidate_id: str
    target: CuriosityAdmissionTarget
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    question_id: str
    human_answer_reference: str
    speaker: str
    epistemic_level: EpistemicLevel
    schema_version: str = "post-m409.1-curiosity-admission-class-v1"
    read_only: bool = True
    persists_results: bool = False
    writes_memory: bool = False
    writes_knowledge: bool = False
    creates_learning_candidate: bool = False
    invokes_learning: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if not self.classification_id.startswith("curiosity-admission-class-"):
            raise ValueError("admission classification identifier is invalid")
        if not self.rationale_codes:
            raise ValueError("admission classification requires rationale")
        if not self.read_only or any(
            (
                self.persists_results,
                self.writes_memory,
                self.writes_knowledge,
                self.creates_learning_candidate,
                self.invokes_learning,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("admission classification violates governed v1 limits")


class CuriosityKnowledgeCandidateAdmissionClassificationFoundation:
    """Pure classification of intended admission destination; performs no admission."""

    def classify(
        self,
        candidate: CuriosityKnowledgeCandidate,
        context: CuriosityAdmissionContext,
    ) -> CuriosityKnowledgeAdmissionClassification:
        target, rationale = self._target(candidate, context)
        fingerprint = sha256(
            repr(
                (
                    candidate.source_fingerprint,
                    candidate.candidate_id,
                    target.value,
                    rationale,
                    context,
                )
            ).encode("utf-8")
        ).hexdigest()
        return CuriosityKnowledgeAdmissionClassification(
            classification_id=f"curiosity-admission-class-{fingerprint[:16]}",
            candidate_id=candidate.candidate_id,
            target=target,
            rationale_codes=rationale,
            source_fingerprint=fingerprint,
            question_id=candidate.question_id,
            human_answer_reference=candidate.human_answer_reference,
            speaker=candidate.speaker,
            epistemic_level=candidate.epistemic_level,
        )

    @staticmethod
    def _target(
        candidate: CuriosityKnowledgeCandidate,
        context: CuriosityAdmissionContext,
    ) -> tuple[CuriosityAdmissionTarget, tuple[str, ...]]:
        if candidate.answer_kind is HumanAnswerKind.CORRECTION:
            return (
                CuriosityAdmissionTarget.REVIEW_REQUIRED,
                ("correction_requires_existing_knowledge_review",),
            )
        if context.conflicts_with_existing_knowledge:
            return (
                CuriosityAdmissionTarget.REVIEW_REQUIRED,
                ("conflict_requires_review",),
            )
        if candidate.epistemic_level is not EpistemicLevel.FACT:
            return (
                CuriosityAdmissionTarget.REVIEW_REQUIRED,
                ("non_fact_candidate_requires_review",),
            )
        if context.sensitive_or_personal:
            if context.contextual_provenance_worth_remembering:
                return (
                    CuriosityAdmissionTarget.MEMORY,
                    ("personal_or_sensitive_routes_to_memory_review_path",),
                )
            return (
                CuriosityAdmissionTarget.REVIEW_REQUIRED,
                ("personal_or_sensitive_requires_explicit_review",),
            )
        if (
            context.durable_generalizable
            and context.contextual_provenance_worth_remembering
        ):
            return (
                CuriosityAdmissionTarget.KNOWLEDGE_AND_MEMORY,
                ("durable_fact", "context_provenance_worth_remembering"),
            )
        if context.durable_generalizable:
            return (
                CuriosityAdmissionTarget.KNOWLEDGE,
                ("durable_fact",),
            )
        if context.contextual_provenance_worth_remembering:
            return (
                CuriosityAdmissionTarget.MEMORY,
                ("context_provenance_worth_remembering",),
            )
        return (
            CuriosityAdmissionTarget.REJECT,
            ("no_governed_admission_value",),
        )
