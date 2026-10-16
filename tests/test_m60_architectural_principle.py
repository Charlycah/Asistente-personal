from datetime import datetime, timezone

import pytest

from core.architectural_principle import (
    ArchitecturalPrincipleEngine,
    ArchitecturalPrincipleManager,
    ArchitecturalPrinciplePolicy,
    ArchitecturalPrincipleSignal,
    ArchitecturalPrincipleSnapshot,
    ArchitecturalPrincipleStatus,
)
from core.attention import AttentionManager
from core.cognitive_cycle import CognitiveCycleManager
from core.cognitive_memory_integration import CognitiveMemoryIntegration
from core.cognitive_memory_store import CognitiveMemoryStore, CognitiveMemoryStoreConfig
from core.cognitive_pipeline import CognitivePipeline
from core.collaboration import CollaborationManager
from core.evolution_guard import EvolutionGuardManager
from core.identity import ROBYIdentity
from core.initiative import InitiativeManager
from core.learning import ExperientialLearningManager
from core.mental_state import ROBYMentalState
from core.planning import PlanningManager
from core.presence import PresenceManager
from core.reasoning import ReasoningManager
from core.reflection import ReflectionManager
from core.relationship_memory import RelationshipMemoryManager
from core.routines_habits import RoutineHabitManager
from core.social_regulation import SocialRegulationManager
from core.stable_personality import StablePersonalityManager
from core.trust_explainability import TrustExplainabilityManager
from core.working_memory import WorkingMemoryManager


def _full_layers():
    return {
        "cognitive_cycle": CognitiveCycleManager(),
        "presence": PresenceManager(),
        "relationship_memory": RelationshipMemoryManager(),
        "initiative": InitiativeManager(),
        "social_regulation": SocialRegulationManager(),
        "stable_personality": StablePersonalityManager(),
        "routines_habits": RoutineHabitManager(),
        "collaboration": CollaborationManager(),
        "trust_explainability": TrustExplainabilityManager(),
        "evolution_guard": EvolutionGuardManager(),
    }


def test_architectural_policy_validates_contract():
    with pytest.raises(ValueError):
        ArchitecturalPrinciplePolicy(aligned_threshold=-0.1)

    with pytest.raises(ValueError):
        ArchitecturalPrinciplePolicy(
            aligned_threshold=0.9,
            consolidated_threshold=0.7,
        )

    with pytest.raises(ValueError):
        ArchitecturalPrinciplePolicy(required_layer_count=0)

    policy = ArchitecturalPrinciplePolicy(consolidated_threshold=0.9)

    assert policy.consolidated_threshold == 0.9


def test_architectural_snapshot_validates_contract():
    with pytest.raises(ValueError):
        ArchitecturalPrincipleSnapshot(
            (),
            ArchitecturalPrincipleStatus.ALIGNED,
            0.8,
            0.1,
            "M50 anchor",
            ("rule",),
            (),
            (),
            False,
        )

    with pytest.raises(ValueError):
        ArchitecturalPrincipleSnapshot(
            (ArchitecturalPrincipleSignal.M50_CONSUMED,),
            ArchitecturalPrincipleStatus.ALIGNED,
            1.2,
            0.1,
            "M50 anchor",
            ("rule",),
            (),
            (),
            False,
        )

    with pytest.raises(ValueError):
        ArchitecturalPrincipleSnapshot(
            (ArchitecturalPrincipleSignal.M50_CONSUMED,),
            ArchitecturalPrincipleStatus.ALIGNED,
            0.8,
            0.1,
            " ",
            ("rule",),
            (),
            (),
            False,
        )


