from __future__ import annotations

from dataclasses import fields

from core.cognitive_maturity.epistemic import EpistemicLevel
from core.governed_reasoning.hypothesis_deepening import (
    GovernedHypothesisDeepeningReport,
    HypothesisDeepeningSourceKind,
    HypothesisDeepeningStatus,
    HypothesisEvidenceAssessment,
    HypothesisEvidenceRelation,
)
from core.governed_reasoning.hypothesis_epistemic_delta import (
    GovernedHypothesisDeltaTrigger,
    GovernedHypothesisEpistemicDeltaFoundationV1,
)
from core.governed_reasoning.hypothesis_update_semantics import (
    GovernedHypothesisUpdateSemanticsFoundationV1,
    GovernedHypothesisUpdateSemanticsReport,
    GovernedHypothesisUpdateSemanticsStatus,
    HypothesisUpdateSemantic,
)


def _assessment(
    relation: HypothesisEvidenceRelation,
    evidence: tuple[str, ...] = ("fact-a",),
    *,
    hypothesis_id: str = "h1",
    proposition: str = "proposition h1",
) -> HypothesisEvidenceAssessment:
    return HypothesisEvidenceAssessment(
        hypothesis_id=hypothesis_id,
        proposition=proposition,
        relation=relation,
        evidence_references=evidence,
        rationale_codes=(f"assessment:{hypothesis_id}",),
        epistemic_level=EpistemicLevel.HYPOTHESIS,
    )


def _report(
    suffix: str,
    assessments: tuple[HypothesisEvidenceAssessment, ...],
    *,
    snapshot: str,
    status: HypothesisDeepeningStatus = HypothesisDeepeningStatus.COMPLETE,
) -> GovernedHypothesisDeepeningReport:
    return GovernedHypothesisDeepeningReport(
        report_id=f"hypothesis-deepening-{suffix:0<16}"[:37],
        status=status,
        source_kind=HypothesisDeepeningSourceKind.SCENARIO_SIMULATION,
        source_reference="scenario-123",
        world_snapshot_id=snapshot,
        assessments=assessments,
        epistemic_gaps=(),
        evidence_codes=(f"world_snapshot:{snapshot}",),
        risk_codes=("prediction_not_fact",),
        source_fingerprint=f"fingerprint-{suffix}",
    )


def _delta(
    before_assessments: tuple[HypothesisEvidenceAssessment, ...],
    after_assessments: tuple[HypothesisEvidenceAssessment, ...],
    *,
    before_status: HypothesisDeepeningStatus = HypothesisDeepeningStatus.COMPLETE,
):
    before = _report(
        "before",
        before_assessments,
        snapshot="world-1",
        status=before_status,
    )
    after = _report("after", after_assessments, snapshot="world-2")
    trigger = GovernedHypothesisDeltaTrigger(
        trigger_id="hypothesis-delta-trigger-evidence-1234567890",
        evidence_references=("evidence-e1",),
        source_reference="scenario-123",
        world_snapshot_id="world-2",
        rationale_codes=("trigger:level2_acquired_evidence",),
    )
    return GovernedHypothesisEpistemicDeltaFoundationV1().compare(
        before,
        trigger,
        after,
    )


def _semantic(delta_report):
    return GovernedHypothesisUpdateSemanticsFoundationV1().classify(
        delta_report
    )


def test_unresolved_to_compatible_is_strengthened_without_truth() -> None:
    result = _semantic(
        _delta(
            (_assessment(HypothesisEvidenceRelation.UNRESOLVED),),
            (_assessment(HypothesisEvidenceRelation.COMPATIBLE),),
        )
    )

    update = result.updates[0]
    assert update.semantic is HypothesisUpdateSemantic.STRENGTHENED
    assert not update.establishes_truth
    assert not result.establishes_truth


def test_unresolved_to_contradicted_is_weakened_without_falsity() -> None:
    result = _semantic(
        _delta(
            (_assessment(HypothesisEvidenceRelation.UNRESOLVED),),
            (_assessment(HypothesisEvidenceRelation.CONTRADICTED),),
        )
    )

    update = result.updates[0]
    assert update.semantic is HypothesisUpdateSemantic.WEAKENED
    assert not update.establishes_falsity
    assert not result.establishes_falsity


def test_compatible_to_contradicted_is_weakened() -> None:
    result = _semantic(
        _delta(
            (_assessment(HypothesisEvidenceRelation.COMPATIBLE),),
            (_assessment(HypothesisEvidenceRelation.CONTRADICTED),),
        )
    )

    assert result.updates[0].semantic is HypothesisUpdateSemantic.WEAKENED


def test_contradicted_to_compatible_is_strengthened() -> None:
    result = _semantic(
        _delta(
            (_assessment(HypothesisEvidenceRelation.CONTRADICTED),),
            (_assessment(HypothesisEvidenceRelation.COMPATIBLE),),
        )
    )

    assert result.updates[0].semantic is HypothesisUpdateSemantic.STRENGTHENED


