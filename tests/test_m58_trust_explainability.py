from datetime import datetime, timezone

import pytest

from core.attention import AttentionManager
from core.cognitive_cycle import CognitiveCycleContext, CognitiveCycleManager
from core.cognitive_memory_integration import CognitiveMemoryIntegration
from core.cognitive_memory_store import CognitiveMemoryStore, CognitiveMemoryStoreConfig
from core.cognitive_pipeline import CognitivePipeline
from core.collaboration import CollaborationEngine, CollaborationManager
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
from core.trust_explainability import (
    TrustExplainabilityEngine,
    TrustExplainabilityManager,
    TrustExplainabilityPolicy,
    TrustExplainabilitySnapshot,
    TrustPosture,
    TrustSignal,
)
from core.working_memory import WorkingMemoryManager


def _contextual_snapshots(text: str):
    now = datetime(2026, 7, 9, tzinfo=timezone.utc)
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
    collaboration_snapshot = CollaborationEngine().evaluate_turn(
        text,
        relationship=relationship_snapshot,
        initiative=initiative_snapshot,
        personality=personality_snapshot,
        routine=routine_snapshot,
        now=now,
    )
    return (
        relationship_snapshot,
        initiative_snapshot,
        social_snapshot,
        personality_snapshot,
        collaboration_snapshot,
    )


def test_trust_policy_validates_contract():
    with pytest.raises(ValueError):
        TrustExplainabilityPolicy(explain_threshold=-0.1)

    with pytest.raises(ValueError):
        TrustExplainabilityPolicy(explain_threshold=0.7, verify_threshold=0.6)

    with pytest.raises(ValueError):
        TrustExplainabilityPolicy(verify_threshold=0.9, audit_threshold=0.8)

    with pytest.raises(ValueError):
        TrustExplainabilityPolicy(max_explanation_items=0)

    policy = TrustExplainabilityPolicy(explain_threshold=0.35)

    assert policy.explain_threshold == 0.35


def test_trust_snapshot_validates_contract():
    with pytest.raises(ValueError):
        TrustExplainabilitySnapshot(
            (),
            TrustPosture.BASELINE,
            0.4,
            0.4,
            "racional",
            ("item",),
            (),
        )

    with pytest.raises(ValueError):
        TrustExplainabilitySnapshot(
            (TrustSignal.RELIABILITY,),
            TrustPosture.BASELINE,
            1.4,
            0.4,
            "racional",
            ("item",),
            (),
        )

    with pytest.raises(ValueError):
        TrustExplainabilitySnapshot(
            (TrustSignal.RELIABILITY,),
            TrustPosture.BASELINE,
            0.4,
            0.4,
            " ",
            ("item",),
            (),
        )


def test_trust_engine_detects_validation_and_explanation_workflow():
    text = "Explica la confianza: ruff check, pytest, trazabilidad y sin regresión"
    snapshots = _contextual_snapshots(text)
    (
        relationship_snapshot,
        initiative_snapshot,
        social_snapshot,
        personality_snapshot,
        collaboration_snapshot,
    ) = snapshots
    engine = TrustExplainabilityEngine()

    snapshot = engine.evaluate_turn(
        text,
        relationship=relationship_snapshot,
        initiative=initiative_snapshot,
        social_regulation=social_snapshot,
        personality=personality_snapshot,
        collaboration=collaboration_snapshot,
        now=datetime(2026, 7, 9, tzinfo=timezone.utc),
    )

    assert TrustSignal.EXPLANATION_REQUEST in snapshot.normalized_signals
    assert TrustSignal.VALIDATION in snapshot.normalized_signals
    assert TrustSignal.TRACEABILITY in snapshot.normalized_signals
    assert snapshot.normalized_posture in {
        TrustPosture.EXPLAIN,
        TrustPosture.VERIFY,
        TrustPosture.AUDIT,
    }
    assert snapshot.relationship_snapshot_id == relationship_snapshot.snapshot_id
    assert snapshot.collaboration_snapshot_id == collaboration_snapshot.snapshot_id
    assert "Confianza y explicabilidad M58:" in snapshot.system_prompt_lines()


def test_trust_manager_uses_history_for_traceability():
    manager = TrustExplainabilityManager()

    first = manager.observe_turn("Validamos con pytest")
    second = manager.observe_turn("Seguimos explicando pytest y la trazabilidad")

    assert manager.history == (first, second)
    assert TrustSignal.TRACEABILITY in second.normalized_signals
    assert second.confidence_score >= first.confidence_score


def test_trust_engine_rejects_naive_datetime():
    engine = TrustExplainabilityEngine()

    with pytest.raises(ValueError):
        engine.evaluate_turn("hola", now=datetime(2026, 7, 9))


def test_trust_to_dict_is_serializable():
    snapshot = TrustExplainabilityEngine().evaluate_turn("Confianza con pytest")
    payload = snapshot.to_dict()

    assert payload["posture"] == snapshot.normalized_posture.value
    assert "validation" in payload["signals"]
    assert payload["id"] == snapshot.snapshot_id


def test_trust_manager_system_prompt_without_history():
    manager = TrustExplainabilityManager()

    assert manager.system_prompt_lines() == (
        "Confianza y explicabilidad M58: sin evaluación aún.",
    )


def test_cognitive_pipeline_includes_m58_trust_explainability(tmp_path):
    store = CognitiveMemoryStore(
        CognitiveMemoryStoreConfig(db_path=tmp_path / "brain.sqlite")
    )
    trust = TrustExplainabilityManager()
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
        trust_explainability=trust,
    )

    result = pipeline.process_turn(
        "Explica confianza con ruff check, pytest, trazabilidad y zip",
        call_llm=False,
    )

    assert result.trust_explainability is trust
    assert trust.last_snapshot is not None
    assert "Confianza y explicabilidad M58:" in result.system_prompt
    assert "Colaboración prolongada M57:" in result.system_prompt
    assert "Rutinas y hábitos M56:" in result.system_prompt
