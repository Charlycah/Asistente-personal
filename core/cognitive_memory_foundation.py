from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class CognitiveMemoryKind(StrEnum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    LONG_TERM = "long_term"


class CognitiveMemoryPersistence(StrEnum):
    TRANSIENT = "transient"
    CONSOLIDATABLE = "consolidatable"
    PERSISTENT = "persistent"


class CognitiveMemoryWriteMode(StrEnum):
    OBSERVED = "observed"
    EXPLICIT_ACCEPTANCE = "explicit_acceptance"
    GOVERNED_CONSOLIDATION = "governed_consolidation"


@dataclass(frozen=True)
class CognitiveMemoryDomain:
    kind: CognitiveMemoryKind
    purpose: str
    authority_key: str
    persistence: CognitiveMemoryPersistence
    write_mode: CognitiveMemoryWriteMode
    stores_personal_data: bool
    operational: bool = False

    def __post_init__(self) -> None:
        if not self.purpose.strip():
            raise ValueError("cognitive memory purpose must not be blank")
        if not self.authority_key.strip():
            raise ValueError("cognitive memory authority key must not be blank")
        if self.operational:
            raise ValueError(
                "M366.1 cognitive memory domains must remain non-operational"
            )


@dataclass(frozen=True)
class CognitiveMemoryFoundationSnapshot:
    schema_version: str
    canonical_authority: str
    domains: tuple[CognitiveMemoryDomain, ...]
    persistence_enabled: bool
    automatic_learning_enabled: bool

    def domain_for(self, kind: CognitiveMemoryKind | str) -> CognitiveMemoryDomain:
        normalized = CognitiveMemoryKind(kind)
        return next(domain for domain in self.domains if domain.kind is normalized)
