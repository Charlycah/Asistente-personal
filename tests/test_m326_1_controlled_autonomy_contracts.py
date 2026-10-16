from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

import pytest

from core import controlled_autonomy

ActionCandidate = controlled_autonomy.ActionCandidate
AutonomyDecision = controlled_autonomy.AutonomyDecision
AutonomyLevel = controlled_autonomy.AutonomyLevel
DecisionDisposition = controlled_autonomy.DecisionDisposition
DecisionEngine = controlled_autonomy.DecisionEngine
DecisionJournal = controlled_autonomy.DecisionJournal
DecisionJournalEntry = controlled_autonomy.DecisionJournalEntry
DecisionOutcome = controlled_autonomy.DecisionOutcome
DecisionPolicy = controlled_autonomy.DecisionPolicy
DecisionSituation = controlled_autonomy.DecisionSituation
OutcomeStatus = controlled_autonomy.OutcomeStatus
Reversibility = controlled_autonomy.Reversibility
RiskAssessment = controlled_autonomy.RiskAssessment
RiskLevel = controlled_autonomy.RiskLevel


NOW = datetime(2026, 7, 26, 18, 0, tzinfo=timezone.utc)


def situation(**changes: object) -> DecisionSituation:
    values: dict[str, object] = {
        "kind": "audio_input_stalled",
        "description": "Vosk is alive but produces no transcriptions",
        "evidence": ("process_alive", "no_transcriptions_20s"),
        "observed_at": NOW,
        "source": "audio_health",
        "urgency": 0.7,
        "situation_id": "situation-1",
    }
    values.update(changes)
    return DecisionSituation(**values)


def candidate(**changes: object) -> ActionCandidate:
    values: dict[str, object] = {
        "action": "restart_vosk",
        "description": "Restart only the Vosk input engine",
        "rationale": ("local_component", "reversible"),
        "reversible": Reversibility.FULL,
        "estimated_cost": 0.1,
        "candidate_id": "candidate-1",
    }
    values.update(changes)
    return ActionCandidate(**values)


def assessment(**changes: object) -> RiskAssessment:
    values: dict[str, object] = {
        "candidate_id": "candidate-1",
        "risk": RiskLevel.LOW,
        "confidence": 0.92,
        "impact": 0.3,
        "reversibility": Reversibility.FULL,
        "reasons": ("isolated restart",),
    }
    values.update(changes)
    return RiskAssessment(**values)


def decision(**changes: object) -> AutonomyDecision:
    values: dict[str, object] = {
        "situation_id": "situation-1",
        "candidate_id": "candidate-1",
        "disposition": DecisionDisposition.SIMULATE,
        "confidence": 0.92,
        "risk": RiskLevel.LOW,
        "rationale": ("simulation mode enabled",),
        "decided_at": NOW,
        "policy_level": AutonomyLevel.AUTONOMOUS_LOW_RISK,
        "decision_id": "decision-1",
    }
    values.update(changes)
    return AutonomyDecision(**values)


def outcome(**changes: object) -> DecisionOutcome:
    values: dict[str, object] = {
        "decision_id": "decision-1",
        "status": OutcomeStatus.NOT_EXECUTED,
        "observed_at": NOW,
        "summary": "Simulation completed without execution",
        "evidence": ("no_executor_invoked",),
        "outcome_id": "outcome-1",
    }
    values.update(changes)
    return DecisionOutcome(**values)


def test_public_enums_expose_expected_values() -> None:
    assert AutonomyLevel.AUTONOMOUS_LOW_RISK.value == "autonomous_low_risk"
    assert DecisionDisposition.REQUEST_CONFIRMATION.value == ("request_confirmation")
    assert RiskLevel.PROHIBITED.value == "prohibited"
    assert Reversibility.NONE.value == "none"
    assert OutcomeStatus.REVERTED.value == "reverted"


