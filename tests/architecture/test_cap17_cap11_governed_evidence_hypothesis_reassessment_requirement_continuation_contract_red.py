from __future__ import annotations

import inspect
from dataclasses import fields
from pathlib import Path

from app.productive_reasoning_local_library_bridge_invocation import (
    GovernedProductiveReasoningLibraryInvocationResult,
)
from core.governed_reasoning.hypothesis_deepening import GovernedHypothesisDeepener
from core.governed_reasoning.multi_hypothesis_discrimination import (
    DiscriminatingEvidenceRequirement,
    GovernedMultiHypothesisDiscriminator,
)

ROOT = Path(__file__).resolve().parents[2]
PRODUCTIVE = ROOT / "app" / "productive_reasoning_local_library_bridge_invocation.py"
ADMISSION = (
    ROOT
    / "app"
    / "governed_long_horizon_investigation_reassessment_requirement_admission.py"
)


def test_red_requirement_preserves_exact_hypothesis_report_lineage() -> None:
    names = {item.name for item in fields(DiscriminatingEvidenceRequirement)}
    assert "source_report_id" in names


def test_red_discriminator_propagates_exact_source_report_into_requirement() -> None:
    source = inspect.getsource(GovernedMultiHypothesisDiscriminator._requirement)
    assert "source_report_id=report.report_id" in source


def test_red_productive_cap17_preserves_completed_local_reasoning_reentry() -> None:
    names = {
        item.name for item in fields(GovernedProductiveReasoningLibraryInvocationResult)
    }
    assert "local_reasoning_reentry" in names


def test_red_governed_reasoning_exposes_same_hypothesis_reassessment_port() -> None:
    assert hasattr(GovernedHypothesisDeepener, "reassess_with_governed_evidence")


def test_red_reassessment_port_is_not_transport_specific() -> None:
    method = getattr(
        GovernedHypothesisDeepener,
        "reassess_with_governed_evidence",
        None,
    )
    assert method is not None
    source = inspect.getsource(method)
    assert "GovernedLocalEvidenceReasoningReentryResult" not in source
    assert "GovernedLevel2ReasoningReentryResult" not in source
    assert "GovernedHypothesisDeepeningReport" in source
    assert "source_report_id" in source
    assert "evidence_id" in source


def test_red_productive_cap17_reaches_existing_reassessment_and_admission() -> None:
    source = PRODUCTIVE.read_text(encoding="utf-8")
    assert "reassess_with_governed_evidence" in source
    assert (
        "GovernedLongHorizonInvestigationReassessmentRequirementAdmissionV1"
        in source
    )
    assert ".consume(" in ADMISSION.read_text(encoding="utf-8")


def test_red_productive_order_is_reentry_record_reassess_then_admit() -> None:
    source = PRODUCTIVE.read_text(encoding="utf-8")
    reentry_at = source.index("reasoning_reentry.reenter")
    record_at = source.index("record_local_evidence_reentry")
    reassess_at = source.find("reassess_with_governed_evidence")
    admission_at = source.find(
        "GovernedLongHorizonInvestigationReassessmentRequirementAdmissionV1"
    )
    assert reassess_at >= 0
    assert admission_at >= 0
    assert reentry_at < record_at < reassess_at < admission_at


def test_red_productive_continuation_does_not_create_parallel_cognitive_authority(
) -> None:
    source = PRODUCTIVE.read_text(encoding="utf-8")
    assert source.count("reasoning_reentry.reenter") == 1
    assert ".reason(" not in source
    for forbidden in (
        "LibraryHypothesisReassessor",
        "CAP17RequirementGenerator",
        "LocalEvidenceDeepeningManager",
        "SecondReasoningRuntime",
    ):
        assert forbidden not in source


def test_red_existing_admission_remains_the_requirement_continuation_owner() -> None:
    source = ADMISSION.read_text(encoding="utf-8")
    assert "GovernedMultiHypothesisProductiveConsumptionV1" in source
    assert "GovernedMultiStepInvestigationProductiveContinuationV1" in source
    assert "invokes_planning: bool = False" in source
