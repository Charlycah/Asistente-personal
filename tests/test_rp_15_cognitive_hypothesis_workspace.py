from datetime import datetime, timezone

import pytest

from app.cognitive_agenda_manager import (
    CognitiveAgendaItem,
    CognitiveAgendaKind,
    CognitiveAgendaSnapshot,
    CognitiveAgendaStatus,
)
from app.cognitive_agenda_reasoning import CognitiveAgendaReasoner
from app.cognitive_hypothesis_workspace import (
    CognitiveHypothesisStatus,
    CognitiveHypothesisTransition,
    CognitiveHypothesisWorkspace,
    CognitiveHypothesisWorkspacePolicy,
)
from app.cognitive_reflection_engine import CognitiveReflectionEngine
from app.cognitive_thought_stream import CognitiveThoughtStream
from app.continuous_internal_cognitive_loop import ContinuousInternalCognitiveLoop

NOW = datetime(2026, 7, 17, 12, 0, tzinfo=timezone.utc)


def item(*, key="focus", score=0.7, status=CognitiveAgendaStatus.ACTIVE):
    return CognitiveAgendaItem(
        key=key,
        kind=CognitiveAgendaKind.PROJECT,
        title=f"Revisar {key}",
        sources=("test",),
        score=score,
        priority=score,
        urgency=0.4,
        relevance=0.8,
        status=status,
        first_seen_at=NOW,
        last_seen_at=NOW,
        expires_at=None,
        rationale="test",
    )


def snapshot(focus, *others):
    items = (focus, *others) if focus is not None else ()
    return CognitiveAgendaSnapshot(
        generated_at=NOW,
        items=items,
        primary_focus=focus,
    )


def inputs(focus, *others):
    agenda = snapshot(focus, *others)
    deliberation = CognitiveAgendaReasoner().deliberate(agenda, now=NOW)
    reflection = CognitiveReflectionEngine().reflect(
        agenda,
        deliberation,
        now=NOW,
    )
    stream = CognitiveThoughtStream().advance(
        agenda,
        deliberation,
        reflection,
        now=NOW,
    )
    return stream, deliberation, reflection


def test_new_thread_creates_continuity_hypothesis():
    result = CognitiveHypothesisWorkspace().evaluate(
        *inputs(item()),
        now=NOW,
    )
    assert result.transition is CognitiveHypothesisTransition.CREATED
    assert result.leading_key == "focus:continuity"
    assert result.hypotheses[0].thread_key == "focus"


def test_supported_hypothesis_uses_deliberation_confidence():
    result = CognitiveHypothesisWorkspace().evaluate(
        *inputs(item(score=0.95)),
        now=NOW,
    )
    hypothesis = result.hypotheses[0]
    assert hypothesis.status is CognitiveHypothesisStatus.SUPPORTED
    assert hypothesis.confidence >= 0.7


def test_reassessment_reflection_adds_alternative_hypothesis():
    focus = item(score=0.66)
    competitor = item(key="other", score=0.65)
    result = CognitiveHypothesisWorkspace().evaluate(
        *inputs(focus, competitor),
        now=NOW,
    )
    keys = {hypothesis.key for hypothesis in result.hypotheses}
    assert "focus:continuity" in keys
    assert "focus:reassessment" in keys


def test_same_thread_updates_revision_count():
    workspace = CognitiveHypothesisWorkspace()
    data = inputs(item())
    workspace.evaluate(*data, now=NOW)
    result = workspace.evaluate(*data, now=NOW)
    continuity = next(
        hypothesis
        for hypothesis in result.hypotheses
        if hypothesis.key == "focus:continuity"
    )
    assert result.transition is CognitiveHypothesisTransition.UPDATED
    assert continuity.revisions == 2


def test_confidence_changes_are_bounded_by_policy_step():
    workspace = CognitiveHypothesisWorkspace(
        policy=CognitiveHypothesisWorkspacePolicy(confidence_step=0.05)
    )
    first = workspace.evaluate(*inputs(item(score=0.95)), now=NOW)
    initial = first.hypotheses[0].confidence
    result = workspace.evaluate(*inputs(item(score=0.2)), now=NOW)
    continuity = next(
        hypothesis
        for hypothesis in result.hypotheses
        if hypothesis.key == "focus:continuity"
    )
    assert initial - continuity.confidence <= 0.05


def test_focus_change_suspends_previous_hypotheses():
    workspace = CognitiveHypothesisWorkspace()
    workspace.evaluate(*inputs(item(key="a")), now=NOW)
    result = workspace.evaluate(*inputs(item(key="b")), now=NOW)
    previous = next(
        hypothesis for hypothesis in result.hypotheses if hypothesis.thread_key == "a"
    )
    assert previous.status is CognitiveHypothesisStatus.SUSPENDED
    assert result.active_thread_key == "b"


def test_missing_stream_suspends_active_workspace():
    workspace = CognitiveHypothesisWorkspace()
    workspace.evaluate(*inputs(item()), now=NOW)
    result = workspace.evaluate(None, None, None, now=NOW)
    assert result.transition is CognitiveHypothesisTransition.SUSPENDED
    assert result.active_thread_key is None
    assert result.leading_key is None


def test_evidence_is_deduplicated():
    result = CognitiveHypothesisWorkspace().evaluate(
        *inputs(item()),
        now=NOW,
    )
    assert result.hypotheses[0].evidence_sources == ("test",)


def test_workspace_never_requests_authorization_or_hidden_reasoning():
    result = CognitiveHypothesisWorkspace().evaluate(
        *inputs(item()),
        now=NOW,
    )
    assert result.requires_user_authorization is False
    assert "hypothesis_workspace:" in result.rationale
    assert not hasattr(result.hypotheses[0], "chain_of_thought")


def test_policy_rejects_invalid_values():
    with pytest.raises(ValueError, match="positive"):
        CognitiveHypothesisWorkspacePolicy(max_hypotheses=0)
    with pytest.raises(ValueError, match="between zero and one"):
        CognitiveHypothesisWorkspacePolicy(confidence_step=1.1)
    with pytest.raises(ValueError, match="must not exceed"):
        CognitiveHypothesisWorkspacePolicy(
            support_threshold=0.4,
            challenge_threshold=0.8,
        )


def test_rp10_exposes_workspace_without_changing_rationale_contract():
    agenda = snapshot(item())

    class Agenda:
        def refresh(self, *, now):
            return agenda

    state = ContinuousInternalCognitiveLoop(agenda_manager=Agenda()).tick(now=NOW)
    assert state.rationale == "agenda:focus"
    assert state.thought_stream is not None
    assert state.hypothesis_workspace is not None
    assert state.hypothesis_workspace.leading_key == "focus:continuity"
