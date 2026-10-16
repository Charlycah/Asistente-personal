from __future__ import annotations

import inspect
from dataclasses import fields
from pathlib import Path

from app.governed_multistep_investigation_episode import (
    GovernedInvestigationEpisodeState,
    GovernedMultiStepInvestigationEpisodeBoundaryV1,
)

ROOT = Path(__file__).resolve().parents[2]
PRODUCTIVE = ROOT / "app" / "productive_reasoning_local_library_bridge_invocation.py"
LOCAL_REENTRY = ROOT / "app" / "governed_local_evidence_reasoning_reentry.py"
EPISODE = ROOT / "app" / "governed_multistep_investigation_episode.py"


def test_cap17_cap11_episode_state_tracks_local_execution_lineage() -> None:
    names = {item.name for item in fields(GovernedInvestigationEpisodeState)}
    assert "local_execution_ids" in names


def test_cap17_cap11_episode_boundary_exposes_local_recording_port() -> None:
    assert hasattr(
        GovernedMultiStepInvestigationEpisodeBoundaryV1,
        "record_local_evidence_reentry",
    )


def test_cap17_cap11_local_recording_port_consumes_existing_reentry() -> None:
    method = (
        GovernedMultiStepInvestigationEpisodeBoundaryV1.record_local_evidence_reentry
    )
    source = inspect.getsource(method)
    assert "GovernedLocalEvidenceReasoningReentryResult" in source
    assert "knowledge_execution_id" in source
    assert "reentry_id" in source


def test_cap17_cap11_local_recording_preserves_original_episode_lineage() -> None:
    method = (
        GovernedMultiStepInvestigationEpisodeBoundaryV1.record_local_evidence_reentry
    )
    source = inspect.getsource(method)
    for token in (
        "originating_reasoning_id",
        "requirement_id",
        "episode_id",
        "source_reference",
        "world_snapshot_id",
    ):
        assert token in source


def test_cap17_cap11_local_recording_accepts_only_successful_reevaluation() -> None:
    method = (
        GovernedMultiStepInvestigationEpisodeBoundaryV1.record_local_evidence_reentry
    )
    source = inspect.getsource(method)
    assert "GovernedLocalEvidenceReasoningReentryStatus.REEVALUATED" in source
    assert "REVIEW_REQUIRED" in source


def test_cap17_cap11_local_recording_consumes_global_acquisition_budget() -> None:
    source = EPISODE.read_text(encoding="utf-8")
    assert "len(self.execution_ids) + len(self.local_execution_ids)" in source
    method = (
        GovernedMultiStepInvestigationEpisodeBoundaryV1.record_local_evidence_reentry
    )
    method_source = inspect.getsource(method)
    assert "consumed_acquisitions" in method_source
    assert "remaining_acquisitions" in method_source


def test_cap17_cap11_local_recording_does_not_fabricate_level2_lineage() -> None:
    method = (
        GovernedMultiStepInvestigationEpisodeBoundaryV1.record_local_evidence_reentry
    )
    source = inspect.getsource(method)
    assert "plan_ids=" not in source
    assert "authorization_ids=" not in source
    assert "GovernedAcquiredEvidenceEnvelope" not in source
    assert "OfficialCapabilityGateway" not in source


def test_cap17_cap11_local_recording_is_idempotent_by_execution_and_reentry() -> None:
    method = (
        GovernedMultiStepInvestigationEpisodeBoundaryV1.record_local_evidence_reentry
    )
    source = inspect.getsource(method)
    assert "local_execution_ids" in source
    assert "reentry_ids" in source
    assert "lineage_reused" in source


def test_cap17_cap11_local_recording_closes_when_budget_is_exhausted() -> None:
    method = (
        GovernedMultiStepInvestigationEpisodeBoundaryV1.record_local_evidence_reentry
    )
    source = inspect.getsource(method)
    assert "GovernedInvestigationEpisodeStatus.CLOSED" in source
    assert "GovernedInvestigationStoppingReason.BUDGET_EXHAUSTED" in source
    assert "GovernedInvestigationContinuationDecision.STOP_REQUIRED" in source


def test_cap17_cap11_local_recording_awaits_requirement_when_budget_remains() -> None:
    method = (
        GovernedMultiStepInvestigationEpisodeBoundaryV1.record_local_evidence_reentry
    )
    source = inspect.getsource(method)
    assert "GovernedInvestigationEpisodeStatus.AWAITING_REQUIREMENT" in source
    assert "GovernedInvestigationContinuationDecision.CONTINUE_ALLOWED" in source


def test_cap17_cap11_productive_contributor_records_completed_local_reentry() -> None:
    source = PRODUCTIVE.read_text(encoding="utf-8")
    assert "record_local_evidence_reentry" in source
    assert "investigation_entry.episode_state" in source
    assert "local_reasoning_reentry" in source


def test_cap17_cap11_productive_contributor_records_only_after_reentry() -> None:
    source = PRODUCTIVE.read_text(encoding="utf-8")
    reenter_at = source.index("reasoning_reentry.reenter")
    record_at = source.index("record_local_evidence_reentry")
    assert reenter_at < record_at


def test_cap17_cap11_productive_path_does_not_reason_twice() -> None:
    source = PRODUCTIVE.read_text(encoding="utf-8")
    assert source.count("reasoning_reentry.reenter") == 1
    assert ".reason(" not in source


def test_cap17_cap11_episode_boundary_never_acquires_evidence() -> None:
    source = EPISODE.read_text(encoding="utf-8")
    assert ".search(" not in source
    assert ".read_text(" not in source
    assert "DocumentReadingService" not in source
    assert "OfficialUnifiedRetrievalExecutionRuntimeGateway" not in source


def test_cap17_cap11_local_reentry_module_remains_acquisition_free() -> None:
    source = LOCAL_REENTRY.read_text(encoding="utf-8")
    assert ".search(" not in source
    assert ".read_text(" not in source
    assert "DocumentReadingService" not in source
    assert "GovernedAcquiredEvidenceEnvelope" not in source


def test_cap17_cap11_level2_recording_contract_remains_present() -> None:
    source = EPISODE.read_text(encoding="utf-8")
    assert "def record_acquisition(" in source
    assert "def record_reentry(" in source
    assert "GovernedAcquiredEvidenceEnvelope" in source


def test_cap17_cap11_knowledge_retrieval_step_schema_is_unchanged() -> None:
    from core.knowledge_retrieval_orchestrator.models import KnowledgeRetrievalStep

    assert {item.name for item in fields(KnowledgeRetrievalStep)} == {
        "source",
        "priority",
        "required",
        "query",
        "step_id",
    }
