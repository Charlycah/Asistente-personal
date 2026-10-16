from __future__ import annotations

from dataclasses import FrozenInstanceError, replace

import pytest

from core.cognitive_maturity import (
    ConversationReflectionAuthority,
    EpistemicAssessment,
    EpistemicLevel,
    HistoricalAnalysisAuthority,
    HistoricalAnalysisStatus,
    create_canonical_cognitive_cycle,
    create_cognitive_turn_dossier,
)
from core.governed_reasoning import ClaimStatus, ClaimType


def _reflection(
    turn_id: str,
    *,
    level: EpistemicLevel | None = None,
):
    cycle = create_canonical_cognitive_cycle(turn_id)
    dossier = create_cognitive_turn_dossier(cycle)
    assessments = ()
    if level is not None:
        assessments = (
            EpistemicAssessment(
                level=level,
                claim_id=f"claim-{turn_id}",
                source_claim_type=ClaimType.OBSERVATION,
                source_claim_status=ClaimStatus.SUPPORTED,
                rationale_codes=("historical_test",),
                public_lead=level.public_lead,
                allows_fact_statement=level is EpistemicLevel.FACT,
                fact_promotion_requires_review=level is not EpistemicLevel.FACT,
            ),
        )
    return ConversationReflectionAuthority().reflect(dossier, assessments)


def test_m389_3_has_one_read_only_historical_authority() -> None:
    authority = HistoricalAnalysisAuthority()
    assert authority.authority_id == "historical_analysis"


def test_m389_3_detects_recurrent_objectives_without_private_text() -> None:
    report = HistoricalAnalysisAuthority().analyze(
        (_reflection("turn-a"), _reflection("turn-b"))
    )
    assert report.status is HistoricalAnalysisStatus.COMPLETE
    assert report.recurrent_objectives[0].count == 2
    assert report.contains_conversation_content is False


def test_m389_3_preserves_epistemic_distribution() -> None:
    report = HistoricalAnalysisAuthority().analyze(
        (
            _reflection("turn-a", level=EpistemicLevel.FACT),
            _reflection("turn-b", level=EpistemicLevel.HYPOTHESIS),
        )
    )
    codes = {item.code for item in report.epistemic_distribution}
    assert {"fact", "hypothesis"} <= codes
    assert report.contradiction_codes == ("fact_and_hypothesis_coexist",)
    assert report.resolves_contradictions is False


def test_m389_3_is_repeatable_independent_of_input_order() -> None:
    first = _reflection("turn-a")
    second = _reflection("turn-b")
    authority = HistoricalAnalysisAuthority()
    assert authority.analyze((first, second)) == authority.analyze((second, first))


def test_m389_3_report_is_immutable_and_non_authoritative() -> None:
    report = HistoricalAnalysisAuthority().analyze((_reflection("turn-a"),))
    assert report.read_only is True
    assert report.grants_authority is False
    assert report.creates_memory is False
    assert report.creates_learning_candidate is False
    with pytest.raises(FrozenInstanceError):
        report.status = HistoricalAnalysisStatus.DEGRADED


def test_m389_3_does_not_mutate_source_reflections() -> None:
    reflection = _reflection("turn-a")
    before = replace(reflection)
    HistoricalAnalysisAuthority().analyze((reflection,))
    assert reflection == before


def test_m389_3_failure_degrades_safely() -> None:
    class BrokenAuthority(HistoricalAnalysisAuthority):
        def analyze(self, reflections):
            raise RuntimeError("synthetic failure")

    report = BrokenAuthority().analyze_safely((_reflection("turn-a"),))
    assert report.status is HistoricalAnalysisStatus.DEGRADED
    assert report.grants_authority is False
    assert report.recurrent_risks[0].code == "historical_analysis_failure"