def test_exactly_unchanged_delta_is_semantically_unchanged() -> None:
    assessment = _assessment(HypothesisEvidenceRelation.UNRESOLVED)
    result = _semantic(_delta((assessment,), (assessment,)))

    assert result.updates[0].semantic is HypothesisUpdateSemantic.UNCHANGED


def test_evidence_only_change_is_indeterminate_not_strengthened() -> None:
    result = _semantic(
        _delta(
            (_assessment(HypothesisEvidenceRelation.COMPATIBLE),),
            (
                _assessment(
                    HypothesisEvidenceRelation.COMPATIBLE,
                    ("fact-a", "evidence-e1"),
                ),
            ),
        )
    )

    update = result.updates[0]
    assert update.semantic is HypothesisUpdateSemantic.INDETERMINATE
    assert update.added_evidence_references == ("evidence-e1",)


def test_new_hypothesis_is_indeterminate_without_prior_assessment() -> None:
    result = _semantic(
        _delta(
            (),
            (
                _assessment(
                    HypothesisEvidenceRelation.COMPATIBLE,
                    ("evidence-e1",),
                    hypothesis_id="h2",
                    proposition="proposition h2",
                ),
            ),
        )
    )

    assert result.updates[0].semantic is HypothesisUpdateSemantic.INDETERMINATE


def test_missing_hypothesis_requires_review_not_weakening_or_deletion() -> None:
    result = _semantic(
        _delta(
            (_assessment(HypothesisEvidenceRelation.UNRESOLVED),),
            (),
        )
    )

    assert result.status is GovernedHypothesisUpdateSemanticsStatus.REVIEW_REQUIRED
    assert result.updates[0].semantic is HypothesisUpdateSemantic.REVIEW_REQUIRED
    assert not result.updates[0].deletes_hypothesis


def test_proposition_conflict_requires_review() -> None:
    result = _semantic(
        _delta(
            (
                _assessment(
                    HypothesisEvidenceRelation.UNRESOLVED,
                    proposition="original proposition",
                ),
            ),
            (
                _assessment(
                    HypothesisEvidenceRelation.UNRESOLVED,
                    proposition="different proposition",
                ),
            ),
        )
    )

    assert result.status is GovernedHypothesisUpdateSemanticsStatus.REVIEW_REQUIRED
    assert result.updates[0].semantic is HypothesisUpdateSemantic.REVIEW_REQUIRED


def test_unmapped_relation_transition_is_indeterminate() -> None:
    result = _semantic(
        _delta(
            (_assessment(HypothesisEvidenceRelation.COMPATIBLE),),
            (_assessment(HypothesisEvidenceRelation.UNRESOLVED),),
        )
    )

    assert result.updates[0].semantic is HypothesisUpdateSemantic.INDETERMINATE


def test_source_review_is_preserved_without_semantic_fabrication() -> None:
    result = _semantic(
        _delta(
            (),
            (),
            before_status=HypothesisDeepeningStatus.SOURCE_REVIEW_REQUIRED,
        )
    )

    assert (
        result.status
        is GovernedHypothesisUpdateSemanticsStatus.SOURCE_REVIEW_REQUIRED
    )
    assert result.updates == ()


def test_semantic_report_preserves_delta_provenance_and_is_deterministic() -> None:
    delta_report = _delta(
        (_assessment(HypothesisEvidenceRelation.UNRESOLVED),),
        (
            _assessment(
                HypothesisEvidenceRelation.COMPATIBLE,
                ("fact-a", "evidence-e1"),
            ),
        ),
    )
    foundation = GovernedHypothesisUpdateSemanticsFoundationV1()

    first = foundation.classify(delta_report)
    second = foundation.classify(delta_report)

    assert first == second
    assert first.source_delta_report_id == delta_report.report_id
    assert first.source_reference == "scenario-123"
    assert first.before_world_snapshot_id == "world-1"
    assert first.after_world_snapshot_id == "world-2"
    assert first.triggering_evidence_references == ("evidence-e1",)


def test_contract_is_read_only_non_mutating_non_persistent_and_non_numeric() -> None:
    defaults = {
        field.name: field.default
        for field in fields(GovernedHypothesisUpdateSemanticsReport)
    }
    for name in (
        "establishes_truth",
        "establishes_falsity",
        "modifies_hypotheses",
        "persists_results",
        "creates_memory",
        "creates_learning_candidate",
        "modifies_world_model",
        "invokes_reasoning",
        "invokes_comparison",
        "invokes_curiosity",
        "invokes_planning",
        "invokes_capabilities",
        "grants_authority",
        "starts_background_process",
    ):
        assert defaults[name] is False
    assert defaults["canonical_authority"] == "governed_reasoning"
    assert defaults["read_only"] is True
    assert defaults["consultative"] is True
