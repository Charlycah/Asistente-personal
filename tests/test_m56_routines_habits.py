from datetime import datetime, timezone

import pytest

from core.attention import AttentionManager
from core.cognitive_cycle import CognitiveCycleContext, CognitiveCycleManager
from core.cognitive_memory_integration import CognitiveMemoryIntegration
from core.cognitive_memory_store import CognitiveMemoryStore, CognitiveMemoryStoreConfig
from core.cognitive_pipeline import CognitivePipeline
from core.identity import ROBYIdentity
from core.initiative import InitiativeEngine, InitiativeManager
from core.learning import ExperientialLearningManager
from core.mental_state import ROBYMentalState
from core.planning import PlanningManager
from core.presence import PresenceManager
from core.reasoning import ReasoningManager
from core.reflection import ReflectionManager
from core.relationship_memory import RelationshipMemoryManager
from core.routines_habits import (
    HabitSupportLevel,
    RoutineHabitEngine,
    RoutineHabitManager,
    RoutineHabitPolicy,
    RoutineHabitSnapshot,
    RoutineSignal,
)
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
    presence = PresenceManager()
    presence_snapshot = presence.observe_user_turn(
        text,
        cycle_result=cycle_result,
        now=datetime(2026, 7, 9, tzinfo=timezone.utc),
    )
    relationship = RelationshipMemoryManager()
    relationship_snapshot = relationship.observe_turn(
        text,
        presence=presence_snapshot,
        now=datetime(2026, 7, 9, tzinfo=timezone.utc),
    )
    initiative_snapshot = InitiativeEngine().evaluate_turn(
        text,
        presence=presence_snapshot,
        relationship=relationship_snapshot,
        now=datetime(2026, 7, 9, tzinfo=timezone.utc),
    )
    social_snapshot = SocialRegulationEngine().regulate_turn(
        text,
        presence=presence_snapshot,
        relationship=relationship_snapshot,
        initiative=initiative_snapshot,
        now=datetime(2026, 7, 9, tzinfo=timezone.utc),
    )
    personality_snapshot = StablePersonalityEngine().evaluate_turn(
        text,
        presence=presence_snapshot,
        relationship=relationship_snapshot,
        social_regulation=social_snapshot,
        now=datetime(2026, 7, 9, tzinfo=timezone.utc),
    )
    return presence_snapshot, relationship_snapshot, personality_snapshot


def test_routine_habit_policy_validates_contract():
    with pytest.raises(ValueError):
        RoutineHabitPolicy(minimum_confidence=1.2)

    with pytest.raises(ValueError):
        RoutineHabitPolicy(continuity_threshold=0.8, stabilization_threshold=0.7)

    with pytest.raises(ValueError):
        RoutineHabitPolicy(max_guidance_items=0)

    policy = RoutineHabitPolicy(minimum_confidence=0.3)

    assert policy.minimum_confidence == 0.3


def test_routine_habit_snapshot_validates_contract():
    with pytest.raises(ValueError):
        RoutineHabitSnapshot((), HabitSupportLevel.OBSERVE, 0.4, 0.4, "ok", ("guía",))

    with pytest.raises(ValueError):
        RoutineHabitSnapshot(
            (RoutineSignal.SUPPORT,),
            HabitSupportLevel.OBSERVE,
            1.4,
            0.4,
            "ok",
            ("guía",),
        )

    with pytest.raises(ValueError):
        RoutineHabitSnapshot(
            (RoutineSignal.SUPPORT,),
            HabitSupportLevel.OBSERVE,
            0.4,
            0.4,
            " ",
            ("guía",),
        )


def test_routine_habit_engine_detects_checkpoint_workflow():
    snapshots = _contextual_snapshots(
        "Seguimos con M56, mismo metodo, luego ruff, pytest y zip"
    )
    presence_snapshot, relationship_snapshot, personality_snapshot = snapshots
    engine = RoutineHabitEngine()

    snapshot = engine.evaluate_turn(
        "Seguimos con M56, mismo metodo, luego ruff, pytest y zip",
        presence=presence_snapshot,
        relationship=relationship_snapshot,
        personality=personality_snapshot,
        now=datetime(2026, 7, 9, tzinfo=timezone.utc),
    )

    assert RoutineSignal.CONTINUATION in snapshot.normalized_signals
    assert RoutineSignal.CHECKPOINT in snapshot.normalized_signals
    assert snapshot.normalized_support_level in {
        HabitSupportLevel.SUGGEST,
        HabitSupportLevel.STABILIZE,
    }
    assert snapshot.personality_snapshot_id == personality_snapshot.snapshot_id
    assert "Rutinas y hábitos M56:" in snapshot.system_prompt_lines()


def test_routine_habit_engine_uses_history_as_repetition_signal():
    manager = RoutineHabitManager()

    first = manager.observe_turn("Hola ROBY")
    second = manager.observe_turn("Seguimos con el mismo método")

    assert manager.history == (first, second)
    assert RoutineSignal.REPETITION in second.normalized_signals
    assert second.continuity_score >= first.continuity_score


def test_routine_habit_engine_rejects_naive_datetime():
    engine = RoutineHabitEngine()

    with pytest.raises(ValueError):
        engine.evaluate_turn("hola", now=datetime(2026, 7, 9))


def test_routine_habit_to_dict_is_serializable():
    snapshot = RoutineHabitEngine().evaluate_turn("Recordá esta rutina de trabajo")
    payload = snapshot.to_dict()

    assert payload["support_level"] == snapshot.normalized_support_level.value
    assert "support" in payload["signals"]
    assert payload["id"] == snapshot.snapshot_id


def test_routine_habit_manager_system_prompt_without_history():
    manager = RoutineHabitManager()

    assert manager.system_prompt_lines() == (
        "Rutinas y hábitos M56: sin evaluación aún.",
    )


def test_cognitive_pipeline_includes_m56_routines_and_habits(tmp_path):
    store = CognitiveMemoryStore(
        CognitiveMemoryStoreConfig(db_path=tmp_path / "brain.sqlite")
    )
    presence = PresenceManager()
    relationship_memory = RelationshipMemoryManager()
    initiative = InitiativeManager()
    social_regulation = SocialRegulationManager()
    stable_personality = StablePersonalityManager()
    routines_habits = RoutineHabitManager()
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
        presence=presence,
        relationship_memory=relationship_memory,
        initiative=initiative,
        social_regulation=social_regulation,
        stable_personality=stable_personality,
        routines_habits=routines_habits,
    )

    result = pipeline.process_turn(
        "Seguimos con M56, mismo metodo, ruff, pytest y zip",
        call_llm=False,
    )

    assert result.routines_habits is routines_habits
    assert routines_habits.last_snapshot is not None
    assert "Rutinas y hábitos M56:" in result.system_prompt
    assert "Personalidad estable M55:" in result.system_prompt
    assert "Regulación social M54:" in result.system_prompt
    assert "Iniciativa controlada M53:" in result.system_prompt
    assert "Memoria de convivencia M52:" in result.system_prompt
    assert "Presencia continua M51:" in result.system_prompt
