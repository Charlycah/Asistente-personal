from __future__ import annotations

from app.cognitive_memory_foundation import CognitiveMemoryFoundation
from core.semantic_memory_foundation import (
    SemanticAdmissionMode,
    SemanticMemoryAuthority,
    SemanticMemoryFoundationSnapshot,
    SemanticMemoryLayer,
)

SEMANTIC_MEMORY_AUTHORITIES: tuple[SemanticMemoryAuthority, ...] = (
    SemanticMemoryAuthority(
        layer=SemanticMemoryLayer.GOVERNED_FACTS,
        authority_key="memory_gateway",
        implementation_path=(
            "domain.governed_permanent_knowledge:GovernedPermanentKnowledge"
        ),
        purpose=(
            "Representar hechos estables, revisables y explícitamente aceptados "
            "sin autoridad de inferencia."
        ),
        admission_mode=SemanticAdmissionMode.EXPLICIT_ACCEPTANCE,
        persistent=False,
        runtime_connected=False,
    ),
    SemanticMemoryAuthority(
        layer=SemanticMemoryLayer.PERSONAL_KNOWLEDGE,
        authority_key="memory_gateway",
        implementation_path="core.personal_knowledge_base:PersonalKnowledgeBase",
        purpose=(
            "Conservar elementos de conocimiento personal estructurados, "
            "versionables y trazables."
        ),
        admission_mode=SemanticAdmissionMode.CURATED_ITEM,
        persistent=False,
        runtime_connected=False,
    ),
    SemanticMemoryAuthority(
        layer=SemanticMemoryLayer.HOUSEHOLD_KNOWLEDGE,
        authority_key="memory_gateway",
        implementation_path="app.household_knowledge:HouseholdKnowledgeService",
        purpose=(
            "Exponer conocimiento doméstico mediante aprendizaje supervisado "
            "y confirmación explícita."
        ),
        admission_mode=SemanticAdmissionMode.SUPERVISED_CONFIRMATION,
        persistent=True,
        runtime_connected=True,
    ),
)


class SemanticMemoryFoundation:
    """Governed reconciliation of ROBY's existing semantic-memory surfaces."""

    SCHEMA_VERSION = "m366.3"

    def __init__(
        self, *, cognitive_memory: CognitiveMemoryFoundation | None = None
    ) -> None:
        self._cognitive_memory = cognitive_memory or CognitiveMemoryFoundation()
        self._validate()

    @property
    def snapshot(self) -> SemanticMemoryFoundationSnapshot:
        semantic_domain = self._cognitive_memory.snapshot.domain_for("semantic")
        return SemanticMemoryFoundationSnapshot(
            schema_version=self.SCHEMA_VERSION,
            canonical_authority=semantic_domain.authority_key,
            authorities=SEMANTIC_MEMORY_AUTHORITIES,
            external_retrieval_is_memory=False,
            persistence_added=False,
            automatic_learning_added=False,
            runtime_behavior_changed=False,
        )

    def _validate(self) -> None:
        semantic_domain = self._cognitive_memory.snapshot.domain_for("semantic")
        layers = [item.layer for item in SEMANTIC_MEMORY_AUTHORITIES]
        if len(layers) != len(set(layers)):
            raise ValueError("semantic memory layers must be unique")
        if set(layers) != set(SemanticMemoryLayer):
            raise ValueError("semantic memory foundation must declare every layer")
        if any(
            item.authority_key != semantic_domain.authority_key
            for item in SEMANTIC_MEMORY_AUTHORITIES
        ):
            raise ValueError("semantic layers must remain under canonical authority")
