from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest

from core.controlled_autonomy import (
    ActionCandidate,
    AutonomyDecision,
    AutonomyLevel,
    DecisionDisposition,
    DecisionJournalEntry,
    DecisionSituation,
    JsonlDecisionJournal,
    Reversibility,
    RiskAssessment,
    RiskLevel,
)
from core.executive_runtime_integration import RuntimeExecutiveIntegration

NOW = datetime(2026, 7, 26, 23, 0, tzinfo=timezone.utc)


def _entry() -> DecisionJournalEntry:
    situation = DecisionSituation(
        kind="runtime_component_degraded",
        description="Executive coordinator is degraded",
        evidence=("component_id=executive.coordinator",),
        observed_at=NOW,
        source="runtime_health",
        urgency=0.5,
        situation_id="situation-persistent-1",
    )
    candidate = ActionCandidate(
        action="verify_component_health",
        description="Verify component health",
        rationale=("verification_before_intervention",),
        reversible=Reversibility.FULL,
        estimated_cost=0.1,
        candidate_id="candidate-persistent-1",
    )
    assessment = RiskAssessment(
        candidate_id=candidate.candidate_id,
        risk=RiskLevel.LOW,
        confidence=0.95,
        impact=0.1,
        reversibility=Reversibility.FULL,
        reasons=("read_only",),
    )
    decision = AutonomyDecision(
        situation_id=situation.situation_id,
        candidate_id=candidate.candidate_id,
        disposition=DecisionDisposition.AUTHORIZE,
        confidence=0.95,
        risk=RiskLevel.LOW,
        rationale=("policy_allows_low_risk_action",),
        decided_at=NOW,
        policy_level=AutonomyLevel.AUTONOMOUS_LOW_RISK,
        decision_id="decision-persistent-1",
    )
    return DecisionJournalEntry(
        situation=situation,
        candidates=(candidate,),
        assessments=(assessment,),
        decision=decision,
        journal_id="journal-persistent-1",
    )


def test_jsonl_journal_survives_restart(tmp_path) -> None:
    path = tmp_path / "decision_journal.jsonl"
    entry = _entry()

    JsonlDecisionJournal(path).append(entry)
    restored = JsonlDecisionJournal(path)

    assert restored.entries() == (entry,)
    assert restored.snapshot().count == 1
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 1
    assert payload["decision"]["decision_id"] == entry.decision.decision_id


def test_jsonl_journal_rejects_corrupt_record(tmp_path) -> None:
    path = tmp_path / "decision_journal.jsonl"
    path.write_text('{"schema_version":1}\n', encoding="utf-8")

    with pytest.raises(ValueError, match="line 1"):
        JsonlDecisionJournal(path)


def test_runtime_autonomous_decision_is_persisted_and_reloaded(
    tmp_path,
    monkeypatch,
) -> None:
    path = tmp_path / "autonomy" / "decision_journal.jsonl"
    runtime = RuntimeExecutiveIntegration(decision_journal_path=path)
    runtime.start(now=NOW)

    def fail_publish(event):
        raise RuntimeError("coordinator unavailable")

    monkeypatch.setattr(runtime.coordinator, "publish", fail_publish)
    with pytest.raises(RuntimeError, match="coordinator unavailable"):
        runtime.publish_text("activar persistencia")

    restored = JsonlDecisionJournal(path)
    assert len(restored.entries()) == 1
    persisted = restored.entries()[0]
    result = runtime.last_autonomy_result
    assert result is not None
    assert result.orchestration.journal_entry == persisted
