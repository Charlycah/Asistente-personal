from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from core.controlled_autonomy import (
    ActionCandidate,
    AutonomyDecision,
    AutonomyLevel,
    DecisionDisposition,
    DecisionJournal,
    DecisionJournalEntry,
    DecisionOutcome,
    DecisionSituation,
    InMemoryDecisionJournal,
    JournalSnapshot,
    OutcomeStatus,
    Reversibility,
    RiskAssessment,
    RiskLevel,
)

NOW = datetime(2026, 7, 26, 21, 0, tzinfo=timezone.utc)


def situation(*, situation_id: str = "situation-1") -> DecisionSituation:
    return DecisionSituation(
        kind="runtime_component_unhealthy",
        description="audio component is unhealthy",
        evidence=("health=unhealthy",),
        observed_at=NOW,
        source="runtime_health",
        urgency=0.9,
        situation_id=situation_id,
    )


def candidate(*, candidate_id: str = "candidate-1") -> ActionCandidate:
    return ActionCandidate(
        action="restart_component",
        description="restart the unhealthy component",
        rationale=("component_is_unhealthy",),
        reversible=Reversibility.FULL,
        candidate_id=candidate_id,
    )


def assessment(*, candidate_id: str = "candidate-1") -> RiskAssessment:
    return RiskAssessment(
        candidate_id=candidate_id,
        risk=RiskLevel.LOW,
        confidence=0.95,
        impact=0.7,
        reversibility=Reversibility.FULL,
        reasons=("known_recovery_action",),
    )


def decision(
    *,
    situation_id: str = "situation-1",
    candidate_id: str = "candidate-1",
    decision_id: str = "decision-1",
) -> AutonomyDecision:
    return AutonomyDecision(
        situation_id=situation_id,
        candidate_id=candidate_id,
        disposition=DecisionDisposition.AUTHORIZE,
        confidence=0.95,
        risk=RiskLevel.LOW,
        rationale=("autonomy_gate_authorized",),
        decided_at=NOW + timedelta(seconds=1),
        policy_level=AutonomyLevel.AUTONOMOUS_LOW_RISK,
        decision_id=decision_id,
    )


def outcome(
    *,
    decision_id: str = "decision-1",
    outcome_id: str = "outcome-1",
) -> DecisionOutcome:
    return DecisionOutcome(
        decision_id=decision_id,
        status=OutcomeStatus.SUCCEEDED,
        observed_at=NOW + timedelta(seconds=2),
        summary="component recovered",
        evidence=("health=healthy",),
        outcome_id=outcome_id,
    )


def entry(
    *,
    situation_id: str = "situation-1",
    candidate_id: str = "candidate-1",
    decision_id: str = "decision-1",
    journal_id: str = "journal-1",
    outcome_id: str | None = "outcome-1",
) -> DecisionJournalEntry:
    current_outcome = None
    if outcome_id is not None:
        current_outcome = outcome(
            decision_id=decision_id,
            outcome_id=outcome_id,
        )
    return DecisionJournalEntry(
        situation=situation(situation_id=situation_id),
        candidates=(candidate(candidate_id=candidate_id),),
        assessments=(assessment(candidate_id=candidate_id),),
        decision=decision(
            situation_id=situation_id,
            candidate_id=candidate_id,
            decision_id=decision_id,
        ),
        outcome=current_outcome,
        journal_id=journal_id,
    )


def test_protocol_is_runtime_checkable() -> None:
    assert isinstance(InMemoryDecisionJournal(), DecisionJournal)


def test_new_journal_is_empty() -> None:
    journal = InMemoryDecisionJournal()
    assert journal.entries() == ()
    assert journal.snapshot().is_empty is True


def test_append_records_entry() -> None:
    journal = InMemoryDecisionJournal()
    current = entry()
    journal.append(current)
    assert journal.entries() == (current,)


def test_append_preserves_insertion_order() -> None:
    first = entry()
    second = entry(
        situation_id="situation-2",
        candidate_id="candidate-2",
        decision_id="decision-2",
        journal_id="journal-2",
        outcome_id="outcome-2",
    )
    journal = InMemoryDecisionJournal()
    journal.append(first)
    journal.append(second)
    assert journal.entries() == (first, second)


def test_entries_returns_immutable_tuple() -> None:
    journal = InMemoryDecisionJournal((entry(),))
    assert isinstance(journal.entries(), tuple)


def test_snapshot_is_immutable_contract() -> None:
    snapshot = InMemoryDecisionJournal((entry(),)).snapshot()
    assert isinstance(snapshot, JournalSnapshot)
    assert snapshot.count == 1
    with pytest.raises(AttributeError):
        snapshot.entries = ()  # type: ignore[misc]


def test_snapshot_does_not_change_after_later_append() -> None:
    journal = InMemoryDecisionJournal((entry(),))
    snapshot = journal.snapshot()
    journal.append(
        entry(
            situation_id="situation-2",
            candidate_id="candidate-2",
            decision_id="decision-2",
            journal_id="journal-2",
            outcome_id="outcome-2",
        )
    )
    assert snapshot.count == 1
    assert journal.snapshot().count == 2


def test_constructor_accepts_initial_entries() -> None:
    current = entry()
    journal = InMemoryDecisionJournal((current,))
    assert journal.entries() == (current,)


