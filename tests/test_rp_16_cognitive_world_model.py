from datetime import datetime, timezone

import pytest

from app.cognitive_agenda_manager import (
    CognitiveAgendaItem,
    CognitiveAgendaKind,
    CognitiveAgendaSnapshot,
    CognitiveAgendaStatus,
)
from app.cognitive_agenda_reasoning import CognitiveAgendaReasoner
from app.cognitive_hypothesis_workspace import CognitiveHypothesisWorkspace
from app.cognitive_reflection_engine import CognitiveReflectionEngine
from app.cognitive_thought_stream import CognitiveThoughtStream
from app.cognitive_world_model import (
    CognitiveWorldEntityKind,
    CognitiveWorldFactStatus,
    CognitiveWorldModel,
    CognitiveWorldModelPolicy,
    CognitiveWorldModelTransition,
)
from app.continuous_internal_cognitive_loop import ContinuousInternalCognitiveLoop

NOW = datetime(2026, 7, 17, 12, 0, tzinfo=timezone.utc)


def item(*, key="focus", score=0.7):
    return CognitiveAgendaItem(
        key=key,
        kind=CognitiveAgendaKind.PROJECT,
        title=f"Revisar {key}",
        sources=("test",),
        score=score,
        priority=score,
        urgency=0.4,
        relevance=0.8,
        status=CognitiveAgendaStatus.ACTIVE,
        first_seen_at=NOW,
        last_seen_at=NOW,
        expires_at=None,
        rationale="test",
    )


def inputs(focus, *others):
    agenda = CognitiveAgendaSnapshot(
        generated_at=NOW,
        items=(focus, *others),
        primary_focus=focus,
    )
    deliberation = CognitiveAgendaReasoner().deliberate(agenda, now=NOW)
    reflection = CognitiveReflectionEngine().reflect(agenda, deliberation, now=NOW)
    stream = CognitiveThoughtStream().advance(agenda, deliberation, reflection, now=NOW)
    workspace = CognitiveHypothesisWorkspace().evaluate(
        stream, deliberation, reflection, now=NOW
    )
    return stream, workspace


def test_new_focus_creates_observed_world_entity():
    result = CognitiveWorldModel().update(*inputs(item()), now=NOW)
    focus = next(entity for entity in result.entities if entity.key == "focus")
    assert result.transition is CognitiveWorldModelTransition.CREATED
    assert focus.kind is CognitiveWorldEntityKind.FOCUS
    assert focus.status is CognitiveWorldFactStatus.OBSERVED


def test_hypotheses_remain_inferred_not_observed():
    result = CognitiveWorldModel().update(*inputs(item()), now=NOW)
    hypothesis = next(
        entity
        for entity in result.entities
        if entity.kind is CognitiveWorldEntityKind.HYPOTHESIS
    )
    assert hypothesis.status in {
        CognitiveWorldFactStatus.INFERRED,
        CognitiveWorldFactStatus.UNCERTAIN,
    }


def test_world_model_links_focus_to_hypothesis():
    result = CognitiveWorldModel().update(*inputs(item()), now=NOW)
    relation = result.relations[0]
    assert relation.subject_key == "focus"
    assert relation.predicate == "interpreted_by"
    assert relation.object_key.endswith(":continuity")


def test_reassessment_creates_alternative_relation():
    result = CognitiveWorldModel().update(
        *inputs(item(score=0.66), item(key="other", score=0.65)),
        now=NOW,
    )
    assert len(result.relations) == 2


def test_repeated_update_preserves_first_seen_and_increments_revision():
    model = CognitiveWorldModel()
    first = model.update(*inputs(item()), now=NOW)
    second = model.update(*inputs(item()), now=NOW)
    a = next(entity for entity in first.entities if entity.key == "focus")
    b = next(entity for entity in second.entities if entity.key == "focus")
    assert b.first_seen_at == a.first_seen_at
    assert b.revisions == 2


def test_focus_change_retires_previous_focus():
    model = CognitiveWorldModel()
    model.update(*inputs(item(key="a")), now=NOW)
    result = model.update(*inputs(item(key="b")), now=NOW)
    previous = next(entity for entity in result.entities if entity.key == "a")
    assert previous.status is CognitiveWorldFactStatus.RETIRED
    assert result.active_focus_key == "b"


def test_leading_hypothesis_change_reframes_model():
    model = CognitiveWorldModel()
    model.update(*inputs(item(score=0.95)), now=NOW)
    result = model.update(
        *inputs(item(score=0.51), item(key="other", score=0.50)),
        now=NOW,
    )
    assert result.transition in {
        CognitiveWorldModelTransition.UPDATED,
        CognitiveWorldModelTransition.REFRAMED,
    }


def test_missing_inputs_suspend_model():
    model = CognitiveWorldModel()
    model.update(*inputs(item()), now=NOW)
    result = model.update(None, None, now=NOW)
    assert result.transition is CognitiveWorldModelTransition.SUSPENDED
    assert result.active_focus_key is None


def test_provenance_is_deduplicated():
    result = CognitiveWorldModel().update(*inputs(item()), now=NOW)
    focus = next(entity for entity in result.entities if entity.key == "focus")
    assert focus.sources == ("test",)


def test_policy_validation():
    with pytest.raises(ValueError, match="positive"):
        CognitiveWorldModelPolicy(max_entities=0)
    with pytest.raises(ValueError, match="between zero and one"):
        CognitiveWorldModelPolicy(uncertainty_threshold=1.1)


def test_rp10_exposes_world_model_without_changing_rationale():
    focus = item()
    agenda = CognitiveAgendaSnapshot(
        generated_at=NOW,
        items=(focus,),
        primary_focus=focus,
    )

    class Agenda:
        def refresh(self, *, now):
            return agenda

    state = ContinuousInternalCognitiveLoop(agenda_manager=Agenda()).tick(now=NOW)
    assert state.rationale == "agenda:focus"
    assert state.world_model is not None
    assert state.world_model.active_focus_key == "focus"
    assert state.world_model.requires_user_authorization is False
