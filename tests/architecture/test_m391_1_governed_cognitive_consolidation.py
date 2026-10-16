from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone
from pathlib import Path

import pytest

from core.cognitive_maturity import (
    CognitiveConsolidationStatus,
    CognitiveInactivityContext,
    CognitiveInactivityKind,
    PendingMattersAuthority,
    PeriodicReflectionAuthority,
    PeriodicReflectionCadence,
    UnifiedEpistemicEvidenceAuthority,
    UnifiedEpistemicStatus,
)
from core.learning_foundation import (
    LearningCandidate,
    LearningCandidateDisposition,
)
from core.memory_consolidation_foundation import (
    ConsolidationAssessment,
    ConsolidationDisposition,
    ConsolidationReason,
    ConsolidationTarget,
)

ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 8, 7, 14, 0, tzinfo=timezone.utc)


def _inactivity(kind=CognitiveInactivityKind.EXTENDED_IDLE):
    return CognitiveInactivityContext(
        kind=kind,
        declared_duration_seconds=3600,
        declaration_code="explicit_idle_window",
        evidence_codes=("caller_declared_inactivity",),
    )


def _periodic_report(open_matter_count=0):
    authority = PeriodicReflectionAuthority()
    schedule = authority.define_schedule(PeriodicReflectionCadence.MANUAL)
    report = authority.review(
        schedule,
        PendingMattersAuthority().analyze((), (), None, None),
        evaluated_at=NOW,
        manual_trigger=True,
    )
    return replace(report, open_matter_count=open_matter_count)


def _memory_assessment():
    return ConsolidationAssessment(
        candidate_id="m391-memory-candidate",
        disposition=ConsolidationDisposition.PROPOSE_LONG_TERM,
        proposed_target=ConsolidationTarget.LONG_TERM,
        reasons=(ConsolidationReason.REPEATED_EVIDENCE,),
        requires_human_confirmation=True,
    )


def _learning_candidate():
    return LearningCandidate(
        candidate_id="m391-learning-candidate",
        subject="coded_subject",
        proposed_value="coded_value",
        observation_ids=("observation-1", "observation-2"),
        confidence=0.8,
        disposition=LearningCandidateDisposition.REVIEW_REQUIRED,
        accepted_as_knowledge=False,
        persistence_authorized=False,
    )


def test_m391_1_extends_existing_periodic_reflection_authority() -> None:
    authority = PeriodicReflectionAuthority()
    assert authority.authority_id == "periodic_reflection"
    assert callable(authority.consolidate)
    assert callable(authority.consolidate_safely)


def test_m391_1_requires_explicit_inactivity_without_background_authority() -> None:
    context = _inactivity()
    assert context.conversation_active is False
    assert context.grants_authority is False
    assert context.starts_background_process is False
    with pytest.raises(ValueError):
        replace(context, conversation_active=True)


def test_m391_1_stable_consolidation_is_read_only() -> None:
    report = PeriodicReflectionAuthority().consolidate(
        _inactivity(),
        _periodic_report(),
    )
    assert report.status is CognitiveConsolidationStatus.STABLE
    assert report.read_only is True
    assert report.grants_authority is False
    assert report.contains_conversation_content is False
    assert report.open_matter_count == 0


def test_m391_1_open_matters_recommend_review_without_resolving_them() -> None:
    report = PeriodicReflectionAuthority().consolidate(
        _inactivity(),
        _periodic_report(open_matter_count=2),
    )
    assert report.status is CognitiveConsolidationStatus.REVIEW_RECOMMENDED
    assert "open_matters:2" in report.summary_codes
    assert report.creates_task is False
    assert report.creates_reminder is False


def test_m391_1_missing_periodic_evidence_remains_insufficient() -> None:
    report = PeriodicReflectionAuthority().consolidate(_inactivity(), None)
    assert report.status is CognitiveConsolidationStatus.INSUFFICIENT_EVIDENCE
    assert report.risk_codes == ("insufficient_consolidation_evidence",)


