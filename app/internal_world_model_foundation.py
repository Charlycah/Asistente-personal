from __future__ import annotations

from core.ambient_context_foundation.models import AmbientContext
from core.cognitive_maturity.epistemic import EpistemicLevel
from core.executive_event_model import ExecutiveEvent
from core.governed_context_representation import (
    GovernedContextRepresentation,
    GovernedContextRepresentationView,
)
from core.governed_household_representation import (
    GovernedHouseholdRepresentation,
    GovernedHouseholdRepresentationView,
    HouseholdSpaceEvidence,
    HouseholdSpatialRelationEvidence,
)
from core.governed_objects_representation import (
    GovernedObjectsRepresentation,
    GovernedObjectsRepresentationView,
)
from core.governed_people_representation import (
    GovernedPeopleRepresentation,
    GovernedPeopleRepresentationView,
    PersonEvidence,
    PersonRelationshipEvidence,
)
from core.governed_places_representation import (
    GovernedPlacesRepresentation,
    GovernedPlacesRepresentationView,
)
from core.governed_timeline_representation import (
    GovernedTimelineRepresentation,
    GovernedTimelineRepresentationView,
    TimelineIntervalEvidence,
    TimelineRelationEvidence,
)
from core.governed_world_integration import (
    GovernedWorldIntegrationSnapshot,
    GovernedWorldIntegrationView,
)
from core.governed_world_stabilization import (
    GovernedWorldStabilizationDiagnostic,
    GovernedWorldStabilizationReport,
)
from core.household_memory import HouseholdMemoryEntry
from core.internal_world_model_foundation import (
    InternalWorldAuthority,
    InternalWorldDomain,
    InternalWorldModelSnapshot,
)
from core.object_knowledge import ObjectKnowledgeProfile
from core.persistent_world_model import (
    PersistentWorldDomain,
    PersistentWorldFact,
    PersistentWorldModelView,
    PersistentWorldSnapshot,
)
from core.personal_identity_and_session_profiles.models import (
    PersonalIdentityProfile,
)
from core.places_knowledge import PlaceKnowledgeProfile
from core.relationship_memory import RelationshipMemoryRecord
from core.unified_cognitive_blackboard import CognitiveBlackboardEntry

INTERNAL_WORLD_AUTHORITIES: tuple[InternalWorldAuthority, ...] = (
    InternalWorldAuthority(
        domain=InternalWorldDomain.SELF,
        authority_key="internal_world_model",
        implementation_path="core.adaptive_cognition.mental_models:MentalModel",
        purpose="Representar modelos revisables de ROBY y otros sujetos.",
        runtime_connected=False,
        persistent=False,
    ),
    InternalWorldAuthority(
        domain=InternalWorldDomain.USER,
        authority_key="internal_world_model",
        implementation_path=(
            "core.personal_identity_and_session_profiles:PersonalIdentityProfile"
        ),
        purpose="Representar identidad y perfil gobernado del usuario.",
        runtime_connected=True,
        persistent=True,
    ),
    InternalWorldAuthority(
        domain=InternalWorldDomain.PROJECTS,
        authority_key="internal_world_model",
        implementation_path="core.task_intelligence:TaskIntelligenceManager",
        purpose="Representar trabajo estructurado, proyectos y tareas existentes.",
        runtime_connected=True,
        persistent=False,
    ),
    InternalWorldAuthority(
        domain=InternalWorldDomain.GOALS,
        authority_key="internal_world_model",
        implementation_path="core.cognitive_goals.manager:CognitiveGoalManager",
        purpose="Representar objetivos cognitivos y sus estados gobernados.",
        runtime_connected=True,
        persistent=False,
    ),
    InternalWorldAuthority(
        domain=InternalWorldDomain.CONTEXT,
        authority_key="internal_world_model",
        implementation_path=(
            "core.unified_cognitive_blackboard:UnifiedCognitiveBlackboard"
        ),
        purpose="Representar contexto cognitivo activo por sesión.",
        runtime_connected=True,
        persistent=False,
    ),
    InternalWorldAuthority(
        domain=InternalWorldDomain.RELATIONSHIPS,
        authority_key="internal_world_model",
        implementation_path="core.relationship_memory:RelationshipMemoryManager",
        purpose="Representar relaciones conocidas y revisables.",
        runtime_connected=True,
        persistent=True,
    ),
    InternalWorldAuthority(
        domain=InternalWorldDomain.MEMORY,
        authority_key="internal_world_model",
        implementation_path="app.canonical_memory_facade:CanonicalMemoryFacade",
        purpose="Exponer memoria gobernada sin duplicar sus almacenes.",
        runtime_connected=True,
        persistent=True,
    ),
    InternalWorldAuthority(
        domain=InternalWorldDomain.CAPABILITIES,
        authority_key="internal_world_model",
        implementation_path="core.capability_registry:CapabilityRegistry",
        purpose="Representar capacidades disponibles sin autorizarlas.",
        runtime_connected=True,
        persistent=False,
    ),
    InternalWorldAuthority(
        domain=InternalWorldDomain.ENVIRONMENT,
        authority_key="internal_world_model",
        implementation_path=(
            "core.ambient_context_foundation.engine:AmbientContextFoundation"
        ),
        purpose="Representar señales ambientales gobernadas.",
        runtime_connected=True,
        persistent=False,
    ),
    InternalWorldAuthority(
        domain=InternalWorldDomain.CONSTRAINTS,
        authority_key="internal_world_model",
        implementation_path="core.scope_guard:ScopeGuard",
        purpose="Representar límites y dominios autorizados.",
        runtime_connected=True,
        persistent=False,
    ),
)


