from __future__ import annotations

from dataclasses import fields
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.governed_level2_read_only_execution_gateway import (
    GovernedAcquiredEvidenceEnvelope,
    GovernedLevel2ExecutionStatus,
)
from app.governed_level2_reasoning_reentry import (
    GovernedLevel2ReasoningReentryFoundationV1,
    GovernedLevel2ReasoningReentryResult,
    GovernedReasoningReentryStatus,
)
from app.governed_reasoning_runtime import (
    OfficialGovernedReasoningRuntimeGateway,
    build_default_governed_reasoning_orchestrator,
)
from core.governed_reasoning import EvidenceSourceType

NOW = datetime(2026, 8, 14, 11, 45, tzinfo=timezone.utc)


def _envelope(
    *,
    status: GovernedLevel2ExecutionStatus = GovernedLevel2ExecutionStatus.ACQUIRED,
    execution_id: str = "level2-read-only-execution-1234567890abcdef12345678",
) -> GovernedAcquiredEvidenceEnvelope:
    acquired = status is GovernedLevel2ExecutionStatus.ACQUIRED
    return GovernedAcquiredEvidenceEnvelope(
        execution_id=execution_id,
        status=status,
        authorization_id="independence-authorization-1234567890abcdef12345678",
        requirement_id="discrimination-requirement-1234567890abcdef",
        plan_id="evidence-acquisition-plan-1234567890abcdef",
        capability_name="local.sensor" if acquired else None,
        evidence_description="room temperature" if acquired else None,
        declared_evidence_output="room_temperature" if acquired else None,
        observed_value=22.4 if acquired else None,
        observation_source_reference="local:test-reader" if acquired else None,
        source_reference="scenario-123",
        world_snapshot_id="world-1",
        rationale_codes=("execution:test",),
        source_fingerprint="f" * 64,
    )


def _foundation() -> tuple[
    GovernedLevel2ReasoningReentryFoundationV1,
    OfficialGovernedReasoningRuntimeGateway,
]:
    runtime = OfficialGovernedReasoningRuntimeGateway(
        build_default_governed_reasoning_orchestrator()
    )
    return GovernedLevel2ReasoningReentryFoundationV1(runtime), runtime


def test_acquired_evidence_reenters_canonical_reasoning_once() -> None:
    foundation, runtime = _foundation()
    result = foundation.reenter(_envelope(), now=NOW)

    assert result.status is GovernedReasoningReentryStatus.REEVALUATED
    assert result.automatic_reevaluation_count == 1
    assert runtime.snapshot.evaluations == 1
    assert result.reasoning_result is not None
    assert result.evidence_id is not None


def test_reentry_uses_canonical_evidence_registry_and_selects_reference() -> None:
    foundation, runtime = _foundation()
    result = foundation.reenter(_envelope(), now=NOW)

    registry = runtime.orchestrator.context_assembler.evidence_registry
    reference = registry.get(result.evidence_id or "")
    assert reference is not None
    assert reference.normalized_source_type is EvidenceSourceType.LEVEL2_ACQUIRED
    assert result.reasoning_result is not None
    assert tuple(
        item.evidence_id for item in result.reasoning_result.context.evidence
    ) == (reference.evidence_id,)


@pytest.mark.parametrize(
    "status",
    (
        GovernedLevel2ExecutionStatus.DENIED,
        GovernedLevel2ExecutionStatus.UNAVAILABLE,
        GovernedLevel2ExecutionStatus.FAILED,
        GovernedLevel2ExecutionStatus.REVIEW_REQUIRED,
    ),
)
def test_non_acquired_execution_never_reenters_reasoning(
    status: GovernedLevel2ExecutionStatus,
) -> None:
    foundation, runtime = _foundation()
    result = foundation.reenter(_envelope(status=status), now=NOW)

    assert result.status is GovernedReasoningReentryStatus.NOT_ELIGIBLE
    assert result.automatic_reevaluation_count == 0
    assert runtime.snapshot.evaluations == 0
    assert result.reasoning_result is None


def test_same_execution_lineage_is_single_use() -> None:
    foundation, runtime = _foundation()
    envelope = _envelope()

    first = foundation.reenter(envelope, now=NOW)
    second = foundation.reenter(envelope, now=NOW)

    assert first.status is GovernedReasoningReentryStatus.REEVALUATED
    assert second.status is GovernedReasoningReentryStatus.ALREADY_CONSUMED
    assert second.automatic_reevaluation_count == 0
    assert runtime.snapshot.evaluations == 1


def test_acquired_observation_remains_evidence_not_truth() -> None:
    foundation, runtime = _foundation()
    result = foundation.reenter(_envelope(), now=NOW)
    reference = runtime.orchestrator.context_assembler.evidence_registry.get(
        result.evidence_id or ""
    )

    assert reference is not None
    assert dict(reference.metadata)["epistemic_role"] == "observation_not_truth"
    assert not result.establishes_truth


def test_lineage_is_preserved_into_canonical_evidence_metadata() -> None:
    foundation, runtime = _foundation()
    envelope = _envelope()
    result = foundation.reenter(envelope, now=NOW)
    reference = runtime.orchestrator.context_assembler.evidence_registry.get(
        result.evidence_id or ""
    )

    assert reference is not None
    metadata = dict(reference.metadata)
    assert result.authorization_id == envelope.authorization_id
    assert result.requirement_id == envelope.requirement_id
    assert result.plan_id == envelope.plan_id
    assert result.source_reference == envelope.source_reference
    assert result.world_snapshot_id == envelope.world_snapshot_id
    assert metadata["authorization_id"] == envelope.authorization_id
    assert metadata["requirement_id"] == envelope.requirement_id
    assert metadata["plan_id"] == envelope.plan_id
    assert metadata["world_snapshot_id"] == envelope.world_snapshot_id


def test_reentry_has_no_follow_up_execution_or_side_effect_authority() -> None:
    defaults = {
        field.name: field.default
        for field in fields(GovernedLevel2ReasoningReentryResult)
    }
    for name in (
        "establishes_truth",
        "persists_memory",
        "modifies_world_model",
        "invokes_capabilities",
        "permits_follow_up_execution",
        "creates_questions",
        "emits_conversation",
        "starts_background_process",
    ):
        assert defaults[name] is False


def test_naive_timestamp_is_rejected_before_reasoning() -> None:
    foundation, runtime = _foundation()

    with pytest.raises(ValueError, match="timezone-aware"):
        foundation.reenter(_envelope(), now=datetime(2026, 8, 14, 11, 45))

    assert runtime.snapshot.evaluations == 0


def test_reentry_does_not_call_execution_curiosity_memory_or_conversation() -> None:
    source = (
        Path(__file__).parents[2] / "app" / "governed_level2_reasoning_reentry.py"
    ).read_text(encoding="utf-8")

    for forbidden in (
        "OfficialCapabilityGateway",
        "OfficialMemoryGateway",
        "OfficialConversationGateway",
        "GovernedEpistemicCuriosity",
        ".execute(",
        "subprocess",
        "requests.",
        "socket.",
    ):
        assert forbidden not in source
