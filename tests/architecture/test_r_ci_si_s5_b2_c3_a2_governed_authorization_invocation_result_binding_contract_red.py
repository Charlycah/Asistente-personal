from __future__ import annotations

from dataclasses import fields, replace
from importlib import import_module
from unittest.mock import patch

import pytest

from app.governed_independence_authorization_boundary import (
    GovernedIndependenceAuthorizationBoundaryV1,
    GovernedInitiationDecision,
    GovernedReadOnlyCapabilityInitiationRequest,
)
from core.capability_registry import CapabilityRegistryManager

MODULE = "app.governed_epistemic_authorization_result_binding"
A1_MODULE = (
    "core.cognitive_maturity."
    "governed_authorization_input_correspondence"
)
A1_TEST_MODULE = (
    "tests.architecture."
    "test_r_ci_si_s5_b2_c3_a1_governed_authorization_input_correspondence_contract_red"
)


def _contract():
    return import_module(MODULE)


def _correspondence():
    a1 = import_module(A1_MODULE)
    fixtures = import_module(A1_TEST_MODULE)
    selection = fixtures._selection()
    report = fixtures._runtime_report(selection)
    result = a1.GovernedAuthorizationInputCorrespondenceAdmission().admit(
        selection,
        report,
        owner=fixtures.OWNER,
        reason=fixtures.REASON,
    )
    assert result is not None
    return result


def _boundary():
    return GovernedIndependenceAuthorizationBoundaryV1(
        CapabilityRegistryManager()
    )


def _bind(contract, correspondence, boundary):
    return contract.GovernedEpistemicAuthorizationResultBindingBridgeV1().bind(
        correspondence,
        boundary,
    )


def test_r1_requires_actual_a1_correspondence_and_preserves_anchors() -> None:
    contract = _contract()
    correspondence = _correspondence()
    boundary = _boundary()

    result = _bind(contract, correspondence, boundary)

    assert result is not None
    assert result.correspondence is correspondence
    assert result.selection is correspondence.selection
    assert result.selected_path_eligibility is (
        correspondence.selected_path_eligibility
    )
    with pytest.raises(TypeError):
        _bind(contract, correspondence.selection, boundary)
    with pytest.raises(TypeError):
        _bind(contract, object(), boundary)


def test_r2_projects_exact_existing_direct_request_from_a1() -> None:
    contract = _contract()
    correspondence = _correspondence()
    boundary = _boundary()

    result = _bind(contract, correspondence, boundary)

    assert result is not None
    request = result.authorization_request
    assert isinstance(request, GovernedReadOnlyCapabilityInitiationRequest)
    assert request.owner == correspondence.owner
    assert request.capability_name == correspondence.capability_name
    assert request.reason == correspondence.reason
    assert request.source_reference == correspondence.source_reference
    assert request.world_snapshot_id == correspondence.world_snapshot_id
    request_fields = {item.name for item in fields(type(request))}
    assert "selected_declared_evidence_output" not in request_fields


def test_r3_invokes_existing_owner_once_only_through_direct_route() -> None:
    contract = _contract()
    correspondence = _correspondence()
    boundary = _boundary()

    with patch.object(
        boundary,
        "evaluate_capability_initiation",
        wraps=boundary.evaluate_capability_initiation,
    ) as direct, patch.object(
        boundary,
        "evaluate",
        wraps=boundary.evaluate,
    ) as planning:
        result = _bind(contract, correspondence, boundary)

    assert result is not None
    direct.assert_called_once_with(result.authorization_request)
    planning.assert_not_called()
    with pytest.raises(TypeError):
        _bind(contract, correspondence, object())


def test_r4_preserves_actual_canonical_report_and_exact_decision() -> None:
    contract = _contract()
    correspondence = _correspondence()
    boundary = _boundary()
    expected = boundary.evaluate_capability_initiation(
        GovernedReadOnlyCapabilityInitiationRequest(
            owner=correspondence.owner,
            capability_name=correspondence.capability_name,
            reason=correspondence.reason,
            source_reference=correspondence.source_reference,
            world_snapshot_id=correspondence.world_snapshot_id,
        )
    )

    with patch.object(
        boundary,
        "evaluate_capability_initiation",
        return_value=expected,
    ):
        result = _bind(contract, correspondence, boundary)

    assert result is not None
    assert result.authorization_report is expected
    assert result.authorization_decision is expected.decision
    assert isinstance(result.authorization_decision, GovernedInitiationDecision)
    result_fields = {
        item.name
        for item in fields(contract.GovernedEpistemicAuthorizationResultBinding)
    }
    assert "translated_decision" not in result_fields
    assert "authorization_score" not in result_fields


