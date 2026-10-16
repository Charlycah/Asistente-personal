from __future__ import annotations

from dataclasses import dataclass

import pytest

from core.governed_reasoning.epistemic_sufficiency import (
    EpistemicSufficiencyStatus,
    GovernedEpistemicSufficiencyAssessmentFoundationV1,
)
from core.governed_reasoning.hypothesis_deepening import (
    GovernedHypothesisDeepeningReport,
    HypothesisDeepeningSourceKind,
    HypothesisDeepeningStatus,
    HypothesisEpistemicGap,
    HypothesisEvidenceAssessment,
    HypothesisEvidenceRelation,
)
from core.governed_reasoning.hypothesis_epistemic_delta import (
    GovernedHypothesisDeltaTrigger,
    GovernedHypothesisEpistemicDeltaFoundationV1,
)
from core.governed_reasoning.hypothesis_update_semantics import (
    GovernedHypothesisUpdateSemanticsFoundationV1,
    HypothesisUpdateSemantic,
)
from core.governed_reasoning.multi_hypothesis_discrimination import (
    GovernedMultiHypothesisDiscriminator,
)


@dataclass(frozen=True)
class ChallengeCase:
    case_id: str
    expected: str
    before_h0: HypothesisEvidenceRelation
    before_h1: HypothesisEvidenceRelation
    after_h0: HypothesisEvidenceRelation
    after_h1: HypothesisEvidenceRelation
    unresolved_after: bool = False


CASES = (
    ChallengeCase("cr1-a", "REVISE", HypothesisEvidenceRelation.COMPATIBLE,
                  HypothesisEvidenceRelation.UNRESOLVED,
                  HypothesisEvidenceRelation.CONTRADICTED,
                  HypothesisEvidenceRelation.COMPATIBLE),
    ChallengeCase("cr1-b", "REVISE", HypothesisEvidenceRelation.COMPATIBLE,
                  HypothesisEvidenceRelation.CONTRADICTED,
                  HypothesisEvidenceRelation.CONTRADICTED,
                  HypothesisEvidenceRelation.COMPATIBLE),
    ChallengeCase("cr1-c", "REVISE", HypothesisEvidenceRelation.UNRESOLVED,
                  HypothesisEvidenceRelation.UNRESOLVED,
                  HypothesisEvidenceRelation.CONTRADICTED,
                  HypothesisEvidenceRelation.COMPATIBLE),
    ChallengeCase("cr1-d", "REVISE", HypothesisEvidenceRelation.COMPATIBLE,
                  HypothesisEvidenceRelation.UNRESOLVED,
                  HypothesisEvidenceRelation.CONTRADICTED,
                  HypothesisEvidenceRelation.COMPATIBLE),
    ChallengeCase("cr2-a", "PRESERVE", HypothesisEvidenceRelation.COMPATIBLE,
                  HypothesisEvidenceRelation.UNRESOLVED,
                  HypothesisEvidenceRelation.COMPATIBLE,
                  HypothesisEvidenceRelation.CONTRADICTED),
    ChallengeCase("cr2-b", "PRESERVE", HypothesisEvidenceRelation.COMPATIBLE,
                  HypothesisEvidenceRelation.CONTRADICTED,
                  HypothesisEvidenceRelation.COMPATIBLE,
                  HypothesisEvidenceRelation.CONTRADICTED),
    ChallengeCase("cr2-c", "PRESERVE", HypothesisEvidenceRelation.UNRESOLVED,
                  HypothesisEvidenceRelation.UNRESOLVED,
                  HypothesisEvidenceRelation.COMPATIBLE,
                  HypothesisEvidenceRelation.CONTRADICTED),
    ChallengeCase("cr2-d", "PRESERVE", HypothesisEvidenceRelation.COMPATIBLE,
                  HypothesisEvidenceRelation.UNRESOLVED,
                  HypothesisEvidenceRelation.COMPATIBLE,
                  HypothesisEvidenceRelation.CONTRADICTED),
    ChallengeCase("cr3-a", "WITHHOLD", HypothesisEvidenceRelation.UNRESOLVED,
                  HypothesisEvidenceRelation.UNRESOLVED,
                  HypothesisEvidenceRelation.UNRESOLVED,
                  HypothesisEvidenceRelation.UNRESOLVED, True),
    ChallengeCase("cr3-b", "WITHHOLD", HypothesisEvidenceRelation.COMPATIBLE,
                  HypothesisEvidenceRelation.UNRESOLVED,
                  HypothesisEvidenceRelation.COMPATIBLE,
                  HypothesisEvidenceRelation.UNRESOLVED, True),
    ChallengeCase("cr3-c", "WITHHOLD", HypothesisEvidenceRelation.UNRESOLVED,
                  HypothesisEvidenceRelation.CONTRADICTED,
                  HypothesisEvidenceRelation.UNRESOLVED,
                  HypothesisEvidenceRelation.CONTRADICTED, True),
    ChallengeCase("cr3-d", "WITHHOLD", HypothesisEvidenceRelation.UNRESOLVED,
                  HypothesisEvidenceRelation.UNRESOLVED,
                  HypothesisEvidenceRelation.UNRESOLVED,
                  HypothesisEvidenceRelation.UNRESOLVED, True),
)


