from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

_SCHEMA_VERSION = "cih-2dh-longitudinal-intellectual-identity-v1"


class LongitudinalIntellectualIdentityStatus(StrEnum):
    SAME = "same"
    DISTINCT = "distinct"
    AMBIGUOUS = "ambiguous"
    INSUFFICIENT = "insufficient"


@dataclass(frozen=True)
class GovernedLongitudinalIntellectualIdentityAssessment:
    """Bounded, consultative assessment of intellectual continuity."""

    assessment_id: str
    status: LongitudinalIntellectualIdentityStatus
    current_artifact_reference: str
    candidate_artifact_reference: str
    evidence_references: tuple[str, ...]
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = _SCHEMA_VERSION
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    consultative: bool = True
    transient: bool = True
    persists: bool = False
    creates_facts: bool = False
    establishes_truth: bool = False
    establishes_causality: bool = False
    creates_learning: bool = False
    modifies_memory: bool = False
    modifies_world_model: bool = False
    creates_topic_identity: bool = False
    opens_investigation: bool = False
    authorizes_inference: bool = False
    authorizes_revision: bool = False
    creates_initiative: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if not self.assessment_id.startswith("longitudinal-intellectual-identity-"):
            raise ValueError("longitudinal identity assessment identifier is invalid")
        if not self.current_artifact_reference.strip():
            raise ValueError(
                "longitudinal identity requires current artifact reference"
            )
        if not self.candidate_artifact_reference.strip():
            raise ValueError(
                "longitudinal identity requires candidate artifact reference"
            )
        if not self.rationale_codes:
            raise ValueError("longitudinal identity requires rationale")
        if len(self.source_fingerprint) != 64:
            raise ValueError("longitudinal identity fingerprint must be SHA-256")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("longitudinal identity authority mismatch")
        if not self.read_only or not self.consultative or not self.transient:
            raise ValueError("longitudinal identity must remain bounded and transient")
        if any(
            (
                self.persists,
                self.creates_facts,
                self.establishes_truth,
                self.establishes_causality,
                self.creates_learning,
                self.modifies_memory,
                self.modifies_world_model,
                self.creates_topic_identity,
                self.opens_investigation,
                self.authorizes_inference,
                self.authorizes_revision,
                self.creates_initiative,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("longitudinal identity violates governed limits")


class GovernedLongitudinalIntellectualIdentityFoundationV1:
    """Assess bounded identity evidence without inferring unsupported continuity."""

    def assess(
        self,
        *,
        current_artifact_reference: str,
        candidate_artifact_reference: str,
        identity_evidence_references: tuple[str, ...] = (),
        shared_intellectual_subject_evidence_references: tuple[str, ...] = (),
        directed_prior_state_evidence_references: tuple[str, ...] = (),
        relational_evidence_references: tuple[str, ...] = (),
    ) -> GovernedLongitudinalIntellectualIdentityAssessment:
        current_reference = current_artifact_reference.strip()
        candidate_reference = candidate_artifact_reference.strip()
        if not current_reference or not candidate_reference:
            raise ValueError("longitudinal identity requires artifact references")

        identity_evidence = self._normalize_references(identity_evidence_references)
        shared_subject_evidence = self._normalize_references(
            shared_intellectual_subject_evidence_references
        )
        directed_prior_state_evidence = self._normalize_references(
            directed_prior_state_evidence_references
        )
        relational_evidence = self._normalize_references(relational_evidence_references)
        evidence_references = (
            identity_evidence
            + shared_subject_evidence
            + directed_prior_state_evidence
            + relational_evidence
        )

        positive_same_composition = bool(
            shared_subject_evidence
            and directed_prior_state_evidence
            and relational_evidence
        )
        if positive_same_composition:
            status = LongitudinalIntellectualIdentityStatus.SAME
            rationale_codes = (
                "longitudinal_identity:positive_same_composition_satisfied",
            )
        elif not evidence_references:
            status = LongitudinalIntellectualIdentityStatus.INSUFFICIENT
            rationale_codes = (
                "longitudinal_identity:identity_evidence_required",
            )
        else:
            status = LongitudinalIntellectualIdentityStatus.INSUFFICIENT
            rationale_codes = (
                "longitudinal_identity:positive_same_composition_incomplete",
            )
        payload = repr(
            (
                _SCHEMA_VERSION,
                current_reference,
                candidate_reference,
                identity_evidence,
                shared_subject_evidence,
                directed_prior_state_evidence,
                relational_evidence,
                status.value,
                rationale_codes,
            )
        )
        fingerprint = sha256(payload.encode("utf-8")).hexdigest()
        return GovernedLongitudinalIntellectualIdentityAssessment(
            assessment_id=f"longitudinal-intellectual-identity-{fingerprint[:24]}",
            status=status,
            current_artifact_reference=current_reference,
            candidate_artifact_reference=candidate_reference,
            evidence_references=evidence_references,
            rationale_codes=rationale_codes,
            source_fingerprint=fingerprint,
        )

    @staticmethod
    def _normalize_references(references: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(reference.strip() for reference in references)
        if any(not reference for reference in normalized):
            raise ValueError(
                "longitudinal identity evidence references must be non-empty"
            )
        return normalized
