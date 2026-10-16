from __future__ import annotations

from app.cognitive_memory_foundation import CognitiveMemoryFoundation
from core.long_term_memory_foundation import (
    LongTermAdmissionMode,
    LongTermMemoryAuthority,
    LongTermMemoryFoundationSnapshot,
    LongTermMemoryLayer,
    LongTermRetentionMode,
)

LONG_TERM_MEMORY_AUTHORITIES: tuple[LongTermMemoryAuthority, ...] = (
    LongTermMemoryAuthority(
        layer=LongTermMemoryLayer.DURABLE_PERSONAL_MEMORY,
        authority_key="memory_gateway",
        implementation_path=(
            "core.memory_runtime_integration:MemoryRuntimeIntegration"
        ),
        purpose=(
            "Conservar recuerdos personales explícitos en el store cognitivo "
            "local, con recuperación, corrección y archivado gobernados."
        ),
        admission_mode=LongTermAdmissionMode.EXPLICIT_REQUEST,
        retention_mode=(
            LongTermRetentionMode.ACTIVE_UNTIL_REVISED_OR_ARCHIVED
        ),
        persistent=True,
        runtime_connected=True,
    ),
    LongTermMemoryAuthority(
        layer=LongTermMemoryLayer.REVISABLE_KNOWLEDGE,
        authority_key="memory_gateway",
        implementation_path=(
            "domain.governed_permanent_knowledge:GovernedPermanentKnowledge"
        ),
        purpose=(
            "Conservar conocimiento aceptado con historial de revisiones y "
            "retractación explícita, sin inferencia automática."
        ),
        admission_mode=LongTermAdmissionMode.EXPLICIT_ACCEPTANCE,
        retention_mode=LongTermRetentionMode.REVISION_HISTORY,
        persistent=False,
        runtime_connected=True,
    ),
    LongTermMemoryAuthority(
        layer=LongTermMemoryLayer.HOUSEHOLD_LIFECYCLE,
        authority_key="memory_gateway",
        implementation_path="core.household_memory:HouseholdMemoryManager",
        purpose=(
            "Conservar memoria doméstica estructurada con estados activo, "
            "completado y archivado bajo supervisión."
        ),
        admission_mode=LongTermAdmissionMode.SUPERVISED_LIFECYCLE,
        retention_mode=LongTermRetentionMode.STATUS_GOVERNED,
        persistent=False,
        runtime_connected=True,
    ),
)


class LongTermMemoryFoundation:
    """Governed reconciliation of ROBY's existing durable memory surfaces."""

    SCHEMA_VERSION = "m366.5"

    def __init__(
        self, *, cognitive_memory: CognitiveMemoryFoundation | None = None
    ) -> None:
        self._cognitive_memory = cognitive_memory or CognitiveMemoryFoundation()
        self._validate()

    @property
    def snapshot(self) -> LongTermMemoryFoundationSnapshot:
        long_term_domain = self._cognitive_memory.snapshot.domain_for("long_term")
        return LongTermMemoryFoundationSnapshot(
            schema_version=self.SCHEMA_VERSION,
            canonical_authority=long_term_domain.authority_key,
            authorities=LONG_TERM_MEMORY_AUTHORITIES,
            consolidation_requires_governance=True,
            forgetting_is_reviewable=True,
            autobiographical_continuity_supported=True,
            consciousness_established=False,
            persistence_added=False,
            automatic_learning_added=False,
            runtime_behavior_changed=False,
        )

    def _validate(self) -> None:
        long_term_domain = self._cognitive_memory.snapshot.domain_for("long_term")
        layers = [item.layer for item in LONG_TERM_MEMORY_AUTHORITIES]
        if len(layers) != len(set(layers)):
            raise ValueError("long-term memory layers must be unique")
        if set(layers) != set(LongTermMemoryLayer):
            raise ValueError("long-term memory foundation must declare every layer")
        if any(
            item.authority_key != long_term_domain.authority_key
            for item in LONG_TERM_MEMORY_AUTHORITIES
        ):
            raise ValueError("long-term layers must remain under canonical authority")
