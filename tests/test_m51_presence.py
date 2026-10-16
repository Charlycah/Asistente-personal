from datetime import datetime, timedelta, timezone

import pytest

from core.attention import AttentionManager
from core.cognitive_cycle import CognitiveCycleContext, CognitiveCycleManager
from core.cognitive_memory_integration import CognitiveMemoryIntegration
from core.cognitive_memory_store import CognitiveMemoryStore, CognitiveMemoryStoreConfig
from core.cognitive_pipeline import CognitivePipeline
from core.identity import ROBYIdentity
from core.learning import ExperientialLearningManager
from core.mental_state import ROBYMentalState
from core.planning import PlanningManager
from core.presence import (
    PresenceManager,
    PresenceMode,
    PresencePolicy,
    PresenceSignal,
    PresenceSignalKind,
    PresenceSnapshot,
)
from core.reasoning import ReasoningManager
from core.reflection import ReflectionManager
from core.working_memory import WorkingMemoryManager


def test_presence_signal_validates_contract():
    with pytest.raises(ValueError):
        PresenceSignal(PresenceSignalKind.USER_TURN, " ")

    with pytest.raises(ValueError):
        PresenceSignal(PresenceSignalKind.USER_TURN, "ok", weight=1.5)

    with pytest.raises(ValueError):
        PresenceSignal(
            PresenceSignalKind.USER_TURN,
            "ok",
            created_at=datetime(2026, 7, 9),
        )


def test_presence_policy_requires_ordered_thresholds():
    with pytest.raises(ValueError):
        PresencePolicy(
            recovery_threshold=0.8,
            attentive_threshold=0.5,
            accompanying_threshold=0.9,
        )


def test_presence_manager_observes_user_turn_as_available():
    manager = PresenceManager()
    now = datetime(2026, 7, 9, tzinfo=timezone.utc)

    snapshot = manager.observe_user_turn("hola ROBY", now=now)

    assert snapshot.normalized_mode is PresenceMode.RECOVERING
    assert snapshot.continuity_score > 0
    assert snapshot.last_user_seen_at == now
    assert snapshot.is_continuous is False
    assert manager.last_snapshot is snapshot


def test_presence_becomes_attentive_after_completed_cycle():
    cycle = CognitiveCycleManager()
    result = cycle.run(
        CognitiveCycleContext(
            "acompañame con esta tarea",
            identity=ROBYIdentity(),
            mental_state=ROBYMentalState(),
            attention=AttentionManager(),
            working_memory=WorkingMemoryManager(),
            reasoning=ReasoningManager(),
            planning=PlanningManager(),
            learning=ExperientialLearningManager(),
            reflection=ReflectionManager(),
        )
    )
    manager = PresenceManager()

    snapshot = manager.observe_user_turn(
        "acompañame con esta tarea",
        cycle_result=result,
        now=result.completed_at,
    )

    assert snapshot.normalized_mode in {
        PresenceMode.ATTENTIVE,
        PresenceMode.ACCOMPANYING,
    }
    assert snapshot.last_cycle_id == result.cycle_id
    assert snapshot.is_continuous is True
    assert "Presencia continua M51:" in snapshot.system_prompt_lines()


def test_presence_detects_silence_without_autonomous_action():
    manager = PresenceManager()
    first = datetime(2026, 7, 9, 12, tzinfo=timezone.utc)
    manager.observe_user_turn("hola", now=first)

    snapshot = manager.observe_silence(now=first + timedelta(hours=1))

    assert snapshot.normalized_mode is PresenceMode.DORMANT
    assert snapshot.continuity_score < 0.28
    assert snapshot.signals[0].normalized_kind is PresenceSignalKind.SILENCE


def test_presence_snapshot_to_dict_is_auditable():
    snapshot = PresenceSnapshot(
        PresenceMode.AVAILABLE,
        0.5,
        signals=(PresenceSignal(PresenceSignalKind.USER_TURN, "turno"),),
    )

    data = snapshot.to_dict()

    assert data["mode"] == "available"
    assert data["continuity_score"] == 0.5
    assert data["signals"][0]["kind"] == "user_turn"


def test_cognitive_pipeline_includes_m51_presence(tmp_path):
    store = CognitiveMemoryStore(
        CognitiveMemoryStoreConfig(db_path=tmp_path / "brain.sqlite")
    )
    presence = PresenceManager()
    cycle = CognitiveCycleManager()
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
        cognitive_cycle=cycle,
        presence=presence,
    )

    result = pipeline.process_turn("ROBY, seguí presente conmigo", call_llm=False)

    assert result.presence is presence
    assert presence.last_snapshot is not None
    assert presence.last_snapshot.last_cycle_id == cycle.last_result.cycle_id
    assert "Presencia continua M51:" in result.system_prompt
