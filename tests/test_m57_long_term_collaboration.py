from datetime import datetime, timezone

import pytest

from core.attention import AttentionManager
from core.cognitive_cycle import CognitiveCycleContext, CognitiveCycleManager
from core.cognitive_memory_integration import CognitiveMemoryIntegration
from core.cognitive_memory_store import CognitiveMemoryStore, CognitiveMemoryStoreConfig
from core.cognitive_pipeline import CognitivePipeline
from core.collaboration import (
    CollaborationEngine,
    CollaborationManager,
    CollaborationPolicy,
    CollaborationSignal,
    CollaborationSnapshot,
    CollaborationStatus,
)
from core.identity import ROBYIdentity
from core.initiative import InitiativeEngine, InitiativeManager
from core.learning import ExperientialLearningManager
from core.mental_state import ROBYMentalState
from core.planning import PlanningManager
from core.presence import PresenceManager
from core.reasoning import ReasoningManager
from core.reflection import ReflectionManager
from core.relationship_memory import RelationshipMemoryManager
from core.routines_habits import RoutineHabitEngine, RoutineHabitManager
from core.social_regulation import SocialRegulationEngine, SocialRegulationManager
from core.stable_personality import StablePersonalityEngine, StablePersonalityManager
from core.working_memory import WorkingMemoryManager


def _contextual_snapshots(text: str):
    cycle_result = CognitiveCycleManager().run(
        CognitiveCycleContext(
            input_text=text,
            identity=ROBYIdentity(),
            mental_state=ROBYMentalState(),
            attention=AttentionManager(),
            working_memory=WorkingMemoryManager(),
            reasoning=ReasoningManager(),
            planning=PlanningManager(),
            learning=ExperientialLearningManager(),
            reflection=ReflectionManager(),
            source="test",
        )
    )
    now = datetime(2026, 7, 9, tzinfo=timezone.utc)
    presence = PresenceManager()
    presence_snapshot = presence.observe_user_turn(
        text,
        cycle_result=cycle_result,
        now=now,
    )
    relationship = RelationshipMemoryManager()
    relationship_snapshot = relationship.observe_turn(
        text,
        presence=presence_snapshot,
        now=now,
    )
    initiative_snapshot = InitiativeEngine().evaluate_turn(
        text,
        presence=presence_snapshot,
        relationship=relationship_snapshot,
        now=now,
    )
    social_snapshot = SocialRegulationEngine().regulate_turn(
        text,
        presence=presence_snapshot,
        relationship=relationship_snapshot,
        initiative=initiative_snapshot,
        now=now,
    )
    personality_snapshot = StablePersonalityEngine().evaluate_turn(
        text,
        presence=presence_snapshot,
        relationship=relationship_snapshot,
        social_regulation=social_snapshot,
        now=now,
    )
    routine_snapshot = RoutineHabitEngine().evaluate_turn(
        text,
        presence=presence_snapshot,
        relationship=relationship_snapshot,
        personality=personality_snapshot,
        now=now,
    )
    return (
        relationship_snapshot,
        initiative_snapshot,
        personality_snapshot,
        routine_snapshot,
    )


def test_collaboration_policy_validates_contract():
    with pytest.raises(ValueError):
        CollaborationPolicy(activation_threshold=-0.1)

    with pytest.raises(ValueError):
        CollaborationPolicy(activation_threshold=0.8, sustained_threshold=0.7)

    with pytest.raises(ValueError):
        CollaborationPolicy(sustained_threshold=0.9, completion_threshold=0.8)

    with pytest.raises(ValueError):
        CollaborationPolicy(max_next_steps=0)

    policy = CollaborationPolicy(activation_threshold=0.4)

    assert policy.activation_threshold == 0.4


