from datetime import datetime, timezone

import pytest

from core.attention import AttentionManager
from core.cognitive_cycle import CognitiveCycleManager
from core.cognitive_memory_integration import CognitiveMemoryIntegration
from core.cognitive_memory_store import CognitiveMemoryStore, CognitiveMemoryStoreConfig
from core.cognitive_pipeline import CognitivePipeline
from core.identity import ROBYIdentity
from core.learning import ExperientialLearningManager
from core.mental_state import ROBYMentalState
from core.planning import PlanningManager
from core.presence import PresenceManager
from core.reasoning import ReasoningManager
from core.reflection import ReflectionManager
from core.relationship_memory import (
    RelationshipMemoryAction,
    RelationshipMemoryCandidate,
    RelationshipMemoryEngine,
    RelationshipMemoryKind,
    RelationshipMemoryManager,
    RelationshipMemoryPolicy,
    RelationshipMemoryRecord,
    RelationshipMemorySnapshot,
)
from core.working_memory import WorkingMemoryManager


def test_relationship_record_validates_contract():
    with pytest.raises(ValueError):
        RelationshipMemoryRecord(" ", RelationshipMemoryKind.USER_PREFERENCE, 0.8, "ok")

    with pytest.raises(ValueError):
        RelationshipMemoryRecord("x", RelationshipMemoryKind.USER_PREFERENCE, 1.2, "ok")

    with pytest.raises(ValueError):
        RelationshipMemoryRecord(
            "x",
            RelationshipMemoryKind.USER_PREFERENCE,
            0.8,
            "ok",
            created_at=datetime(2026, 7, 9),
        )


def test_relationship_policy_requires_ordered_thresholds():
    with pytest.raises(ValueError):
        RelationshipMemoryPolicy(remember_threshold=0.4, review_threshold=0.5)

    policy = RelationshipMemoryPolicy(remember_threshold=0.7, review_threshold=0.4)

    assert policy.action_for(0.8) is RelationshipMemoryAction.REMEMBER
    assert policy.action_for(0.5) is RelationshipMemoryAction.REVIEW
    assert policy.action_for(0.2) is RelationshipMemoryAction.IGNORE


def test_relationship_engine_remembers_project_rhythm():
    engine = RelationshipMemoryEngine()
    now = datetime(2026, 7, 9, tzinfo=timezone.utc)

    snapshot = engine.evaluate_turn(
        "Seguimos con M52, mismo metodo, despues me pasas el zip",
        now=now,
    )

    assert snapshot.has_context is True
    assert (
        snapshot.records[-1].normalized_kind is RelationshipMemoryKind.USER_PREFERENCE
    )
    assert snapshot.records[-1].confidence >= 0.72
    assert snapshot.created_at == now


def test_relationship_engine_reviews_weak_interaction_pattern():
    engine = RelationshipMemoryEngine()

    snapshot = engine.evaluate_turn(
        "Necesito que analices esta idea general para más adelante",
    )

    assert snapshot.records == ()
    assert len(snapshot.reviewed_candidates) == 1
    assert (
        snapshot.reviewed_candidates[0].normalized_action
        is RelationshipMemoryAction.REVIEW
    )


def test_relationship_engine_ignores_transient_context():
    engine = RelationshipMemoryEngine()

    snapshot = engine.evaluate_turn("Hoy lo vemos después")

    assert snapshot.records == ()
    assert len(snapshot.ignored_candidates) == 1
    assert (
        snapshot.ignored_candidates[0].normalized_kind
        is RelationshipMemoryKind.TRANSIENT
    )


def test_relationship_manager_accumulates_records_with_presence():
    presence = PresenceManager()
    presence_snapshot = presence.observe_user_turn(
        "Continuamos con el mismo método",
        now=datetime(2026, 7, 9, tzinfo=timezone.utc),
    )
    manager = RelationshipMemoryManager()

    snapshot = manager.observe_turn(
        "Continuamos con el mismo método y calidad",
        presence=presence_snapshot,
    )

    assert manager.last_snapshot is snapshot
    assert snapshot.presence_snapshot_id == presence_snapshot.snapshot_id
    assert snapshot.continuity_score == presence_snapshot.continuity_score
    assert snapshot.familiarity_score > 0
    assert "Memoria de convivencia M52:" in snapshot.system_prompt_lines()


def test_relationship_snapshot_to_dict_is_auditable():
    candidate = RelationshipMemoryCandidate(
        "prefiero respuestas breves",
        RelationshipMemoryKind.USER_PREFERENCE,
        RelationshipMemoryAction.REMEMBER,
        0.8,
        "preference_supports_continuity",
    )
    record = candidate.to_record(created_at=datetime(2026, 7, 9, tzinfo=timezone.utc))
    snapshot = RelationshipMemorySnapshot(0.4, 0.5, 0.6, records=(record,))

    data = snapshot.to_dict()

    assert data["has_context"] is True
    assert data["records"][0]["kind"] == "user_preference"
    assert data["familiarity_score"] == 0.4


def test_cognitive_pipeline_includes_m52_relationship_memory(tmp_path):
    store = CognitiveMemoryStore(
        CognitiveMemoryStoreConfig(db_path=tmp_path / "brain.sqlite")
    )
    presence = PresenceManager()
    relationship_memory = RelationshipMemoryManager()
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
        relationship_memory=relationship_memory,
    )

    result = pipeline.process_turn(
        "ROBY, seguimos con el mismo metodo y despues me pasas el zip",
        call_llm=False,
    )

    assert result.relationship_memory is relationship_memory
    assert relationship_memory.last_snapshot is not None
    assert relationship_memory.last_snapshot.has_context is True
    assert "Memoria de convivencia M52:" in result.system_prompt
    assert "Presencia continua M51:" in result.system_prompt
