from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.internal_world_model_foundation import InternalWorldModelFoundation
from core.ambient_context_foundation.models import (
    AmbientContext,
    AmbientContextFoundationRequest,
    AmbientObservationSignal,
)
from core.governed_context_representation import (
    ContextRepresentationStatus,
    GovernedContextSource,
)
from core.unified_cognitive_blackboard import CognitiveBlackboardEntry

ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 8, 7, 18, tzinfo=timezone.utc)


def _entry(
    *, kind: str = "context", key: str = "mode", value: str = "work"
) -> CognitiveBlackboardEntry:
    return CognitiveBlackboardEntry(
        owner="owner",
        session_id="session",
        domain="conversation",
        kind=kind,
        key=key,
        value=value,
        confidence=0.9,
        source_reference_ids=("explicit-source",),
        created_at=NOW,
    )


def _ambient(*, ready: bool = True) -> AmbientContext:
    observation = AmbientObservationSignal(
        observation_ref="room-observation",
        source="home_system",
        scope="room",
        privacy_level="personal",
        confidence=0.8,
        observed_at=NOW,
    )
    request = AmbientContextFoundationRequest(
        owner="owner",
        observation=observation,
        ambient_context_declared=True,
        explicit_user_consent=True,
    )
    if ready:
        return AmbientContext(
            request=request,
            status="ready",
            action="establish",
            observation_available=True,
            context_resolution_required=True,
            external_provider_required=False,
            presence_inference_allowed=False,
            activity_inference_allowed=False,
            acoustic_analysis_allowed=False,
            environmental_condition_analysis_allowed=False,
            spatial_inference_allowed=False,
            automation_allowed=False,
            rationale=("explicit governed observation",),
            created_at=NOW,
        )
    request = AmbientContextFoundationRequest(
        owner="owner",
        observation=None,
        ambient_context_declared=True,
        explicit_user_consent=True,
    )
    return AmbientContext(
        request=request,
        status="review_required",
        action="withhold",
        observation_available=False,
        context_resolution_required=False,
        external_provider_required=False,
        presence_inference_allowed=False,
        activity_inference_allowed=False,
        acoustic_analysis_allowed=False,
        environmental_condition_analysis_allowed=False,
        spatial_inference_allowed=False,
        automation_allowed=False,
        rationale=("insufficient explicit observation",),
        created_at=NOW,
    )


def test_m392_6_projects_explicit_blackboard_context_only() -> None:
    report = InternalWorldModelFoundation().context_representation((_entry(),))
    assert report.status is ContextRepresentationStatus.COMPLETE
    assert report.items[0].key == "mode"
    assert report.items[0].source is GovernedContextSource.COGNITIVE_BLACKBOARD


def test_m392_6_ignores_non_context_blackboard_entries() -> None:
    report = InternalWorldModelFoundation().context_representation(
        (_entry(kind="signal"),)
    )
    assert report.status is ContextRepresentationStatus.EMPTY
    assert report.items == ()


def test_m392_6_projects_ready_ambient_context() -> None:
    report = InternalWorldModelFoundation().context_representation(
        ambient_contexts=(_ambient(),)
    )
    assert report.status is ContextRepresentationStatus.COMPLETE
    assert report.items[0].source is GovernedContextSource.AMBIENT_CONTEXT
    assert report.items[0].value == "room-observation"


def test_m392_6_non_ready_ambient_context_requires_review() -> None:
    report = InternalWorldModelFoundation().context_representation(
        ambient_contexts=(_ambient(ready=False),)
    )
    assert report.status is ContextRepresentationStatus.REVIEW_REQUIRED
    assert report.items == ()
    assert report.risk_codes


def test_m392_6_preserves_internal_world_authority() -> None:
    report = InternalWorldModelFoundation().context_representation()
    assert report.canonical_authority == "internal_world_model"
    assert report.grants_authority is False


def test_m392_6_empty_input_stays_empty() -> None:
    report = InternalWorldModelFoundation().context_representation()
    assert report.status is ContextRepresentationStatus.EMPTY
    assert report.items == ()


def test_m392_6_preserves_evidence_references() -> None:
    entry = _entry()
    report = InternalWorldModelFoundation().context_representation((entry,))
    assert entry.entry_id in report.items[0].evidence_refs
    assert "explicit-source" in report.items[0].evidence_refs


def test_m392_6_is_deterministic() -> None:
    entries = (_entry(key="b"), _entry(key="a"))
    foundation = InternalWorldModelFoundation()
    first = foundation.context_representation(entries)
    second = foundation.context_representation(entries)
    assert first == second


def test_m392_6_is_read_only_and_non_operational() -> None:
    report = InternalWorldModelFoundation().context_representation((_entry(),))
    assert report.read_only is True
    assert report.persistence_added is False
    assert report.context_inference_added is False
    assert report.personal_state_inference_added is False
    assert report.location_tracking_added is False
    assert report.automation_added is False
    assert report.runtime_behavior_changed is False
    assert report.starts_background_process is False


def test_m392_6_does_not_infer_personal_state() -> None:
    report = InternalWorldModelFoundation().context_representation(
        (_entry(key="declared_context", value="travel"),)
    )
    assert report.items[0].value == "travel"
    assert report.personal_state_inference_added is False


def test_m392_6_report_is_immutable() -> None:
    report = InternalWorldModelFoundation().context_representation((_entry(),))
    with pytest.raises(FrozenInstanceError):
        report.status = ContextRepresentationStatus.EMPTY  # type: ignore[misc]


def test_m392_6_preserves_canonical_core_contract_position() -> None:
    path = ROOT / "app" / "official_conversation_gateway.py"
    lines = path.read_text(encoding="utf-8").splitlines()
    hits = [
        index + 1
        for index, line in enumerate(lines)
        if "CanonicalCognitiveCore(" in line
    ]
    assert hits == [52]


def test_m392_6_does_not_reference_private_credentials() -> None:
    source = (ROOT / "core" / "governed_context_representation.py").read_text(
        encoding="utf-8"
    )
    assert "credentials.json" not in source
    assert ".roby" not in source


def test_m392_6_does_not_use_wall_clock_or_background_runtime() -> None:
    source = (ROOT / "core" / "governed_context_representation.py").read_text(
        encoding="utf-8"
    )
    assert "datetime.now" not in source
    assert "asyncio" not in source
    assert "threading" not in source
    assert "sleep(" not in source


def test_m392_6_documentation_declares_governed_limits() -> None:
    text = (ROOT / "docs" / "M392_6_GOVERNED_CONTEXT.md").read_text(
        encoding="utf-8"
    )
    for phrase in (
        "internal_world_model",
        "no crea una autoridad paralela",
        "no infiere estados personales",
        "no activa automatizaciones",
    ):
        assert phrase in text
