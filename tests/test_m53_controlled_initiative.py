from datetime import datetime, timezone

import pytest

from core.attention import AttentionManager
from core.cognitive_cycle import CognitiveCycleContext, CognitiveCycleManager
from core.cognitive_memory_integration import CognitiveMemoryIntegration
from core.cognitive_memory_store import CognitiveMemoryStore, CognitiveMemoryStoreConfig
from core.cognitive_pipeline import CognitivePipeline
from core.identity import ROBYIdentity
from core.initiative import (
    InitiativeCandidate,
    InitiativeDecision,
    InitiativeEngine,
    InitiativeKind,
    InitiativeManager,
    InitiativePolicy,
    InitiativeSnapshot,
)
from core.learning import ExperientialLearningManager
from core.mental_state import ROBYMentalState
from core.planning import PlanningManager
from core.presence import PresenceManager
from core.reasoning import ReasoningManager
from core.reflection import ReflectionManager
from core.relationship_memory import RelationshipMemoryManager
from core.working_memory import WorkingMemoryManager


def test_initiative_candidate_validates_contract():
    with pytest.raises(ValueError):
        InitiativeCandidate(InitiativeKind.OFFER_NEXT_STEP, 1.2, "ok")

    with pytest.raises(ValueError):
        InitiativeCandidate(InitiativeKind.OFFER_NEXT_STEP, 0.8, " ")

    with pytest.raises(ValueError):
        InitiativeCandidate(
            InitiativeKind.OFFER_NEXT_STEP,
            0.8,
            "ok",
            message=" ",
        )


def test_initiative_policy_requires_ordered_thresholds():
    with pytest.raises(ValueError):
        InitiativePolicy(propose_threshold=0.4, ask_threshold=0.5)

    policy = InitiativePolicy(
        propose_threshold=0.7,
        ask_threshold=0.5,
        minimum_trust_to_propose=0.2,
    )

    assert policy.propose_threshold == 0.7
    assert policy.ask_threshold == 0.5


def test_initiative_engine_proposes_next_step_with_context():
    presence = PresenceManager()
    cycle_result = CognitiveCycleManager().run(
        CognitiveCycleContext(
            input_text="Seguimos con M53, mismo metodo, despues me pasas el zip",
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
    presence_snapshot = presence.observe_user_turn(
        "Seguimos con M53, mismo metodo, despues me pasas el zip",
        cycle_result=cycle_result,
        now=datetime(2026, 7, 9, tzinfo=timezone.utc),
    )
    relationship = RelationshipMemoryManager()
    relationship_snapshot = relationship.observe_turn(
        "Seguimos con M53, mismo metodo, despues me pasas el zip",
        presence=presence_snapshot,
        now=datetime(2026, 7, 9, tzinfo=timezone.utc),
    )
    engine = InitiativeEngine()

    snapshot = engine.evaluate_turn(
        "Seguimos con M53, mismo metodo, despues me pasas el zip",
        presence=presence_snapshot,
        relationship=relationship_snapshot,
        now=datetime(2026, 7, 9, tzinfo=timezone.utc),
    )

    assert snapshot.normalized_decision is InitiativeDecision.PROPOSE
    assert snapshot.candidate.normalized_kind is InitiativeKind.OFFER_NEXT_STEP
    assert snapshot.should_intervene is True
    assert snapshot.intervention_text is not None
    assert snapshot.presence_snapshot_id == presence_snapshot.snapshot_id
    assert snapshot.relationship_snapshot_id == relationship_snapshot.snapshot_id


def test_initiative_engine_suppresses_without_relationship_trust():
    presence = PresenceManager()
    presence_snapshot = presence.observe_user_turn(
        "Seguimos con M53, mismo metodo",
        now=datetime(2026, 7, 9, tzinfo=timezone.utc),
    )
    engine = InitiativeEngine()

    snapshot = engine.evaluate_turn(
        "Seguimos con M53, mismo metodo",
        presence=presence_snapshot,
        relationship=None,
    )

    assert snapshot.normalized_decision is InitiativeDecision.SUPPRESS
    assert snapshot.should_intervene is False
    assert snapshot.restraint_reason == "relationship_trust_too_low"


def test_initiative_engine_respects_explicit_boundaries():
    presence = PresenceManager()
    presence_snapshot = presence.observe_user_turn(
        "No hagas nada todavía",
        now=datetime(2026, 7, 9, tzinfo=timezone.utc),
    )
    relationship = RelationshipMemoryManager()
    relationship_snapshot = relationship.observe_turn(
        "No hagas nada todavía y mantené el límite",
        presence=presence_snapshot,
    )
    engine = InitiativeEngine()

    snapshot = engine.evaluate_turn(
        "No hagas nada todavía",
        presence=presence_snapshot,
        relationship=relationship_snapshot,
    )

    assert snapshot.candidate.normalized_kind is InitiativeKind.PROTECT_BOUNDARY
    assert snapshot.normalized_decision is InitiativeDecision.WAIT
    assert snapshot.should_intervene is False
    assert snapshot.intervention_text is None


def test_initiative_manager_keeps_auditable_history():
    manager = InitiativeManager()

    snapshot = manager.observe_turn("Analizá esto sin tomar iniciativa")

    assert manager.last_snapshot is snapshot
    assert manager.history == (snapshot,)
    assert "Iniciativa controlada M53:" in snapshot.system_prompt_lines()
    assert snapshot.to_dict()["candidate"]["kind"] == "wait"


def test_initiative_snapshot_rejects_inconsistent_intervention():
    candidate = InitiativeCandidate(
        InitiativeKind.OFFER_NEXT_STEP,
        0.8,
        "ok",
        "Propongo avanzar.",
    )

    with pytest.raises(ValueError):
        InitiativeSnapshot(
            InitiativeDecision.PROPOSE,
            candidate,
            should_intervene=True,
            intervention_text=None,
        )

    with pytest.raises(ValueError):
        InitiativeSnapshot(
            InitiativeDecision.WAIT,
            candidate,
            should_intervene=False,
            intervention_text="No debería estar",
        )


def test_cognitive_pipeline_includes_m53_controlled_initiative(tmp_path):
    store = CognitiveMemoryStore(
        CognitiveMemoryStoreConfig(db_path=tmp_path / "brain.sqlite")
    )
    presence = PresenceManager()
    relationship_memory = RelationshipMemoryManager()
    initiative = InitiativeManager()
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
    )

    result = pipeline.process_turn(
        "ROBY, seguimos con M53, mismo metodo y luego me pasas el zip",
        call_llm=False,
    )

    assert result.initiative is initiative
    assert initiative.last_snapshot is not None
    assert initiative.last_snapshot.should_intervene is True
    assert "Iniciativa controlada M53:" in result.system_prompt
    assert "Memoria de convivencia M52:" in result.system_prompt
    assert "Presencia continua M51:" in result.system_prompt
