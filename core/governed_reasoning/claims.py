from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable
from uuid import uuid4

from core.governed_reasoning.evidence import EvidenceReference, EvidenceStatus


class ClaimType(str, Enum):
    """Naturaleza semántica de una afirmación registrable."""

    FACT = "fact"
    OBSERVATION = "observation"
    RULE_RESULT = "rule_result"
    ASSUMPTION = "assumption"
    HYPOTHESIS = "hypothesis"
    ABSENCE_OF_EVIDENCE = "absence_of_evidence"
    CONFLICT_STATEMENT = "conflict_statement"


class ClaimOrigin(str, Enum):
    """Procedencia de creación del claim, separada de su verdad."""

    EVIDENCE = "evidence"
    HUMAN = "human"
    RULE = "rule"
    SYSTEM = "system"


class ClaimStatus(str, Enum):
    """Estado de evaluación y ciclo de vida del claim."""

    PROPOSED = "proposed"
    SUPPORTED = "supported"
    CORROBORATED = "corroborated"
    DISPUTED = "disputed"
    REFUTED = "refuted"
    STALE = "stale"
    SUPERSEDED = "superseded"
    REVIEW_REQUIRED = "review_required"


class EvidenceLinkRole(str, Enum):
    """Papel explícito de una evidencia respecto de un claim."""

    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    CONTEXT = "context"


