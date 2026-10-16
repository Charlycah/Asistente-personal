from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any

from .canonical_cognitive_cycle import (
    CanonicalCognitiveCycle,
    CognitiveCycleParticipation,
    CognitiveCyclePhase,
)
from .cognitive_authority_map import CognitiveAuthorityMap
from .cognitive_operational_inventory import CognitiveAuthority


class CognitiveAdapterKind(StrEnum):
    MEMORY = "memory"
    PLANNING = "planning"
    DECISION = "decision"
    REFLECTION = "reflection"
    OBSERVABILITY = "observability"


class CognitiveAdapterMode(StrEnum):
    REQUEST_RESPONSE = "request_response"
    READ_ONLY = "read_only"
    OBSERVATIONAL = "observational"


@dataclass(frozen=True)
class CognitiveIntegrationRequest:
    adapter: CognitiveAdapterKind
    turn_id: str
    payload: dict[str, Any]


@dataclass(frozen=True)
class CognitiveIntegrationResult:
    adapter: CognitiveAdapterKind
    authority: CognitiveAuthority
    primary: str
    accepted: bool
    payload: dict[str, Any]


@dataclass(frozen=True)
class CognitiveIntegrationAdapter:
    kind: CognitiveAdapterKind
    authority: CognitiveAuthority
    phase: CognitiveCyclePhase
    primary: str
    participation: CognitiveCycleParticipation
    mode: CognitiveAdapterMode
    purpose: str


@dataclass(frozen=True)
class CognitiveIntegrationAdapterSnapshot:
    schema_version: str
    adapters: tuple[CognitiveIntegrationAdapter, ...]

    def adapter_for(
        self, kind: CognitiveAdapterKind
    ) -> CognitiveIntegrationAdapter:
        return next(adapter for adapter in self.adapters if adapter.kind is kind)

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "adapters": [asdict(adapter) for adapter in self.adapters],
        }


_ADAPTER_DEFINITION: tuple[
    tuple[
        CognitiveAdapterKind,
        CognitiveAuthority,
        CognitiveCyclePhase,
        CognitiveAdapterMode,
        str,
    ],
    ...,
] = (
    (
        CognitiveAdapterKind.MEMORY,
        CognitiveAuthority.MEMORY,
        CognitiveCyclePhase.MEMORY,
        CognitiveAdapterMode.REQUEST_RESPONSE,
        "Unificar solicitudes de lectura y escritura de memoria sin elegir "
        "una implementación especializada.",
    ),
    (
        CognitiveAdapterKind.PLANNING,
        CognitiveAuthority.PLANNING,
        CognitiveCyclePhase.PLANNING,
        CognitiveAdapterMode.REQUEST_RESPONSE,
        "Unificar solicitudes de planificación conservando la autoridad "
        "ejecutiva y los planificadores en sombra.",
    ),
    (
        CognitiveAdapterKind.DECISION,
        CognitiveAuthority.DECISION,
        CognitiveCyclePhase.DECISION,
        CognitiveAdapterMode.REQUEST_RESPONSE,
        "Unificar alternativas y resultados de decisión sin competir con "
        "la coordinación cognitiva oficial.",
    ),
    (
        CognitiveAdapterKind.REFLECTION,
        CognitiveAuthority.REFLECTION,
        CognitiveCyclePhase.REFLECTION,
        CognitiveAdapterMode.READ_ONLY,
        "Unificar aportes reflexivos consultivos sin reabrir una decisión "
        "ya resuelta.",
    ),
    (
        CognitiveAdapterKind.OBSERVABILITY,
        CognitiveAuthority.OBSERVABILITY,
        CognitiveCyclePhase.OBSERVABILITY,
        CognitiveAdapterMode.OBSERVATIONAL,
        "Unificar eventos de observabilidad sin intervenir en el turno.",
    ),
)


class CognitiveIntegrationAdapters:
    """Read-only integration contracts over existing cognitive authorities."""

    SCHEMA_VERSION = "m342.4"

    def __init__(
        self,
        *,
        authority_map: CognitiveAuthorityMap | None = None,
        cycle: CanonicalCognitiveCycle | None = None,
    ) -> None:
        self._authority_map = authority_map or CognitiveAuthorityMap()
        self._cycle = cycle or CanonicalCognitiveCycle(
            authority_map=self._authority_map
        )
        self._adapters = self._build_adapters()
        self._validate()

    @property
    def snapshot(self) -> CognitiveIntegrationAdapterSnapshot:
        return CognitiveIntegrationAdapterSnapshot(
            schema_version=self.SCHEMA_VERSION,
            adapters=self._adapters,
        )

    def describe_request(
        self,
        request: CognitiveIntegrationRequest,
    ) -> CognitiveIntegrationResult:
        """Resolve the official destination without invoking any component."""
        adapter = self.snapshot.adapter_for(request.adapter)
        return CognitiveIntegrationResult(
            adapter=adapter.kind,
            authority=adapter.authority,
            primary=adapter.primary,
            accepted=True,
            payload=dict(request.payload),
        )

    def _build_adapters(self) -> tuple[CognitiveIntegrationAdapter, ...]:
        authority_snapshot = self._authority_map.snapshot
        cycle_snapshot = self._cycle.snapshot
        return tuple(
            CognitiveIntegrationAdapter(
                kind=kind,
                authority=authority,
                phase=phase,
                primary=authority_snapshot.authority_for(authority).primary,
                participation=cycle_snapshot.stage_for(phase).participation,
                mode=mode,
                purpose=purpose,
            )
            for kind, authority, phase, mode, purpose in _ADAPTER_DEFINITION
        )

    def _validate(self) -> None:
        kinds = [adapter.kind for adapter in self._adapters]
        authorities = [adapter.authority for adapter in self._adapters]
        phases = [adapter.phase for adapter in self._adapters]

        if len(kinds) != len(set(kinds)):
            raise ValueError("each cognitive adapter kind must be unique")
        if len(authorities) != len(set(authorities)):
            raise ValueError("each cognitive adapter authority must be unique")
        if len(phases) != len(set(phases)):
            raise ValueError("each cognitive adapter phase must be unique")

        authority_snapshot = self._authority_map.snapshot
        cycle_snapshot = self._cycle.snapshot
        for adapter in self._adapters:
            assignment = authority_snapshot.authority_for(adapter.authority)
            stage = cycle_snapshot.stage_for(adapter.phase)
            if adapter.primary != assignment.primary:
                raise ValueError(
                    f"adapter {adapter.kind.value} must use official authority"
                )
            if stage.authority is not adapter.authority:
                raise ValueError(
                    f"adapter {adapter.kind.value} does not match cycle phase"
                )
            if adapter.participation is not stage.participation:
                raise ValueError(
                    f"adapter {adapter.kind.value} participation is inconsistent"
                )
