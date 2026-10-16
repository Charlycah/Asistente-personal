from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any

from .canonical_cognitive_state_facade import CanonicalCognitiveStateFacade
from .canonical_decision_facade import CanonicalDecisionFacade
from .canonical_memory_facade import CanonicalMemoryFacade
from .canonical_planning_facade import CanonicalPlanningFacade
from .canonical_reflection_facade import CanonicalReflectionFacade


class CanonicalCognitiveCoreDomain(StrEnum):
    MEMORY = "memory"
    PLANNING = "planning"
    DECISION = "decision"
    STATE = "state"
    REFLECTION = "reflection"


@dataclass(frozen=True)
class CanonicalCognitiveCoreComponent:
    domain: CanonicalCognitiveCoreDomain
    facade: str
    schema_version: str
    primary: str
    bound: bool
    observational: bool
    execution_authority: bool
    purpose: str


@dataclass(frozen=True)
class CanonicalCognitiveCoreSnapshot:
    schema_version: str
    components: tuple[CanonicalCognitiveCoreComponent, ...]

    def component_for(
        self,
        domain: CanonicalCognitiveCoreDomain,
    ) -> CanonicalCognitiveCoreComponent:
        return next(
            component for component in self.components if component.domain is domain
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "components": [asdict(component) for component in self.components],
        }


class CanonicalCognitiveCore:
    """Read-only coordinator for the five canonical cognitive facades.

    This core does not replace domain authorities or execute cognitive work. It
    only exposes one stable observability boundary over the canonical facades.
    """

    SCHEMA_VERSION = "m343.0"

    def __init__(
        self,
        *,
        memory: CanonicalMemoryFacade,
        planning: CanonicalPlanningFacade,
        decision: CanonicalDecisionFacade,
        state: CanonicalCognitiveStateFacade,
        reflection: CanonicalReflectionFacade,
    ) -> None:
        self._facades = {
            CanonicalCognitiveCoreDomain.MEMORY: memory,
            CanonicalCognitiveCoreDomain.PLANNING: planning,
            CanonicalCognitiveCoreDomain.DECISION: decision,
            CanonicalCognitiveCoreDomain.STATE: state,
            CanonicalCognitiveCoreDomain.REFLECTION: reflection,
        }
        self._validate()

    @property
    def snapshot(self) -> CanonicalCognitiveCoreSnapshot:
        purposes = {
            CanonicalCognitiveCoreDomain.MEMORY: (
                "Memoria oficial y sus implementaciones subordinadas."
            ),
            CanonicalCognitiveCoreDomain.PLANNING: (
                "Planificación ejecutiva gobernada y sus colaboradores."
            ),
            CanonicalCognitiveCoreDomain.DECISION: (
                "Coordinación de decisión final y motores consultivos."
            ),
            CanonicalCognitiveCoreDomain.STATE: (
                "Estado cognitivo persistible y proyecciones derivadas."
            ),
            CanonicalCognitiveCoreDomain.REFLECTION: (
                "Reflexión residente y motores especializados subordinados."
            ),
        }
        components = tuple(
            CanonicalCognitiveCoreComponent(
                domain=domain,
                facade=f"{facade.__class__.__module__}:{facade.__class__.__name__}",
                schema_version=facade.snapshot.schema_version,
                primary=facade.snapshot.primary,
                bound=facade.bound,
                observational=True,
                execution_authority=False,
                purpose=purposes[domain],
            )
            for domain, facade in self._facades.items()
        )
        return CanonicalCognitiveCoreSnapshot(
            schema_version=self.SCHEMA_VERSION,
            components=components,
        )

    def facade_for(self, domain: CanonicalCognitiveCoreDomain):
        return self._facades[domain]

    def _validate(self) -> None:
        expected = set(CanonicalCognitiveCoreDomain)
        actual = set(self._facades)
        if actual != expected:
            raise ValueError("canonical cognitive core must expose all five domains")

        identities = [id(facade) for facade in self._facades.values()]
        if len(identities) != len(set(identities)):
            raise ValueError("canonical cognitive facades must be distinct instances")

        for domain, facade in self._facades.items():
            snapshot = facade.snapshot
            if not snapshot.primary:
                raise ValueError(f"canonical {domain.value} facade needs a primary")
            if not snapshot.schema_version:
                raise ValueError(
                    f"canonical {domain.value} facade needs a schema version"
                )
