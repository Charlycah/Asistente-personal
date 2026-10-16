from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone

import pytest

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
from core.visual_attention import (
    InMemoryVisualAttentionRepository,
    VisualAttentionAction,
    VisualAttentionEngine,
    VisualAttentionEvidence,
    VisualAttentionItem,
    VisualAttentionPolicy,
    VisualAttentionPriority,
    VisualAttentionRequest,
    VisualAttentionStatus,
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

NOW = datetime(2026, 7, 12, 3, 0, tzinfo=timezone.utc)


def scene_result():
    context = VisualUnderstandingFoundationEngine().establish(
        VisualUnderstandingFoundationRequest(
            owner="Carlos",
            observation=VisualObservationSignal(
                observation_ref="obs-001",
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
            visual_context=context,
            purpose=VisualObservationPurpose.SCENE_CONTEXT,
        ),
        now=NOW,
    )
    return SceneUnderstandingEngine().understand(
        SceneUnderstandingRequest(
            owner="Carlos",
            resolved_observation=resolution,
            evidence=(
                SceneEvidence(
                    evidence_ref="scene-1",
                    observation_ref="obs-001",
                    scene_kind=SceneKind.WORKSPACE,
                    confidence=0.94,
                    attributes=("desk", "indoor"),
                ),
            ),
        ),
        now=NOW,
    )


def object_profile(scene=None):
    scene = scene or scene_result()
    return ObjectKnowledgeEngine().build(
        ObjectKnowledgeRequest(
            owner="Carlos",
            scene_understanding=scene,
            evidence=(
                ObjectEvidence(
                    evidence_ref="obj-e-1",
                    observation_ref="obs-001",
                    object_ref="obj-1",
                    object_kind=ObjectKind.ELECTRONICS,
                    label="Laptop",
                    confidence=0.92,
                    attributes=("open",),
                    count=1,
                ),
                ObjectEvidence(
                    evidence_ref="obj-e-2",
                    observation_ref="obs-001",
                    object_ref="obj-2",
                    object_kind=ObjectKind.DOCUMENT,
                    label="Notebook",
                    confidence=0.9,
                    attributes=("paper",),
                    count=1,
                ),
            ),
        ),
        now=NOW,
    )


def evidence(**changes):
    values = dict(
        evidence_ref="att-e-1",
        observation_ref="obs-001",
        object_ref="obj-1",
        priority=VisualAttentionPriority.HIGH,
        confidence=0.93,
        reason="user focus",
    )
    values.update(changes)
    return VisualAttentionEvidence(**values)


def request(**changes):
    scene = changes.pop("scene_understanding", scene_result())
    objects = changes.pop("object_knowledge", object_profile(scene))
    values = dict(
        owner="Carlos",
        scene_understanding=scene,
        object_knowledge=objects,
        evidence=(evidence(),),
    )
    values.update(changes)
    return VisualAttentionRequest(**values)


def build(*, policy=None, repository=None, **changes):
    return VisualAttentionEngine(policy=policy, repository=repository).prioritize(
        request(**changes), now=NOW
    )


def test_builds_attention_plan():
    result = build()
    assert result.status is VisualAttentionStatus.AVAILABLE
    assert result.action is VisualAttentionAction.PRIORITIZE
    assert result.focus_items[0].object_ref == "obj-1"


@pytest.mark.parametrize("priority", list(VisualAttentionPriority))
def test_supports_each_priority(priority):
    assert (
        build(evidence=(evidence(priority=priority),)).focus_items[0].priority
        is priority
    )


def test_normalizes_reason():
    assert evidence(reason="  USER FOCUS ").reason == "user focus"


def test_owner_mismatch_blocks():
    assert build(owner="Other").status is VisualAttentionStatus.BLOCKED


def test_object_owner_mismatch_blocks():
    objects = replace(
        object_profile(),
        request=replace(object_profile().request, owner="Other"),
        profile_id="",
    )
    assert build(object_knowledge=objects).status is VisualAttentionStatus.BLOCKED


def test_lineage_mismatch_blocks():
    scene_a = scene_result()
    scene_b = replace(scene_a, rationale=("different",), understanding_id="")
    objects = object_profile(scene_a)
    assert (
        build(scene_understanding=scene_b, object_knowledge=objects).status
        is VisualAttentionStatus.BLOCKED
    )


def test_undeclared_attention_not_applicable():
    assert (
        build(attention_declared=False).status is VisualAttentionStatus.NOT_APPLICABLE
    )


def test_unavailable_scene_requires_review():
    scene = replace(
        scene_result(),
        status="review_required",
        action="confirm",
        dominant_scene=None,
        accepted_evidence=(),
        attributes=(),
        confidence=0.0,
        scene_understood=False,
        confirmation_required=True,
        rationale=("review",),
        understanding_id="",
    )
    objects = object_profile(scene_result())
    assert (
        build(scene_understanding=scene, object_knowledge=objects).status
        is VisualAttentionStatus.BLOCKED
    )


def test_unavailable_object_knowledge_requires_review():
    objects = replace(
        object_profile(),
        status="review_required",
        action="confirm",
        objects=(),
        confidence=0.0,
        object_knowledge_available=False,
        confirmation_required=True,
        rationale=("review",),
        profile_id="",
    )
    assert (
        build(object_knowledge=objects).status is VisualAttentionStatus.REVIEW_REQUIRED
    )


def test_wrong_observation_is_ignored():
    assert (
        build(evidence=(evidence(observation_ref="other"),)).status
        is VisualAttentionStatus.REVIEW_REQUIRED
    )


def test_unknown_object_is_ignored():
    assert (
        build(evidence=(evidence(object_ref="missing"),)).status
        is VisualAttentionStatus.REVIEW_REQUIRED
    )


def test_low_confidence_is_ignored():
    assert (
        build(evidence=(evidence(confidence=0.69),)).status
        is VisualAttentionStatus.REVIEW_REQUIRED
    )


def test_threshold_is_inclusive():
    assert (
        build(evidence=(evidence(confidence=0.7),)).status
        is VisualAttentionStatus.AVAILABLE
    )


def test_external_evidence_rejected_by_default():
    assert (
        build(evidence=(evidence(externally_supplied=True),)).status
        is VisualAttentionStatus.REVIEW_REQUIRED
    )


def test_policy_allows_external_evidence():
    assert (
        build(
            policy=VisualAttentionPolicy(allow_external_evidence=True),
            evidence=(evidence(externally_supplied=True),),
        ).status
        is VisualAttentionStatus.AVAILABLE
    )


def test_evidence_limit_blocks():
    result = build(
        policy=VisualAttentionPolicy(maximum_evidence_items=1),
        evidence=(evidence(evidence_ref="a"), evidence(evidence_ref="b")),
    )
    assert result.status is VisualAttentionStatus.BLOCKED


def test_focus_limit_blocks():
    result = build(
        policy=VisualAttentionPolicy(maximum_focus_items=1),
        evidence=(
            evidence(object_ref="obj-1"),
            evidence(evidence_ref="b", object_ref="obj-2"),
        ),
    )
    assert result.status is VisualAttentionStatus.BLOCKED


def test_long_reference_is_filtered():
    assert (
        build(
            policy=VisualAttentionPolicy(maximum_reference_length=3),
            evidence=(evidence(evidence_ref="long"),),
        ).status
        is VisualAttentionStatus.REVIEW_REQUIRED
    )


def test_duplicate_evidence_prefers_higher_confidence():
    result = build(
        evidence=(
            evidence(priority="low", confidence=0.8),
            evidence(priority="critical", confidence=0.95),
        )
    )
    assert result.focus_items[0].priority is VisualAttentionPriority.CRITICAL


def test_same_object_reasons_are_consolidated():
    result = build(
        evidence=(
            evidence(evidence_ref="a", reason="user focus"),
            evidence(evidence_ref="b", reason="task relevance", confidence=0.9),
        )
    )
    assert result.focus_items[0].reasons == ("task relevance", "user focus")


def test_conflicting_close_priorities_require_review():
    result = build(
        evidence=(
            evidence(evidence_ref="a", priority="high", confidence=0.9),
            evidence(evidence_ref="b", priority="critical", confidence=0.88),
        )
    )
    assert result.status is VisualAttentionStatus.REVIEW_REQUIRED


def test_clear_priority_difference_is_accepted():
    result = build(
        evidence=(
            evidence(evidence_ref="a", priority="high", confidence=0.95),
            evidence(evidence_ref="b", priority="critical", confidence=0.8),
        )
    )
    assert result.focus_items[0].priority is VisualAttentionPriority.HIGH


def test_items_are_sorted_by_priority_then_confidence():
    result = build(
        evidence=(
            evidence(
                evidence_ref="a", object_ref="obj-1", priority="normal", confidence=0.99
            ),
            evidence(
                evidence_ref="b",
                object_ref="obj-2",
                priority="critical",
                confidence=0.8,
            ),
        )
    )
    assert [item.object_ref for item in result.focus_items] == ["obj-2", "obj-1"]


def test_plan_confidence_is_minimum_focus_confidence():
    result = build(
        evidence=(
            evidence(evidence_ref="a", object_ref="obj-1", confidence=0.9),
            evidence(evidence_ref="b", object_ref="obj-2", confidence=0.8),
        )
    )
    assert result.confidence == 0.8


def test_reason_limit_applies():
    policy = VisualAttentionPolicy(maximum_reasons_per_item=1)
    result = build(
        policy=policy,
        evidence=(
            evidence(evidence_ref="a", reason="a"),
            evidence(evidence_ref="b", reason="b", confidence=0.91),
        ),
    )
    assert len(result.focus_items[0].reasons) == 1


def test_deterministic_identifier():
    first = build()
    second = VisualAttentionEngine().prioritize(request(), now=NOW)
    assert first.plan_id == second.plan_id


def test_different_timestamp_changes_identifier():
    first = build()
    second = VisualAttentionEngine().prioritize(request(), now=NOW.replace(minute=1))
    assert first.plan_id != second.plan_id


def test_plan_is_frozen():
    with pytest.raises(FrozenInstanceError):
        build().confidence = 0.1


def test_request_is_frozen():
    with pytest.raises(FrozenInstanceError):
        request().owner = "Other"


def test_repository_persists_plan():
    repo = InMemoryVisualAttentionRepository()
    result = build(repository=repo)
    assert repo.get(result.plan_id) == result
    assert repo.list_all() == (result,)


def test_repository_rejects_duplicate_plan():
    repo = InMemoryVisualAttentionRepository()
    result = build(repository=repo)
    with pytest.raises(ValueError):
        repo.add(result)


def test_naive_timestamp_rejected():
    with pytest.raises(ValueError):
        VisualAttentionEngine().prioritize(request(), now=datetime(2026, 7, 12))


@pytest.mark.parametrize(
    "field",
    [
        "gaze_control_allowed",
        "image_cropping_allowed",
        "pixel_access_allowed",
        "object_detection_allowed",
        "object_tracking_allowed",
        "text_extraction_allowed",
        "product_search_allowed",
        "place_recognition_allowed",
        "biometric_analysis_allowed",
    ],
)
def test_downstream_capabilities_are_disabled(field):
    assert getattr(build(), field) is False


def test_plan_rejects_forbidden_capability():
    base = build()
    with pytest.raises(ValueError):
        replace(base, gaze_control_allowed=True, plan_id="")


@pytest.mark.parametrize("value", [-0.1, 1.1])
def test_evidence_confidence_validation(value):
    with pytest.raises(ValueError):
        evidence(confidence=value)


@pytest.mark.parametrize("value", [0, -1])
def test_policy_limits_must_be_positive(value):
    with pytest.raises(ValueError):
        VisualAttentionPolicy(maximum_focus_items=value)


def test_blank_evidence_fields_rejected():
    with pytest.raises(ValueError):
        evidence(reason=" ")


def test_blank_owner_rejected():
    with pytest.raises(ValueError):
        request(owner=" ")


def test_item_requires_reasons():
    with pytest.raises(ValueError):
        VisualAttentionItem(
            object_ref="obj",
            priority="high",
            confidence=0.9,
            reasons=(),
            evidence_refs=("e",),
        )


def test_inactive_plan_cannot_expose_focus_items():
    base = build()
    with pytest.raises(ValueError):
        replace(
            base,
            status="blocked",
            action="withhold",
            attention_available=False,
            confidence=0.0,
            rationale=("blocked",),
            plan_id="",
        )


def test_identifier_rejects_tampering():
    with pytest.raises(ValueError):
        replace(build(), plan_id="invalid")