@dataclass(frozen=True)
class ClaimConfidence:
    """Confianza declarada simple; M81 incorporará el cálculo multifactorial."""

    score: float
    rationale: str

    def __post_init__(self) -> None:
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("claim confidence must be between zero and one")
        if not self.rationale.strip():
            raise ValueError("claim confidence rationale must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {"score": self.score, "rationale": self.rationale}


@dataclass(frozen=True)
class ClaimEvidenceLink:
    """Enlace inmutable a una versión concreta de evidencia M77."""

    evidence_id: str
    role: EvidenceLinkRole | str
    source_type: str
    source_id: str
    evidence_fingerprint: str

    def __post_init__(self) -> None:
        EvidenceLinkRole(self.role)
        if not self.evidence_id.strip():
            raise ValueError("claim evidence id must not be empty")
        if not self.source_type.strip() or not self.source_id.strip():
            raise ValueError("claim evidence provenance must not be empty")
        if len(self.evidence_fingerprint) != 64:
            raise ValueError("claim evidence fingerprint must be SHA-256")

    @classmethod
    def from_reference(
        cls,
        reference: EvidenceReference,
        *,
        role: EvidenceLinkRole | str = EvidenceLinkRole.SUPPORTS,
    ) -> ClaimEvidenceLink:
        return cls(
            evidence_id=reference.evidence_id,
            role=role,
            source_type=reference.normalized_source_type.value,
            source_id=reference.source_id,
            evidence_fingerprint=reference.fingerprint,
        )

    @property
    def normalized_role(self) -> EvidenceLinkRole:
        return EvidenceLinkRole(self.role)

    def to_dict(self) -> dict[str, str]:
        return {
            "evidence_id": self.evidence_id,
            "role": self.normalized_role.value,
            "source_type": self.source_type,
            "source_id": self.source_id,
            "evidence_fingerprint": self.evidence_fingerprint,
        }


@dataclass(frozen=True)
class Claim:
    """Afirmación inmutable y evaluable, distinta de evidencia e inferencia."""

    subject: str
    predicate: str
    object_value: str
    claim_type: ClaimType | str
    origin: ClaimOrigin | str
    status: ClaimStatus | str = ClaimStatus.PROPOSED
    evidence_links: tuple[ClaimEvidenceLink, ...] = ()
    confidence: ClaimConfidence | None = None
    owner: str = "shared"
    rule_reference: str | None = None
    supersedes: str | None = None
    valid_from: datetime | None = None
    valid_until: datetime | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    claim_id: str = field(default_factory=lambda: uuid4().hex)
    revision: int = 1

    def __post_init__(self) -> None:
        claim_type = ClaimType(self.claim_type)
        origin = ClaimOrigin(self.origin)
        status = ClaimStatus(self.status)
        for value, name in (
            (self.subject, "subject"),
            (self.predicate, "predicate"),
            (self.object_value, "object"),
            (self.owner, "owner"),
            (self.claim_id, "id"),
        ):
            if not value.strip():
                raise ValueError(f"claim {name} must not be empty")
        if self.created_at.tzinfo is None:
            raise ValueError("claim creation timestamp must be timezone-aware")
        for timestamp in (self.valid_from, self.valid_until):
            if timestamp is not None and timestamp.tzinfo is None:
                raise ValueError("claim validity timestamps must be timezone-aware")
        if self.valid_from and self.valid_until and self.valid_until < self.valid_from:
            raise ValueError("claim validity end cannot precede start")
        if self.revision < 1:
            raise ValueError("claim revision must be positive")
        if self.rule_reference is not None and not self.rule_reference.strip():
            raise ValueError("claim rule reference must not be blank")
        if self.supersedes is not None and not self.supersedes.strip():
            raise ValueError("claim superseded reference must not be blank")
        evidence_ids = [link.evidence_id for link in self.evidence_links]
        if len(evidence_ids) != len(set(evidence_ids)):
            raise ValueError("claim must not repeat evidence links")
        supporting = tuple(
            link
            for link in self.evidence_links
            if link.normalized_role is EvidenceLinkRole.SUPPORTS
        )
        if claim_type in {ClaimType.FACT, ClaimType.OBSERVATION} and not supporting:
            raise ValueError(
                "factual and observational claims require supporting evidence"
            )
        if claim_type is ClaimType.RULE_RESULT:
            if origin is not ClaimOrigin.RULE or not self.rule_reference:
                raise ValueError("rule-result claims require rule origin and reference")
        elif self.rule_reference is not None:
            raise ValueError("only rule-result claims may declare a rule reference")
        if origin is ClaimOrigin.RULE and claim_type is not ClaimType.RULE_RESULT:
            raise ValueError("rule origin is reserved for rule-result claims")
        if (
            status in {ClaimStatus.SUPPORTED, ClaimStatus.CORROBORATED}
            and not supporting
        ):
            raise ValueError("supported claims require supporting evidence")
        if status is ClaimStatus.CORROBORATED and len(supporting) < 2:
            raise ValueError(
                "corroborated claims require at least two supporting evidences"
            )
        if claim_type is ClaimType.ABSENCE_OF_EVIDENCE and supporting:
            raise ValueError(
                "absence of evidence cannot use supporting evidence as proof"
            )

    @property
    def normalized_type(self) -> ClaimType:
        return ClaimType(self.claim_type)

    @property
    def normalized_origin(self) -> ClaimOrigin:
        return ClaimOrigin(self.origin)

    @property
    def normalized_status(self) -> ClaimStatus:
        return ClaimStatus(self.status)

    @property
    def fingerprint(self) -> str:
        links = "|".join(
            f"{link.evidence_id}:{link.normalized_role.value}"
            for link in sorted(self.evidence_links, key=lambda item: item.evidence_id)
        )
        payload = "|".join(
            (
                self.subject.strip().casefold(),
                self.predicate.strip().casefold(),
                self.object_value.strip().casefold(),
                self.normalized_type.value,
                self.normalized_origin.value,
                self.owner.strip().casefold(),
                links,
                self.rule_reference or "",
            )
        )
        return sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.claim_id,
            "revision": self.revision,
            "subject": self.subject,
            "predicate": self.predicate,
            "object": self.object_value,
            "type": self.normalized_type.value,
            "origin": self.normalized_origin.value,
            "status": self.normalized_status.value,
            "owner": self.owner,
            "evidence_links": [link.to_dict() for link in self.evidence_links],
            "confidence": self.confidence.to_dict() if self.confidence else None,
            "rule_reference": self.rule_reference,
            "supersedes": self.supersedes,
            "valid_from": self.valid_from.isoformat() if self.valid_from else None,
            "valid_until": self.valid_until.isoformat() if self.valid_until else None,
            "created_at": self.created_at.isoformat(),
            "fingerprint": self.fingerprint,
        }


@runtime_checkable
class ClaimRepository(Protocol):
    """Contrato de persistencia para claims y su historial inmutable."""

    def save(self, claim: Claim) -> Claim: ...

    def get(self, claim_id: str) -> Claim | None: ...

    def get_by_fingerprint(self, fingerprint: str) -> Claim | None: ...

    def list_all(self) -> tuple[Claim, ...]: ...

    def list_history(self, claim_id: str) -> tuple[Claim, ...]: ...


class InMemoryClaimRepository:
    """Repositorio determinista que conserva cada revisión del claim."""

    def __init__(self) -> None:
        self._current: dict[str, Claim] = {}
        self._history: dict[str, list[Claim]] = {}
        self._fingerprints: dict[str, str] = {}

    def save(self, claim: Claim) -> Claim:
        current = self._current.get(claim.claim_id)
        if current is not None and claim.revision != current.revision + 1:
            raise ValueError("claim revision must advance exactly by one")
        if current is None and claim.revision != 1:
            raise ValueError("new claims must start at revision one")
        duplicate_id = self._fingerprints.get(claim.fingerprint)
        if duplicate_id is not None and duplicate_id != claim.claim_id:
            raise ValueError("duplicate claim fingerprint")
        self._current[claim.claim_id] = claim
        self._history.setdefault(claim.claim_id, []).append(claim)
        self._fingerprints[claim.fingerprint] = claim.claim_id
        return claim

    def get(self, claim_id: str) -> Claim | None:
        return self._current.get(claim_id)

    def get_by_fingerprint(self, fingerprint: str) -> Claim | None:
        claim_id = self._fingerprints.get(fingerprint)
        return self._current.get(claim_id) if claim_id else None

    def list_all(self) -> tuple[Claim, ...]:
        return tuple(sorted(self._current.values(), key=_claim_sort_key))

    def list_history(self, claim_id: str) -> tuple[Claim, ...]:
        return tuple(self._history.get(claim_id, ()))


