from __future__ import annotations

from dataclasses import fields, replace
from importlib import import_module

import pytest

from core.cognitive_maturity.canonical_runtime_readiness_projection import (
    CanonicalRuntimeReadinessProjectionReport,
)

MODULE = (
    "core.cognitive_maturity."
    "governed_authorization_input_correspondence"
)
C2_B_MODULE = "core.cognitive_maturity.governed_epistemic_path_selection"
C2_B_TEST_MODULE = (
    "tests.architecture."
    "test_r_ci_si_s5_b2_c2_b_governed_epistemic_path_selection_contract_red"
)
OWNER = "fixture.owner"
REASON = "Resolve the selected governed epistemic need."
REASONING_SOURCE = "reasoning-source-123"
WORLD_SNAPSHOT = "world-snapshot-123"


def _contract():
    return import_module(MODULE)


def _selection():
    c2_b = import_module(C2_B_MODULE)
    fixtures = import_module(C2_B_TEST_MODULE)
    determinacy_basis = fixtures._determinacy_basis()
    return c2_b.GovernedEpistemicPathSelectionMaterialization().select(
        determinacy_basis
    )


def _runtime_report(selection):
    observation = selection.selected_path_eligibility.runtime_observation
    return CanonicalRuntimeReadinessProjectionReport(
        assessment_id="runtime-assessment-123",
        requirement_id=selection.requirement_identity,
        epistemic_need_identity=selection.epistemic_need_identity,
        reasoning_source_reference=REASONING_SOURCE,
        world_snapshot_id=WORLD_SNAPSHOT,
        self_gap_source_reference=selection.epistemic_need_source_reference,
        self_gap_lineage_kind=selection.epistemic_need_lineage_kind,
        observations=(observation,),
    )


def _correspond(contract, selection, report, owner=OWNER, reason=REASON):
    return contract.GovernedAuthorizationInputCorrespondenceAdmission().admit(
        selection,
        report,
        owner=owner,
        reason=reason,
    )


def test_r1_requires_actual_governed_epistemic_path_selection_anchor() -> None:
    contract = _contract()
    selection = _selection()
    report = _runtime_report(selection)

    result = _correspond(contract, selection, report)

    assert result is not None
    assert result.selection is selection
    with pytest.raises(TypeError):
        _correspond(contract, selection.selected_path_eligibility, report)
    with pytest.raises(TypeError):
        _correspond(contract, selection.determinacy_basis, report)
    with pytest.raises(TypeError):
        _correspond(contract, object(), report)


def test_r2_requires_actual_runtime_report_and_observation_identity() -> None:
    contract = _contract()
    selection = _selection()
    report = _runtime_report(selection)

    result = _correspond(contract, selection, report)

    assert result is not None
    assert result.runtime_report is report
    assert result.runtime_observation is (
        selection.selected_path_eligibility.runtime_observation
    )
    with pytest.raises(TypeError):
        _correspond(contract, selection, object())
    equal_but_detached = replace(report.observations[0])
    detached_report = replace(report, observations=(equal_but_detached,))
    assert _correspond(contract, selection, detached_report) is None


def test_r3_requires_exact_epistemic_need_lineage_correspondence() -> None:
    contract = _contract()
    selection = _selection()
    report = _runtime_report(selection)
    mismatches = (
        replace(report, epistemic_need_identity="roby.self.other"),
        replace(report, self_gap_source_reference="other-source"),
        replace(report, self_gap_lineage_kind="other-lineage"),
    )

    for mismatch in mismatches:
        assert _correspond(contract, selection, mismatch) is None


def test_r4_preserves_exact_selected_c_d_and_actual_anchors() -> None:
    contract = _contract()
    selection = _selection()
    report = _runtime_report(selection)

    result = _correspond(contract, selection, report)

    assert result is not None
    assert result.selection is selection
    assert result.selected_path_eligibility is selection.selected_path_eligibility
    assert result.runtime_report is report
    assert result.runtime_observation is report.observations[0]
    assert result.capability_name == selection.selected_capability_name
    assert result.selected_declared_evidence_output == (
        selection.selected_declared_evidence_output
    )
    assert result.epistemic_need_identity == selection.epistemic_need_identity
    assert result.epistemic_need_source_reference == (
        selection.epistemic_need_source_reference
    )
    assert result.epistemic_need_lineage_kind == (
        selection.epistemic_need_lineage_kind
    )
    assert result.requirement_identity == selection.requirement_identity