def test_duplicate_journal_id_is_rejected() -> None:
    journal = InMemoryDecisionJournal((entry(),))
    duplicate = entry(
        situation_id="situation-2",
        candidate_id="candidate-2",
        decision_id="decision-2",
        journal_id="journal-1",
        outcome_id="outcome-2",
    )
    with pytest.raises(ValueError, match="journal id"):
        journal.append(duplicate)


def test_duplicate_decision_id_is_rejected() -> None:
    journal = InMemoryDecisionJournal((entry(),))
    duplicate = entry(
        situation_id="situation-2",
        candidate_id="candidate-2",
        decision_id="decision-1",
        journal_id="journal-2",
        outcome_id="outcome-2",
    )
    with pytest.raises(ValueError, match="decision id"):
        journal.append(duplicate)


def test_duplicate_outcome_id_is_rejected() -> None:
    journal = InMemoryDecisionJournal((entry(),))
    duplicate = entry(
        situation_id="situation-2",
        candidate_id="candidate-2",
        decision_id="decision-2",
        journal_id="journal-2",
        outcome_id="outcome-1",
    )
    with pytest.raises(ValueError, match="outcome id"):
        journal.append(duplicate)


def test_failed_append_does_not_mutate_journal() -> None:
    current = entry()
    journal = InMemoryDecisionJournal((current,))
    with pytest.raises(ValueError):
        journal.append(replace(current))
    assert journal.entries() == (current,)


def test_lookup_by_journal_id() -> None:
    current = entry()
    journal = InMemoryDecisionJournal((current,))
    assert journal.by_journal_id("journal-1") is current


def test_lookup_by_decision_id() -> None:
    current = entry()
    journal = InMemoryDecisionJournal((current,))
    assert journal.by_decision_id("decision-1") is current


def test_lookup_by_outcome_id() -> None:
    current = entry()
    journal = InMemoryDecisionJournal((current,))
    assert journal.by_outcome_id("outcome-1") is current


def test_lookup_returns_none_when_missing() -> None:
    journal = InMemoryDecisionJournal((entry(),))
    assert journal.by_journal_id("missing") is None
    assert journal.by_decision_id("missing") is None
    assert journal.by_outcome_id("missing") is None


@pytest.mark.parametrize(
    ("method_name", "label"),
    [
        ("by_journal_id", "journal id"),
        ("by_decision_id", "decision id"),
        ("by_outcome_id", "outcome id"),
        ("for_situation", "situation id"),
        ("for_candidate", "candidate id"),
    ],
)
def test_blank_lookup_identifiers_are_rejected(
    method_name: str,
    label: str,
) -> None:
    journal = InMemoryDecisionJournal()
    method = getattr(journal, method_name)
    with pytest.raises(ValueError, match=label):
        method("  ")


def test_filter_by_situation_preserves_order() -> None:
    first = entry()
    second = entry(
        candidate_id="candidate-2",
        decision_id="decision-2",
        journal_id="journal-2",
        outcome_id="outcome-2",
    )
    third = entry(
        situation_id="situation-2",
        candidate_id="candidate-3",
        decision_id="decision-3",
        journal_id="journal-3",
        outcome_id="outcome-3",
    )
    journal = InMemoryDecisionJournal((first, second, third))
    assert journal.for_situation("situation-1") == (first, second)


def test_filter_by_candidate_checks_all_generated_candidates() -> None:
    selected = candidate(candidate_id="candidate-1")
    alternative = candidate(candidate_id="candidate-2")
    current = replace(
        entry(),
        candidates=(selected, alternative),
        assessments=(assessment(candidate_id="candidate-1"),),
    )
    journal = InMemoryDecisionJournal((current,))
    assert journal.for_candidate("candidate-2") == (current,)


def test_completed_returns_only_entries_with_outcome() -> None:
    completed = entry()
    pending = entry(
        situation_id="situation-2",
        candidate_id="candidate-2",
        decision_id="decision-2",
        journal_id="journal-2",
        outcome_id=None,
    )
    journal = InMemoryDecisionJournal((completed, pending))
    assert journal.completed() == (completed,)


def test_pending_returns_only_entries_without_outcome() -> None:
    completed = entry()
    pending = entry(
        situation_id="situation-2",
        candidate_id="candidate-2",
        decision_id="decision-2",
        journal_id="journal-2",
        outcome_id=None,
    )
    journal = InMemoryDecisionJournal((completed, pending))
    assert journal.pending() == (pending,)


def test_pending_entry_has_no_outcome_lookup() -> None:
    pending = entry(outcome_id=None)
    journal = InMemoryDecisionJournal((pending,))
    assert journal.by_outcome_id("outcome-1") is None


def test_journal_does_not_expose_mutating_storage() -> None:
    journal = InMemoryDecisionJournal((entry(),))
    exposed = journal.entries()
    exposed += (entry(
        situation_id="situation-2",
        candidate_id="candidate-2",
        decision_id="decision-2",
        journal_id="journal-2",
        outcome_id="outcome-2",
    ),)
    assert len(exposed) == 2
    assert len(journal.entries()) == 1


def test_journal_has_no_execution_methods() -> None:
    journal = InMemoryDecisionJournal()
    forbidden = {
        "execute",
        "run_action",
        "retry",
        "revert",
        "notify_user",
        "persist",
        "save",
    }
    assert forbidden.isdisjoint(dir(journal))
