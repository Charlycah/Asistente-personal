from __future__ import annotations

from app.cognitive_memory_foundation import CognitiveMemoryFoundation
from core.episodic_memory_foundation import (
    EpisodicAdmissionMode,
    EpisodicMemoryAuthority,
    EpisodicMemoryFoundationSnapshot,
    EpisodicMemoryLayer,
)

EPISODIC_MEMORY_AUTHORITIES: tuple[EpisodicMemoryAuthority, ...] = (
    EpisodicMemoryAuthority(
        layer=EpisodicMemoryLayer.COGNITIVE_CYCLE,
        authority_key="episodic_memory",
        implementation_path=(
            "app.cognitive_episodic_memory:CognitiveEpisodicMemory"
        ),
        purpose=(
            "Registrar transiciones cognitivas concisas y trazables durante "
            "el ciclo interno existente."
        ),
        admission_mode=EpisodicAdmissionMode.OBSERVED_TRANSITION,
        persistent=False,
        runtime_connected=True,
    ),
    EpisodicMemoryAuthority(
        layer=EpisodicMemoryLayer.GOVERNED_AGGREGATE,
        authority_key="episodic_memory",
        implementation_path=(
            "core.adaptive_cognition.episodic_memory:EpisodicMemoryManager"
        ),
        purpose=(
            "Representar experiencias delimitadas mediante revisiones "
            "inmutables y captura gobernada explícita."
        ),
        admission_mode=EpisodicAdmissionMode.EXPLICIT_CAPTURE,
        persistent=False,
        runtime_connected=False,
    ),
)


class EpisodicMemoryFoundation:
    """Governed reconciliation of ROBY's existing episodic memory layers."""

    SCHEMA_VERSION = "m366.2"

    def __init__(
        self, *, cognitive_memory: CognitiveMemoryFoundation | None = None
    ) -> None:
        self._cognitive_memory = cognitive_memory or CognitiveMemoryFoundation()
        self._validate()

    @property
    def snapshot(self) -> EpisodicMemoryFoundationSnapshot:
        episodic_domain = self._cognitive_memory.snapshot.domain_for("episodic")
        return EpisodicMemoryFoundationSnapshot(
            schema_version=self.SCHEMA_VERSION,
            canonical_authority=episodic_domain.authority_key,
            authorities=EPISODIC_MEMORY_AUTHORITIES,
            persistence_added=False,
            automatic_capture_added=False,
            runtime_behavior_changed=False,
        )

    def _validate(self) -> None:
        snapshot = self._cognitive_memory.snapshot
        episodic_domain = snapshot.domain_for("episodic")
        layers = [item.layer for item in EPISODIC_MEMORY_AUTHORITIES]
        if len(layers) != len(set(layers)):
            raise ValueError("episodic memory layers must be unique")
        if set(layers) != set(EpisodicMemoryLayer):
            raise ValueError("episodic memory foundation must declare every layer")
        if any(
            item.authority_key != episodic_domain.authority_key
            for item in EPISODIC_MEMORY_AUTHORITIES
        ):
            raise ValueError("episodic layers must remain under canonical authority")
