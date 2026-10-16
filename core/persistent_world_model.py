from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from hashlib import sha256

from core.cognitive_maturity.epistemic import EpistemicLevel


class PersistentWorldDomain(StrEnum):
    USER = "user"
    RELATIONSHIPS = "relationships"
    MEMORY = "memory"
    HOUSEHOLD = "household"
    ENVIRONMENT = "environment"


class PersistentWorldStatus(StrEnum):
    COMPLETE = "complete"
    EMPTY = "empty"
    CONFLICT_REVIEW_REQUIRED = "conflict_review_required"
    DEGRADED = "degraded"


PERSISTENT_WORLD_SOURCE_AUTHORITIES = (
    "personal_identity_profile",
    "relationship_memory",
    "canonical_memory",
    "household_memory",
)


@dataclass(frozen=True)
class PersistentWorldFact:
    fact_id: str
    domain: PersistentWorldDomain
    fact_key: str
    value: str
    source_authority: str
    source_reference: str
    epistemic_level: EpistemicLevel
    evidence_codes: tuple[str, ...]
    persisted_by_source: bool
    active: bool = True
    source_updated_at: datetime | None = None

    def __post_init__(self) -> None:
        for value, label in (
            (self.fact_id, "fact id"),
            (self.fact_key, "fact key"),
            (self.value, "fact value"),
            (self.source_authority, "source authority"),
            (self.source_reference, "source reference"),
        ):
            if not value.strip():
                raise ValueError(f"persistent world {label} must not be blank")
        if self.source_authority not in PERSISTENT_WORLD_SOURCE_AUTHORITIES:
            raise ValueError("persistent world source authority is not governed")
        if not self.persisted_by_source:
            raise ValueError("persistent world facts require a persistent source")
        if any(not code.strip() for code in self.evidence_codes):
            raise ValueError("persistent world evidence codes must not be blank")
        if self.source_updated_at is not None and self.source_updated_at.tzinfo is None:
            raise ValueError("persistent world timestamps must be timezone-aware")


@dataclass(frozen=True)
class PersistentWorldSnapshot:
    snapshot_id: str
    status: PersistentWorldStatus
    facts: tuple[PersistentWorldFact, ...]
    source_authorities: tuple[str, ...]
    evidence_codes: tuple[str, ...]
    conflict_keys: tuple[str, ...]
    risk_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "m391.2"
    canonical_authority: str = "internal_world_model"
    read_only: bool = True
    persistence_added: bool = False
    duplicates_storage: bool = False
    modifies_source_data: bool = False
    grants_authority: bool = False
    infers_missing_facts: bool = False
    resolves_conflicts: bool = False
    runtime_behavior_changed: bool = False
    starts_background_process: bool = False

    def __post_init__(self) -> None:
        if not self.snapshot_id.startswith("persistent-world-"):
            raise ValueError("persistent world snapshot identifier is invalid")
        if self.canonical_authority != "internal_world_model":
            raise ValueError("persistent world must preserve canonical authority")
        if tuple(sorted(self.facts, key=_fact_sort_key)) != self.facts:
            raise ValueError("persistent world facts must use canonical ordering")
        if tuple(sorted(set(self.source_authorities))) != self.source_authorities:
            raise ValueError("persistent world sources must be unique and ordered")
        if any(
            (
                not self.read_only,
                self.persistence_added,
                self.duplicates_storage,
                self.modifies_source_data,
                self.grants_authority,
                self.infers_missing_facts,
                self.resolves_conflicts,
                self.runtime_behavior_changed,
                self.starts_background_process,
            )
        ):
            raise ValueError("persistent world snapshot violates governed limits")

    def facts_for(
        self,
        domain: PersistentWorldDomain | str,
        *,
        active_only: bool = True,
    ) -> tuple[PersistentWorldFact, ...]:
        normalized = PersistentWorldDomain(domain)
        return tuple(
            fact
            for fact in self.facts
            if fact.domain is normalized and (fact.active or not active_only)
        )


class PersistentWorldModelView:
    """Pure governed view over facts persisted by existing authorities."""

    CANONICAL_AUTHORITY = "internal_world_model"

    def build(
        self,
        facts: tuple[PersistentWorldFact, ...] = (),
    ) -> PersistentWorldSnapshot:
        ordered = tuple(sorted(facts, key=_fact_sort_key))
        conflicts = self._conflict_keys(ordered)
        status = self._status(ordered, conflicts)
        source_authorities = tuple(
            sorted({fact.source_authority for fact in ordered})
        )
        evidence_codes = tuple(
            dict.fromkeys(
                code
                for fact in ordered
                for code in (
                    f"source:{fact.source_authority}",
                    f"epistemic:{fact.epistemic_level.value}",
                    *fact.evidence_codes,
                )
            )
        )
        risk_codes = tuple(
            [f"world_conflict:{key}" for key in conflicts]
            + (["persistent_world_empty"] if not ordered else [])
        )
        fingerprint = _fingerprint(ordered, conflicts)
        return PersistentWorldSnapshot(
            snapshot_id=f"persistent-world-{fingerprint[:16]}",
            status=status,
            facts=ordered,
            source_authorities=source_authorities,
            evidence_codes=evidence_codes,
            conflict_keys=conflicts,
            risk_codes=risk_codes,
            source_fingerprint=fingerprint,
        )

    @staticmethod
    def _conflict_keys(
        facts: tuple[PersistentWorldFact, ...],
    ) -> tuple[str, ...]:
        fact_values: dict[str, set[str]] = {}
        for fact in facts:
            if not fact.active or fact.epistemic_level is not EpistemicLevel.FACT:
                continue
            key = f"{fact.domain.value}:{fact.fact_key}"
            fact_values.setdefault(key, set()).add(fact.value.strip())
        return tuple(
            sorted(key for key, values in fact_values.items() if len(values) > 1)
        )

    @staticmethod
    def _status(
        facts: tuple[PersistentWorldFact, ...],
        conflicts: tuple[str, ...],
    ) -> PersistentWorldStatus:
        if conflicts:
            return PersistentWorldStatus.CONFLICT_REVIEW_REQUIRED
        if not facts:
            return PersistentWorldStatus.EMPTY
        return PersistentWorldStatus.COMPLETE


def _fact_sort_key(fact: PersistentWorldFact) -> tuple[str, str, str, str]:
    return (
        fact.domain.value,
        fact.fact_key.casefold(),
        fact.source_authority,
        fact.fact_id,
    )


def _fingerprint(
    facts: tuple[PersistentWorldFact, ...],
    conflicts: tuple[str, ...],
) -> str:
    payload = "\n".join(
        (
            *(
                "|".join(
                    (
                        fact.fact_id,
                        fact.domain.value,
                        fact.fact_key,
                        fact.value,
                        fact.source_authority,
                        fact.source_reference,
                        fact.epistemic_level.value,
                        ",".join(fact.evidence_codes),
                        str(fact.active),
                        (
                            fact.source_updated_at.isoformat()
                            if fact.source_updated_at is not None
                            else ""
                        ),
                    )
                )
                for fact in facts
            ),
            *(f"conflict:{key}" for key in conflicts),
        )
    )
    return sha256(payload.encode("utf-8")).hexdigest()
