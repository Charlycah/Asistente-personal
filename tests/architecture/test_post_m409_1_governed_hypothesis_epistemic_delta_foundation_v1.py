from __future__ import annotations

from dataclasses import fields

import pytest

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
    GovernedHypothesisEpistemicDeltaReport,
    GovernedHypothesisEpistemicDeltaStatus,
    HypothesisEpistemicDeltaKind,
)


def _assessment(
    hypothesis_id: str,
    relation: HypothesisEvidenceRelation,
    evidence: tuple[str, ...],
    *,
    proposition: str | None = None,
) -> HypothesisEvidenceAssessment:
    return HypothesisEvidenceAssessment(
        hypothesis_id=hypothesis_id,
        proposition=proposition or f"proposition {hypothesis_id}",
        relation=relation,
        evidence_references=evidence,
        rationale_codes=(f"assessment:{hypothesis_id}",),
        epistemic_level=EpistemicLevel.HYPOTHESIS,
    )


def _report(
    report_suffix: str,
    assessments: tuple[HypothesisEvidenceAssessment, ...],
    *,
    snapshot: str,
    source_reference: str = "scenario-123",
    status: HypothesisDeepeningStatus = HypothesisDeepeningStatus.COMPLETE,
) -> GovernedHypothesisDeepeningReport:
    return GovernedHypothesisDeepeningReport(
        report_id=f"hypothesis-deepening-{report_suffix:0<16}"[:37],
        status=status,
        source_kind=HypothesisDeepeningSourceKind.SCENARIO_SIMULATION,
        source_reference=source_reference,
        world_snapshot_id=snapshot,
        assessments=assessments,
        epistemic_gaps=(),
        evidence_codes=(f"world_snapshot:{snapshot}",),
        risk_codes=("prediction_not_fact",),
        source_fingerprint=f"fingerprint-{report_suffix}",
    )


def _trigger(snapshot: str = "world-2") -> GovernedHypothesisDeltaTrigger:
    return GovernedHypothesisDeltaTrigger(
        trigger_id="hypothesis-delta-trigger-evidence-1234567890",
        evidence_references=("evidence-e1",),
        source_reference="scenario-123",
        world_snapshot_id=snapshot,
        rationale_codes=("trigger:level2_acquired_evidence",),
    )


def test_same_relation_and_evidence_produces_unchanged_delta() -> None:
    h1 = _assessment("h1", HypothesisEvidenceRelation.UNRESOLVED, ("fact-a",))
    before = _report("before", (h1,), snapshot="world-1")
    after = _report("after", (h1,), snapshot="world-2")

    result = GovernedHypothesisEpistemicDeltaFoundationV1().compare(
        before, _trigger(), after
    )

    assert result.status is GovernedHypothesisEpistemicDeltaStatus.COMPLETE
    assert result.deltas[0].kind is HypothesisEpistemicDeltaKind.UNCHANGED


def test_new_evidence_with_same_relation_is_evidence_changed() -> None:
    before = _report(
        "before",
        (_assessment("h1", HypothesisEvidenceRelation.UNRESOLVED, ("fact-a",)),),
        snapshot="world-1",
    )
    after = _report(
        "after",
        (
            _assessment(
                "h1",
                HypothesisEvidenceRelation.UNRESOLVED,
                ("fact-a", "evidence-e1"),
            ),
        ),
        snapshot="world-2",
    )

    delta = GovernedHypothesisEpistemicDeltaFoundationV1().compare(
        before, _trigger(), after
    ).deltas[0]

    assert delta.kind is HypothesisEpistemicDeltaKind.EVIDENCE_CHANGED
    assert delta.added_evidence_references == ("evidence-e1",)
    assert delta.removed_evidence_references == ()


def test_relation_change_is_structural_not_strengthening_or_truth() -> None:
    before = _report(
        "before",
        (_assessment("h1", HypothesisEvidenceRelation.UNRESOLVED, ("fact-a",)),),
        snapshot="world-1",
    )
    after = _report(
        "after",
        (_assessment("h1", HypothesisEvidenceRelation.COMPATIBLE, ("fact-a",)),),
        snapshot="world-2",
    )

    delta = GovernedHypothesisEpistemicDeltaFoundationV1().compare(
        before, _trigger(), after
    ).deltas[0]

    assert delta.kind is HypothesisEpistemicDeltaKind.RELATION_CHANGED
    assert delta.before_relation is HypothesisEvidenceRelation.UNRESOLVED
    assert delta.after_relation is HypothesisEvidenceRelation.COMPATIBLE
    assert not delta.establishes_truth
    assert not delta.establishes_falsity


def test_relation_and_evidence_change_are_both_visible() -> None:
    before = _report(
        "before",
        (_assessment("h1", HypothesisEvidenceRelation.UNRESOLVED, ("fact-a",)),),
        snapshot="world-1",
    )
    after = _report(
        "after",
        (
            _assessment(
                "h1",
                HypothesisEvidenceRelation.CONTRADICTED,
                ("fact-a", "evidence-e1"),
            ),
        ),
        snapshot="world-2",
    )

    delta = GovernedHypothesisEpistemicDeltaFoundationV1().compare(
        before, _trigger(), after
    ).deltas[0]

    assert (
        delta.kind
        is HypothesisEpistemicDeltaKind.RELATION_AND_EVIDENCE_CHANGED
    )
    assert delta.added_evidence_references == ("evidence-e1",)
    assert not delta.establishes_falsity


