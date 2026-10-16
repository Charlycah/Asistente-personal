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
from core.social_regulation import SocialRegulationEngine, SocialRegulationManager
from core.stable_personality import (
    PersonalityExpression,
    PersonalityTrait,
    StablePersonalityEngine,
    StablePersonalityManager,
    StablePersonalityPolicy,
    StablePersonalitySnapshot,
)
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
    return presence_snapshot, relationship_snapshot, social_snapshot


def test_stable_personality_policy_validates_contract():
    with pytest.raises(ValueError):
        StablePersonalityPolicy(baseline_traits=())

    with pytest.raises(ValueError):
        StablePersonalityPolicy(minimum_consistency=1.2)

    policy = StablePersonalityPolicy(
        baseline_traits=(PersonalityTrait.CALM, PersonalityTrait.PRECISE),
        minimum_consistency=0.8,
    )

    assert policy.normalized_traits == (
        PersonalityTrait.CALM,
        PersonalityTrait.PRECISE,
    )


def test_stable_personality_snapshot_validates_contract():
    with pytest.raises(ValueError):
        StablePersonalitySnapshot(
            PersonalityExpression.NEUTRAL,
            (),
            0.8,
            "ok",
            ("guía",),
        )

    with pytest.raises(ValueError):
        StablePersonalitySnapshot(
            PersonalityExpression.NEUTRAL,
            (PersonalityTrait.CALM,),
            1.4,
            "ok",
            ("guía",),
        )

    with pytest.raises(ValueError):
        StablePersonalitySnapshot(
            PersonalityExpression.NEUTRAL,
            (PersonalityTrait.CALM,),
            0.8,
            " ",
            ("guía",),
        )


def test_stable_personality_preserves_baseline_without_context():
    engine = StablePersonalityEngine()

    snapshot = engine.evaluate_turn("Hola ROBY")

    assert snapshot.normalized_expression is PersonalityExpression.NEUTRAL
    assert PersonalityTrait.CONSISTENT in snapshot.normalized_traits
    assert snapshot.consistency_score >= 0.72
    assert "Personalidad estable M55:" in snapshot.system_prompt_lines()


def test_stable_personality_becomes_repairing_with_social_repair():
    presence_snapshot, relationship_snapshot, social_snapshot = _contextual_snapshots(
        "Falló ruff, arreglamos y después corro pytest"
    )
    engine = StablePersonalityEngine()

    snapshot = engine.evaluate_turn(
        "Falló ruff, arreglamos y después corro pytest",
        presence=presence_snapshot,
        relationship=relationship_snapshot,
        social_regulation=social_snapshot,
    )

    assert snapshot.normalized_expression is PersonalityExpression.REPAIRING
    assert snapshot.social_regulation_snapshot_id == social_snapshot.snapshot_id
    assert "reparación" in " ".join(snapshot.guidance)


def test_stable_personality_respects_boundary_with_direct_expression():
    presence_snapshot, relationship_snapshot, social_snapshot = _contextual_snapshots(
        "No hagas cambios sin avisarme"
    )
    engine = StablePersonalityEngine()

    snapshot = engine.evaluate_turn(
        "No hagas cambios sin avisarme",
        presence=presence_snapshot,
        relationship=relationship_snapshot,
        social_regulation=social_snapshot,
    )

    assert snapshot.normalized_expression is PersonalityExpression.DIRECT
    assert "límite" in " ".join(snapshot.guidance)
    assert snapshot.presence_snapshot_id == presence_snapshot.snapshot_id


def test_stable_personality_manager_keeps_history():
    manager = StablePersonalityManager()

    snapshot = manager.observe_turn("Perfecto, seguimos")

    assert manager.last_snapshot is snapshot
    assert manager.history == (snapshot,)
    assert snapshot.to_dict()["expression"] == snapshot.normalized_expression.value


def test_stable_personality_rejects_naive_datetime():
    engine = StablePersonalityEngine()

    with pytest.raises(ValueError):
        engine.evaluate_turn("hola", now=datetime(2026, 7, 9))


def test_cognitive_pipeline_includes_m55_stable_personality(tmp_path):
    store = CognitiveMemoryStore(
        CognitiveMemoryStoreConfig(db_path=tmp_path / "brain.sqlite")
    )
    presence = PresenceManager()
    relationship_memory = RelationshipMemoryManager()
    initiative = InitiativeManager()
    social_regulation = SocialRegulationManager()
    stable_personality = StablePersonalityManager()
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
    )

    result = pipeline.process_turn(
        "ROBY, seguimos con M55, mismo metodo y luego me pasas el zip",
        call_llm=False,
    )

    assert result.stable_personality is stable_personality
    assert stable_personality.last_snapshot is not None
    assert "Personalidad estable M55:" in result.system_prompt
    assert "Regulación social M54:" in result.system_prompt
    assert "Iniciativa controlada M53:" in result.system_prompt
    assert "Memoria de convivencia M52:" in result.system_prompt
    assert "Presencia continua M51:" in result.system_prompt
