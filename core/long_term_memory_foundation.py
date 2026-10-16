from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class LongTermMemoryLayer(StrEnum):
    DURABLE_PERSONAL_MEMORY = "durable_personal_memory"
    REVISABLE_KNOWLEDGE = "revisable_knowledge"
    HOUSEHOLD_LIFECYCLE = "household_lifecycle"


class LongTermAdmissionMode(StrEnum):
    EXPLICIT_REQUEST = "explicit_request"
    EXPLICIT_ACCEPTANCE = "explicit_acceptance"
    SUPERVISED_LIFECYCLE = "supervised_lifecycle"


class LongTermRetentionMode(StrEnum):
    ACTIVE_UNTIL_REVISED_OR_ARCHIVED = "active_until_revised_or_archived"
    REVISION_HISTORY = "revision_history"
    STATUS_GOVERNED = "status_governed"


@dataclass(frozen=True)
class LongTermMemoryAuthority:
    layer: LongTermMemoryLayer
    authority_key: str
    implementation_path: str
    purpose: str
    admission_mode: LongTermAdmissionMode
    retention_mode: LongTermRetentionMode
    persistent: bool
    runtime_connected: bool
    automatic_consolidation: bool = False
    irreversible_forgetting: bool = False
    consciousness_claim: bool = False

    def __post_init__(self) -> None:
        if not self.authority_key.strip():
            raise ValueError("long-term memory authority key must not be blank")
        if ":" not in self.implementation_path:
            raise ValueError("long-term memory implementation must identify a symbol")
        if not self.purpose.strip():
            raise ValueError("long-term memory purpose must not be blank")
        if self.automatic_consolidation:
            raise ValueError("M366.5 cannot enable automatic consolidation")
        if self.irreversible_forgetting:
            raise ValueError("M366.5 cannot enable irreversible forgetting")
        if self.consciousness_claim:
            raise ValueError("M366.5 cannot claim machine consciousness")


@dataclass(frozen=True)
class LongTermMemoryFoundationSnapshot:
    schema_version: str
    canonical_authority: str
    authorities: tuple[LongTermMemoryAuthority, ...]
    consolidation_requires_governance: bool
    forgetting_is_reviewable: bool
    autobiographical_continuity_supported: bool
    consciousness_established: bool
    persistence_added: bool
    automatic_learning_added: bool
    runtime_behavior_changed: bool

    def authority_for(
        self, layer: LongTermMemoryLayer | str
    ) -> LongTermMemoryAuthority:
        normalized = LongTermMemoryLayer(layer)
        return next(item for item in self.authorities if item.layer is normalized)