def test_r5_projects_reasoning_source_and_snapshot_from_same_report() -> None:
    contract = _contract()
    selection = _selection()
    report = _runtime_report(selection)

    result = _correspond(contract, selection, report)

    assert result is not None
    assert result.source_reference == report.reasoning_source_reference
    assert result.world_snapshot_id == report.world_snapshot_id
    assert result.epistemic_need_source_reference == (
        selection.epistemic_need_source_reference
    )
    assert result.source_reference != result.epistemic_need_source_reference
    result_fields = {
        item.name
        for item in fields(contract.GovernedAuthorizationInputCorrespondence)
    }
    assert "detached_source_reference" not in result_fields
    assert "detached_world_snapshot_id" not in result_fields


def test_r6_requires_explicit_nonblank_owner_and_reason_without_inference() -> None:
    contract = _contract()
    selection = _selection()
    report = _runtime_report(selection)

    result = _correspond(contract, selection, report)

    assert result is not None
    assert result.owner == OWNER
    assert result.reason == REASON
    for owner in ("", "   "):
        assert _correspond(contract, selection, report, owner=owner) is None
    for reason in ("", "   "):
        assert _correspond(contract, selection, report, reason=reason) is None


def test_r7_correspondence_is_not_authorization() -> None:
    contract = _contract()
    boundary = contract.GovernedAuthorizationInputCorrespondenceAdmission()
    selection = _selection()
    result = _correspond(contract, selection, _runtime_report(selection))

    assert result is not None
    result_fields = {
        item.name
        for item in fields(contract.GovernedAuthorizationInputCorrespondence)
    }
    forbidden_fields = {
        "authorized",
        "authorization_decision",
        "may_initiate",
        "must_ask",
        "must_abstain",
        "review_required",
        "authorized_for_acquisition",
        "authorized_for_execution",
    }
    assert result_fields.isdisjoint(forbidden_fields)
    for flag in (
        "invokes_authorization_owner",
        "interprets_authorization_policy",
        "creates_authorization_decision",
        "authorizes_acquisition",
        "authorizes_execution",
    ):
        assert getattr(boundary, flag) is False


def test_r8_boundary_is_read_only_derivational_inert_and_core_only() -> None:
    contract = _contract()
    boundary = contract.GovernedAuthorizationInputCorrespondenceAdmission()

    assert boundary.read_only is True
    assert boundary.derivational is True
    inert_flags = (
        "mutates_selection",
        "mutates_runtime_report",
        "queries_capability_registry",
        "queries_official_runtime",
        "reconstructs_selection",
        "reconstructs_eligibility",
        "reconstructs_runtime_observation",
        "reconstructs_runtime_report",
        "synthesizes_planning",
        "synthesizes_source_reference",
        "synthesizes_world_snapshot",
        "infers_owner",
        "generates_reason",
        "ranks_paths",
        "reselects_paths",
        "inspects_preferences",
        "interprets_comparative_effects",
        "inspects_evidence_content",
        "plans_acquisition",
        "acquires_evidence",
        "invokes_selected_capability",
        "queries_selected_source",
        "asks_human",
        "creates_questions",
        "assigns_relevance",
        "invokes_curiosity",
        "invokes_initiative",
        "invokes_conversation",
        "persists_results",
        "creates_learning_candidate",
        "modifies_memory",
        "executes_actions",
        "creates_cognitive_authority",
        "claims_subjective_experience",
        "claims_consciousness",
    )
    for flag in inert_flags:
        assert getattr(boundary, flag) is False

    source = contract.__file__
    with open(source, encoding="utf-8") as handle:
        assert "from app." not in handle.read()
