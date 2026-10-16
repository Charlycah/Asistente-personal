from dataclasses import fields

from core.cognitive_maturity.governed_epistemic_curiosity import (
    EpistemicCuriosityOutcome,
    EpistemicCuriosityQuestionKind,
    EpistemicCuriosityRelevance,
    EpistemicCuriositySourceKind,
    GovernedEpistemicCuriosityFoundation,
)
from core.cognitive_maturity.hypothesis_gap_curiosity_evidence import (
    HypothesisGapCuriosityEvidenceAdapter,
)
from core.governed_reasoning.hypothesis_deepening import (
    GovernedHypothesisDeepeningReport,
    HypothesisDeepeningSourceKind,
    HypothesisDeepeningStatus,
    HypothesisEpistemicGap,
)


def _gap() -> HypothesisEpistemicGap:
    return HypothesisEpistemicGap(
        gap_id="hypothesis-gap-1234567890abcdef",
        hypothesis_id="h-1",
        subject="The kitchen window is open",
        source_kind=HypothesisDeepeningSourceKind.SCENARIO_SIMULATION,
        source_reference="scenario-simulation-1234567890abcdef",
        known_elements=("fact-window",),
        unknown_element="explicit evidence sufficient to discriminate hypothesis",
        evidence_codes=("world_snapshot:world-1", "scenario:no_persistent_fact"),
        hypothesis="The kitchen window is open",
    )


def _report(
    *, gaps: tuple[HypothesisEpistemicGap, ...]
) -> GovernedHypothesisDeepeningReport:
    gap = _gap()
    return GovernedHypothesisDeepeningReport(
        report_id="hypothesis-deepening-1234567890abcdef",
        status=(
            HypothesisDeepeningStatus.EPISTEMIC_GAPS_PRESENT
            if gaps
            else HypothesisDeepeningStatus.COMPLETE
        ),
        source_kind=HypothesisDeepeningSourceKind.SCENARIO_SIMULATION,
        source_reference=gap.source_reference,
        world_snapshot_id="world-1",
        assessments=(),
        epistemic_gaps=gaps,
        evidence_codes=("world_snapshot:world-1",),
        risk_codes=("scenario_unresolved",),
        source_fingerprint="scenario-source-fingerprint",
    )


def test_adapter_preserves_gap_lineage_without_inventing_relevance() -> None:
    gap = _gap()

    evidence = HypothesisGapCuriosityEvidenceAdapter().adapt(gap)

    assert evidence.source_kind is EpistemicCuriositySourceKind.REASONING
    assert evidence.source_reference == gap.gap_id
    assert evidence.subject == gap.subject
    assert evidence.known_elements == gap.known_elements
    assert evidence.unknown_element == gap.unknown_element
    assert evidence.hypothesis == gap.hypothesis
    assert evidence.relevance is EpistemicCuriosityRelevance.UNKNOWN
    assert f"hypothesis_gap:{gap.gap_id}" in evidence.evidence_codes
    assert f"hypothesis:{gap.hypothesis_id}" in evidence.evidence_codes
    assert (
        "reasoning_source:scenario_simulation:"
        "scenario-simulation-1234567890abcdef"
    ) in evidence.evidence_codes


def test_unknown_relevance_fails_closed_at_existing_curiosity_authority() -> None:
    evidence = HypothesisGapCuriosityEvidenceAdapter().adapt(_gap())

    report = GovernedEpistemicCuriosityFoundation().evaluate(evidence)

    assert report.outcome is EpistemicCuriosityOutcome.ABSTAIN
    assert report.question_candidate is None
    assert "relevance_not_yet_governed" in report.rationale_codes


def test_explicit_relevance_remains_owned_by_curiosity_not_adapter() -> None:
    adapter = HypothesisGapCuriosityEvidenceAdapter()
    evidence = adapter.adapt(
        _gap(),
        relevance=EpistemicCuriosityRelevance.RELEVANT,
    )

    report = GovernedEpistemicCuriosityFoundation().evaluate(evidence)

    assert report.outcome is EpistemicCuriosityOutcome.QUESTION_CANDIDATE
    assert report.question_candidate is not None
    assert (
        report.question_candidate.question_kind
        is EpistemicCuriosityQuestionKind.HYPOTHESIS_CHECK
    )
    assert not adapter.creates_questions
    assert report.question_candidate.source_reference == _gap().gap_id


def test_gap_free_report_projects_zero_curiosity_evidence() -> None:
    report = _report(gaps=())

    evidence = HypothesisGapCuriosityEvidenceAdapter().adapt_report(report)

    assert evidence == ()


def test_adapter_is_read_only_and_cannot_bypass_learning_or_memory() -> None:
    defaults = {
        field.name: field.default
        for field in fields(HypothesisGapCuriosityEvidenceAdapter)
    }

    for field_name in (
        "creates_questions",
        "creates_learning_candidates",
        "persists_results",
        "modifies_memory",
        "executes_actions",
        "grants_authority",
    ):
        assert defaults[field_name] is False