def test_collaboration_snapshot_validates_contract():
    with pytest.raises(ValueError):
        CollaborationSnapshot(
            (),
            CollaborationStatus.OBSERVED,
            0.4,
            0.4,
            "objetivo",
            "foco",
            ("paso",),
        )

    with pytest.raises(ValueError):
        CollaborationSnapshot(
            (CollaborationSignal.SHARED_GOAL,),
            CollaborationStatus.OBSERVED,
            1.2,
            0.4,
            "objetivo",
            "foco",
            ("paso",),
        )

    with pytest.raises(ValueError):
        CollaborationSnapshot(
            (CollaborationSignal.SHARED_GOAL,),
            CollaborationStatus.OBSERVED,
            0.4,
            0.4,
            " ",
            "foco",
            ("paso",),
        )


def test_collaboration_engine_detects_long_running_milestone_workflow():
    text = "Seguimos con M57, mismo metodo, luego ruff, pytest y zip"
    snapshots = _contextual_snapshots(text)
    (
        relationship_snapshot,
        initiative_snapshot,
        personality_snapshot,
        routine,
    ) = snapshots
    engine = CollaborationEngine()

    snapshot = engine.evaluate_turn(
        text,
        relationship=relationship_snapshot,
        initiative=initiative_snapshot,
        personality=personality_snapshot,
        routine=routine,
        now=datetime(2026, 7, 9, tzinfo=timezone.utc),
    )

    assert CollaborationSignal.CONTINUATION in snapshot.normalized_signals
    assert CollaborationSignal.SHARED_GOAL in snapshot.normalized_signals
    assert CollaborationSignal.CHECKPOINT in snapshot.normalized_signals
    assert CollaborationSignal.DELIVERY in snapshot.normalized_signals
    assert snapshot.normalized_status in {
        CollaborationStatus.ACTIVE,
        CollaborationStatus.SUSTAINED,
        CollaborationStatus.COMPLETED,
    }
    assert snapshot.relationship_snapshot_id == relationship_snapshot.snapshot_id
    assert snapshot.routine_snapshot_id == routine.snapshot_id
    assert "Colaboración prolongada M57:" in snapshot.system_prompt_lines()


def test_collaboration_manager_uses_history_for_continuity():
    manager = CollaborationManager()

    first = manager.observe_turn("Definimos un objetivo compartido")
    second = manager.observe_turn("Revisamos el siguiente paso")

    assert manager.history == (first, second)
    assert CollaborationSignal.CONTINUATION in second.normalized_signals
    assert second.continuity_score >= first.continuity_score


def test_collaboration_engine_rejects_naive_datetime():
    engine = CollaborationEngine()

    with pytest.raises(ValueError):
        engine.evaluate_turn("hola", now=datetime(2026, 7, 9))


def test_collaboration_to_dict_is_serializable():
    snapshot = CollaborationEngine().evaluate_turn("Seguimos con M57 y zip")
    payload = snapshot.to_dict()

    assert payload["status"] == snapshot.normalized_status.value
    assert "continuation" in payload["signals"]
    assert payload["id"] == snapshot.snapshot_id


def test_collaboration_manager_system_prompt_without_history():
    manager = CollaborationManager()

    assert manager.system_prompt_lines() == (
        "Colaboración prolongada M57: sin evaluación aún.",
    )


def test_cognitive_pipeline_includes_m57_long_term_collaboration(tmp_path):
    store = CognitiveMemoryStore(
        CognitiveMemoryStoreConfig(db_path=tmp_path / "brain.sqlite")
    )
    collaboration = CollaborationManager()
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
        collaboration=collaboration,
    )

    result = pipeline.process_turn(
        "Seguimos con M57, mismo metodo, ruff, pytest y zip",
        call_llm=False,
    )

    assert result.collaboration is collaboration
    assert collaboration.last_snapshot is not None
    assert "Colaboración prolongada M57:" in result.system_prompt
    assert "Rutinas y hábitos M56:" in result.system_prompt
    assert "Personalidad estable M55:" in result.system_prompt
