from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

from core.cognitive_maturity import (
    ConversationReflectionAuthority,
    EpistemicAssessment,
    EpistemicLevel,
    FunctionalPsychologyAuthority,
    FunctionalPsychologyStatus,
    HistoricalAnalysisAuthority,
    create_canonical_cognitive_cycle,
    create_cognitive_turn_dossier,
)
from core.governed_reasoning import ClaimStatus, ClaimType

ROOT = Path(__file__).resolve().parents[2]


def _assessment(claim_id: str, level: EpistemicLevel) -> EpistemicAssessment:
    return EpistemicAssessment(
        level=level,
        claim_id=claim_id,
        source_claim_type=ClaimType.OBSERVATION,
        source_claim_status=ClaimStatus.SUPPORTED,
        rationale_codes=("functional_psychology_test",),
        public_lead=level.public_lead,
        allows_fact_statement=level is EpistemicLevel.FACT,
        fact_promotion_requires_review=level is not EpistemicLevel.FACT,
    )


def _reflection(turn_id: str, level: EpistemicLevel):
    dossier = create_cognitive_turn_dossier(create_canonical_cognitive_cycle(turn_id))
    return ConversationReflectionAuthority().reflect(
        dossier,
        (_assessment(f"claim-{turn_id}", level),),
    )


def _sources():
    assessments = (
        _assessment("claim-a", EpistemicLevel.FACT),
        _assessment("claim-b", EpistemicLevel.HYPOTHESIS),
    )
    reflections = (
        _reflection("turn-a", EpistemicLevel.FACT),
        _reflection("turn-b", EpistemicLevel.HYPOTHESIS),
    )
    history = HistoricalAnalysisAuthority().analyze(reflections)
    return assessments, reflections, history


def test_m389_4_has_one_read_only_functional_psychology_authority() -> None:
    authority = FunctionalPsychologyAuthority()
    assert authority.authority_id == "functional_psychology"


def test_m389_4_uses_only_coded_m389_sources() -> None:
    assessments, reflections, history = _sources()
    report = FunctionalPsychologyAuthority().analyze(
        assessments,
        reflections,
        history,
    )
    assert report.status is FunctionalPsychologyStatus.COMPLETE
    assert report.source_assessment_count == 2
    assert report.source_reflection_ids == tuple(
        sorted(item.report_id for item in reflections)
    )
    assert report.source_history_id == history.report_id
    assert report.contains_conversation_content is False


def test_m389_4_emits_functional_not_clinical_indicators() -> None:
    assessments, reflections, history = _sources()
    report = FunctionalPsychologyAuthority().analyze(
        assessments,
        reflections,
        history,
    )
    cognitive_codes = {item.code for item in report.cognitive_style_indicators}
    assert "fact_oriented_processing" in cognitive_codes
    assert "exploratory_hypothesis_processing" in cognitive_codes
    assert report.performs_clinical_diagnosis is False
    assert report.infers_mental_disorder is False
    assert report.prescribes_action is False


def test_m389_4_is_non_authoritative_and_has_no_side_effects() -> None:
    report = FunctionalPsychologyAuthority().analyze(*_sources())
    assert report.read_only is True
    assert report.grants_authority is False
    assert report.creates_memory is False
    assert report.modifies_memory is False
    assert report.creates_learning_candidate is False
    assert report.modifies_learning is False
    assert report.modifies_planning is False
    assert report.modifies_permissions is False


def test_m389_4_does_not_mutate_sources() -> None:
    assessments, reflections, history = _sources()
    before_assessments = tuple(replace(item) for item in assessments)
    before_reflections = tuple(replace(item) for item in reflections)
    before_history = replace(history)
    FunctionalPsychologyAuthority().analyze(assessments, reflections, history)
    assert assessments == before_assessments
    assert reflections == before_reflections
    assert history == before_history


def test_m389_4_is_deterministic_and_input_order_independent() -> None:
    assessments, reflections, history = _sources()
    authority = FunctionalPsychologyAuthority()
    first = authority.analyze(assessments, reflections, history)
    second = authority.analyze(
        tuple(reversed(assessments)),
        tuple(reversed(reflections)),
        history,
    )
    assert first == second


def test_m389_4_report_is_immutable() -> None:
    report = FunctionalPsychologyAuthority().analyze(*_sources())
    with pytest.raises(FrozenInstanceError):
        report.status = FunctionalPsychologyStatus.DEGRADED


def test_m389_4_insufficient_evidence_is_explicit_and_safe() -> None:
    report = FunctionalPsychologyAuthority().analyze((), (), None)
    assert report.status is FunctionalPsychologyStatus.INSUFFICIENT_EVIDENCE
    assert report.caution_codes == (
        "no_cognitive_assessments",
        "no_conversation_reflections",
        "no_historical_analysis",
    )


def test_m389_4_failure_degrades_without_authority() -> None:
    class BrokenAuthority(FunctionalPsychologyAuthority):
        def analyze(self, assessments, reflections, history):
            raise RuntimeError("synthetic failure")

    report = BrokenAuthority().analyze_safely((), (), None)
    assert report.status is FunctionalPsychologyStatus.DEGRADED
    assert report.grants_authority is False
    assert report.caution_codes == ("functional_psychology_failure",)


def test_m389_4_does_not_reference_credentials_or_governed_mutators() -> None:
    path = ROOT / "core" / "cognitive_maturity" / "functional_psychology.py"
    source = path.read_text(encoding="utf-8")
    assert "credentials.json" not in source
    assert ".roby" not in source
    assert "memory.store" not in source
    assert "learn(" not in source
    assert "plan(" not in source
    assert "grant_permission" not in source


def test_m389_4_preserves_canonical_core_constructor_line() -> None:
    path = ROOT / "app" / "official_conversation_gateway.py"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    lines = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "CanonicalCognitiveCore"
    ]
    assert lines == [52]
