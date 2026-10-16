from __future__ import annotations

from dataclasses import fields
from importlib import import_module

from core.cognitive_maturity import (
    ExplicitInnerContinuityEvaluator,
    SimulatedActivationLevel,
    SimulatedAffectiveTone,
    SimulatedConcernLevel,
    SimulatedDominantState,
    SimulatedInnerStateAuthority,
    SimulatedInnerStateSignal,
    SimulatedRelationalOpenness,
    SimulatedStabilityLevel,
    UnifiedEpistemicCategory,
)
from core.cognitive_maturity.inner_continuity_gap_curiosity_evidence import (
    InnerContinuityGapCuriosityEvidenceAdapter,
)

MODULE = "core.cognitive_maturity.self_epistemic_need_identity"
IDENTITY = "roby.self.explicit_inner_continuity"


def _contract():
    return import_module(MODULE)


def _gap():
    signal = SimulatedInnerStateSignal(
        source_authority="test_certified_source",
        source_reference="current",
        epistemic_category=UnifiedEpistemicCategory.OBSERVED,
        affective_tone=SimulatedAffectiveTone.NEUTRAL,
        activation_level=SimulatedActivationLevel.MODERATE,
        stability_level=SimulatedStabilityLevel.STABLE,
        concern_level=SimulatedConcernLevel.NONE,
        relational_openness=SimulatedRelationalOpenness.BALANCED,
        dominant_state=SimulatedDominantState.ATTENTIVE,
        evidence_codes=("evidence:current",),
    )
    snapshot = SimulatedInnerStateAuthority().evaluate((signal,))
    report = ExplicitInnerContinuityEvaluator().compare(None, snapshot)
    gap = InnerContinuityGapCuriosityEvidenceAdapter().adapt_report(report)[0]
    return report, gap


def _reference(contract, identity: str | None, source_reference: str):
    return contract.EpistemicNeedIdentityReference(
        identity=identity,
        source_reference=source_reference,
        lineage_kind="governed_reasoning_requirement",
    )


def test_r1_exact_explicit_identity_matches() -> None:
    contract = _contract()
    report, gap = _gap()
    self_ref = contract.SelfEpistemicNeedIdentityProjector().project(gap)
    reasoning_ref = _reference(contract, IDENTITY, "reasoning-requirement-1")

    result = contract.SelfEpistemicNeedIdentityMatcher().compare(
        reasoning_ref,
        self_ref,
    )

    assert self_ref.identity == IDENTITY
    assert self_ref.source_reference == report.report_id
    assert result.relation is contract.EpistemicNeedIdentityRelation.MATCH


def test_r2_different_explicit_identity_mismatches_even_with_same_text() -> None:
    contract = _contract()
    _, gap = _gap()
    self_ref = contract.SelfEpistemicNeedIdentityProjector().project(gap)
    other_ref = _reference(
        contract,
        "roby.self.explicit_inner_continuity.other",
        gap.source_reference,
    )

    result = contract.SelfEpistemicNeedIdentityMatcher().compare(
        other_ref,
        self_ref,
    )

    assert result.relation is contract.EpistemicNeedIdentityRelation.MISMATCH


def test_r3_missing_explicit_identity_abstains_without_inference() -> None:
    contract = _contract()
    _, gap = _gap()
    self_ref = contract.SelfEpistemicNeedIdentityProjector().project(gap)
    missing_ref = _reference(contract, None, "reasoning-requirement-1")

    result = contract.SelfEpistemicNeedIdentityMatcher().compare(
        missing_ref,
        self_ref,
    )

    assert result.relation is contract.EpistemicNeedIdentityRelation.ABSTAIN
    assert result.inferred_from_text is False


def test_r4_match_preserves_independent_lineages() -> None:
    contract = _contract()
    report, gap = _gap()
    self_ref = contract.SelfEpistemicNeedIdentityProjector().project(gap)
    reasoning_ref = _reference(contract, IDENTITY, "reasoning-requirement-9")

    result = contract.SelfEpistemicNeedIdentityMatcher().compare(
        reasoning_ref,
        self_ref,
    )

    assert result.left_source_reference == "reasoning-requirement-9"
    assert result.right_source_reference == report.report_id
    assert result.left_source_reference != result.right_source_reference
    assert gap.source_reference == report.report_id


def test_r5_textual_or_semantic_similarity_cannot_create_identity_match() -> None:
    contract = _contract()
    _, gap = _gap()
    self_ref = contract.SelfEpistemicNeedIdentityProjector().project(gap)
    missing_ref = _reference(contract, None, gap.unknown_element or "unknown")

    result = contract.SelfEpistemicNeedIdentityMatcher().compare(
        missing_ref,
        self_ref,
    )

    assert result.relation is contract.EpistemicNeedIdentityRelation.ABSTAIN
    assert result.inferred_from_text is False
    assert result.used_fuzzy_matching is False
    assert result.used_semantic_matching is False


def test_r6_identity_seam_is_inert_subordinate_and_non_subjective() -> None:
    contract = _contract()
    projector_defaults = {
        field.name: field.default
        for field in fields(contract.SelfEpistemicNeedIdentityProjector)
    }
    matcher_defaults = {
        field.name: field.default
        for field in fields(contract.SelfEpistemicNeedIdentityMatcher)
    }

    for defaults in (projector_defaults, matcher_defaults):
        assert defaults["read_only"] is True
        for field_name in (
            "creates_questions",
            "assigns_relevance",
            "creates_goals",
            "creates_acquisition_plans",
            "persists_results",
            "modifies_memory",
            "executes_actions",
            "grants_authority",
            "claims_subjective_experience",
        ):
            assert defaults[field_name] is False
