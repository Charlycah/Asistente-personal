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
from core.cognitive_maturity.governed_epistemic_curiosity import (
    EpistemicCuriosityOutcome,
    EpistemicCuriosityRelevance,
    EpistemicCuriositySourceKind,
    GovernedEpistemicCuriosityFoundation,
    MultisourceKnowledgeGapEvidence,
)

MODULE = "core.cognitive_maturity.inner_continuity_gap_curiosity_evidence"
ADAPTER = "InnerContinuityGapCuriosityEvidenceAdapter"


def _adapter_class():
    return getattr(import_module(MODULE), ADAPTER)


def _snapshot(reference: str):
    signal = SimulatedInnerStateSignal(
        source_authority="test_certified_source",
        source_reference=reference,
        epistemic_category=UnifiedEpistemicCategory.OBSERVED,
        affective_tone=SimulatedAffectiveTone.NEUTRAL,
        activation_level=SimulatedActivationLevel.MODERATE,
        stability_level=SimulatedStabilityLevel.STABLE,
        concern_level=SimulatedConcernLevel.NONE,
        relational_openness=SimulatedRelationalOpenness.BALANCED,
        dominant_state=SimulatedDominantState.ATTENTIVE,
        evidence_codes=(f"evidence:{reference}",),
    )
    return SimulatedInnerStateAuthority().evaluate((signal,))


def _insufficient_report():
    return ExplicitInnerContinuityEvaluator().compare(None, _snapshot("current"))


def _complete_report():
    return ExplicitInnerContinuityEvaluator().compare(
        _snapshot("previous"),
        _snapshot("current"),
    )


def test_r1_insufficient_self_evidence_projects_one_curiosity_gap() -> None:
    evidence = _adapter_class()().adapt_report(_insufficient_report())

    assert len(evidence) == 1
    gap = evidence[0]
    assert isinstance(gap, MultisourceKnowledgeGapEvidence)
    assert gap.source_kind is EpistemicCuriositySourceKind.REASONING
    assert gap.source_reference == _insufficient_report().report_id
    assert gap.unknown_element is not None
    assert gap.relevance is EpistemicCuriosityRelevance.UNKNOWN


def test_r2_projection_preserves_lineage_without_inventing_self_facts() -> None:
    report = _insufficient_report()

    gap = _adapter_class()().adapt_report(report)[0]

    assert f"inner_continuity_report:{report.report_id}" in gap.evidence_codes
    assert f"source_fingerprint:{report.source_fingerprint}" in gap.evidence_codes
    for code in report.evidence_codes + report.uncertainty_codes:
        assert code in gap.evidence_codes
    assert report.current_snapshot_id in gap.known_elements
    assert report.previous_snapshot_id is None
    assert "conscious" not in " ".join(gap.known_elements).lower()


def test_r3_unknown_relevance_stops_before_curiosity_question() -> None:
    gap = _adapter_class()().adapt_report(_insufficient_report())[0]

    result = GovernedEpistemicCuriosityFoundation().evaluate(gap)

    assert gap.relevance is EpistemicCuriosityRelevance.UNKNOWN
    assert result.outcome is EpistemicCuriosityOutcome.ABSTAIN
    assert result.question_candidate is None
    assert "relevance_not_yet_governed" in result.rationale_codes


def test_r4_complete_continuity_projects_zero_self_epistemic_gaps() -> None:
    evidence = _adapter_class()().adapt_report(_complete_report())

    assert evidence == ()


def test_r5_adapter_is_read_only_and_cannot_cross_governed_domains() -> None:
    adapter_class = _adapter_class()
    defaults = {field.name: field.default for field in fields(adapter_class)}

    assert defaults["read_only"] is True
    for field_name in (
        "creates_questions",
        "creates_learning_candidates",
        "persists_results",
        "modifies_memory",
        "executes_actions",
        "grants_authority",
    ):
        assert defaults[field_name] is False


def test_r6_adapter_is_subordinate_and_cannot_claim_subjective_experience() -> None:
    adapter = _adapter_class()()
    gap = adapter.adapt_report(_insufficient_report())[0]

    assert adapter.SOURCE_AUTHORITY == "explicit_inner_continuity"
    assert adapter.TARGET_CONTRACT == "GovernedEpistemicCuriosity"
    assert adapter.grants_authority is False
    projected_text = " ".join(
        (gap.subject, *(gap.known_elements), gap.unknown_element or "")
    ).lower()
    for prohibited_claim in ("i am conscious", "subjective experience", "real emotion"):
        assert prohibited_claim not in projected_text
