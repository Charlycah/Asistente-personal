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
from core.social_regulation import (
    SocialDistance,
    SocialRegulationAction,
    SocialRegulationEngine,
    SocialRegulationManager,
    SocialRegulationPolicy,
    SocialRegulationSnapshot,
    SocialTone,
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
    return presence_snapshot, relationship_snapshot, initiative_snapshot


def test_social_regulation_policy_validates_thresholds():
    with pytest.raises(ValueError):
        SocialRegulationPolicy(high_trust_threshold=0.2, low_trust_threshold=0.4)

    policy = SocialRegulationPolicy(
        high_trust_threshold=0.7,
        low_trust_threshold=0.3,
        familiar_continuity_threshold=0.6,
    )

    assert policy.high_trust_threshold == 0.7
    assert policy.low_trust_threshold == 0.3


def test_social_regulation_snapshot_validates_contract():
    with pytest.raises(ValueError):
        SocialRegulationSnapshot(
            SocialTone.NEUTRAL,
            SocialDistance.BALANCED,
            SocialRegulationAction.ACKNOWLEDGE,
            1.2,
            "ok",
            ("guía",),
        )

    with pytest.raises(ValueError):
        SocialRegulationSnapshot(
            SocialTone.NEUTRAL,
            SocialDistance.BALANCED,
            SocialRegulationAction.ACKNOWLEDGE,
            0.8,
            " ",
            ("guía",),
        )

    with pytest.raises(ValueError):
        SocialRegulationSnapshot(
            SocialTone.NEUTRAL,
            SocialDistance.BALANCED,
            SocialRegulationAction.ACKNOWLEDGE,
            0.8,
            "ok",
            (),
        )


def test_social_regulation_respects_explicit_boundary():
    (
        presence_snapshot,
        relationship_snapshot,
        initiative_snapshot,
    ) = _contextual_snapshots("No hagas nada todavía y no toques el pipeline")
    engine = SocialRegulationEngine()

    snapshot = engine.regulate_turn(
        "No hagas nada todavía y no toques el pipeline",
        presence=presence_snapshot,
        relationship=relationship_snapshot,
        initiative=initiative_snapshot,
    )

    assert snapshot.normalized_tone is SocialTone.BOUNDARY_RESPECTING
    assert snapshot.normalized_action is SocialRegulationAction.RESPECT_BOUNDARY
    assert "Reconocer el límite" in " ".join(snapshot.guidance)


def test_social_regulation_repairs_after_error_signal():
    (
        presence_snapshot,
        relationship_snapshot,
        initiative_snapshot,
    ) = _contextual_snapshots("Falló ruff, arreglamos y después corro pytest")
    engine = SocialRegulationEngine()

    snapshot = engine.regulate_turn(
        "Falló ruff, arreglamos y después corro pytest",
        presence=presence_snapshot,
        relationship=relationship_snapshot,
        initiative=initiative_snapshot,
    )

    assert snapshot.normalized_tone is SocialTone.REPAIRING
    assert snapshot.normalized_action is SocialRegulationAction.REPAIR_TRUST
    assert "reparación" in " ".join(snapshot.guidance)


def test_social_regulation_confirms_next_step_when_initiative_is_allowed():
    (
        presence_snapshot,
        relationship_snapshot,
        initiative_snapshot,
    ) = _contextual_snapshots("Seguimos con M54, mismo metodo y luego el zip")
    engine = SocialRegulationEngine()

    snapshot = engine.regulate_turn(
        "Seguimos con M54, mismo metodo y luego el zip",
        presence=presence_snapshot,
        relationship=relationship_snapshot,
        initiative=initiative_snapshot,
    )

    assert initiative_snapshot.should_intervene is True
    assert snapshot.normalized_tone is SocialTone.SUPPORTIVE
    assert snapshot.normalized_action is SocialRegulationAction.CONFIRM_NEXT_STEP
    assert snapshot.initiative_snapshot_id == initiative_snapshot.snapshot_id


def test_social_regulation_manager_keeps_auditable_history():
    manager = SocialRegulationManager()

    snapshot = manager.observe_turn("Perfecto, seguimos")

    assert manager.last_snapshot is snapshot
    assert manager.history == (snapshot,)
    assert "Regulación social M54:" in snapshot.system_prompt_lines()
    assert snapshot.to_dict()["tone"] == snapshot.normalized_tone.value


def test_social_regulation_rejects_naive_datetime():
    engine = SocialRegulationEngine()

    with pytest.raises(ValueError):
        engine.regulate_turn("hola", now=datetime(2026, 7, 9))


def test_cognitive_pipeline_includes_m54_social_regulation(tmp_path):
    store = CognitiveMemoryStore(
        CognitiveMemoryStoreConfig(db_path=tmp_path / "brain.sqlite")
    )
    presence = PresenceManager()
    relationship_memory = RelationshipMemoryManager()
    initiative = InitiativeManager()
    social_regulation = SocialRegulationManager()
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
    )

    result = pipeline.process_turn(
        "ROBY, seguimos con M54, mismo metodo y luego me pasas el zip",
        call_llm=False,
    )

    assert result.social_regulation is social_regulation
    assert social_regulation.last_snapshot is not None
    assert "Regulación social M54:" in result.system_prompt
    assert "Iniciativa controlada M53:" in result.system_prompt
    assert "Memoria de convivencia M52:" in result.system_prompt
    assert "Presencia continua M51:" in result.system_prompt
