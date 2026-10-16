from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any, Protocol

from core.governed_decision_advisory import (
    GovernedDecisionAdvisor,
    GovernedDecisionAdvisoryReport,
    GovernedDecisionOption,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)
from core.governed_reasoning.causal_prediction import (
    GovernedCausalPredictionReport,
)
from core.governed_reasoning.scenario_simulation import (
    GovernedScenarioSimulationReport,
)
from core.intelligent_personal_organization import (
    IntelligentPersonalOrganizationReport,
)
from core.mental_model_decision_evidence import MentalModelDecisionEvidence


class DecisionCoordinator(Protocol):
    def intercept(
        self,
        request: GovernedConversationPipelineRequest,
        *,
        now: datetime,
    ) -> GovernedOperationalInterception | None: ...


class CanonicalDecisionRole(StrEnum):
    PRIMARY = "primary"
    COLLABORATOR = "collaborator"
    SPECIALIZED = "specialized"
    SHADOW = "shadow"
    LEGACY = "legacy"


class CanonicalDecisionOperation(StrEnum):
    INTERCEPT = "intercept"
    ADVISE = "advise"
    CONSOLIDATE = "consolidate"
    ASSESS = "assess"
    OBSERVE = "observe"


@dataclass(frozen=True)
class CanonicalDecisionComponent:
    key: str
    path: str
    role: CanonicalDecisionRole
    operations: tuple[CanonicalDecisionOperation, ...]
    operational: bool
    purpose: str


@dataclass(frozen=True)
class CanonicalDecisionSnapshot:
    schema_version: str
    primary: str
    components: tuple[CanonicalDecisionComponent, ...]

    def component_for(self, key: str) -> CanonicalDecisionComponent:
        return next(component for component in self.components if component.key == key)

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "primary": self.primary,
            "components": [asdict(component) for component in self.components],
        }


CANONICAL_DECISION_COMPONENTS: tuple[CanonicalDecisionComponent, ...] = (
    CanonicalDecisionComponent(
        key="unified_cognitive_coordination",
        path="app.unified_cognitive_coordination:UnifiedCognitiveCoordinator",
        role=CanonicalDecisionRole.PRIMARY,
        operations=(CanonicalDecisionOperation.INTERCEPT,),
        operational=True,
        purpose="Única autoridad operativa para coordinación cognitiva final.",
    ),
    CanonicalDecisionComponent(
        key="executive_director",
        path="app.executive_cognitive_director:ExecutiveCognitiveDirector",
        role=CanonicalDecisionRole.COLLABORATOR,
        operations=(CanonicalDecisionOperation.ADVISE,),
        operational=True,
        purpose="Aporta dirección ejecutiva consultiva sin autoridad final.",
    ),
    CanonicalDecisionComponent(
        key="cognitive_decision_kernel",
        path="core.cognitive_planning.decision_kernel:CognitiveDecisionKernel",
        role=CanonicalDecisionRole.SPECIALIZED,
        operations=(CanonicalDecisionOperation.CONSOLIDATE,),
        operational=False,
        purpose=(
            "Consolida artefactos cognitivos sin enrutar ni ejecutar capacidades."
        ),
    ),
    CanonicalDecisionComponent(
        key="controlled_autonomy_decision_policy",
        path="core.controlled_autonomy.decision_policy:DecisionPolicyEngine",
        role=CanonicalDecisionRole.SPECIALIZED,
        operations=(CanonicalDecisionOperation.ASSESS,),
        operational=False,
        purpose="Decide dentro del subsistema gobernado de autonomía controlada.",
    ),
    CanonicalDecisionComponent(
        key="adaptive_knowledge_evolution_decision",
        path="core.adaptive_cognition.knowledge_evolution:KnowledgeEvolutionEngine",
        role=CanonicalDecisionRole.SPECIALIZED,
        operations=(CanonicalDecisionOperation.ASSESS,),
        operational=False,
        purpose="Evalúa propuestas de evolución de conocimiento bajo revisión.",
    ),
    CanonicalDecisionComponent(
        key="cognitive_planning_shadow_decision",
        path="core.cognitive_planning.decision_kernel:CognitiveDecisionKernel",
        role=CanonicalDecisionRole.SHADOW,
        operations=(CanonicalDecisionOperation.OBSERVE,),
        operational=False,
        purpose="Observa decisiones de planificación sin autoridad operativa.",
    ),
    CanonicalDecisionComponent(
        key="legacy_decision_contracts",
        path="core.cognitive_planning.models:PlannedResponseDecision",
        role=CanonicalDecisionRole.LEGACY,
        operations=(CanonicalDecisionOperation.ASSESS,),
        operational=False,
        purpose="Contratos históricos conservados para compatibilidad interna.",
    ),
)


class CanonicalDecisionFacade:
    """Single decision contract over unified cognitive coordination.

    The facade neither activates decision engines nor changes precedence. When
    bound, it delegates interception to the existing official coordinator.
    """

    SCHEMA_VERSION = "m342.7"
    PRIMARY = "unified_cognitive_coordination"

    def __init__(self, coordinator: DecisionCoordinator | None = None) -> None:
        self._coordinator = coordinator
        self._validate()

    @property
    def snapshot(self) -> CanonicalDecisionSnapshot:
        return CanonicalDecisionSnapshot(
            schema_version=self.SCHEMA_VERSION,
            primary=self.PRIMARY,
            components=CANONICAL_DECISION_COMPONENTS,
        )

    @property
    def bound(self) -> bool:
        return self._coordinator is not None

    def intercept(
        self,
        request: GovernedConversationPipelineRequest,
        *,
        now: datetime,
    ) -> GovernedOperationalInterception | None:
        return self._require_coordinator().intercept(request, now=now)

    def advise(
        self,
        options: tuple[GovernedDecisionOption, ...],
        *,
        organization: IntelligentPersonalOrganizationReport | None = None,
        scenarios: GovernedScenarioSimulationReport | None = None,
        causal: GovernedCausalPredictionReport | None = None,
        mental_model_evidence: tuple[MentalModelDecisionEvidence, ...] = (),
    ) -> GovernedDecisionAdvisoryReport:
        """Return a read-only M391.6 recommendation without execution authority."""
        return GovernedDecisionAdvisor().assess(
            options,
            organization=organization,
            scenarios=scenarios,
            causal=causal,
            mental_model_evidence=mental_model_evidence,
        )

    def _require_coordinator(self) -> DecisionCoordinator:
        if self._coordinator is None:
            raise RuntimeError(
                "canonical decision facade is not bound to a coordinator"
            )
        return self._coordinator

    def _validate(self) -> None:
        keys = [component.key for component in CANONICAL_DECISION_COMPONENTS]
        if len(keys) != len(set(keys)):
            raise ValueError("canonical decision component keys must be unique")

        primaries = [
            component
            for component in CANONICAL_DECISION_COMPONENTS
            if component.role is CanonicalDecisionRole.PRIMARY
        ]
        if len(primaries) != 1 or primaries[0].key != self.PRIMARY:
            raise ValueError("canonical decision must declare one official primary")

        for component in CANONICAL_DECISION_COMPONENTS:
            if not component.operations:
                raise ValueError(f"decision component {component.key} needs operations")
            if component.role is CanonicalDecisionRole.SHADOW:
                if component.operational:
                    raise ValueError("shadow decision components cannot be operational")
                if component.operations != (CanonicalDecisionOperation.OBSERVE,):
                    raise ValueError("shadow decision components may only observe")