class InternalWorldModelFoundation:
    """Governed inventory of ROBY's existing internal-world authorities."""

    SCHEMA_VERSION = "m367.1"
    CANONICAL_AUTHORITY = "internal_world_model"

    def __init__(self) -> None:
        self._validate()


    def stabilize_integrated_world(
        self,
        snapshot: GovernedWorldIntegrationSnapshot,
    ) -> GovernedWorldStabilizationReport:
        return GovernedWorldStabilizationDiagnostic().inspect(snapshot)

    def integrated_world(
        self,
        household: GovernedHouseholdRepresentation,
        people: GovernedPeopleRepresentation,
        places: GovernedPlacesRepresentation,
        objects: GovernedObjectsRepresentation,
        timeline: GovernedTimelineRepresentation,
        context: GovernedContextRepresentation,
    ) -> GovernedWorldIntegrationSnapshot:
        return GovernedWorldIntegrationView().build(
            household,
            people,
            places,
            objects,
            timeline,
            context,
        )

    def context_representation(
        self,
        blackboard_entries: tuple[CognitiveBlackboardEntry, ...] = (),
        *,
        ambient_contexts: tuple[AmbientContext, ...] = (),
    ) -> GovernedContextRepresentation:
        return GovernedContextRepresentationView().build(
            blackboard_entries,
            ambient_contexts=ambient_contexts,
        )

    def timeline_representation(
        self,
        events: tuple[ExecutiveEvent, ...] = (),
        *,
        intervals: tuple[TimelineIntervalEvidence, ...] = (),
        relations: tuple[TimelineRelationEvidence, ...] = (),
    ) -> GovernedTimelineRepresentation:
        return GovernedTimelineRepresentationView().build(
            events,
            intervals=intervals,
            relations=relations,
        )

    def objects_representation(
        self,
        profiles: tuple[ObjectKnowledgeProfile, ...] = (),
    ) -> GovernedObjectsRepresentation:
        return GovernedObjectsRepresentationView().build(profiles)

    def places_representation(
        self,
        profiles: tuple[PlaceKnowledgeProfile, ...] = (),
    ) -> GovernedPlacesRepresentation:
        return GovernedPlacesRepresentationView().build(profiles)

    def people_representation(
        self,
        profiles: tuple[PersonalIdentityProfile, ...] = (),
        *,
        people: tuple[PersonEvidence, ...] = (),
        relationship_records: tuple[RelationshipMemoryRecord, ...] = (),
        relationships: tuple[PersonRelationshipEvidence, ...] = (),
    ) -> GovernedPeopleRepresentation:
        return GovernedPeopleRepresentationView().build(
            profiles,
            people,
            relationship_records,
            relationships,
        )

    def household_representation(
        self,
        household_entries: tuple[HouseholdMemoryEntry, ...] = (),
        *,
        spaces: tuple[HouseholdSpaceEvidence, ...] = (),
        relations: tuple[HouseholdSpatialRelationEvidence, ...] = (),
    ) -> GovernedHouseholdRepresentation:
        return GovernedHouseholdRepresentationView().build(
            household_entries,
            spaces,
            relations,
        )

    def persistent_snapshot(
        self,
        facts: tuple[PersistentWorldFact, ...] = (),
        *,
        household_entries: tuple[HouseholdMemoryEntry, ...] = (),
    ) -> PersistentWorldSnapshot:
        household_facts = tuple(
            self._household_fact(entry) for entry in household_entries
        )
        return PersistentWorldModelView().build((*facts, *household_facts))

    @staticmethod
    def _household_fact(entry: HouseholdMemoryEntry) -> PersistentWorldFact:
        category = entry.normalized_category.value
        normalized_title = "-".join(entry.title.casefold().split())
        return PersistentWorldFact(
            fact_id=f"household:{entry.entry_id}",
            domain=PersistentWorldDomain.HOUSEHOLD,
            fact_key=f"{category}:{normalized_title}",
            value=entry.details,
            source_authority="household_memory",
            source_reference=entry.entry_id,
            epistemic_level=EpistemicLevel.FACT,
            evidence_codes=(
                f"household_category:{category}",
                f"household_source:{entry.source}",
            ),
            persisted_by_source=True,
            active=entry.normalized_status.value != "archived",
            source_updated_at=entry.updated_at,
        )

    @property
    def snapshot(self) -> InternalWorldModelSnapshot:
        return InternalWorldModelSnapshot(
            schema_version=self.SCHEMA_VERSION,
            canonical_authority=self.CANONICAL_AUTHORITY,
            authorities=INTERNAL_WORLD_AUTHORITIES,
            supported_domains=tuple(InternalWorldDomain),
            read_only=True,
            inference_added=False,
            persistence_added=False,
            runtime_behavior_changed=False,
            consciousness_claimed=False,
        )

    @staticmethod
    def _validate() -> None:
        domains = tuple(item.domain for item in INTERNAL_WORLD_AUTHORITIES)
        if len(domains) != len(set(domains)):
            raise ValueError("internal world domains must be unique")
        if set(domains) != set(InternalWorldDomain):
            raise ValueError("internal world model must declare every domain")
        if {item.authority_key for item in INTERNAL_WORLD_AUTHORITIES} != {
            "internal_world_model"
        }:
            raise ValueError("internal world model must preserve one authority")
