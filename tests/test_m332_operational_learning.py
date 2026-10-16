from datetime import datetime, timezone

import pytest

from core.controlled_autonomy import (
    DeterministicOperationalLearner,
    ExperienceMemorySnapshot,
    ExperiencePattern,
    JsonOperationalLearningStore,
    OperationalLearningDisposition,
)
from core.executive_runtime_integration import RuntimeExecutiveIntegration

NOW = datetime(2026, 7, 28, 2, 0, tzinfo=timezone.utc)


def _pattern(*, succeeded=0, degraded=0, failed=0, unknown=0):
    occurrences = succeeded + degraded + failed + unknown
    return ExperiencePattern(
        situation_kind="component_unhealthy",
        action="verify_component_health",
        occurrences=occurrences,
        succeeded=succeeded,
        degraded=degraded,
        failed=failed,
        unknown=unknown,
        last_observed_at=NOW,
        last_summary="Audited result.",
    )


def test_insufficient_evidence_never_adjusts_behavior():
    result = DeterministicOperationalLearner().learn(
        experience=ExperienceMemorySnapshot((_pattern(succeeded=2),)),
        situation_kind="component_unhealthy",
        action="verify_component_health",
        observed_at=NOW,
    )

    assert result.disposition is OperationalLearningDisposition.INSUFFICIENT_EVIDENCE
    assert result.adjustment == 0.0


def test_successful_evidence_produces_bounded_favorable_recommendation():
    result = DeterministicOperationalLearner().learn(
        experience=ExperienceMemorySnapshot((_pattern(succeeded=4),)),
        situation_kind="component_unhealthy",
        action="verify_component_health",
        observed_at=NOW,
    )

    assert result.disposition is OperationalLearningDisposition.FAVOR
    assert result.adjustment == 0.2
    assert result.success_rate == 1.0


def test_failed_evidence_produces_bounded_caution():
    result = DeterministicOperationalLearner().learn(
        experience=ExperienceMemorySnapshot((_pattern(failed=4),)),
        situation_kind="component_unhealthy",
        action="verify_component_health",
        observed_at=NOW,
    )

    assert result.disposition is OperationalLearningDisposition.CAUTION
    assert result.adjustment == -0.2
    assert result.failure_rate == 1.0


def test_mixed_evidence_can_remain_neutral():
    result = DeterministicOperationalLearner().learn(
        experience=ExperienceMemorySnapshot(
            (_pattern(succeeded=2, failed=2),)
        ),
        situation_kind="component_unhealthy",
        action="verify_component_health",
        observed_at=NOW,
    )

    assert result.disposition is OperationalLearningDisposition.NEUTRAL
    assert result.adjustment == 0.0


def test_runtime_persists_learning_without_execution(tmp_path):
    snapshot = ExperienceMemorySnapshot((_pattern(succeeded=3),))

    class FixedMemory:
        def snapshot(self):
            return snapshot

        def remember(self, result):
            raise AssertionError("learning must not execute or remember outcomes")

    runtime = RuntimeExecutiveIntegration(
        decision_journal_path=tmp_path / "decision_journal.jsonl",
        experience_memory=FixedMemory(),
    )
    result = runtime.learn_from_operational_experience(
        "component_unhealthy",
        "verify_component_health",
        observed_at=NOW,
    )
    restored = RuntimeExecutiveIntegration(
        decision_journal_path=tmp_path / "decision_journal.jsonl"
    )

    assert restored.operational_learnings().learnings == (result,)
    assert restored.snapshot.operational_learning_count == 1
    assert restored.snapshot.actionable_operational_learning_count == 1
    assert restored.snapshot.autonomous_cycle_count == 0


def test_store_rejects_duplicate_and_corrupt_data(tmp_path):
    learner = DeterministicOperationalLearner()
    learning = learner.learn(
        experience=ExperienceMemorySnapshot((_pattern(succeeded=3),)),
        situation_kind="component_unhealthy",
        action="verify_component_health",
        observed_at=NOW,
    )
    store = JsonOperationalLearningStore(tmp_path / "learning.json")
    store.append(learning)

    with pytest.raises(ValueError, match="duplicate operational learning id"):
        store.append(learning)

    path = tmp_path / "broken.json"
    path.write_text("{broken", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid operational learning file"):
        JsonOperationalLearningStore(path)
