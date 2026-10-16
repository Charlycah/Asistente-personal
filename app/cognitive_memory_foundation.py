from __future__ import annotations

from app.canonical_memory_facade import CanonicalMemoryFacade
from core.cognitive_memory_foundation import (
    CognitiveMemoryDomain,
    CognitiveMemoryFoundationSnapshot,
    CognitiveMemoryKind,
    CognitiveMemoryPersistence,
    CognitiveMemoryWriteMode,
)

COGNITIVE_MEMORY_DOMAINS: tuple[CognitiveMemoryDomain, ...] = (
    CognitiveMemoryDomain(
        kind=CognitiveMemoryKind.EPISODIC,
        purpose="Conservar experiencias cognitivas situadas y trazables.",
        authority_key="episodic_memory",
        persistence=CognitiveMemoryPersistence.CONSOLIDATABLE,
        write_mode=CognitiveMemoryWriteMode.GOVERNED_CONSOLIDATION,
        stores_personal_data=True,
    ),
    CognitiveMemoryDomain(
        kind=CognitiveMemoryKind.SEMANTIC,
        purpose="Representar conocimiento estable, revisable y con procedencia.",
        authority_key="memory_gateway",
        persistence=CognitiveMemoryPersistence.PERSISTENT,
        write_mode=CognitiveMemoryWriteMode.EXPLICIT_ACCEPTANCE,
        stores_personal_data=True,
    ),
    CognitiveMemoryDomain(
        kind=CognitiveMemoryKind.PROCEDURAL,
        purpose="Representar procedimientos aprobados sin ejecutarlos.",
        authority_key="memory_gateway",
        persistence=CognitiveMemoryPersistence.PERSISTENT,
        write_mode=CognitiveMemoryWriteMode.EXPLICIT_ACCEPTANCE,
        stores_personal_data=False,
    ),
    CognitiveMemoryDomain(
        kind=CognitiveMemoryKind.LONG_TERM,
        purpose="Gobernar la consolidación durable de recuerdos autorizados.",
        authority_key="memory_gateway",
        persistence=CognitiveMemoryPersistence.PERSISTENT,
        write_mode=CognitiveMemoryWriteMode.GOVERNED_CONSOLIDATION,
        stores_personal_data=True,
    ),
)


class CognitiveMemoryFoundation:
    """Governed taxonomy over ROBY's existing canonical memory authority."""

    SCHEMA_VERSION = "m366.1"

    def __init__(
        self, *, canonical_memory: CanonicalMemoryFacade | None = None
    ) -> None:
        self._canonical_memory = canonical_memory or CanonicalMemoryFacade()
        self._validate()

    @property
    def snapshot(self) -> CognitiveMemoryFoundationSnapshot:
        return CognitiveMemoryFoundationSnapshot(
            schema_version=self.SCHEMA_VERSION,
            canonical_authority=self._canonical_memory.snapshot.primary,
            domains=COGNITIVE_MEMORY_DOMAINS,
            persistence_enabled=False,
            automatic_learning_enabled=False,
        )

    def _validate(self) -> None:
        kinds = [domain.kind for domain in COGNITIVE_MEMORY_DOMAINS]
        if len(kinds) != len(set(kinds)):
            raise ValueError("cognitive memory kinds must be unique")
        if set(kinds) != set(CognitiveMemoryKind):
            raise ValueError("cognitive memory foundation must declare every kind")

        component_keys = {
            component.key for component in self._canonical_memory.snapshot.components
        }
        for domain in COGNITIVE_MEMORY_DOMAINS:
            if domain.authority_key not in component_keys:
                raise ValueError(
                    f"unknown canonical memory authority: {domain.authority_key}"
                )