@pytest.mark.parametrize("field", ["kind", "description", "source", "situation_id"])
def test_situation_rejects_blank_identity(field: str) -> None:
    with pytest.raises(ValueError):
        situation(**{field: " "})


def test_situation_requires_evidence() -> None:
    with pytest.raises(ValueError):
        situation(evidence=())


def test_situation_requires_aware_timestamp() -> None:
    with pytest.raises(ValueError):
        situation(observed_at=datetime(2026, 7, 26))


@pytest.mark.parametrize("urgency", [-0.01, 1.01])
def test_situation_rejects_invalid_urgency(urgency: float) -> None:
    with pytest.raises(ValueError):
        situation(urgency=urgency)


def test_candidate_normalizes_reversibility() -> None:
    value = candidate(reversible="partial")
    assert value.reversible is Reversibility.PARTIAL


def test_candidate_rejects_negative_cost() -> None:
    with pytest.raises(ValueError):
        candidate(estimated_cost=-0.01)


def test_candidate_requires_rationale() -> None:
    with pytest.raises(ValueError):
        candidate(rationale=())


def test_assessment_normalizes_enums() -> None:
    value = assessment(risk="medium", reversibility="partial")
    assert value.risk is RiskLevel.MEDIUM
    assert value.reversibility is Reversibility.PARTIAL


@pytest.mark.parametrize(
    ("field", "value"),
    (("confidence", -0.1), ("confidence", 1.1), ("impact", -0.1), ("impact", 1.1)),
)
def test_assessment_rejects_invalid_scores(field: str, value: float) -> None:
    with pytest.raises(ValueError):
        assessment(**{field: value})


def test_policy_defaults_to_safe_simulation() -> None:
    policy = DecisionPolicy()
    assert policy.autonomy_level is AutonomyLevel.RECOMMEND
    assert policy.simulation_mode is True
    assert policy.maximum_automatic_risk is RiskLevel.LOW
    assert policy.maximum_attempts == 1


@pytest.mark.parametrize("confidence", [-0.01, 1.01])
def test_policy_rejects_invalid_confidence(confidence: float) -> None:
    with pytest.raises(ValueError):
        DecisionPolicy(minimum_confidence=confidence)


def test_policy_rejects_non_positive_attempt_limit() -> None:
    with pytest.raises(ValueError):
        DecisionPolicy(maximum_attempts=0)


def test_policy_rejects_blank_or_duplicate_prohibited_actions() -> None:
    with pytest.raises(ValueError):
        DecisionPolicy(prohibited_actions=("",))
    with pytest.raises(ValueError):
        DecisionPolicy(prohibited_actions=("send_email", "send_email"))


@pytest.mark.parametrize(
    "disposition",
    (
        DecisionDisposition.RECOMMEND,
        DecisionDisposition.REQUEST_CONFIRMATION,
        DecisionDisposition.AUTHORIZE,
        DecisionDisposition.SIMULATE,
    ),
)
def test_action_dispositions_require_candidate(
    disposition: DecisionDisposition,
) -> None:
    with pytest.raises(ValueError):
        decision(disposition=disposition, candidate_id=None)


def test_observe_and_block_can_exist_without_candidate() -> None:
    observed = decision(
        disposition=DecisionDisposition.OBSERVE,
        candidate_id=None,
        policy_level=AutonomyLevel.OBSERVE_ONLY,
    )
    blocked = decision(
        disposition=DecisionDisposition.BLOCK,
        candidate_id=None,
        risk=RiskLevel.PROHIBITED,
        policy_level=AutonomyLevel.PROHIBITED,
    )
    assert observed.candidate_id is None
    assert blocked.risk is RiskLevel.PROHIBITED


def test_authorization_requires_low_risk_autonomous_policy() -> None:
    with pytest.raises(ValueError):
        decision(
            disposition=DecisionDisposition.AUTHORIZE,
            policy_level=AutonomyLevel.CONFIRM_BEFORE_ACTION,
        )
    with pytest.raises(ValueError):
        decision(
            disposition=DecisionDisposition.AUTHORIZE,
            risk=RiskLevel.MEDIUM,
        )


