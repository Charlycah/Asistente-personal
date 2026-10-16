from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ProceduralMemoryLayer(StrEnum):
    GOVERNED_PLANS = "governed_plans"
    ROUTINES_HABITS = "routines_habits"
    TASK_PROCEDURES = "task_procedures"


class ProceduralAdmissionMode(StrEnum):
    EXPLICIT_ACCEPTANCE = "explicit_acceptance"
    SUPERVISED_OBSERVATION = "supervised_observation"
    GOVERNED_TASK_DEFINITION = "governed_task_definition"


@dataclass(frozen=True)
class ProceduralMemoryAuthority:
    layer: ProceduralMemoryLayer
    authority_key: str
    implementation_path: str
    purpose: str
    admission_mode: ProceduralAdmissionMode
    persistent: bool
    runtime_connected: bool
    execution_authority: bool = False
    automatic_promotion: bool = False

    def __post_init__(self) -> None:
        if not self.authority_key.strip():
            raise ValueError("procedural memory authority key must not be blank")
        if ":" not in self.implementation_path:
            raise ValueError("procedural memory implementation must identify a symbol")
        if not self.purpose.strip():
            raise ValueError("procedural memory purpose must not be blank")
        if self.execution_authority:
            raise ValueError("M366.4 cannot grant procedural execution authority")
        if self.automatic_promotion:
            raise ValueError("M366.4 cannot enable automatic procedural promotion")


@dataclass(frozen=True)
class ProceduralMemoryFoundationSnapshot:
    schema_version: str
    canonical_authority: str
    authorities: tuple[ProceduralMemoryAuthority, ...]
    remembered_procedure_authorizes_execution: bool
    persistence_added: bool
    automatic_learning_added: bool
    runtime_behavior_changed: bool

    def authority_for(
        self, layer: ProceduralMemoryLayer | str
    ) -> ProceduralMemoryAuthority:
        normalized = ProceduralMemoryLayer(layer)
        return next(item for item in self.authorities if item.layer is normalized)
