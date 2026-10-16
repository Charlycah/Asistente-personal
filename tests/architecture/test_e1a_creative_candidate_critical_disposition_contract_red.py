from __future__ import annotations

import inspect

from app import governed_reasoning_runtime


def test_e1a_requires_bounded_creative_candidate_critical_disposition_red() -> None:
    """RED: novel synthesis hypothesis has no bounded critical disposition yet.

    The missing surface belongs to the existing governed-reasoning authority. It
    must consume the exact canonical novel-synthesis hypothesis admission, preserve
    its lineage and tentative status, remain a derived read-only assessment, and
    stop before proposal creation or any planning/execution/memory/learning action.
    """

    result_type_name = "GovernedCreativeCandidateCriticalDisposition"
    method_name = "evaluate_creative_candidate_critical_disposition"

    result_type = getattr(governed_reasoning_runtime, result_type_name, None)
    method = getattr(
        governed_reasoning_runtime.OfficialGovernedReasoningRuntimeGateway,
        method_name,
        None,
    )

    assert result_type is not None, (
        "E1-A RED confirmed: governed reasoning can admit an exact novel-synthesis "
        "hypothesis, but exposes no bounded critical-disposition artifact for that "
        "creative candidate."
    )
    assert method is not None, (
        "E1-A RED confirmed: OfficialGovernedReasoningRuntimeGateway exposes no "
        "critical-disposition seam for the canonical novel-synthesis hypothesis."
    )

    signature = inspect.signature(method)
    assert "admission" in signature.parameters
    annotation = signature.parameters["admission"].annotation
    assert annotation in (
        governed_reasoning_runtime.CanonicalNovelSynthesisGovernedHypothesisAdmission,
        "CanonicalNovelSynthesisGovernedHypothesisAdmission",
    )

    required_fields = {
        "disposition_id",
        "status",
        "synthesis_source_fingerprint",
        "hypothesis_candidate_id",
        "hypothesis_source_claim_fingerprint",
        "critical_evaluation_reference_ids",
        "rationale_codes",
        "independent_evidence_required",
        "canonical_authority",
        "read_only",
        "derived_assessment",
        "registers_as_evidence",
        "establishes_truth",
        "establishes_causality",
        "creates_proposal",
        "invokes_planning",
        "invokes_execution",
        "creates_memory",
        "creates_learning",
        "grants_authority",
        "starts_background_process",
    }
    assert required_fields.issubset(result_type.__dataclass_fields__)

    fields = result_type.__dataclass_fields__
    assert fields["canonical_authority"].default == "governed_reasoning"
    assert fields["read_only"].default is True
    assert fields["derived_assessment"].default is True
    assert fields["independent_evidence_required"].default is True

    for field_name in (
        "registers_as_evidence",
        "establishes_truth",
        "establishes_causality",
        "creates_proposal",
        "invokes_planning",
        "invokes_execution",
        "creates_memory",
        "creates_learning",
        "grants_authority",
        "starts_background_process",
    ):
        assert fields[field_name].default is False


def test_e1a_contract_stops_before_proposal_and_action_authorities() -> None:
    """The E1-A reasoning seam must not absorb downstream authorities."""

    # Existing governed reasoning may mention planning/memory elsewhere; this test is
    # intentionally scoped to the new method once it exists.
    method = getattr(
        governed_reasoning_runtime.OfficialGovernedReasoningRuntimeGateway,
        "evaluate_creative_candidate_critical_disposition",
        None,
    )
    assert method is not None, "E1-A RED confirmed: critical-disposition seam absent."
    method_source = inspect.getsource(method)

    assert "GovernedProposalModel" not in method_source
    assert "GovernedProposalInbox" not in method_source
    assert ".create(" not in method_source
    assert ".enqueue(" not in method_source
    assert "Planning" not in method_source
    assert "Execution" not in method_source
    assert "Memory" not in method_source
    assert "Learning" not in method_source
