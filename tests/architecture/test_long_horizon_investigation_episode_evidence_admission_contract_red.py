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
    "app.governed_long_horizon_investigation_episode_evidence_admission"
)


def _load_contract():
    spec = find_spec(EXPECTED_MODULE)
    assert spec is not None, "RED: episode evidence admission bridge missing"
    module = import_module(EXPECTED_MODULE)
    status = getattr(
        module,
        "GovernedInvestigationEpisodeEvidenceAdmissionStatus",
        None,
    )
    result = getattr(
        module,
        "GovernedInvestigationEpisodeEvidenceAdmissionResult",
        None,
    )
    bridge = getattr(
        module,
        "GovernedLongHorizonInvestigationEpisodeEvidenceAdmissionV1",
        None,
    )
    return status, result, bridge


def test_red_episode_evidence_admission_bridge_and_public_contract_exist():
    status, result, bridge = _load_contract()
    assert status is not None
    assert result is not None
    assert bridge is not None
    assert callable(getattr(bridge, "consume", None))


def test_red_bridge_delegates_only_to_existing_episode_boundary():
    _, _, bridge = _load_contract()
    source = inspect.getsource(bridge)

    assert "GovernedMultiStepInvestigationEpisodeBoundaryV1" in source
    assert ".record_acquisition(" in source
    assert "GovernedMultiStepInvestigationExecutionReentryV1" not in source
    assert "GovernedLevel2ReadOnlyExecutionGatewayV1" not in source


def test_red_exact_existing_envelope_is_forwarded_without_reexecution():
    _, _, bridge = _load_contract()
    source = inspect.getsource(bridge)
    tree = ast.parse(source)

    assert "execution_result.evidence_envelope" in source
    assert ".record_acquisition(" in source
    assert ".execute(" not in source
    assert sum(
        1
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "record_acquisition"
    ) <= 1


def test_red_checkpoint_projection_is_fail_closed_and_preserves_episode_identity():
    _, _, bridge = _load_contract()
    source = inspect.getsource(bridge)

    for token in (
        "checkpoint.episode_id",
        "checkpoint.originating_reasoning_id",
        "checkpoint.requirement_ids",
        "checkpoint.source_reference",
        "checkpoint.world_snapshot_ids",
        "GovernedInvestigationEpisodeStatus.OPEN",
        "GovernedInvestigationEpisodeStatus.READY_FOR_PLANNING",
    ):
        assert token in source
    assert ".start(" not in source


def test_red_success_only_enables_later_reasoning_reentry_without_invoking_it():
    status, result, bridge = _load_contract()
    source = inspect.getsource(bridge)
    result_source = inspect.getsource(result)

    assert hasattr(status, "ADMITTED")
    assert hasattr(status, "NOT_ELIGIBLE")
    assert hasattr(status, "REVIEW_REQUIRED")
    assert "eligible_for_existing_reasoning_reentry" in result_source
    assert "GovernedInvestigationEpisodeStatus.AWAITING_REENTRY" in source
    assert "GovernedLevel2ReasoningReentryFoundationV1" not in source
    assert ".reenter(" not in source
    assert ".reason(" not in source


def test_red_bridge_does_not_operationalize_later_or_unrelated_capabilities():
    _, _, bridge = _load_contract()
    source = inspect.getsource(bridge)

    for forbidden in (
        "OfficialCapabilityGateway",
        "PlanningFoundation(",
        "GovernedIndependenceAuthorizationBoundaryV1",
        "EvidenceRegistry",
        "OfficialMemoryGateway",
        "WorldModel",
        "record_reentry(",
        "while ",
        "for ",
        "subprocess",
        "requests.",
        "socket.",
    ):
        assert forbidden not in source


def test_existing_episode_and_reasoning_owners_are_already_canonical():
    episode_source = inspect.getsource(GovernedMultiStepInvestigationEpisodeBoundaryV1)
    reasoning_source = inspect.getsource(GovernedLevel2ReasoningReentryFoundationV1)

    assert "def record_acquisition(" in episode_source
    assert "GovernedInvestigationEpisodeStatus.AWAITING_REENTRY" in episode_source
    assert "def record_reentry(" in episode_source
    assert "EvidenceRegistry" not in episode_source
    assert "def reenter(" in reasoning_source
    assert "evidence_registry" in reasoning_source
    assert '"epistemic_role", "observation_not_truth"' in reasoning_source