def test_r5_requires_exact_report_to_a1_binding_and_preserves_d() -> None:
    contract = _contract()
    correspondence = _correspondence()
    boundary = _boundary()
    request = GovernedReadOnlyCapabilityInitiationRequest(
        owner=correspondence.owner,
        capability_name=correspondence.capability_name,
        reason=correspondence.reason,
        source_reference=correspondence.source_reference,
        world_snapshot_id=correspondence.world_snapshot_id,
    )
    report = boundary.evaluate_capability_initiation(request)

    with patch.object(
        boundary,
        "evaluate_capability_initiation",
        return_value=report,
    ):
        result = _bind(contract, correspondence, boundary)

    assert result is not None
    assert result.capability_name == correspondence.capability_name
    assert result.selected_declared_evidence_output == (
        correspondence.selected_declared_evidence_output
    )
    assert result.declared_evidence_output_independently_authorized is False
    mismatches = (
        replace(report, capability_name="other-capability"),
        replace(report, source_reference="other-source"),
        replace(report, world_snapshot_id="other-snapshot"),
    )
    for mismatch in mismatches:
        with patch.object(
            boundary,
            "evaluate_capability_initiation",
            return_value=mismatch,
        ):
            assert _bind(contract, correspondence, boundary) is None


def test_r6_preserves_owner_internal_ids_without_s5_reinterpretation() -> None:
    contract = _contract()
    correspondence = _correspondence()
    boundary = _boundary()

    result = _bind(contract, correspondence, boundary)

    assert result is not None
    report = result.authorization_report
    assert result.authorization_id == report.authorization_id
    assert result.independence_level is report.independence_level
    assert result.authorization_requirement_id == report.requirement_id
    assert result.authorization_plan_id == report.plan_id
    assert result.rationale_codes == report.rationale_codes
    assert result.source_fingerprint == report.source_fingerprint
    assert result.requirement_identity == correspondence.requirement_identity
    assert result.authorization_requirement_id != result.requirement_identity
    assert result.direct_ids_are_s5_lineage is False
    assert result.synthesizes_planning is False


def test_r7_owner_failure_or_invalid_output_cannot_create_decision() -> None:
    contract = _contract()
    correspondence = _correspondence()
    boundary = _boundary()
    bridge = contract.GovernedEpistemicAuthorizationResultBindingBridgeV1()

    with patch.object(
        boundary,
        "evaluate_capability_initiation",
        side_effect=RuntimeError("owner failure"),
    ) as direct:
        with pytest.raises(RuntimeError, match="owner failure"):
            bridge.bind(correspondence, boundary)
        direct.assert_called_once()

    with patch.object(
        boundary,
        "evaluate_capability_initiation",
        return_value=None,
    ) as direct:
        assert bridge.bind(correspondence, boundary) is None
        direct.assert_called_once()

    with patch.object(
        boundary,
        "evaluate_capability_initiation",
        return_value=object(),
    ) as direct:
        assert bridge.bind(correspondence, boundary) is None
        direct.assert_called_once()

    assert bridge.fabricates_authorization_decision is False
    assert bridge.retries_authorization_owner is False


def test_r8_binding_is_nonexecutive_and_stops_after_authorization() -> None:
    contract = _contract()
    correspondence = _correspondence()
    boundary = _boundary()
    bridge = contract.GovernedEpistemicAuthorizationResultBindingBridgeV1()

    result = bridge.bind(correspondence, boundary)

    assert result is not None
    assert result.read_only is True
    assert result.derivational is True
    assert result.authorization_report.execution_authorized is False
    inert_flags = (
        "creates_authorization_policy",
        "interprets_authorization_policy",
        "queries_capability_registry",
        "queries_official_runtime",
        "reruns_a1_admission",
        "reconstructs_selection",
        "reconstructs_eligibility",
        "ranks_paths",
        "reselects_paths",
        "plans_acquisition",
        "invokes_productive_authorization_consumption",
        "acquires_evidence",
        "invokes_selected_capability",
        "queries_selected_source",
        "authorizes_execution",
        "executes_actions",
        "asks_human",
        "creates_questions",
        "assigns_relevance",
        "invokes_curiosity",
        "invokes_initiative",
        "invokes_conversation",
        "persists_results",
        "creates_learning_candidate",
        "modifies_memory",
        "modifies_world_model",
        "creates_cognitive_authority",
        "claims_subjective_experience",
        "claims_consciousness",
    )
    for flag in inert_flags:
        assert getattr(bridge, flag) is False
