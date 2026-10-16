from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any, Protocol


class ReflectionAuthority(Protocol):
    def reflect(self, *args: Any, **kwargs: Any) -> Any: ...


class CanonicalReflectionRole(StrEnum):
    PRIMARY = "primary"
    COLLABORATOR = "collaborator"
    SPECIALIZED = "specialized"
    OBSERVER = "observer"
    LEGACY = "legacy"


class CanonicalReflectionOperation(StrEnum):
    REFLECT = "reflect"
    CONTRIBUTE = "contribute"
    REVIEW = "review"
    OBSERVE = "observe"
    ASSESS = "assess"


@dataclass(frozen=True)
class CanonicalReflectionComponent:
    key: str
    path: str
    role: CanonicalReflectionRole
    operations: tuple[CanonicalReflectionOperation, ...]
    operational: bool
    purpose: str


@dataclass(frozen=True)
class CanonicalReflectionSnapshot:
    schema_version: str
    primary: str
    components: tuple[CanonicalReflectionComponent, ...]

    def component_for(self, key: str) -> CanonicalReflectionComponent:
        return next(component for component in self.components if component.key == key)

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "primary": self.primary,
            "components": [asdict(component) for component in self.components],
        }


CANONICAL_REFLECTION_COMPONENTS: tuple[CanonicalReflectionComponent, ...] = (
    CanonicalReflectionComponent(
        key="cognitive_core_resident",
        path="app.cognitive_core_runtime:CognitiveCoreRuntime",
        role=CanonicalReflectionRole.PRIMARY,
        operations=(CanonicalReflectionOperation.REFLECT,),
        operational=True,
        purpose="Única autoridad residente para la reflexión cognitiva oficial.",
    ),
    CanonicalReflectionComponent(
        key="adaptive_cognition",
        path="app.adaptive_cognition_runtime:OfficialAdaptiveCognitionRuntimeGateway",
        role=CanonicalReflectionRole.COLLABORATOR,
        operations=(CanonicalReflectionOperation.CONTRIBUTE,),
        operational=True,
        purpose="Aporta evaluación adaptativa consultiva sin autoridad final.",
    ),
    CanonicalReflectionComponent(
        key="resident_reflection_engine",
        path="app.cognitive_reflection_engine:CognitiveReflectionEngine",
        role=CanonicalReflectionRole.SPECIALIZED,
        operations=(CanonicalReflectionOperation.REVIEW,),
        operational=False,
        purpose="Revisa el foco de agenda sin mutar estado autoritativo.",
    ),
    CanonicalReflectionComponent(
        key="metacognitive_reflection_engine",
        path="core.reflection:ReflectionEngine",
        role=CanonicalReflectionRole.SPECIALIZED,
        operations=(CanonicalReflectionOperation.ASSESS,),
        operational=False,
        purpose="Produce resultados metacognitivos determinísticos y auditables.",
    ),
    CanonicalReflectionComponent(
        key="reflection_runtime_contributor",
        path="core.reflection_runtime_integration:ReflectionRuntimeContributor",
        role=CanonicalReflectionRole.OBSERVER,
        operations=(CanonicalReflectionOperation.OBSERVE,),
        operational=False,
        purpose="Proyecta reflexión consultiva sin reescribir decisiones.",
    ),
    CanonicalReflectionComponent(
        key="controlled_autonomy_self_reflection",
        path="core.controlled_autonomy.self_reflection:SelfReflectionEngine",
        role=CanonicalReflectionRole.SPECIALIZED,
        operations=(CanonicalReflectionOperation.ASSESS,),
        operational=False,
        purpose="Evalúa resultados dentro de la autonomía controlada.",
    ),
    CanonicalReflectionComponent(
        key="legacy_reflection_contracts",
        path="core.living_conversation.reflection:ConversationReflection",
        role=CanonicalReflectionRole.LEGACY,
        operations=(CanonicalReflectionOperation.REVIEW,),
        operational=False,
        purpose="Contratos históricos conservados para compatibilidad interna.",
    ),
)


class CanonicalReflectionFacade:
    """Single reflection contract over the resident cognitive authority.

    The facade does not schedule reflection or mutate state. When bound, it
    delegates an explicit reflection request to the existing authority.
    """

    SCHEMA_VERSION = "m342.9"
    PRIMARY = "cognitive_core_resident"

    def __init__(self, authority: ReflectionAuthority | None = None) -> None:
        self._authority = authority
        self._validate()

    @property
    def snapshot(self) -> CanonicalReflectionSnapshot:
        return CanonicalReflectionSnapshot(
            schema_version=self.SCHEMA_VERSION,
            primary=self.PRIMARY,
            components=CANONICAL_REFLECTION_COMPONENTS,
        )

    @property
    def bound(self) -> bool:
        return self._authority is not None

    def reflect(self, *args: Any, **kwargs: Any) -> Any:
        return self._require_authority().reflect(*args, **kwargs)

    def _require_authority(self) -> ReflectionAuthority:
        if self._authority is None:
            raise RuntimeError(
                "canonical reflection facade is not bound to an authority"
            )
        return self._authority

    def _validate(self) -> None:
        keys = [component.key for component in CANONICAL_REFLECTION_COMPONENTS]
        if len(keys) != len(set(keys)):
            raise ValueError("canonical reflection component keys must be unique")

        primaries = [
            component
            for component in CANONICAL_REFLECTION_COMPONENTS
            if component.role is CanonicalReflectionRole.PRIMARY
        ]
        if len(primaries) != 1 or primaries[0].key != self.PRIMARY:
            raise ValueError("canonical reflection must declare one official primary")

        for component in CANONICAL_REFLECTION_COMPONENTS:
            if not component.operations:
                raise ValueError(
                    f"reflection component {component.key} needs operations"
                )
            if component.role is CanonicalReflectionRole.OBSERVER:
                if component.operational:
                    raise ValueError("reflection observers cannot be operational")
                if component.operations != (CanonicalReflectionOperation.OBSERVE,):
                    raise ValueError("reflection observers may only observe")
