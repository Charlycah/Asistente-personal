from datetime import datetime, timezone

import pytest

from core.controlled_autonomy import (
    CapabilityAssessment,
    CapabilityAvailability,
    ContextSignalKind,
    DeterministicContextualInitiativeEvaluator,
    JsonContextualInitiativeStore,
    NextStepProposal,
)
from core.executive_runtime_integration import RuntimeExecutiveIntegration

NOW = datetime(2026, 7, 28, 1, 0, tzinfo=timezone.utc)


def _proposal(**overrides):
    values = {
        "proposal_id": "proposal-1",
        "selection_id": "selection-1",
        "goal_id": "goal-1",
        "plan_id": "plan-1",
        "step_id": "step-1",
        "proposed_at": NOW,
        "description": "Inspect current state.",
        "rationale": "Collect auditable evidence.",
        "risk": "low",
        "required_capability": "verify_component_health",
        "authorization_required": True,
        "blockers": (),
        "summary": "A safe step is available.",
    }
    values.update(overrides)
    return NextStepProposal(**values)


def _available():
    return CapabilityAssessment(
        capability_id="verify_component_health",
        availability=CapabilityAvailability.AVAILABLE,
        risk="low",
        reversible=True,
        authorization_required=False,
        missing_dependencies=(),
        reasons=("available",),
    )


def test_ready_step_supports_contextual_proposal():
    result = DeterministicContextualInitiativeEvaluator().evaluate(
        proposal=_proposal(), capability=_available(), observed_at=NOW
    )

    assert result.should_propose
    assert result.signals[0].kind is ContextSignalKind.NEXT_STEP_READY
    assert any(
        item.kind is ContextSignalKind.AUTHORIZATION_REQUIRED
        for item in result.signals
    )


def test_blocked_step_suppresses_contextual_proposal():
    result = DeterministicContextualInitiativeEvaluator().evaluate(
        proposal=_proposal(blockers=("Waiting for user input.",)),
        capability=_available(),
        observed_at=NOW,
    )

    assert not result.should_propose
    assert result.signals[0].kind is ContextSignalKind.GOAL_BLOCKED


def test_unavailable_capability_suppresses_contextual_proposal():
    unavailable = CapabilityAssessment(
        capability_id="verify_component_health",
        availability=CapabilityAvailability.DISABLED,
        risk="low",
        reversible=True,
        authorization_required=False,
        missing_dependencies=(),
        reasons=("capability_disabled",),
    )

    result = DeterministicContextualInitiativeEvaluator().evaluate(
        proposal=_proposal(), capability=unavailable, observed_at=NOW
    )

    assert not result.should_propose
    assert result.signals[0].kind is ContextSignalKind.CAPABILITY_UNAVAILABLE


def test_non_actionable_proposal_is_explicit():
    result = DeterministicContextualInitiativeEvaluator().evaluate(
        proposal=_proposal(
            goal_id=None,
            plan_id=None,
            step_id=None,
            required_capability=None,
            authorization_required=False,
        ),
        capability=None,
        observed_at=NOW,
    )

    assert not result.should_propose
    assert result.signals[0].kind is ContextSignalKind.NO_ACTIONABLE_STEP


def test_runtime_persists_contextual_initiative_without_execution(tmp_path):
    runtime = RuntimeExecutiveIntegration(
        decision_journal_path=tmp_path / "decision_journal.jsonl"
    )
    runtime.next_step_proposal_store.append(_proposal())

    result = runtime.evaluate_contextual_initiative("proposal-1", observed_at=NOW)
    restored = RuntimeExecutiveIntegration(
        decision_journal_path=tmp_path / "decision_journal.jsonl"
    )

    assert result.should_propose
    assert restored.contextual_initiatives().initiatives == (result,)
    assert restored.snapshot.contextual_initiative_count == 1
    assert restored.snapshot.proposal_candidate_count == 1
    assert restored.snapshot.autonomous_cycle_count == 0


def test_store_rejects_duplicate_and_corrupt_data(tmp_path):
    store = JsonContextualInitiativeStore(tmp_path / "initiatives.json")
    initiative = DeterministicContextualInitiativeEvaluator().evaluate(
        proposal=_proposal(), capability=_available(), observed_at=NOW
    )
    store.append(initiative)

    with pytest.raises(ValueError, match="duplicate contextual initiative id"):
        store.append(initiative)

    path = tmp_path / "broken.json"
    path.write_text("{broken", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid contextual initiative file"):
        JsonContextualInitiativeStore(path)
