from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class EpisodicMemoryLayer(StrEnum):
    COGNITIVE_CYCLE = "cognitive_cycle"
    GOVERNED_AGGREGATE = "governed_aggregate"


class EpisodicAdmissionMode(StrEnum):
    OBSERVED_TRANSITION = "observed_transition"
    EXPLICIT_CAPTURE = "explicit_capture"


@dataclass(frozen=True)
class EpisodicMemoryAuthority:
    layer: EpisodicMemoryLayer
    authority_key: str
    implementation_path: str
    purpose: str
    admission_mode: EpisodicAdmissionMode
    persistent: bool
    runtime_connected: bool
    automatic_consolidation: bool = False

    def __post_init__(self) -> None:
        if not self.authority_key.strip():
            raise ValueError("episodic authority key must not be blank")
        if ":" not in self.implementation_path:
            raise ValueError("episodic implementation path must identify a symbol")
        if not self.purpose.strip():
            raise ValueError("episodic authority purpose must not be blank")
        if self.automatic_consolidation:
            raise ValueError("M366.2 cannot enable automatic episodic consolidation")


@dataclass(frozen=True)
class EpisodicMemoryFoundationSnapshot:
    schema_version: str
    canonical_authority: str
    authorities: tuple[EpisodicMemoryAuthority, ...]
    persistence_added: bool
    automatic_capture_added: bool
    runtime_behavior_changed: bool

    def authority_for(
        self, layer: EpisodicMemoryLayer | str
    ) -> EpisodicMemoryAuthority:
        normalized = EpisodicMemoryLayer(layer)
        return next(item for item in self.authorities if item.layer is normalized)