def test_new_hypothesis_is_observed_without_truth_promotion() -> None:
    before = _report("before", (), snapshot="world-1")
    after = _report(
        "after",
        (_assessment("h2", HypothesisEvidenceRelation.COMPATIBLE, ("evidence-e1",)),),
        snapshot="world-2",
    )

    delta = GovernedHypothesisEpistemicDeltaFoundationV1().compare(
        before, _trigger(), after
    ).deltas[0]

    assert delta.kind is HypothesisEpistemicDeltaKind.NEW_HYPOTHESIS
    assert delta.proposition_before is None
    assert not delta.establishes_truth


def test_missing_hypothesis_requires_review_without_deletion() -> None:
    before = _report(
        "before",
        (_assessment("h1", HypothesisEvidenceRelation.UNRESOLVED, ("fact-a",)),),
        snapshot="world-1",
    )
    after = _report("after", (), snapshot="world-2")

    result = GovernedHypothesisEpistemicDeltaFoundationV1().compare(
        before, _trigger(), after
    )

    assert result.status is GovernedHypothesisEpistemicDeltaStatus.REVIEW_REQUIRED
    assert result.deltas[0].kind is HypothesisEpistemicDeltaKind.MISSING_FROM_AFTER
    assert not result.deltas[0].deletes_hypothesis
    assert not result.deltas[0].revokes_evidence


def test_same_hypothesis_id_with_changed_proposition_requires_review() -> None:
    before = _report(
        "before",
        (
            _assessment(
                "h1",
                HypothesisEvidenceRelation.UNRESOLVED,
                (),
                proposition="original proposition",
            ),
        ),
        snapshot="world-1",
    )
    after = _report(
        "after",
        (
            _assessment(
                "h1",
                HypothesisEvidenceRelation.UNRESOLVED,
                (),
                proposition="different proposition",
            ),
        ),
        snapshot="world-2",
    )

    result = GovernedHypothesisEpistemicDeltaFoundationV1().compare(
        before, _trigger(), after
    )

    assert result.status is GovernedHypothesisEpistemicDeltaStatus.REVIEW_REQUIRED
    assert result.deltas[0].kind is HypothesisEpistemicDeltaKind.PROPOSITION_CONFLICT


def test_trigger_must_identify_after_snapshot_and_same_source_lineage() -> None:
    before = _report("before", (), snapshot="world-1")
    after = _report("after", (), snapshot="world-2")

    with pytest.raises(ValueError, match="after snapshot"):
        GovernedHypothesisEpistemicDeltaFoundationV1().compare(
            before, _trigger("wrong-snapshot"), after
        )

    other_source_after = _report(
        "after-two", (), snapshot="world-2", source_reference="scenario-other"
    )
    with pytest.raises(ValueError, match="one source reference"):
        GovernedHypothesisEpistemicDeltaFoundationV1().compare(
            before, _trigger(), other_source_after
        )


def test_source_review_is_preserved_without_fabricating_deltas() -> None:
    before = _report(
        "before",
        (),
        snapshot="world-1",
        status=HypothesisDeepeningStatus.SOURCE_REVIEW_REQUIRED,
    )
    after = _report("after", (), snapshot="world-2")

    result = GovernedHypothesisEpistemicDeltaFoundationV1().compare(
        before, _trigger(), after
    )

    assert (
        result.status
        is GovernedHypothesisEpistemicDeltaStatus.SOURCE_REVIEW_REQUIRED
    )
    assert result.deltas == ()


def test_same_inputs_are_deterministic_and_preserve_explicit_lineage() -> None:
    before = _report(
        "before",
        (_assessment("h1", HypothesisEvidenceRelation.UNRESOLVED, ("fact-a",)),),
        snapshot="world-1",
    )
    after = _report(
        "after",
        (
            _assessment(
                "h1",
                HypothesisEvidenceRelation.COMPATIBLE,
                ("fact-a", "evidence-e1"),
            ),
        ),
        snapshot="world-2",
    )
    foundation = GovernedHypothesisEpistemicDeltaFoundationV1()

    first = foundation.compare(before, _trigger(), after)
    second = foundation.compare(before, _trigger(), after)

    assert first == second
    assert first.before_report_id == before.report_id
    assert first.after_report_id == after.report_id
    assert first.before_world_snapshot_id == "world-1"
    assert first.after_world_snapshot_id == "world-2"
    assert first.triggering_evidence_references == ("evidence-e1",)


def test_contract_is_read_only_non_authoritative_and_non_persistent() -> None:
    defaults = {
        field.name: field.default
        for field in fields(GovernedHypothesisEpistemicDeltaReport)
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
