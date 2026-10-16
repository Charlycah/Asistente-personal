from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class SemanticMemoryLayer(StrEnum):
    GOVERNED_FACTS = "governed_facts"
    PERSONAL_KNOWLEDGE = "personal_knowledge"
    HOUSEHOLD_KNOWLEDGE = "household_knowledge"


class SemanticAdmissionMode(StrEnum):
    EXPLICIT_ACCEPTANCE = "explicit_acceptance"
    CURATED_ITEM = "curated_item"
    SUPERVISED_CONFIRMATION = "supervised_confirmation"


@dataclass(frozen=True)
class SemanticMemoryAuthority:
    layer: SemanticMemoryLayer
    authority_key: str
    implementation_path: str
    purpose: str
    admission_mode: SemanticAdmissionMode
    persistent: bool
    runtime_connected: bool
    automatic_promotion: bool = False

    def __post_init__(self) -> None:
        if not self.authority_key.strip():
            raise ValueError("semantic memory authority key must not be blank")
        if ":" not in self.implementation_path:
            raise ValueError("semantic memory implementation must identify a symbol")
        if not self.purpose.strip():
            raise ValueError("semantic memory purpose must not be blank")
        if self.automatic_promotion:
            raise ValueError("M366.3 cannot enable automatic semantic promotion")


@dataclass(frozen=True)
class SemanticMemoryFoundationSnapshot:
    schema_version: str
    canonical_authority: str
    authorities: tuple[SemanticMemoryAuthority, ...]
    external_retrieval_is_memory: bool
    persistence_added: bool
    automatic_learning_added: bool
    runtime_behavior_changed: bool

    def authority_for(
        self, layer: SemanticMemoryLayer | str
    ) -> SemanticMemoryAuthority:
        normalized = SemanticMemoryLayer(layer)
        return next(item for item in self.authorities if item.layer is normalized)
