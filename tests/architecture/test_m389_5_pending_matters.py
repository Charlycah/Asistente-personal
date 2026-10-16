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
    HistoricalAnalysisAuthority,
    PendingMatterCategory,
    PendingMatterResolution,
    PendingMattersAuthority,
    PendingMattersStatus,
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
        rationale_codes=("pending_matters_test",),
        public_lead=level.public_lead,
        allows_fact_statement=level is EpistemicLevel.FACT,
        fact_promotion_requires_review=level is not EpistemicLevel.FACT,
    )


def _sources():
    cycle = create_canonical_cognitive_cycle("m389-5-turn")
    dossier = create_cognitive_turn_dossier(cycle)
    assessments = (
        _assessment("known", EpistemicLevel.FACT),
        _assessment("unknown", EpistemicLevel.UNKNOWN),
    )
    reflection = ConversationReflectionAuthority().reflect(dossier, assessments)
    reflections = (reflection,)
    history = HistoricalAnalysisAuthority().analyze(reflections)
    psychology = FunctionalPsychologyAuthority().analyze(
        assessments,
        reflections,
        history,
    )
    return assessments, reflections, history, psychology


def test_m389_5_has_one_read_only_pending_matters_authority() -> None:
    authority = PendingMattersAuthority()
    assert authority.authority_id == "pending_matters"


def test_m389_5_uses_only_coded_m389_sources() -> None:
    report = PendingMattersAuthority().analyze(*_sources())
    assert report.status is PendingMattersStatus.COMPLETE
    assert report.source_assessment_count == 2
    assert len(report.source_reflection_ids) == 1
    assert report.source_history_id is not None
    assert report.source_psychology_id is not None
    assert report.contains_conversation_content is False


def test_m389_5_detects_unknown_claim_without_private_content() -> None:
    report = PendingMattersAuthority().analyze(*_sources())
    unknown = [
        item
        for item in report.matters
        if item.category is PendingMatterCategory.INSUFFICIENT_INFORMATION
    ]
    assert len(unknown) == 1
    assert unknown[0].epistemic_level is EpistemicLevel.UNKNOWN
    assert unknown[0].resolution_state is PendingMatterResolution.UNKNOWN
    assert unknown[0].requires_follow_up is True
    assert unknown[0].summary_code == "review_claim:unknown"


def test_m389_5_statistics_are_derived_from_matters() -> None:
    report = PendingMattersAuthority().analyze(*_sources())
    assert report.statistics.total == len(report.matters)
    assert report.statistics.unknown_count == 1
    assert sum(count for _, count in report.statistics.category_counts) == len(
        report.matters
    )


def test_m389_5_is_non_authoritative_and_has_no_side_effects() -> None:
    report = PendingMattersAuthority().analyze(*_sources())
    assert report.read_only is True
    assert report.grants_authority is False
    assert report.creates_memory is False
    assert report.modifies_memory is False
    assert report.creates_learning_candidate is False
    assert report.modifies_learning is False
    assert report.modifies_planning is False
    assert report.modifies_permissions is False
    assert report.creates_task is False
    assert report.creates_reminder is False
    assert report.schedules_action is False
    assert report.resolves_matters is False


def test_m389_5_does_not_mutate_sources() -> None:
    assessments, reflections, history, psychology = _sources()
    before_assessments = tuple(replace(item) for item in assessments)
    before_reflections = tuple(replace(item) for item in reflections)
    before_history = replace(history)
    before_psychology = replace(psychology)
    PendingMattersAuthority().analyze(
        assessments,
        reflections,
        history,
        psychology,
    )
    assert assessments == before_assessments
    assert reflections == before_reflections
    assert history == before_history
    assert psychology == before_psychology


def test_m389_5_is_deterministic_and_input_order_independent() -> None:
    assessments, reflections, history, psychology = _sources()
    authority = PendingMattersAuthority()
    first = authority.analyze(assessments, reflections, history, psychology)
    second = authority.analyze(
        tuple(reversed(assessments)),
        tuple(reversed(reflections)),
        history,
        psychology,
    )
    assert first == second


def test_m389_5_report_and_matters_are_immutable() -> None:
    report = PendingMattersAuthority().analyze(*_sources())
    with pytest.raises(FrozenInstanceError):
        report.status = PendingMattersStatus.DEGRADED
    with pytest.raises(FrozenInstanceError):
        report.matters[0].summary_code = "changed"


def test_m389_5_insufficient_evidence_is_explicit_and_safe() -> None:
    report = PendingMattersAuthority().analyze((), (), None, None)
    assert report.status is PendingMattersStatus.INSUFFICIENT_EVIDENCE
    assert report.matters == ()
    assert report.statistics.total == 0


def test_m389_5_failure_degrades_without_inventing_matters() -> None:
    class BrokenAuthority(PendingMattersAuthority):
        def analyze(self, assessments, reflections, history, psychology):
            raise RuntimeError("synthetic failure")

    report = BrokenAuthority().analyze_safely((), (), None, None)
    assert report.status is PendingMattersStatus.DEGRADED
    assert report.matters == ()
    assert report.grants_authority is False
    assert report.risk_codes == ("pending_matters_failure",)


def test_m389_5_does_not_reference_credentials_or_governed_mutators() -> None:
    path = ROOT / "core" / "cognitive_maturity" / "pending_matters.py"
    source = path.read_text(encoding="utf-8")
    assert "credentials.json" not in source
    assert ".roby" not in source
    assert "memory.store" not in source
    assert "learn(" not in source
    assert "plan(" not in source
    assert "grant_permission" not in source
    assert "create_task(" not in source
    assert "create_reminder(" not in source


def test_m389_5_preserves_canonical_core_constructor_line() -> None:
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
