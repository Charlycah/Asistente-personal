from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any

from .cognitive_authority_map import CognitiveAuthorityMap
from .cognitive_operational_inventory import CognitiveAuthority


class CognitiveCyclePhase(StrEnum):
    ENTRY = "entry"
    CONTEXT = "context"
    MEMORY = "memory"
    KNOWLEDGE = "knowledge"
    REASONING = "reasoning"
    PLANNING = "planning"
    DECISION = "decision"
    GOVERNANCE = "governance"
    EXECUTION = "execution"
    REFLECTION = "reflection"
    OBSERVABILITY = "observability"
    RESPONSE = "response"


class CognitiveCycleParticipation(StrEnum):
    REQUIRED = "required"
    CONDITIONAL = "conditional"
    CONSULTATIVE = "consultative"
    OBSERVATIONAL = "observational"
    BOUNDARY = "boundary"


@dataclass(frozen=True)
class CognitiveCycleStage:
    sequence: int
    phase: CognitiveCyclePhase
    authority: CognitiveAuthority
    primary: str
    participation: CognitiveCycleParticipation
    purpose: str


@dataclass(frozen=True)
class CanonicalCognitiveCycleSnapshot:
    schema_version: str
    stages: tuple[CognitiveCycleStage, ...]

    def stage_for(self, phase: CognitiveCyclePhase) -> CognitiveCycleStage:
        return next(stage for stage in self.stages if stage.phase is phase)

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "stages": [asdict(stage) for stage in self.stages],
        }


_CYCLE_DEFINITION: tuple[
    tuple[
        CognitiveCyclePhase,
        CognitiveAuthority,
        CognitiveCycleParticipation,
        str,
    ],
    ...,
] = (
    (
        CognitiveCyclePhase.ENTRY,
        CognitiveAuthority.ENTRY,
        CognitiveCycleParticipation.BOUNDARY,
        "Aceptar el turno por la única frontera conversacional oficial.",
    ),
    (
        CognitiveCyclePhase.CONTEXT,
        CognitiveAuthority.CONTEXT,
        CognitiveCycleParticipation.REQUIRED,
        "Restituir la continuidad contextual aplicable al turno.",
    ),
    (
        CognitiveCyclePhase.MEMORY,
        CognitiveAuthority.MEMORY,
        CognitiveCycleParticipation.CONDITIONAL,
        "Consultar memoria únicamente cuando el turno la requiera.",
    ),
    (
        CognitiveCyclePhase.KNOWLEDGE,
        CognitiveAuthority.KNOWLEDGE,
        CognitiveCycleParticipation.CONSULTATIVE,
        "Aportar conocimiento sin adquirir autoridad de ejecución.",
    ),
    (
        CognitiveCyclePhase.REASONING,
        CognitiveAuthority.REASONING,
        CognitiveCycleParticipation.REQUIRED,
        "Producir razonamiento gobernado para el turno.",
    ),
    (
        CognitiveCyclePhase.PLANNING,
        CognitiveAuthority.PLANNING,
        CognitiveCycleParticipation.CONDITIONAL,
        "Construir un plan sólo cuando la solicitud lo necesite.",
    ),
    (
        CognitiveCyclePhase.DECISION,
        CognitiveAuthority.DECISION,
        CognitiveCycleParticipation.REQUIRED,
        "Resolver la coordinación cognitiva y la estrategia del turno.",
    ),
    (
        CognitiveCyclePhase.GOVERNANCE,
        CognitiveAuthority.GOVERNANCE,
        CognitiveCycleParticipation.REQUIRED,
        "Aplicar políticas antes de cualquier capacidad ejecutable.",
    ),
    (
        CognitiveCyclePhase.EXECUTION,
        CognitiveAuthority.EXECUTION,
        CognitiveCycleParticipation.CONDITIONAL,
        "Orquestar capacidades registradas cuando la decisión lo autorice.",
    ),
    (
        CognitiveCyclePhase.REFLECTION,
        CognitiveAuthority.REFLECTION,
        CognitiveCycleParticipation.CONSULTATIVE,
        "Aportar evaluación reflexiva acotada sin reabrir la decisión.",
    ),
    (
        CognitiveCyclePhase.OBSERVABILITY,
        CognitiveAuthority.OBSERVABILITY,
        CognitiveCycleParticipation.OBSERVATIONAL,
        "Exponer el estado operacional sin intervenir en el turno.",
    ),
    (
        CognitiveCyclePhase.RESPONSE,
        CognitiveAuthority.ENTRY,
        CognitiveCycleParticipation.BOUNDARY,
        "Devolver la respuesta por la misma frontera oficial.",
    ),
)


class CanonicalCognitiveCycle:
    """Read-only ordering of official cognitive authorities for one turn."""

    SCHEMA_VERSION = "m342.3"

    def __init__(self, *, authority_map: CognitiveAuthorityMap | None = None) -> None:
        self._authority_map = authority_map or CognitiveAuthorityMap()
        self._stages = self._build_stages()
        self._validate()

    @property
    def snapshot(self) -> CanonicalCognitiveCycleSnapshot:
        return CanonicalCognitiveCycleSnapshot(
            schema_version=self.SCHEMA_VERSION,
            stages=self._stages,
        )

    def _build_stages(self) -> tuple[CognitiveCycleStage, ...]:
        authority_snapshot = self._authority_map.snapshot
        return tuple(
            CognitiveCycleStage(
                sequence=index,
                phase=phase,
                authority=authority,
                primary=authority_snapshot.authority_for(authority).primary,
                participation=participation,
                purpose=purpose,
            )
            for index, (phase, authority, participation, purpose) in enumerate(
                _CYCLE_DEFINITION,
                start=1,
            )
        )

    def _validate(self) -> None:
        sequences = tuple(stage.sequence for stage in self._stages)
        phases = tuple(stage.phase for stage in self._stages)

        if sequences != tuple(range(1, len(self._stages) + 1)):
            raise ValueError("cognitive cycle stages must be sequential")
        if len(phases) != len(set(phases)):
            raise ValueError("cognitive cycle phases must be unique")
        if phases[0] is not CognitiveCyclePhase.ENTRY:
            raise ValueError("cognitive cycle must begin at entry")
        if phases[-1] is not CognitiveCyclePhase.RESPONSE:
            raise ValueError("cognitive cycle must end at response")

        covered = {stage.authority for stage in self._stages}
        if covered != set(CognitiveAuthority):
            raise ValueError("cognitive cycle must cover every authority")

        authority_snapshot = self._authority_map.snapshot
        for stage in self._stages:
            expected = authority_snapshot.authority_for(stage.authority).primary
            if stage.primary != expected:
                raise ValueError(
                    f"cycle stage {stage.phase.value} does not use official authority"
                )
