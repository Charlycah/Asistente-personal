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
    VisualAttentionEngine,
    VisualAttentionEvidence,
    VisualAttentionPriority,
    VisualAttentionRequest,
)
from core.visual_context_integration import (
    InMemoryVisualContextIntegrationRepository,
    IntegratedVisualContext,
    VisualContextIntegrationEngine,
    VisualContextIntegrationPolicy,
    VisualContextIntegrationRepository,
    VisualContextIntegrationRequest,
    VisualIntegrationAction,
    VisualIntegrationStatus,
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

NOW = datetime(2026, 7, 12, 5, 0, tzinfo=timezone.utc)


def chain():
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
    scene = SceneUnderstandingEngine().understand(
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
    objects = ObjectKnowledgeEngine().build(
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
                ),
            ),
        ),
        now=NOW,
    )
    attention = VisualAttentionEngine().prioritize(
        VisualAttentionRequest(
            owner="Carlos",
            scene_understanding=scene,
            object_knowledge=objects,
            evidence=(
                VisualAttentionEvidence(
                    evidence_ref="att-1",
                    observation_ref="obs-001",
                    object_ref="obj-1",
                    priority=VisualAttentionPriority.HIGH,
                    confidence=0.93,
                    reason="user focus",
                ),
            ),
        ),
        now=NOW,
    )
    return context, resolution, scene, objects, attention


def request(**changes):
    context, resolution, scene, objects, attention = chain()
    values = dict(
        owner="Carlos",
        visual_context=context,
        resolved_observation=resolution,
        scene_understanding=scene,
        object_knowledge=objects,
        attention_plan=attention,
    )
    values.update(changes)
    return VisualContextIntegrationRequest(**values)


def integrate(*, policy=None, repository=None, **changes):
    return VisualContextIntegrationEngine(
        policy=policy, repository=repository
    ).integrate(request(**changes), now=NOW)


def test_integrates_complete_visual_context():
    result = integrate()
    assert result.status is VisualIntegrationStatus.READY
    assert result.action is VisualIntegrationAction.INTEGRATE
    assert result.attention_available


def test_exposes_all_lineage_ids():
    result = integrate()
    assert all(
        (
            result.visual_context_id,
            result.resolution_id,
            result.scene_understanding_id,
            result.object_knowledge_id,
            result.attention_plan_id,
        )
    )


def test_exposes_all_governed_capabilities():
    result = integrate()
    assert result.observation_context_available
    assert result.resolution_available
    assert result.scene_understanding_available
    assert result.object_knowledge_available
    assert result.attention_available


@pytest.mark.parametrize(
    "field",
    [
        "pixel_access_allowed",
        "camera_control_allowed",
        "object_detection_allowed",
        "object_tracking_allowed",
        "text_extraction_allowed",
        "product_search_allowed",
        "place_recognition_allowed",
        "biometric_analysis_allowed",
    ],
)
def test_never_authorizes_perception_or_actuation(field):
    assert getattr(integrate(), field) is False


def test_not_requested_is_not_applicable():
    result = integrate(integration_requested=False)
    assert result.status is VisualIntegrationStatus.NOT_APPLICABLE
    assert result.action is VisualIntegrationAction.NONE


def test_owner_mismatch_blocks():
    assert integrate(owner="Other").status is VisualIntegrationStatus.BLOCKED


def test_non_ready_foundation_blocks():
    context, resolution, scene, objects, attention = chain()
    context = replace(
        context,
        status="review_required",
        action="confirm",
        observation_available=False,
        observation_resolution_required=False,
        external_provider_required=False,
        rationale=("review",),
        context_id="",
    )
    result = integrate(
        visual_context=context,
        resolved_observation=resolution,
        scene_understanding=scene,
        object_knowledge=objects,
        attention_plan=attention,
    )
    assert result.status is VisualIntegrationStatus.BLOCKED


def test_policy_can_accept_non_ready_foundation_as_partial():
    context, _, _, _, _ = chain()
    context = replace(
        context,
        status="review_required",
        action="confirm",
        observation_available=False,
        observation_resolution_required=False,
        external_provider_required=False,
        rationale=("review",),
        context_id="",
    )
    result = integrate(
        policy=VisualContextIntegrationPolicy(require_ready_foundation=False),
        visual_context=context,
        resolved_observation=None,
        scene_understanding=None,
        object_knowledge=None,
        attention_plan=None,
    )
    assert result.status is VisualIntegrationStatus.PARTIAL


