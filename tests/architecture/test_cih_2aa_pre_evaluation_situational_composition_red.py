from __future__ import annotations

from datetime import datetime, timezone

from app.governed_reasoning_runtime import OfficialGovernedReasoningRuntimeGateway
from core.governed_reasoning import (
    GovernedTurnBoundProductiveSituationalClaimBinder,
    TurnBoundProductiveSituationalClaimBindingStatus,
)

_NOW = datetime(2026, 9, 13, 21, 0, tzinfo=timezone.utc)
_TEXT = "Mañana viene alguien a casa y todavía me falta organizar varias cosas."


def test_cih_2aa_productive_episode_receives_bounded_situational_claim() -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()

    episode = gateway.evaluate_productive_episode(
        owner="owner-1",
        session_id="session-1",
        turn_id="turn-1",
        text=_TEXT,
        now=_NOW,
        scope_reference="session-1",
        observe_productive_intake=False,
    )

    matching = tuple(
        claim
        for claim in episode.result.context.claims
        if claim.subject == "current_turn_situation"
        and claim.predicate == "may_have_relevant_support"
        and claim.object_value == "organization_support"
    )
    assert len(matching) == 1
    claim = matching[0]
    assert claim.normalized_type.value == "hypothesis"
    assert claim.normalized_origin.value == "system"
    assert claim.normalized_status.value == "proposed"
    assert claim.confidence is None
    assert claim.evidence_links == ()


def test_cih_2aa_productive_input_fingerprint_represents_binding() -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()

    bounded = gateway.evaluate_productive_episode(
        owner="owner-1",
        session_id="session-bounded",
        turn_id="turn-bounded",
        text=_TEXT,
        now=_NOW,
        scope_reference="session-bounded",
        observe_productive_intake=False,
    )
    ordinary = gateway.evaluate_productive_episode(
        owner="owner-1",
        session_id="session-ordinary",
        turn_id="turn-ordinary",
        text="La capital de Japón es Tokio.",
        now=_NOW,
        scope_reference="session-ordinary",
        observe_productive_intake=False,
    )

    assert bounded.input_fingerprint != ordinary.input_fingerprint


def test_cih_2aa_unrelated_text_fails_closed_without_situational_claim() -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()

    episode = gateway.evaluate_productive_episode(
        owner="owner-1",
        session_id="session-2",
        turn_id="turn-2",
        text="La capital de Japón es Tokio.",
        now=_NOW,
        scope_reference="session-2",
        observe_productive_intake=False,
    )

    assert not any(
        claim.predicate == "may_have_relevant_support"
        for claim in episode.result.context.claims
    )


def test_cih_2aa_existing_episode_wins_without_re_evaluation() -> None:
    gateway = OfficialGovernedReasoningRuntimeGateway()

    first = gateway.evaluate_productive_episode(
        owner="owner-1",
        session_id="session-3",
        turn_id="turn-3",
        text="Texto ordinario sin semántica CIH.",
        now=_NOW,
        scope_reference="session-3",
        observe_productive_intake=False,
    )
    evaluations = gateway.snapshot.evaluations
    second = gateway.evaluate_productive_episode(
        owner="owner-1",
        session_id="session-3",
        turn_id="turn-3",
        text=_TEXT,
        now=_NOW,
        scope_reference="session-3",
        observe_productive_intake=False,
    )

    assert second is first
    assert gateway.snapshot.evaluations == evaluations
    assert not any(
        claim.predicate == "may_have_relevant_support"
        for claim in second.result.context.claims
    )


def test_cih_2aa_turn_bound_binder_is_governed_and_fail_closed() -> None:
    binder = GovernedTurnBoundProductiveSituationalClaimBinder()

    assert binder.canonical_authority == "governed_reasoning"
    assert binder.read_only is True
    assert binder.transient is True
    assert binder.persists_results is False
    assert binder.registers_claims is False
    assert binder.executes_actions is False
    assert (
        TurnBoundProductiveSituationalClaimBindingStatus.BOUND.value
        == "bound"
    )
