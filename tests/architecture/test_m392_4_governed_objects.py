from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.internal_world_model_foundation import InternalWorldModelFoundation
from core.governed_objects_representation import ObjectRepresentationStatus
from core.object_knowledge import (
    ObjectEvidence,
    ObjectKind,
    ObjectKnowledgeEngine,
    ObjectKnowledgeRequest,
)
from core.scene_understanding import (
    SceneEvidence,
    SceneKind,
    SceneUnderstandingEngine,
    SceneUnderstandingRequest,
)
from core.visual_observation_resolution import (
    VisualObservationPurpose,
    VisualObservationResolutionEngine,
    VisualObservationResolutionRequest,
)
from core.visual_understanding_foundation import (
    VisualMediaType,
    VisualObservationSignal,
    VisualObservationSource,
    VisualPrivacyLevel,
    VisualUnderstandingFoundationEngine,
    VisualUnderstandingFoundationRequest,
)

ROOT = Path(__file__).resolve().parents[2]
NOW = datetime(2026, 8, 7, 18, 0, tzinfo=timezone.utc)


def _profile():
    visual = VisualUnderstandingFoundationEngine().establish(
        VisualUnderstandingFoundationRequest(
            owner="Carlos",
            observation=VisualObservationSignal(
                observation_ref="obs-m392-4",
                source=VisualObservationSource.MOBILE_CAMERA,
                media_type=VisualMediaType.PHOTO,
                privacy_level=VisualPrivacyLevel.PERSONAL,
                confidence=0.96,
                observed_at=NOW,
                source_device_id="phone-main",
            ),
            explicit_user_consent=True,
        ),
        now=NOW,
    )
    resolution = VisualObservationResolutionEngine().resolve(
        VisualObservationResolutionRequest(
            owner="Carlos",
            visual_context=visual,
            purpose=VisualObservationPurpose.SCENE_CONTEXT,
        ),
        now=NOW,
    )
    scene = SceneUnderstandingEngine().understand(
        SceneUnderstandingRequest(
            owner="Carlos",
            resolved_observation=resolution,
            evidence=(
                SceneEvidence(
                    evidence_ref="scene-m392-4",
                    observation_ref="obs-m392-4",
                    scene_kind=SceneKind.WORKSPACE,
                    confidence=0.94,
                    attributes=("desk",),
                ),
            ),
        ),
        now=NOW,
    )
    request = ObjectKnowledgeRequest(
        owner="Carlos",
        scene_understanding=scene,
        evidence=(
            ObjectEvidence(
                evidence_ref="object-evidence-m392-4",
                observation_ref="obs-m392-4",
                object_ref="laptop-main",
                object_kind=ObjectKind.ELECTRONICS,
                label="Laptop",
                confidence=0.92,
                attributes=("silver", "open"),
            ),
        ),
        knowledge_declared=True,
    )
    return ObjectKnowledgeEngine().build(request, now=NOW)


def test_m392_4_preserves_internal_world_model_authority() -> None:
    report = InternalWorldModelFoundation().objects_representation((_profile(),))
    assert report.canonical_authority == "internal_world_model"
    assert report.source_authority == "object_knowledge"


def test_m392_4_projects_only_available_declared_knowledge() -> None:
    report = InternalWorldModelFoundation().objects_representation((_profile(),))
    assert report.status is ObjectRepresentationStatus.COMPLETE
    assert report.objects[0].label == "laptop"
    assert report.objects[0].object_ref == "laptop-main"


def test_m392_4_keeps_source_evidence_traceability() -> None:
    profile = _profile()
    report = InternalWorldModelFoundation().objects_representation((profile,))
    item = report.objects[0]
    assert item.source_profile_id == profile.profile_id
    assert item.evidence_refs == ("object-evidence-m392-4",)


def test_m392_4_does_not_add_inventory_or_tracking() -> None:
    report = InternalWorldModelFoundation().objects_representation((_profile(),))
    assert report.inventory_added is False
    assert report.object_detection_added is False
    assert report.object_tracking_added is False


def test_m392_4_does_not_infer_location_or_ownership() -> None:
    report = InternalWorldModelFoundation().objects_representation((_profile(),))
    assert report.location_inferred is False
    assert report.ownership_inferred is False
    assert not hasattr(report.objects[0], "location")
    assert not hasattr(report.objects[0], "owner")


def test_m392_4_is_read_only_and_non_persistent() -> None:
    report = InternalWorldModelFoundation().objects_representation((_profile(),))
    assert report.read_only is True
    assert report.persistence_added is False
    assert report.modifies_source_data is False


def test_m392_4_is_deterministic() -> None:
    profile = _profile()
    foundation = InternalWorldModelFoundation()
    first = foundation.objects_representation((profile,))
    second = foundation.objects_representation((profile,))
    assert first == second


def test_m392_4_empty_input_stays_empty() -> None:
    report = InternalWorldModelFoundation().objects_representation()
    assert report.status is ObjectRepresentationStatus.EMPTY
    assert report.objects == ()


def test_m392_4_unavailable_profile_requires_review() -> None:
    profile = replace(
        _profile(),
        status="review_required",
        action="confirm",
        objects=(),
        confidence=0.0,
        object_knowledge_available=False,
        confirmation_required=True,
        profile_id="",
    )
    report = InternalWorldModelFoundation().objects_representation((profile,))
    assert report.status is ObjectRepresentationStatus.REVIEW_REQUIRED
    assert report.objects == ()


def test_m392_4_rejects_duplicate_profile_ids() -> None:
    profile = _profile()
    with pytest.raises(ValueError, match="profile ids must be unique"):
        InternalWorldModelFoundation().objects_representation((profile, profile))


def test_m392_4_report_is_immutable() -> None:
    report = InternalWorldModelFoundation().objects_representation((_profile(),))
    with pytest.raises(FrozenInstanceError):
        report.status = ObjectRepresentationStatus.EMPTY  # type: ignore[misc]


def test_m392_4_preserves_canonical_core_contract_position() -> None:
    path = ROOT / "app" / "official_conversation_gateway.py"
    lines = path.read_text(encoding="utf-8").splitlines()
    hits = [
        index + 1
        for index, line in enumerate(lines)
        if "CanonicalCognitiveCore(" in line
    ]
    assert hits == [52]


def test_m392_4_does_not_reference_private_credentials() -> None:
    source = (ROOT / "core" / "governed_objects_representation.py").read_text(
        encoding="utf-8"
    )
    assert "credentials.json" not in source
    assert ".roby" not in source