def test_resolution_lineage_mismatch_blocks():
    context, resolution, scene, objects, attention = chain()
    other = replace(
        resolution, request=replace(resolution.request, owner="Other"), resolution_id=""
    )
    assert (
        integrate(
            visual_context=context,
            resolved_observation=other,
            scene_understanding=scene,
            object_knowledge=objects,
            attention_plan=attention,
        ).status
        is VisualIntegrationStatus.BLOCKED
    )


def test_scene_without_resolution_blocks():
    _, _, scene, objects, attention = chain()
    assert (
        integrate(
            resolved_observation=None,
            scene_understanding=scene,
            object_knowledge=objects,
            attention_plan=attention,
        ).status
        is VisualIntegrationStatus.BLOCKED
    )


def test_scene_lineage_mismatch_blocks():
    context, resolution, scene, objects, attention = chain()
    other_scene = replace(scene, rationale=("other",), understanding_id="")
    assert (
        integrate(
            visual_context=context,
            resolved_observation=resolution,
            scene_understanding=other_scene,
            object_knowledge=objects,
            attention_plan=attention,
        ).status
        is VisualIntegrationStatus.BLOCKED
    )


def test_objects_without_scene_blocks():
    _, resolution, _, objects, attention = chain()
    assert (
        integrate(
            resolved_observation=resolution,
            scene_understanding=None,
            object_knowledge=objects,
            attention_plan=attention,
        ).status
        is VisualIntegrationStatus.BLOCKED
    )


def test_object_lineage_mismatch_blocks():
    context, resolution, scene, objects, attention = chain()
    other_objects = replace(
        objects, request=replace(objects.request, owner="Other"), profile_id=""
    )
    assert (
        integrate(
            visual_context=context,
            resolved_observation=resolution,
            scene_understanding=scene,
            object_knowledge=other_objects,
            attention_plan=attention,
        ).status
        is VisualIntegrationStatus.BLOCKED
    )


def test_attention_without_objects_blocks():
    _, resolution, scene, _, attention = chain()
    assert (
        integrate(
            resolved_observation=resolution,
            scene_understanding=scene,
            object_knowledge=None,
            attention_plan=attention,
        ).status
        is VisualIntegrationStatus.BLOCKED
    )


def test_attention_lineage_mismatch_blocks():
    context, resolution, scene, objects, attention = chain()
    other_attention = replace(
        attention, request=replace(attention.request, owner="Other"), plan_id=""
    )
    assert (
        integrate(
            visual_context=context,
            resolved_observation=resolution,
            scene_understanding=scene,
            object_knowledge=objects,
            attention_plan=other_attention,
        ).status
        is VisualIntegrationStatus.BLOCKED
    )