def test_m391_1_consumes_m366_assessment_without_persisting_memory() -> None:
    report = PeriodicReflectionAuthority().consolidate(
        _inactivity(),
        _periodic_report(),
        memory_assessment=_memory_assessment(),
    )
    assert report.status is CognitiveConsolidationStatus.MEMORY_CANDIDATE_AVAILABLE
    assert report.memory_candidate_available is True
    assert report.source_memory_assessment_candidate_id == "m391-memory-candidate"
    assert report.creates_memory is False
    assert report.modifies_memory is False


def test_m391_1_consumes_existing_learning_candidate_without_accepting_it() -> None:
    report = PeriodicReflectionAuthority().consolidate(
        _inactivity(),
        _periodic_report(),
        learning_candidate=_learning_candidate(),
    )
    assert report.status is CognitiveConsolidationStatus.LEARNING_CANDIDATE_AVAILABLE
    assert report.learning_candidate_available is True
    assert report.creates_learning_candidate is False
    assert report.accepts_learning_candidate is False
    assert report.modifies_learning is False


def test_m391_1_multiple_candidates_remain_governed_review() -> None:
    report = PeriodicReflectionAuthority().consolidate(
        _inactivity(),
        _periodic_report(),
        memory_assessment=_memory_assessment(),
        learning_candidate=_learning_candidate(),
    )
    assert report.status is CognitiveConsolidationStatus.REVIEW_RECOMMENDED
    assert report.memory_candidate_available is True
    assert report.learning_candidate_available is True


def test_m391_1_epistemic_conflict_is_exposed_not_repaired() -> None:
    epistemic = UnifiedEpistemicEvidenceAuthority().unify(None)
    epistemic = replace(
        epistemic,
        status=UnifiedEpistemicStatus.CONFLICT_REVIEW_REQUIRED,
        conflict_codes=("epistemic_conflict:synthetic",),
        risk_codes=("requires_human_review",),
    )
    report = PeriodicReflectionAuthority().consolidate(
        _inactivity(),
        _periodic_report(),
        epistemic_report=epistemic,
    )
    assert report.status is CognitiveConsolidationStatus.CONFLICT_PRESENT
    assert "epistemic_conflict:synthetic" in report.risk_codes
    assert report.modifies_memory is False
    assert report.modifies_learning is False


def test_m391_1_same_evidence_produces_same_report() -> None:
    authority = PeriodicReflectionAuthority()
    context = _inactivity()
    periodic = _periodic_report()
    assert authority.consolidate(context, periodic) == authority.consolidate(
        context,
        periodic,
    )


def test_m391_1_contracts_are_immutable() -> None:
    context = _inactivity()
    report = PeriodicReflectionAuthority().consolidate(
        context,
        _periodic_report(),
    )
    with pytest.raises(FrozenInstanceError):
        context.declared_duration_seconds = 2
    with pytest.raises(FrozenInstanceError):
        report.status = CognitiveConsolidationStatus.DEGRADED


def test_m391_1_failure_degrades_without_side_effects() -> None:
    class BrokenAuthority(PeriodicReflectionAuthority):
        def consolidate(self, *args, **kwargs):
            raise RuntimeError("synthetic failure")

    report = BrokenAuthority().consolidate_safely(
        _inactivity(),
        _periodic_report(),
    )
    assert report.status is CognitiveConsolidationStatus.DEGRADED
    assert report.risk_codes == ("cognitive_consolidation_failure",)
    assert report.starts_background_process is False
    assert report.executes_action is False


def test_m391_1_has_no_runtime_automation_or_private_credentials_reference() -> None:
    paths = (
        ROOT / "core" / "cognitive_maturity" / "cognitive_consolidation.py",
        ROOT / "core" / "cognitive_maturity" / "periodic_reflection.py",
    )
    source = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    assert "credentials.json" not in source
    assert ".roby" not in source
    assert "threading" not in source
    assert "asyncio" not in source
    assert "sleep(" not in source
    assert "memory.store" not in source
    assert "create_task(" not in source
    assert "create_reminder(" not in source


def test_m391_1_preserves_canonical_core_constructor_line() -> None:
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
