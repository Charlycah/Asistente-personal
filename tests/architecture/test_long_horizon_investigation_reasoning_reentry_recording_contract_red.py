from __future__ import annotations

import ast
import inspect
from importlib import import_module
from importlib.util import find_spec

from app.governed_level2_reasoning_reentry import (
    GovernedLevel2ReasoningReentryFoundationV1,
)
from app.governed_multistep_investigation_episode import (
    GovernedMultiStepInvestigationEpisodeBoundaryV1,
)

EXPECTED_MODULE = (
    "app.governed_long_horizon_investigation_reasoning_reentry_recording"
)


def _load_contract():
    spec = find_spec(EXPECTED_MODULE)
    assert spec is not None, "RED: reasoning reentry recording bridge missing"
    module = import_module(EXPECTED_MODULE)
    status = getattr(
        module,
        "GovernedInvestigationReasoningReentryRecordingStatus",
        None,
    )
    result = getattr(
        module,
        "GovernedInvestigationReasoningReentryRecordingResult",
        None,
    )
    bridge = getattr(
        module,
        "GovernedLongHorizonInvestigationReasoningReentryRecordingV1",
        None,
    )
    return status, result, bridge


def test_red_reasoning_reentry_recording_bridge_and_public_contract_exist():
    status, result, bridge = _load_contract()
    assert status is not None
    assert result is not None
    assert bridge is not None
    assert callable(getattr(bridge, "consume", None))


def test_red_bridge_delegates_only_to_existing_reasoning_and_episode_owners():
    _, _, bridge = _load_contract()
    source = inspect.getsource(bridge)

    assert "GovernedLevel2ReasoningReentryFoundationV1" in source
    assert "GovernedMultiStepInvestigationEpisodeBoundaryV1" in source
    assert ".reenter(" in source
    assert ".record_reentry(" in source
    assert "GovernedMultiStepInvestigationReasoningClosureV1" not in source
    assert ".reason(" not in source


def test_red_exact_envelope_then_exact_reentry_are_forwarded_once():
    _, _, bridge = _load_contract()
    source = inspect.getsource(bridge)
    tree = ast.parse(source)

    assert "admission.evidence_envelope" in source
    assert "admission.resulting_episode_state" in source
    assert sum(
        1
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "reenter"
    ) <= 1
    assert sum(
        1
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "record_reentry"
    ) <= 1
    assert ".record_acquisition(" not in source


def test_red_eligibility_and_lineage_fail_closed_before_episode_recording():
    _, _, bridge = _load_contract()
    source = inspect.getsource(bridge)

    for token in (
        "GovernedInvestigationEpisodeEvidenceAdmissionStatus.ADMITTED",
        "eligible_for_existing_reasoning_reentry",
        "GovernedInvestigationEpisodeStatus.AWAITING_REENTRY",
        "GovernedReasoningReentryStatus.REEVALUATED",
        "execution_id",
        "authorization_id",
        "requirement_id",
        "plan_id",
        "source_reference",
        "world_snapshot_id",
    ):
        assert token in source


def test_red_result_preserves_first_continuation_or_second_terminal_recording():
    status, result, bridge = _load_contract()
    result_source = inspect.getsource(result)
    bridge_source = inspect.getsource(bridge)

    assert hasattr(status, "RECORDED_CONTINUATION")
    assert hasattr(status, "RECORDED_CLOSED")
    assert hasattr(status, "NOT_ELIGIBLE")
    assert hasattr(status, "REVIEW_REQUIRED")
    assert "reasoning_reentry" in result_source
    assert "transition" in result_source
    assert "resulting_episode_state" in result_source
    assert "GovernedInvestigationEpisodeStatus.AWAITING_REQUIREMENT" in bridge_source
    assert "GovernedInvestigationEpisodeStatus.CLOSED" in bridge_source
    assert "GovernedInvestigationStoppingReason.BUDGET_EXHAUSTED" in bridge_source


def test_red_bridge_does_not_create_requirement_or_operationalize_later_steps():
    _, _, bridge = _load_contract()
    source = inspect.getsource(bridge)

    for forbidden in (
        "DiscriminatingEvidenceRequirement(",
        "GovernedMultiStepInvestigationProductiveContinuationV1",
        "PlanningFoundation(",
        "GovernedIndependenceAuthorizationBoundaryV1",
        "GovernedLevel2ReadOnlyExecutionGatewayV1",
        "OfficialCapabilityGateway",
        "OfficialMemoryGateway",
        "WorldModel",
        "while ",
        "subprocess",
        "requests.",
        "socket.",
    ):
        assert forbidden not in source


def test_existing_reasoning_and_episode_reentry_owners_are_canonical():
    reasoning_source = inspect.getsource(GovernedLevel2ReasoningReentryFoundationV1)
    episode_source = inspect.getsource(GovernedMultiStepInvestigationEpisodeBoundaryV1)

    assert "def reenter(" in reasoning_source
    assert "evidence_registry" in reasoning_source
    assert '"epistemic_role", "observation_not_truth"' in reasoning_source
    assert "def record_reentry(" in episode_source
    assert "GovernedInvestigationEpisodeStatus.AWAITING_REQUIREMENT" in episode_source
    assert "GovernedInvestigationEpisodeStatus.CLOSED" in episode_source
    assert "GovernedInvestigationStoppingReason.BUDGET_EXHAUSTED" in episode_source
