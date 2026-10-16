from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone

import pytest

from core.scene_understanding import (
    InMemorySceneUnderstandingRepository,
    SceneEvidence,
    SceneKind,
    SceneUnderstandingAction,
    SceneUnderstandingEngine,
    SceneUnderstandingPolicy,
    SceneUnderstandingRequest,
    SceneUnderstandingResult,
    SceneUnderstandingStatus,
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

NOW = datetime(2026, 7, 12, 1, 0, tzinfo=timezone.utc)


def resolved_observation(*, purpose=VisualObservationPurpose.SCENE_CONTEXT, **changes):
    foundation_values = dict(
        owner="Carlos",
        observation=VisualObservationSignal(
            observation_ref="obs-001",
            source=VisualObservationSource.MOBILE_CAMERA,
            media_type=VisualMediaType.PHOTO,
            privacy_level=VisualPrivacyLevel.PERSONAL,
            confidence=0.95,
            observed_at=NOW,
            source_device_id="phone-main",
        ),
        explicit_user_consent=True,
    )
    foundation_values.update(changes.pop("foundation", {}))
    context = VisualUnderstandingFoundationEngine().establish(
        VisualUnderstandingFoundationRequest(**foundation_values), now=NOW
    )
    resolution_values = dict(
        owner="Carlos",
        visual_context=context,
        purpose=purpose,
    )
    resolution_values.update(changes)
    return VisualObservationResolutionEngine().resolve(
        VisualObservationResolutionRequest(**resolution_values), now=NOW
    )


def evidence(**changes):
    values = dict(
        evidence_ref="scene-001",
        observation_ref="obs-001",
        scene_kind=SceneKind.OUTDOOR,
        confidence=0.92,
        attributes=("daylight", "open space"),
    )
    values.update(changes)
    return SceneEvidence(**values)


def request(**changes):
    values = dict(
        owner="Carlos",
        resolved_observation=resolved_observation(),
        evidence=(evidence(),),
    )
    values.update(changes)
    return SceneUnderstandingRequest(**values)


def understand(*, policy=None, **changes):
    return SceneUnderstandingEngine(policy=policy).understand(
        request(**changes), now=NOW
    )


def test_understands_declared_scene():
    result = understand()
    assert result.status is SceneUnderstandingStatus.UNDERSTOOD
    assert result.action is SceneUnderstandingAction.CONSOLIDATE
    assert result.dominant_scene is SceneKind.OUTDOOR
    assert result.scene_understood


def test_preserves_normalized_attributes():
    result = understand()
    assert result.attributes == ("daylight", "open space")


@pytest.mark.parametrize("kind", list(SceneKind))
def test_supports_each_scene_kind(kind):
    result = understand(evidence=(evidence(scene_kind=kind),))
    assert result.dominant_scene is kind


def test_owner_mismatch_is_blocked():
    result = understand(owner="Other")
    assert result.status is SceneUnderstandingStatus.BLOCKED
    assert result.rationale == ("scene_understanding_owner_mismatch",)


def test_undeclared_understanding_is_not_applicable():
    result = understand(understanding_declared=False)
    assert result.status is SceneUnderstandingStatus.NOT_APPLICABLE
    assert result.action is SceneUnderstandingAction.NONE


def test_non_scene_purpose_is_not_applicable():
    result = understand(
        resolved_observation=resolved_observation(
            purpose=VisualObservationPurpose.OBJECT_CONTEXT
        )
    )
    assert result.status is SceneUnderstandingStatus.NOT_APPLICABLE
    assert result.rationale == ("scene_understanding_not_required",)


def test_unresolved_observation_requires_review():
    resolution = resolved_observation(candidates=())
    altered = replace(
        resolution,
        status="review_required",
        action="confirm",
        selected_candidate=None,
        observation_resolved=False,
        scene_understanding_required=False,
        rationale=("manual_review",),
        resolution_id="",
    )
    result = understand(resolved_observation=altered)
    assert result.status is SceneUnderstandingStatus.REVIEW_REQUIRED


def test_wrong_observation_lineage_is_ignored():
    result = understand(evidence=(evidence(observation_ref="other"),))
    assert result.status is SceneUnderstandingStatus.REVIEW_REQUIRED


def test_low_confidence_evidence_is_ignored():
    result = understand(evidence=(evidence(confidence=0.69),))
    assert result.status is SceneUnderstandingStatus.REVIEW_REQUIRED


def test_confidence_threshold_is_inclusive():
    result = understand(evidence=(evidence(confidence=0.7),))
    assert result.status is SceneUnderstandingStatus.UNDERSTOOD


def test_external_evidence_is_rejected_by_default():
    result = understand(evidence=(evidence(externally_supplied=True),))
    assert result.status is SceneUnderstandingStatus.REVIEW_REQUIRED


def test_policy_can_allow_external_evidence():
    policy = SceneUnderstandingPolicy(allow_external_evidence=True)
    result = understand(policy=policy, evidence=(evidence(externally_supplied=True),))
    assert result.status is SceneUnderstandingStatus.UNDERSTOOD


def test_evidence_limit_is_blocked():
    policy = SceneUnderstandingPolicy(maximum_evidence_items=1)
    result = understand(
        policy=policy,
        evidence=(evidence(evidence_ref="a"), evidence(evidence_ref="b")),
    )
    assert result.status is SceneUnderstandingStatus.BLOCKED


def test_long_reference_is_filtered():
    policy = SceneUnderstandingPolicy(maximum_reference_length=3)
    result = understand(policy=policy, evidence=(evidence(evidence_ref="long"),))
    assert result.status is SceneUnderstandingStatus.REVIEW_REQUIRED


def test_highest_confidence_scene_wins():
    result = understand(
        evidence=(
            evidence(
                evidence_ref="indoor",
                scene_kind=SceneKind.INDOOR,
                confidence=0.8,
            ),
            evidence(
                evidence_ref="outdoor",
                scene_kind=SceneKind.OUTDOOR,
                confidence=0.95,
            ),
        )
    )
    assert result.dominant_scene is SceneKind.OUTDOOR


def test_close_competing_scenes_require_review():
    result = understand(
        evidence=(
            evidence(evidence_ref="a", scene_kind=SceneKind.INDOOR, confidence=0.9),
            evidence(evidence_ref="b", scene_kind=SceneKind.OUTDOOR, confidence=0.86),
        )
    )
    assert result.status is SceneUnderstandingStatus.REVIEW_REQUIRED
    assert result.rationale == ("scene_evidence_conflict",)


def test_policy_controls_ambiguity_margin():
    policy = SceneUnderstandingPolicy(ambiguity_margin=0.01)
    result = understand(
        policy=policy,
        evidence=(
            evidence(evidence_ref="a", scene_kind=SceneKind.INDOOR, confidence=0.9),
            evidence(evidence_ref="b", scene_kind=SceneKind.OUTDOOR, confidence=0.86),
        ),
    )
    assert result.status is SceneUnderstandingStatus.UNDERSTOOD


def test_same_scene_evidence_is_consolidated():
    result = understand(
        evidence=(
            evidence(evidence_ref="a", attributes=("daylight",)),
            evidence(evidence_ref="b", confidence=0.85, attributes=("crowded",)),
        )
    )
    assert len(result.accepted_evidence) == 2
    assert result.attributes == ("crowded", "daylight")


def test_duplicate_reference_keeps_highest_confidence_deterministically():
    low = evidence(evidence_ref="same", confidence=0.8, scene_kind=SceneKind.INDOOR)
    high = evidence(evidence_ref="same", confidence=0.95, scene_kind=SceneKind.OUTDOOR)
    result = understand(evidence=(low, high))
    assert result.dominant_scene is SceneKind.OUTDOOR
    assert result.accepted_evidence == (high,)


def test_attribute_limit_is_enforced():
    policy = SceneUnderstandingPolicy(maximum_attributes=2)
    result = understand(
        policy=policy,
        evidence=(evidence(attributes=("c", "a", "b")),),
    )
    assert result.attributes == ("a", "b")


def test_attributes_are_casefolded_and_deduplicated():
    item = evidence(attributes=("Bright", "bright", "Open"))
    assert item.attributes == ("bright", "open")


def test_result_confidence_is_winner_confidence():
    result = understand(evidence=(evidence(confidence=0.88),))
    assert result.confidence == 0.88


@pytest.mark.parametrize(
    "field",
    [
        "object_recognition_allowed",
        "text_extraction_allowed",
        "place_recognition_allowed",
        "biometric_analysis_allowed",
        "pixel_access_allowed",
    ],
)
def test_never_authorizes_downstream_visual_capabilities(field):
    assert not getattr(understand(), field)


def test_result_is_immutable():
    result = understand()
    with pytest.raises(FrozenInstanceError):
        result.confidence = 0.1


def test_evidence_is_immutable():
    item = evidence()
    with pytest.raises(FrozenInstanceError):
        item.confidence = 0.1


def test_request_is_immutable():
    item = request()
    with pytest.raises(FrozenInstanceError):
        item.owner = "Other"


def test_same_input_and_timestamp_produce_same_id():
    item = request()
    first = SceneUnderstandingEngine().understand(item, now=NOW)
    second = SceneUnderstandingEngine().understand(item, now=NOW)
    assert first.understanding_id == second.understanding_id


def test_input_order_does_not_change_id():
    a = evidence(evidence_ref="a", confidence=0.95)
    b = evidence(evidence_ref="b", confidence=0.8)
    first = SceneUnderstandingEngine().understand(request(evidence=(a, b)), now=NOW)
    second = SceneUnderstandingEngine().understand(request(evidence=(b, a)), now=NOW)
    assert first.understanding_id == second.understanding_id


def test_repository_persists_result():
    repository = InMemorySceneUnderstandingRepository()
    engine = SceneUnderstandingEngine(repository=repository)
    result = engine.understand(request(), now=NOW)
    assert repository.get(result.understanding_id) == result
    assert repository.list_all() == (result,)


def test_repository_rejects_duplicate_id():
    repository = InMemorySceneUnderstandingRepository()
    engine = SceneUnderstandingEngine(repository=repository)
    item = request()
    engine.understand(item, now=NOW)
    with pytest.raises(ValueError, match="already exists"):
        engine.understand(item, now=NOW)


def test_naive_timestamp_is_rejected():
    with pytest.raises(ValueError, match="timezone-aware"):
        SceneUnderstandingEngine().understand(
            request(), now=datetime(2026, 7, 12, 1, 0)
        )


@pytest.mark.parametrize(
    "kwargs",
    [
        {"minimum_evidence_confidence": -0.1},
        {"minimum_evidence_confidence": 1.1},
        {"ambiguity_margin": -0.1},
        {"ambiguity_margin": 1.1},
        {"maximum_evidence_items": 0},
        {"maximum_reference_length": 0},
        {"maximum_attributes": 0},
    ],
)
def test_invalid_policy_is_rejected(kwargs):
    with pytest.raises(ValueError):
        SceneUnderstandingPolicy(**kwargs)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"evidence_ref": " "},
        {"observation_ref": " "},
        {"confidence": -0.1},
        {"confidence": 1.1},
        {"attributes": ("",)},
        {"scene_kind": "invalid"},
    ],
)
def test_invalid_evidence_is_rejected(kwargs):
    with pytest.raises(ValueError):
        evidence(**kwargs)


def test_blank_owner_is_rejected():
    with pytest.raises(ValueError, match="owner"):
        request(owner=" ")


def test_non_understood_result_cannot_expose_scene():
    base = understand()
    with pytest.raises(ValueError):
        SceneUnderstandingResult(
            request=base.request,
            status=SceneUnderstandingStatus.REVIEW_REQUIRED,
            action=SceneUnderstandingAction.CONFIRM,
            dominant_scene=SceneKind.OUTDOOR,
            accepted_evidence=(),
            attributes=(),
            confidence=0,
            scene_understood=False,
            confirmation_required=True,
            object_recognition_allowed=False,
            text_extraction_allowed=False,
            place_recognition_allowed=False,
            biometric_analysis_allowed=False,
            pixel_access_allowed=False,
            rationale=("review",),
            created_at=NOW,
        )


def test_cannot_forge_pixel_access_authorization():
    base = understand()
    with pytest.raises(ValueError, match="cannot authorize"):
        replace(base, pixel_access_allowed=True, understanding_id="")


def test_public_exports_are_available():
    from core.scene_understanding import SceneUnderstandingEngine as Exported

    assert Exported is SceneUnderstandingEngine
