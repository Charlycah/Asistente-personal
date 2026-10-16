from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
from typing import Protocol

from core.governed_reasoning.cross_domain_concept_synthesis import (
    GovernedCrossDomainConceptSynthesisCandidate,
)
from core.governed_reasoning.evidence import EvidenceReference, EvidenceRegistry
from core.governed_reasoning.hierarchical_concept_composition import (
    CanonicalProductiveConceptEpisode,
)


class SemanticDomainAdmissionStatus(StrEnum):
    ADMITTED = "admitted"
    REJECTED = "rejected"


@dataclass(frozen=True)
class SemanticDomainAdmissionResult:
    status: SemanticDomainAdmissionStatus
    owner: str
    session_id: str
    turn_id: str
    evidence_id: str
    concept_episode_id: str | None
    domain_reference: str | None
    synthesis_candidate: GovernedCrossDomainConceptSynthesisCandidate | None
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "cap-19-semantic-domain-admission-v1"
    canonical_reasoning_authority: str = "governed_reasoning"
    persists: bool = False
    creates_memory: bool = False
    creates_learning: bool = False
    modifies_world_model: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        required = (
            self.owner,
            self.session_id,
            self.turn_id,
            self.evidence_id,
            self.source_fingerprint,
        )
        if any(not value.strip() for value in required):
            raise ValueError("semantic-domain admission requires complete lineage")
        if not self.rationale_codes:
            raise ValueError("semantic-domain admission requires rationale")
        if self.canonical_reasoning_authority != "governed_reasoning":
            raise ValueError("semantic-domain admission authority mismatch")
        if any(
            (
                self.persists,
                self.creates_memory,
                self.creates_learning,
                self.modifies_world_model,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("semantic-domain admission violates governed limits")
        if self.status is SemanticDomainAdmissionStatus.ADMITTED and (
            self.concept_episode_id is None or self.domain_reference is None
        ):
            raise ValueError("admitted semantic domain requires concept and domain")


class ProductiveCrossDomainBindingGateway(Protocol):
    def productive_concept_episode(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
    ) -> CanonicalProductiveConceptEpisode | None: ...

    def bind_productive_cross_domain_concept(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
        domain_reference: str,
        concept_episode: CanonicalProductiveConceptEpisode,
    ) -> GovernedCrossDomainConceptSynthesisCandidate | None: ...


class SemanticDomainAdmissionCrossDomainBinding:
    """Admit explicit governed domain evidence into the existing CAP-19 binding."""

    DOMAIN_METADATA_KEY = "semantic_domain"
    SESSION_METADATA_KEY = "session_id"
    CONCEPT_METADATA_KEY = "concept_episode_id"

    def __init__(
        self,
        *,
        evidence_registry: EvidenceRegistry,
        reasoning_gateway: ProductiveCrossDomainBindingGateway,
    ) -> None:
        self._evidence_registry = evidence_registry
        self._reasoning_gateway = reasoning_gateway

    def admit(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
        evidence_id: str,
    ) -> SemanticDomainAdmissionResult:
        normalized_owner = owner.strip()
        normalized_session = session_id.strip()
        normalized_turn = turn_id.strip()
        normalized_evidence_id = evidence_id.strip()
        if any(
            not value
            for value in (
                normalized_owner,
                normalized_session,
                normalized_turn,
                normalized_evidence_id,
            )
        ):
            raise ValueError(
                "semantic-domain admission requires complete request lineage"
            )

        evidence = self._evidence_registry.get(normalized_evidence_id)
        if evidence is None:
            return self._rejected(
                owner=normalized_owner,
                session_id=normalized_session,
                turn_id=normalized_turn,
                evidence_id=normalized_evidence_id,
                rationale="semantic_domain_admission:registered_evidence_required",
            )
        concept = self._reasoning_gateway.productive_concept_episode(
            owner=normalized_owner,
            session_id=normalized_session,
            turn_id=normalized_turn,
        )
        if concept is None:
            return self._rejected(
                owner=normalized_owner,
                session_id=normalized_session,
                turn_id=normalized_turn,
                evidence_id=evidence.evidence_id,
                rationale="semantic_domain_admission:productive_concept_required",
                evidence=evidence,
            )
        metadata = self._metadata(evidence)
        domain = metadata.get(self.DOMAIN_METADATA_KEY, "").strip()
        evidence_session = metadata.get(self.SESSION_METADATA_KEY, "").strip()
        evidence_concept = metadata.get(self.CONCEPT_METADATA_KEY, "").strip()
        if not domain or not evidence_session or not evidence_concept:
            return self._rejected(
                owner=normalized_owner,
                session_id=normalized_session,
                turn_id=normalized_turn,
                evidence_id=evidence.evidence_id,
                rationale=(
                    "semantic_domain_admission:"
                    "explicit_structured_domain_evidence_required"
                ),
                evidence=evidence,
                concept=concept,
            )
        if evidence.owner.casefold() not in {normalized_owner.casefold(), "shared"}:
            return self._rejected(
                owner=normalized_owner,
                session_id=normalized_session,
                turn_id=normalized_turn,
                evidence_id=evidence.evidence_id,
                rationale="semantic_domain_admission:evidence_owner_mismatch",
                evidence=evidence,
                concept=concept,
                domain=domain,
            )
        if (
            evidence_session != normalized_session
            or evidence_concept != concept.episode_id
        ):
            return self._rejected(
                owner=normalized_owner,
                session_id=normalized_session,
                turn_id=normalized_turn,
                evidence_id=evidence.evidence_id,
                rationale="semantic_domain_admission:evidence_concept_lineage_mismatch",
                evidence=evidence,
                concept=concept,
                domain=domain,
            )

        synthesis = self._reasoning_gateway.bind_productive_cross_domain_concept(
            owner=normalized_owner,
            session_id=normalized_session,
            turn_id=normalized_turn,
            domain_reference=domain,
            concept_episode=concept,
        )
        return self._result(
            status=SemanticDomainAdmissionStatus.ADMITTED,
            owner=normalized_owner,
            session_id=normalized_session,
            turn_id=normalized_turn,
            evidence_id=evidence.evidence_id,
            concept=concept,
            domain=domain,
            synthesis=synthesis,
            rationale=(
                "semantic_domain_admission:registered_evidence",
                "semantic_domain_admission:explicit_structured_domain",
                "semantic_domain_admission:concept_lineage_preserved",
                "semantic_domain_admission:existing_cross_domain_binding_reused",
            ),
            evidence=evidence,
        )

    @staticmethod
    def _metadata(evidence: EvidenceReference) -> dict[str, str]:
        metadata: dict[str, str] = {}
        for key, value in evidence.metadata:
            if key in metadata and metadata[key] != value:
                return {}
            metadata[key] = value
        return metadata

    def _rejected(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
        evidence_id: str,
        rationale: str,
        evidence: EvidenceReference | None = None,
        concept: CanonicalProductiveConceptEpisode | None = None,
        domain: str | None = None,
    ) -> SemanticDomainAdmissionResult:
        return self._result(
            status=SemanticDomainAdmissionStatus.REJECTED,
            owner=owner,
            session_id=session_id,
            turn_id=turn_id,
            evidence_id=evidence_id,
            concept=concept,
            domain=domain,
            synthesis=None,
            rationale=(rationale,),
            evidence=evidence,
        )

    @staticmethod
    def _result(
        *,
        status: SemanticDomainAdmissionStatus,
        owner: str,
        session_id: str,
        turn_id: str,
        evidence_id: str,
        concept: CanonicalProductiveConceptEpisode | None,
        domain: str | None,
        synthesis: GovernedCrossDomainConceptSynthesisCandidate | None,
        rationale: tuple[str, ...],
        evidence: EvidenceReference | None,
    ) -> SemanticDomainAdmissionResult:
        fingerprint = sha256(
            repr(
                (
                    owner.casefold(),
                    session_id,
                    turn_id,
                    evidence_id,
                    evidence.fingerprint if evidence is not None else "missing",
                    concept.episode_id if concept is not None else "missing",
                    domain.casefold() if domain is not None else "missing",
                    status.value,
                    rationale,
                )
            ).encode("utf-8")
        ).hexdigest()
        return SemanticDomainAdmissionResult(
            status=status,
            owner=owner,
            session_id=session_id,
            turn_id=turn_id,
            evidence_id=evidence_id,
            concept_episode_id=concept.episode_id if concept is not None else None,
            domain_reference=domain,
            synthesis_candidate=synthesis,
            rationale_codes=rationale,
            source_fingerprint=fingerprint,
        )