class ClaimRegistryManager:
    """Registra, consulta y versiona claims sin ejecutar inferencias."""

    def __init__(self, repository: ClaimRepository | None = None) -> None:
        self.repository = repository or InMemoryClaimRepository()

    def register(self, claim: Claim) -> Claim:
        return self.repository.save(claim)

    def register_from_evidence(
        self,
        *,
        subject: str,
        predicate: str,
        object_value: str,
        claim_type: ClaimType | str,
        evidence: tuple[EvidenceReference, ...],
        owner: str = "shared",
        confidence: ClaimConfidence | None = None,
        created_at: datetime | None = None,
    ) -> Claim:
        links = tuple(
            ClaimEvidenceLink.from_reference(reference)
            for reference in sorted(
                evidence,
                key=lambda item: (item.normalized_source_type.value, item.source_id),
            )
        )
        status = ClaimStatus.CORROBORATED if len(links) >= 2 else ClaimStatus.SUPPORTED
        if any(
            reference.normalized_status is EvidenceStatus.REVIEW_REQUIRED
            for reference in evidence
        ):
            status = ClaimStatus.REVIEW_REQUIRED
        claim = Claim(
            subject=subject,
            predicate=predicate,
            object_value=object_value,
            claim_type=claim_type,
            origin=ClaimOrigin.EVIDENCE,
            status=status,
            evidence_links=links,
            confidence=confidence,
            owner=owner,
            created_at=created_at or datetime.now(timezone.utc),
        )
        return self.register(claim)

    def revise_status(
        self,
        claim_id: str,
        status: ClaimStatus | str,
        *,
        confidence: ClaimConfidence | None = None,
        created_at: datetime | None = None,
    ) -> Claim:
        current = self._require(claim_id)
        revised = replace(
            current,
            status=ClaimStatus(status),
            confidence=confidence if confidence is not None else current.confidence,
            created_at=created_at or datetime.now(timezone.utc),
            revision=current.revision + 1,
        )
        return self.repository.save(revised)

    def supersede(
        self,
        claim_id: str,
        replacement: Claim,
        *,
        created_at: datetime | None = None,
    ) -> tuple[Claim, Claim]:
        current = self._require(claim_id)
        if replacement.claim_id == current.claim_id:
            raise ValueError("replacement claim must have a different id")
        replacement_with_link = replace(replacement, supersedes=current.claim_id)
        saved_replacement = self.register(replacement_with_link)
        superseded = replace(
            current,
            status=ClaimStatus.SUPERSEDED,
            created_at=created_at or datetime.now(timezone.utc),
            revision=current.revision + 1,
        )
        return self.repository.save(superseded), saved_replacement

    def get(self, claim_id: str) -> Claim | None:
        return self.repository.get(claim_id)

    def find_duplicate(self, claim: Claim) -> Claim | None:
        return self.repository.get_by_fingerprint(claim.fingerprint)

    def list_all(
        self,
        *,
        owner: str | None = None,
        status: ClaimStatus | str | None = None,
        claim_type: ClaimType | str | None = None,
    ) -> tuple[Claim, ...]:
        claims = self.repository.list_all()
        if owner is not None:
            claims = tuple(item for item in claims if item.owner == owner)
        if status is not None:
            normalized_status = ClaimStatus(status)
            claims = tuple(
                item for item in claims if item.normalized_status is normalized_status
            )
        if claim_type is not None:
            normalized_type = ClaimType(claim_type)
            claims = tuple(
                item for item in claims if item.normalized_type is normalized_type
            )
        return claims

    def history(self, claim_id: str) -> tuple[Claim, ...]:
        return self.repository.list_history(claim_id)

    def _require(self, claim_id: str) -> Claim:
        claim = self.repository.get(claim_id)
        if claim is None:
            raise KeyError(f"claim not found: {claim_id}")
        return claim


def _claim_sort_key(claim: Claim) -> tuple[str, str, str, str]:
    return (
        claim.owner.casefold(),
        claim.subject.casefold(),
        claim.predicate.casefold(),
        claim.claim_id,
    )
