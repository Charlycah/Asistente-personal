from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .cognitive_operational_inventory import (
    COGNITIVE_CAPABILITY_INVENTORY,
    CognitiveAuthority,
    CognitiveCapabilityRecord,
    CognitiveCapabilityState,
)


@dataclass(frozen=True)
class CognitiveAuthorityAssignment:
    """Official responsibility assignment without changing runtime behavior."""

    authority: CognitiveAuthority
    primary: str
    collaborators: tuple[str, ...] = ()
    observers: tuple[str, ...] = ()
    shadow: tuple[str, ...] = ()
    rationale: str = ""

    @property
    def referenced_components(self) -> tuple[str, ...]:
        return (
            (self.primary,)
            + self.collaborators
            + self.observers
            + self.shadow
        )


@dataclass(frozen=True)
class CognitiveAuthorityMapSnapshot:
    schema_version: str
    assignments: tuple[CognitiveAuthorityAssignment, ...]

    def authority_for(
        self, authority: CognitiveAuthority
    ) -> CognitiveAuthorityAssignment:
        return next(
            assignment
            for assignment in self.assignments
            if assignment.authority is authority
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "assignments": [asdict(item) for item in self.assignments],
        }


COGNITIVE_AUTHORITY_ASSIGNMENTS: tuple[CognitiveAuthorityAssignment, ...] = (
    CognitiveAuthorityAssignment(
        authority=CognitiveAuthority.ENTRY,
        primary="conversation_entry",
        rationale="Única frontera oficial para aceptar turnos interactivos.",
    ),
    CognitiveAuthorityAssignment(
        authority=CognitiveAuthority.CONTEXT,
        primary="context_continuity",
        rationale="Autoridad para continuidad contextual del runtime oficial.",
    ),
    CognitiveAuthorityAssignment(
        authority=CognitiveAuthority.MEMORY,
        primary="memory_gateway",
        rationale="Única frontera oficial para acceso a memorias especializadas.",
    ),
    CognitiveAuthorityAssignment(
        authority=CognitiveAuthority.KNOWLEDGE,
        primary="knowledge_runtime",
        rationale="Autoridad consultiva para conocimiento dentro del grafo oficial.",
    ),
    CognitiveAuthorityAssignment(
        authority=CognitiveAuthority.REASONING,
        primary="governed_reasoning",
        rationale="Autoridad de razonamiento gobernado extremo a extremo.",
    ),
    CognitiveAuthorityAssignment(
        authority=CognitiveAuthority.PLANNING,
        primary="executive_planning",
        shadow=("cognitive_planner_shadow",),
        rationale=(
            "El planificador ejecutivo mantiene la autoridad; el planificador "
            "cognitivo continúa observando sin intervenir."
        ),
    ),
    CognitiveAuthorityAssignment(
        authority=CognitiveAuthority.DECISION,
        primary="unified_cognitive_coordination",
        collaborators=("executive_director",),
        rationale=(
            "La coordinación unificada posee la autoridad final y el director "
            "ejecutivo aporta señales consultivas."
        ),
    ),
    CognitiveAuthorityAssignment(
        authority=CognitiveAuthority.EXECUTION,
        primary="capability_orchestrator",
        rationale="Única autoridad para orquestar capacidades registradas.",
    ),
    CognitiveAuthorityAssignment(
        authority=CognitiveAuthority.REFLECTION,
        primary="cognitive_core_resident",
        collaborators=("adaptive_cognition",),
        rationale=(
            "El núcleo residente conserva la autoridad y la cognición adaptativa "
            "aporta evaluación consultiva."
        ),
    ),
    CognitiveAuthorityAssignment(
        authority=CognitiveAuthority.GOVERNANCE,
        primary="governed_capability_routing",
        rationale="Autoridad para aplicar políticas al enrutamiento de capacidades.",
    ),
    CognitiveAuthorityAssignment(
        authority=CognitiveAuthority.OBSERVABILITY,
        primary="runtime_observability",
        observers=("conversation_entry",),
        rationale=(
            "La observabilidad unificada es la autoridad; la frontera de "
            "conversación sólo aporta eventos de turno."
        ),
    ),
)


class CognitiveAuthorityMap:
    """Validated, read-only map of one primary authority per responsibility."""

    SCHEMA_VERSION = "m342.2"

    def __init__(
        self,
        *,
        capabilities: tuple[
            CognitiveCapabilityRecord, ...
        ] = COGNITIVE_CAPABILITY_INVENTORY,
        assignments: tuple[
            CognitiveAuthorityAssignment, ...
        ] = COGNITIVE_AUTHORITY_ASSIGNMENTS,
    ) -> None:
        self._capabilities = capabilities
        self._assignments = assignments
        self._validate()

    @property
    def snapshot(self) -> CognitiveAuthorityMapSnapshot:
        return CognitiveAuthorityMapSnapshot(
            schema_version=self.SCHEMA_VERSION,
            assignments=self._assignments,
        )

    def _validate(self) -> None:
        records = {record.key: record for record in self._capabilities}
        assigned = [assignment.authority for assignment in self._assignments]

        if len(assigned) != len(set(assigned)):
            raise ValueError("each cognitive authority must have one assignment")
        if set(assigned) != set(CognitiveAuthority):
            raise ValueError("all cognitive authorities must be assigned")

        for assignment in self._assignments:
            components = assignment.referenced_components
            if len(components) != len(set(components)):
                raise ValueError(
                    f"authority {assignment.authority.value} repeats a component"
                )
            for key in components:
                if key not in records:
                    raise ValueError(f"unknown cognitive component: {key}")

            primary = records[assignment.primary]
            if primary.authority is not assignment.authority:
                raise ValueError(
                    f"primary {primary.key} does not belong to "
                    f"{assignment.authority.value}"
                )
            if not primary.canonical:
                raise ValueError(f"primary {primary.key} must be canonical")

            for key in assignment.shadow:
                if records[key].state is not CognitiveCapabilityState.SHADOW:
                    raise ValueError(f"shadow component {key} must remain shadow")