def _assessment(
    hypothesis_id: str,
    relation: HypothesisEvidenceRelation,
    *,
    evidence: tuple[str, ...],
) -> HypothesisEvidenceAssessment:
    return HypothesisEvidenceAssessment(
        hypothesis_id=hypothesis_id,
        proposition=f"candidate explanation {hypothesis_id}",
        relation=relation,
        evidence_references=evidence,
        rationale_codes=(f"challenge:{hypothesis_id}:{relation.value}",),
    )


def _gap(hypothesis_id: str, case_id: str) -> HypothesisEpistemicGap:
    return HypothesisEpistemicGap(
        gap_id=f"hypothesis-gap-{case_id}-{hypothesis_id}",
        hypothesis_id=hypothesis_id,
        subject=f"candidate explanation {hypothesis_id}",
        source_kind=HypothesisDeepeningSourceKind.SCENARIO_SIMULATION,
        source_reference=f"critical-reasoning-{case_id}",
        known_elements=("initial-observation",),
        unknown_element=f"discriminating evidence for {hypothesis_id}",
        evidence_codes=("world_snapshot:after",),
        hypothesis=f"candidate explanation {hypothesis_id}",
    )


def _report(
    case: ChallengeCase,
    *,
    after: bool,
) -> GovernedHypothesisDeepeningReport:
    snapshot = f"{case.case_id}-{'after' if after else 'before'}"
    h0 = case.after_h0 if after else case.before_h0
    h1 = case.after_h1 if after else case.before_h1
    gaps = (
        (_gap("h0", case.case_id), _gap("h1", case.case_id))
        if after and case.unresolved_after
        else ()
    )
    status = (
        HypothesisDeepeningStatus.EPISTEMIC_GAPS_PRESENT
        if gaps
        else HypothesisDeepeningStatus.COMPLETE
    )
    return GovernedHypothesisDeepeningReport(
        report_id=f"hypothesis-deepening-{case.case_id}-{'a' if after else 'b'}",
        status=status,
        source_kind=HypothesisDeepeningSourceKind.SCENARIO_SIMULATION,
        source_reference=f"critical-reasoning-{case.case_id}",
        world_snapshot_id=snapshot,
        assessments=(
            _assessment(
                "h0",
                h0,
                evidence=("initial-observation", "challenge-evidence"),
            ),
            _assessment(
                "h1",
                h1,
                evidence=("initial-observation", "challenge-evidence"),
            ),
        ),
        epistemic_gaps=gaps,
        evidence_codes=(f"world_snapshot:{snapshot}",),
        risk_codes=("challenge_not_truth_claim",),
        source_fingerprint=(
            f"fingerprint-{case.case_id}-{'after' if after else 'before'}"
        ),
    )


def _evaluate(case: ChallengeCase) -> tuple[str, object, object]:
    before = _report(case, after=False)
    after = _report(case, after=True)
    trigger = GovernedHypothesisDeltaTrigger(
        trigger_id=f"hypothesis-delta-trigger-{case.case_id}-challenge",
        evidence_references=("challenge-evidence",),
        source_reference=f"critical-reasoning-{case.case_id}",
        world_snapshot_id=after.world_snapshot_id,
        rationale_codes=("trigger:discriminating_challenge_evidence",),
    )
    delta = GovernedHypothesisEpistemicDeltaFoundationV1().compare(
        before, trigger, after
    )
    semantics = GovernedHypothesisUpdateSemanticsFoundationV1().classify(delta)
    discrimination = GovernedMultiHypothesisDiscriminator().compare(after)
    sufficiency = GovernedEpistemicSufficiencyAssessmentFoundationV1().assess(
        after,
        discrimination=discrimination,
        update_semantics=semantics,
    )
    updates = {item.hypothesis_id: item.semantic for item in semantics.updates}

    if sufficiency.status is not EpistemicSufficiencyStatus.SUFFICIENT:
        disposition = "WITHHOLD"
    elif (
        updates.get("h0") is HypothesisUpdateSemantic.WEAKENED
        and case.after_h1 is HypothesisEvidenceRelation.COMPATIBLE
    ):
        disposition = "REVISE"
    elif (
        case.after_h0 is HypothesisEvidenceRelation.COMPATIBLE
        and case.after_h1 is HypothesisEvidenceRelation.CONTRADICTED
    ):
        disposition = "PRESERVE"
    else:
        disposition = "WITHHOLD"
    return disposition, semantics, sufficiency


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.case_id)
def test_12_case_existing_authority_critical_reasoning_challenge(
    case: ChallengeCase,
) -> None:
    disposition, semantics, sufficiency = _evaluate(case)

    assert disposition == case.expected
    assert semantics.canonical_authority == "governed_reasoning"
    assert sufficiency.canonical_authority == "governed_reasoning"
    assert not semantics.establishes_truth
    assert not semantics.establishes_falsity
    assert not semantics.modifies_hypotheses
    assert not semantics.persists_results
    assert not sufficiency.establishes_truth
    assert not sufficiency.establishes_falsity
    assert not sufficiency.authorizes_stopping
    assert not sufficiency.persists_results
