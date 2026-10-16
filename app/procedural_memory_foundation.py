from __future__ import annotations

from app.cognitive_memory_foundation import CognitiveMemoryFoundation
from core.procedural_memory_foundation import (
    ProceduralAdmissionMode,
    ProceduralMemoryAuthority,
    ProceduralMemoryFoundationSnapshot,
    ProceduralMemoryLayer,
)

PROCEDURAL_MEMORY_AUTHORITIES: tuple[ProceduralMemoryAuthority, ...] = (
    ProceduralMemoryAuthority(
        layer=ProceduralMemoryLayer.GOVERNED_PLANS,
        authority_key="memory_gateway",
        implementation_path="domain.governed_plan:GovernedPlanModel",
        purpose=(
            "Representar secuencias cognitivas gobernadas, dependencias y "
            "autorizaciones sin ejecutarlas."
        ),
        admission_mode=ProceduralAdmissionMode.EXPLICIT_ACCEPTANCE,
        persistent=False,
        runtime_connected=False,
    ),
    ProceduralMemoryAuthority(
        layer=ProceduralMemoryLayer.ROUTINES_HABITS,
        authority_key="memory_gateway",
        implementation_path="core.routines_habits:RoutineHabitManager",
        purpose=(
            "Conservar rutinas y hábitos supervisados como conocimiento de "
            "continuidad, sin convertir repetición en autorización."
        ),
        admission_mode=ProceduralAdmissionMode.SUPERVISED_OBSERVATION,
        persistent=False,
        runtime_connected=False,
    ),
    ProceduralMemoryAuthority(
        layer=ProceduralMemoryLayer.TASK_PROCEDURES,
        authority_key="memory_gateway",
        implementation_path="core.task_intelligence:TaskIntelligenceManager",
        purpose=(
            "Representar tareas, dependencias y pasos operativos gobernados "
            "sin asumir ejecución autónoma."
        ),
        admission_mode=ProceduralAdmissionMode.GOVERNED_TASK_DEFINITION,
        persistent=False,
        runtime_connected=False,
    ),
)


class ProceduralMemoryFoundation:
    """Governed reconciliation of ROBY's existing procedural knowledge."""

    SCHEMA_VERSION = "m366.4"

    def __init__(
        self, *, cognitive_memory: CognitiveMemoryFoundation | None = None
    ) -> None:
        self._cognitive_memory = cognitive_memory or CognitiveMemoryFoundation()
        self._validate()

    @property
    def snapshot(self) -> ProceduralMemoryFoundationSnapshot:
        procedural_domain = self._cognitive_memory.snapshot.domain_for("procedural")
        return ProceduralMemoryFoundationSnapshot(
            schema_version=self.SCHEMA_VERSION,
            canonical_authority=procedural_domain.authority_key,
            authorities=PROCEDURAL_MEMORY_AUTHORITIES,
            remembered_procedure_authorizes_execution=False,
            persistence_added=False,
            automatic_learning_added=False,
            runtime_behavior_changed=False,
        )

    def _validate(self) -> None:
        procedural_domain = self._cognitive_memory.snapshot.domain_for("procedural")
        layers = [item.layer for item in PROCEDURAL_MEMORY_AUTHORITIES]
        if len(layers) != len(set(layers)):
            raise ValueError("procedural memory layers must be unique")
        if set(layers) != set(ProceduralMemoryLayer):
            raise ValueError("procedural memory foundation must declare every layer")
        if any(
            item.authority_key != procedural_domain.authority_key
            for item in PROCEDURAL_MEMORY_AUTHORITIES
        ):
            raise ValueError("procedural layers must remain under canonical authority")