def test_low_risk_authorization_is_representable_but_not_executable() -> None:
    value = decision(disposition=DecisionDisposition.AUTHORIZE)
    assert value.disposition is DecisionDisposition.AUTHORIZE
    assert not hasattr(value, "execute")


def test_prohibited_risk_must_be_blocked() -> None:
    with pytest.raises(ValueError):
        decision(risk=RiskLevel.PROHIBITED)


def test_outcome_requires_aware_timestamp_and_evidence() -> None:
    with pytest.raises(ValueError):
        outcome(observed_at=datetime(2026, 7, 26))
    with pytest.raises(ValueError):
        outcome(evidence=())


def test_journal_connects_complete_audit_record() -> None:
    entry = DecisionJournalEntry(
        situation=situation(),
        candidates=(candidate(),),
        assessments=(assessment(),),
        decision=decision(),
        outcome=outcome(),
        journal_id="journal-1",
    )
    assert entry.decision.situation_id == entry.situation.situation_id
    assert entry.outcome is not None
    assert entry.outcome.decision_id == entry.decision.decision_id


def test_journal_rejects_mismatched_situation() -> None:
    with pytest.raises(ValueError):
        DecisionJournalEntry(
            situation=situation(),
            candidates=(candidate(),),
            assessments=(assessment(),),
            decision=decision(situation_id="other"),
        )


def test_journal_rejects_unknown_selected_candidate() -> None:
    with pytest.raises(ValueError):
        DecisionJournalEntry(
            situation=situation(),
            candidates=(candidate(),),
            assessments=(assessment(),),
            decision=decision(candidate_id="unknown"),
        )


def test_journal_rejects_unknown_assessment_candidate() -> None:
    with pytest.raises(ValueError):
        DecisionJournalEntry(
            situation=situation(),
            candidates=(candidate(),),
            assessments=(assessment(candidate_id="unknown"),),
            decision=decision(),
        )


def test_journal_rejects_duplicate_candidates_and_assessments() -> None:
    with pytest.raises(ValueError):
        DecisionJournalEntry(
            situation=situation(),
            candidates=(candidate(), replace(candidate())),
            assessments=(),
            decision=decision(),
        )
    with pytest.raises(ValueError):
        DecisionJournalEntry(
            situation=situation(),
            candidates=(candidate(),),
            assessments=(assessment(), replace(assessment())),
            decision=decision(),
        )


def test_journal_rejects_mismatched_outcome() -> None:
    with pytest.raises(ValueError):
        DecisionJournalEntry(
            situation=situation(),
            candidates=(candidate(),),
            assessments=(assessment(),),
            decision=decision(),
            outcome=outcome(decision_id="other"),
        )


class EngineDouble:
    def decide(
        self,
        situation: DecisionSituation,
        candidates: tuple[ActionCandidate, ...],
        assessments: tuple[RiskAssessment, ...],
        policy: DecisionPolicy,
    ) -> AutonomyDecision:
        return decision()


class JournalDouble:
    def __init__(self) -> None:
        self._entries: list[DecisionJournalEntry] = []

    def append(self, entry: DecisionJournalEntry) -> None:
        self._entries.append(entry)

    def entries(self) -> tuple[DecisionJournalEntry, ...]:
        return tuple(self._entries)


def test_protocols_support_structural_runtime_checks() -> None:
    assert isinstance(EngineDouble(), DecisionEngine)
    assert isinstance(JournalDouble(), DecisionJournal)


def test_journal_protocol_double_is_append_only_from_contract_surface() -> None:
    journal = JournalDouble()
    entry = DecisionJournalEntry(
        situation=situation(),
        candidates=(candidate(),),
        assessments=(assessment(),),
        decision=decision(),
    )
    journal.append(entry)
    assert journal.entries() == (entry,)
