from datetime import datetime, timezone

import pytest

from core.attention import AttentionManager
from core.cognitive_cycle import CognitiveCycleManager
from core.cognitive_memory_integration import CognitiveMemoryIntegration
from core.cognitive_memory_store import CognitiveMemoryStore, CognitiveMemoryStoreConfig
from core.cognitive_pipeline import CognitivePipeline
from core.collaboration import CollaborationManager
from core.evolution_guard import (
    EvolutionGuardEngine,
    EvolutionGuardManager,
    EvolutionGuardPolicy,
    EvolutionGuardSnapshot,
    EvolutionSignal,
    EvolutionStatus,
)
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
    }


def test_evolution_policy_validates_contract():
    with pytest.raises(ValueError):
        EvolutionGuardPolicy(guarded_threshold=-0.1)

    with pytest.raises(ValueError):
        EvolutionGuardPolicy(guarded_threshold=0.8, safe_threshold=0.7)

    with pytest.raises(ValueError):
        EvolutionGuardPolicy(max_required_checks=0)

    policy = EvolutionGuardPolicy(safe_threshold=0.8)

    assert policy.safe_threshold == 0.8


def test_evolution_snapshot_validates_contract():
    with pytest.raises(ValueError):
        EvolutionGuardSnapshot(
            (),
            EvolutionStatus.SAFE,
            0.9,
            0.1,
            ("M50",),
            ("pytest",),
            (),
            True,
        )

    with pytest.raises(ValueError):
        EvolutionGuardSnapshot(
            (EvolutionSignal.M50_ANCHOR,),
            EvolutionStatus.SAFE,
            1.4,
            0.1,
            ("M50",),
            ("pytest",),
            (),
            True,
        )

    with pytest.raises(ValueError):
        EvolutionGuardSnapshot(
            (EvolutionSignal.M50_ANCHOR,),
            EvolutionStatus.SAFE,
            0.9,
            0.1,
            (" ",),
            ("pytest",),
            (),
            True,
        )


def test_evolution_engine_detects_safe_m50_evolution():
    layers = _full_layers()
    engine = EvolutionGuardEngine()

    snapshot = engine.evaluate_turn(
        "M59 evolución sin romper arquitectura M50, contratos, ruff y pytest",
        now=datetime(2026, 7, 9, tzinfo=timezone.utc),
        **layers,
    )

    assert EvolutionSignal.M50_ANCHOR in snapshot.normalized_signals
    assert EvolutionSignal.CONTRACT_PRESERVATION in snapshot.normalized_signals
    assert EvolutionSignal.VALIDATION_GATE in snapshot.normalized_signals
    assert snapshot.normalized_status in {EvolutionStatus.SAFE, EvolutionStatus.GUARDED}
    assert snapshot.m50_anchor_present is True
    assert snapshot.missing_layers == ()
    assert "Evolución arquitectónica M59:" in snapshot.system_prompt_lines()


def test_evolution_engine_blocks_without_m50_anchor():
    engine = EvolutionGuardEngine()

    snapshot = engine.evaluate_turn(
        "Agregar una capa sin ancla cognitiva",
        now=datetime(2026, 7, 9, tzinfo=timezone.utc),
    )

    assert snapshot.normalized_status is EvolutionStatus.BLOCKED
    assert snapshot.m50_anchor_present is False
    assert "presence" in snapshot.missing_layers


def test_evolution_manager_uses_history_for_compatibility():
    layers = _full_layers()
    manager = EvolutionGuardManager()

    first = manager.observe_turn("M50 contratos y pytest", **layers)
    second = manager.observe_turn(
        "Seguimos con compatibilidad y sin regresiones",
        **layers,
    )

    assert manager.history == (first, second)
    assert first.m50_anchor_present is True
    assert second.m50_anchor_present is True
    assert EvolutionSignal.BACKWARD_COMPATIBILITY in second.normalized_signals


def test_evolution_engine_rejects_naive_datetime():
    engine = EvolutionGuardEngine()

    with pytest.raises(ValueError):
        engine.evaluate_turn("M50", now=datetime(2026, 7, 9))


def test_evolution_to_dict_is_serializable():
    layers = _full_layers()
    snapshot = EvolutionGuardEngine().evaluate_turn("M50 ruff pytest", **layers)
    payload = snapshot.to_dict()

    assert payload["status"] == snapshot.normalized_status.value
    assert "m50_anchor" in payload["signals"]
    assert payload["id"] == snapshot.snapshot_id


def test_cognitive_pipeline_includes_m59_evolution_guard(tmp_path):
    store = CognitiveMemoryStore(
        CognitiveMemoryStoreConfig(db_path=tmp_path / "brain.sqlite")
    )
    evolution_guard = EvolutionGuardManager()
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
        evolution_guard=evolution_guard,
    )

    result = pipeline.process_turn(
        "M59 evolución sin romper M50, contratos, ruff check y pytest",
        call_llm=False,
    )

    assert result.evolution_guard is evolution_guard
    assert evolution_guard.last_snapshot is not None
    assert "Evolución arquitectónica M59:" in result.system_prompt
    assert "Confianza y explicabilidad M58:" in result.system_prompt
    assert "Colaboración prolongada M57:" in result.system_prompt