@pytest.mark.parametrize(
    "component",
    ["resolution", "scene", "objects", "attention"],
)
def test_upstream_review_requires_confirmation(component):
    context, resolution, scene, objects, attention = chain()
    if component == "resolution":
        resolution = replace(
            resolution,
            status="review_required",
            action="confirm",
            selected_candidate=None,
            observation_resolved=False,
            rationale=("review",),
            resolution_id="",
        )
        scene = None
        objects = None
        attention = None
    elif component == "scene":
        scene = replace(
            scene,
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
        objects = None
        attention = None
    elif component == "objects":
        objects = replace(
            objects,
            status="review_required",
            action="confirm",
            objects=(),
            confidence=0.0,
            object_knowledge_available=False,
            confirmation_required=True,
            rationale=("review",),
            profile_id="",
        )
        attention = None
    else:
        attention = replace(
            attention,
            status="review_required",
            action="confirm",
            focus_items=(),
            confidence=0.0,
            attention_available=False,
            confirmation_required=True,
            rationale=("review",),
            plan_id="",
        )
    result = integrate(
        visual_context=context,
        resolved_observation=resolution,
        scene_understanding=scene,
        object_knowledge=objects,
        attention_plan=attention,
    )
    assert result.status is VisualIntegrationStatus.REVIEW_REQUIRED
    assert result.confirmation_required


def test_missing_attention_is_partial_by_default():
    assert integrate(attention_plan=None).status is VisualIntegrationStatus.PARTIAL


def test_missing_attention_can_be_allowed():
    result = integrate(
        policy=VisualContextIntegrationPolicy(require_attention_lineage=False),
        attention_plan=None,
    )
    assert result.status is VisualIntegrationStatus.PARTIAL


def test_partial_can_be_blocked_by_policy():
    result = integrate(
        policy=VisualContextIntegrationPolicy(allow_partial_context=False),
        attention_plan=None,
    )
    assert result.status is VisualIntegrationStatus.BLOCKED


@pytest.mark.parametrize(
    ("missing", "expected_capability"),
    [
        ("resolution", "observation_context_available"),
        ("scene", "resolution_available"),
        ("objects", "scene_understanding_available"),
        ("attention", "object_knowledge_available"),
    ],
)
def test_partial_context_retains_available_upstream_capabilities(
    missing, expected_capability
):
    context, resolution, scene, objects, attention = chain()
    if missing == "resolution":
        resolution = scene = objects = attention = None
    elif missing == "scene":
        scene = objects = attention = None
    elif missing == "objects":
        objects = attention = None
    else:
        attention = None
    result = integrate(
        visual_context=context,
        resolved_observation=resolution,
        scene_understanding=scene,
        object_knowledge=objects,
        attention_plan=attention,
    )
    assert result.status is VisualIntegrationStatus.PARTIAL
    assert getattr(result, expected_capability)


def test_partial_action_is_retain_partial():
    assert (
        integrate(attention_plan=None).action is VisualIntegrationAction.RETAIN_PARTIAL
    )


def test_ready_does_not_require_confirmation():
    assert integrate().confirmation_required is False


def test_result_is_immutable():
    with pytest.raises(FrozenInstanceError):
        integrate().status = VisualIntegrationStatus.BLOCKED


def test_request_is_immutable():
    with pytest.raises(FrozenInstanceError):
        request().owner = "Other"


def test_policy_is_immutable():
    with pytest.raises(FrozenInstanceError):
        VisualContextIntegrationPolicy().allow_partial_context = False


def test_owner_is_trimmed():
    assert request(owner="  Carlos  ").owner == "Carlos"


def test_blank_owner_rejected():
    with pytest.raises(ValueError):
        request(owner="   ")


def test_naive_timestamp_rejected():
    with pytest.raises(ValueError):
        VisualContextIntegrationEngine().integrate(request(), now=datetime(2026, 1, 1))


def test_deterministic_with_same_timestamp():
    first = VisualContextIntegrationEngine().integrate(request(), now=NOW)
    second = VisualContextIntegrationEngine().integrate(request(), now=NOW)
    assert first.integration_id == second.integration_id


def test_different_timestamp_changes_identity():
    later = datetime(2026, 7, 12, 5, 1, tzinfo=timezone.utc)
    first = VisualContextIntegrationEngine().integrate(request(), now=NOW)
    second = VisualContextIntegrationEngine().integrate(request(), now=later)
    assert first.integration_id != second.integration_id


def test_repository_stores_result():
    repository = InMemoryVisualContextIntegrationRepository()
    result = integrate(repository=repository)
    assert repository.get(result.integration_id) == result


def test_repository_lists_results():
    repository = InMemoryVisualContextIntegrationRepository()
    result = integrate(repository=repository)
    assert repository.list_all() == (result,)


def test_repository_protocol_runtime_checkable():
    assert isinstance(
        InMemoryVisualContextIntegrationRepository(), VisualContextIntegrationRepository
    )


def test_repository_rejects_duplicate():
    repository = InMemoryVisualContextIntegrationRepository()
    result = integrate(repository=repository)
    with pytest.raises(ValueError):
        repository.add(result)


def test_inconsistent_integration_id_rejected():
    result = integrate()
    with pytest.raises(ValueError):
        replace(result, integration_id="wrong")


@pytest.mark.parametrize(
    "field",
    [
        "pixel_access_allowed",
        "camera_control_allowed",
        "object_detection_allowed",
        "object_tracking_allowed",
        "text_extraction_allowed",
        "product_search_allowed",
        "place_recognition_allowed",
        "biometric_analysis_allowed",
    ],
)
def test_forbidden_capability_cannot_be_enabled(field):
    result = integrate()
    with pytest.raises(ValueError):
        replace(result, **{field: True}, integration_id="")


def test_review_requires_confirmation_invariant():
    result = integrate()
    with pytest.raises(ValueError):
        replace(
            result,
            status="review_required",
            confirmation_required=False,
            integration_id="",
        )


def test_inactive_cannot_expose_lineage():
    result = integrate(integration_requested=False)
    with pytest.raises(ValueError):
        replace(result, visual_context_id="ctx", integration_id="")


def test_rationale_is_tuple():
    assert isinstance(integrate().rationale, tuple)


def test_ready_rationale_is_stable():
    assert integrate().rationale == ("visual_context_integration_ready",)


def test_module_does_not_expose_pixel_or_provider_operations():
    import core.visual_context_integration as module

    forbidden = {
        "read_pixels",
        "open_camera",
        "detect_objects",
        "extract_text",
        "call_provider",
    }
    assert forbidden.isdisjoint(set(dir(module)))


def test_result_type_can_be_constructed_only_with_consistent_state():
    assert isinstance(integrate(), IntegratedVisualContext)