def test_architectural_engine_consolidates_phase_v_with_full_layers():
    layers = _full_layers()
    snapshot = ArchitecturalPrincipleEngine().evaluate_turn(
        "M60 principio arquitectónico: Fase V no reemplaza M50, lo consume "
        "como ancla con capas opcionales y contratos compatibles.",
        now=datetime(2026, 7, 9, tzinfo=timezone.utc),
        **layers,
    )

    assert ArchitecturalPrincipleSignal.M50_CONSUMED in snapshot.normalized_signals
    assert ArchitecturalPrincipleSignal.NON_REPLACEMENT in snapshot.normalized_signals
    assert ArchitecturalPrincipleSignal.OPTIONAL_LAYERS in snapshot.normalized_signals
    assert snapshot.normalized_status is ArchitecturalPrincipleStatus.CONSOLIDATED
    assert snapshot.phase_v_closed is True
    assert snapshot.missing_layers == ()
    assert "Principio arquitectónico M60:" in snapshot.system_prompt_lines()


def test_architectural_engine_reports_partial_without_m50_anchor():
    snapshot = ArchitecturalPrincipleEngine().evaluate_turn(
        "Agregar convivencia sin ciclo cognitivo",
        now=datetime(2026, 7, 9, tzinfo=timezone.utc),
    )

    assert snapshot.phase_v_closed is False
    assert snapshot.normalized_status in {
        ArchitecturalPrincipleStatus.PARTIAL,
        ArchitecturalPrincipleStatus.VIOLATED,
    }
    assert "presence" in snapshot.missing_layers


def test_architectural_manager_keeps_history_and_improves_alignment():
    layers = _full_layers()
    manager = ArchitecturalPrincipleManager()

    first = manager.observe_turn("M50 ancla y contratos", **layers)
    second = manager.observe_turn(
        "Fase V cerramos con capas opcionales compatibles",
        **layers,
    )

    assert manager.history == (first, second)
    assert second.alignment_score >= first.alignment_score
    assert manager.last_snapshot is second


def test_architectural_engine_rejects_naive_datetime():
    with pytest.raises(ValueError):
        ArchitecturalPrincipleEngine().evaluate_turn(
            "M60",
            now=datetime(2026, 7, 9),
        )


def test_architectural_to_dict_is_serializable():
    snapshot = ArchitecturalPrincipleEngine().evaluate_turn(
        "M60 Fase V M50 arquitectura compatible",
        **_full_layers(),
    )
    payload = snapshot.to_dict()

    assert payload["id"] == snapshot.snapshot_id
    assert payload["phase_v_closed"] is True
    assert "m50_consumed" in payload["signals"]


def test_cognitive_pipeline_includes_m60_architectural_principle(tmp_path):
    store = CognitiveMemoryStore(
        CognitiveMemoryStoreConfig(db_path=tmp_path / "brain.sqlite")
    )
    architectural_principle = ArchitecturalPrincipleManager()
    pipeline = CognitivePipeline(
        CognitiveMemoryIntegration(store),
        identity=ROBYIdentity(),
        mental_state=ROBYMentalState(),
        attention=AttentionManager(),
        working_memory=WorkingMemoryManager(),
        reasoning=ReasoningManager(),
        planning=PlanningManager(),
        learning=ExperientialLearningManager(),
        reflection=ReflectionManager(),
        cognitive_cycle=CognitiveCycleManager(),
        presence=PresenceManager(),
        relationship_memory=RelationshipMemoryManager(),
        initiative=InitiativeManager(),
        social_regulation=SocialRegulationManager(),
        stable_personality=StablePersonalityManager(),
        routines_habits=RoutineHabitManager(),
        collaboration=CollaborationManager(),
        trust_explainability=TrustExplainabilityManager(),
        evolution_guard=EvolutionGuardManager(),
        architectural_principle=architectural_principle,
    )

    result = pipeline.process_turn(
        "M60 principio arquitectónico: Fase V no reemplaza M50, lo consume",
        call_llm=False,
    )

    assert result.architectural_principle is architectural_principle
    assert architectural_principle.last_snapshot is not None
    assert architectural_principle.last_snapshot.phase_v_closed is True
    assert "Principio arquitectónico M60:" in result.system_prompt
    assert "Evolución arquitectónica M59:" in result.system_prompt
