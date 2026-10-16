from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone

import pytest

from core.object_knowledge import (
    InMemoryObjectKnowledgeRepository,
    ObjectEvidence,
    ObjectKind,
    ObjectKnowledgeAction,
    ObjectKnowledgeEngine,
    ObjectKnowledgeItem,
    ObjectKnowledgePolicy,
    ObjectKnowledgeRequest,
    ObjectKnowledgeStatus,
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

NOW = datetime(2026, 7, 12, 2, 0, tzinfo=timezone.utc)


def scene_result(**changes):
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
    values = dict(
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
    )
    values.update(changes)
    return SceneUnderstandingEngine().understand(
        SceneUnderstandingRequest(**values), now=NOW
    )


def evidence(**changes):
    values = dict(
        evidence_ref="obj-e-1",
        observation_ref="obs-001",
        object_ref="obj-1",
        object_kind=ObjectKind.ELECTRONICS,
        label="Laptop",
        confidence=0.92,
        attributes=("open", "silver"),
        count=1,
    )
    values.update(changes)
    return ObjectEvidence(**values)


def request(**changes):
    values = dict(
        owner="Carlos",
        scene_understanding=scene_result(),
        evidence=(evidence(),),
    )
    values.update(changes)
    return ObjectKnowledgeRequest(**values)


def build(*, policy=None, repository=None, **changes):
    return ObjectKnowledgeEngine(policy=policy, repository=repository).build(
        request(**changes), now=NOW
    )


def test_builds_object_knowledge_profile():
    result = build()
    assert result.status is ObjectKnowledgeStatus.AVAILABLE
    assert result.action is ObjectKnowledgeAction.CONSOLIDATE
    assert result.object_knowledge_available
    assert result.objects[0].label == "laptop"


@pytest.mark.parametrize("kind", list(ObjectKind))
def test_supports_each_object_kind(kind):
    result = build(evidence=(evidence(object_kind=kind),))
    assert result.objects[0].object_kind is kind


def test_normalizes_label_and_attributes():
    item = evidence(label="  LAPTOP ", attributes=(" Open ", "OPEN", "Silver"))
    assert item.label == "laptop"
    assert item.attributes == ("open", "silver")


def test_owner_mismatch_is_blocked():
    result = build(owner="Other")
    assert result.status is ObjectKnowledgeStatus.BLOCKED
    assert result.rationale == ("object_knowledge_owner_mismatch",)


def test_undeclared_knowledge_is_not_applicable():
    result = build(knowledge_declared=False)
    assert result.status is ObjectKnowledgeStatus.NOT_APPLICABLE
    assert result.action is ObjectKnowledgeAction.NONE


def test_unavailable_scene_requires_review():
    altered = replace(
        scene_result(),
        status="review_required",
        action="confirm",
        dominant_scene=None,
        accepted_evidence=(),
        attributes=(),
        confidence=0.0,
        scene_understood=False,
        confirmation_required=True,
        rationale=("manual_review",),
        understanding_id="",
    )
    result = build(scene_understanding=altered)
    assert result.status is ObjectKnowledgeStatus.REVIEW_REQUIRED


def test_blocked_scene_blocks_knowledge():
    altered = replace(
        scene_result(),
        status="blocked",
        action="withhold",
        dominant_scene=None,
        accepted_evidence=(),
        attributes=(),
        confidence=0.0,
        scene_understood=False,
        confirmation_required=False,
        rationale=("blocked",),
        understanding_id="",
    )
    result = build(scene_understanding=altered)
    assert result.status is ObjectKnowledgeStatus.BLOCKED


def test_wrong_observation_lineage_is_ignored():
    result = build(evidence=(evidence(observation_ref="other"),))
    assert result.status is ObjectKnowledgeStatus.REVIEW_REQUIRED


def test_low_confidence_is_ignored():
    result = build(evidence=(evidence(confidence=0.69),))
    assert result.status is ObjectKnowledgeStatus.REVIEW_REQUIRED


def test_confidence_threshold_is_inclusive():
    result = build(evidence=(evidence(confidence=0.7),))
    assert result.status is ObjectKnowledgeStatus.AVAILABLE


def test_external_evidence_is_rejected_by_default():
    result = build(evidence=(evidence(externally_supplied=True),))
    assert result.status is ObjectKnowledgeStatus.REVIEW_REQUIRED


def test_policy_can_allow_external_evidence():
    policy = ObjectKnowledgePolicy(allow_external_evidence=True)
    result = build(policy=policy, evidence=(evidence(externally_supplied=True),))
    assert result.status is ObjectKnowledgeStatus.AVAILABLE


def test_evidence_limit_blocks():
    policy = ObjectKnowledgePolicy(maximum_evidence_items=1)
    result = build(
        policy=policy,
        evidence=(evidence(evidence_ref="a"), evidence(evidence_ref="b")),
    )
    assert result.status is ObjectKnowledgeStatus.BLOCKED


def test_object_limit_blocks():
    policy = ObjectKnowledgePolicy(maximum_objects=1)
    result = build(
        policy=policy,
        evidence=(evidence(object_ref="a"), evidence(evidence_ref="b", object_ref="b")),
    )
    assert result.status is ObjectKnowledgeStatus.BLOCKED


def test_long_evidence_reference_is_filtered():
    policy = ObjectKnowledgePolicy(maximum_reference_length=3)
    result = build(policy=policy, evidence=(evidence(evidence_ref="long"),))
    assert result.status is ObjectKnowledgeStatus.REVIEW_REQUIRED


def test_long_object_reference_is_filtered():
    policy = ObjectKnowledgePolicy(maximum_reference_length=3)
    result = build(policy=policy, evidence=(evidence(object_ref="long"),))
    assert result.status is ObjectKnowledgeStatus.REVIEW_REQUIRED


def test_duplicate_evidence_prefers_higher_confidence():
    result = build(
        evidence=(
            evidence(confidence=0.8, label="tablet"),
            evidence(confidence=0.95, label="laptop"),
        )
    )
    assert result.objects[0].label == "laptop"


def test_same_object_evidence_is_consolidated():
    result = build(
        evidence=(
            evidence(evidence_ref="a", attributes=("open",), confidence=0.8),
            evidence(evidence_ref="b", attributes=("silver",), confidence=0.95),
        )
    )
    item = result.objects[0]
    assert item.attributes == ("open", "silver")
    assert item.evidence_refs == ("a", "b")
    assert item.confidence == 0.95


def test_count_uses_maximum_accepted_count():
    result = build(
        evidence=(
            evidence(evidence_ref="a", count=1),
            evidence(evidence_ref="b", count=3),
        )
    )
    assert result.objects[0].count == 3


def test_close_conflict_requires_review():
    result = build(
        evidence=(
            evidence(evidence_ref="a", label="laptop", confidence=0.9),
            evidence(evidence_ref="b", label="tablet", confidence=0.86),
        )
    )
    assert result.status is ObjectKnowledgeStatus.REVIEW_REQUIRED
    assert result.rationale == ("object_evidence_conflict",)


def test_clear_winner_resolves_conflict():
    result = build(
        evidence=(
            evidence(evidence_ref="a", label="laptop", confidence=0.95),
            evidence(evidence_ref="b", label="tablet", confidence=0.8),
        )
    )
    assert result.objects[0].label == "laptop"


def test_policy_controls_ambiguity_margin():
    policy = ObjectKnowledgePolicy(ambiguity_margin=0.01)
    result = build(
        policy=policy,
        evidence=(
            evidence(evidence_ref="a", label="laptop", confidence=0.9),
            evidence(evidence_ref="b", label="tablet", confidence=0.86),
        ),
    )
    assert result.status is ObjectKnowledgeStatus.AVAILABLE


def test_multiple_objects_are_sorted_deterministically():
    result = build(
        evidence=(
            evidence(
                object_ref="b",
                evidence_ref="b",
                object_kind="vehicle",
                label="car",
            ),
            evidence(
                object_ref="a",
                evidence_ref="a",
                object_kind="animal",
                label="dog",
            ),
        )
    )
    assert [item.label for item in result.objects] == ["dog", "car"]


def test_profile_confidence_is_conservative_minimum():
    result = build(
        evidence=(
            evidence(object_ref="a", evidence_ref="a", confidence=0.9),
            evidence(object_ref="b", evidence_ref="b", confidence=0.75),
        )
    )
    assert result.confidence == 0.75


def test_attribute_limit_is_applied():
    policy = ObjectKnowledgePolicy(maximum_attributes_per_object=2)
    result = build(policy=policy, evidence=(evidence(attributes=("c", "a", "b")),))
    assert result.objects[0].attributes == ("a", "b")


def test_profile_is_immutable():
    result = build()
    with pytest.raises(FrozenInstanceError):
        result.confidence = 0.1


def test_nested_item_is_immutable():
    result = build()
    with pytest.raises(FrozenInstanceError):
        result.objects[0].label = "other"


def test_request_evidence_is_tuple():
    req = ObjectKnowledgeRequest(
        owner="Carlos",
        scene_understanding=scene_result(),
        evidence=[evidence()],
    )
    assert isinstance(req.evidence, tuple)


def test_repository_persists_profile():
    repository = InMemoryObjectKnowledgeRepository()
    result = build(repository=repository)
    assert repository.get(result.profile_id) == result
    assert repository.list_all() == (result,)


def test_repository_rejects_duplicate_profile():
    repository = InMemoryObjectKnowledgeRepository()
    result = build(repository=repository)
    with pytest.raises(ValueError, match="already exists"):
        repository.add(result)


def test_same_input_and_timestamp_is_deterministic():
    first = ObjectKnowledgeEngine().build(request(), now=NOW)
    second = ObjectKnowledgeEngine().build(request(), now=NOW)
    assert first.profile_id == second.profile_id


def test_different_timestamp_changes_identifier():
    first = ObjectKnowledgeEngine().build(request(), now=NOW)
    second = ObjectKnowledgeEngine().build(request(), now=NOW.replace(minute=1))
    assert first.profile_id != second.profile_id


def test_naive_timestamp_is_rejected():
    with pytest.raises(ValueError, match="timezone-aware"):
        ObjectKnowledgeEngine().build(request(), now=datetime(2026, 7, 12))


@pytest.mark.parametrize(
    "field",
    [
        "object_detection_allowed",
        "object_tracking_allowed",
        "text_extraction_allowed",
        "product_search_allowed",
        "place_recognition_allowed",
        "biometric_analysis_allowed",
        "pixel_access_allowed",
    ],
)
def test_downstream_capabilities_remain_disabled(field):
    assert getattr(build(), field) is False


def test_profile_rejects_forbidden_capability():
    result = build()
    with pytest.raises(ValueError, match="cannot authorize"):
        replace(result, object_detection_allowed=True, profile_id="")


def test_non_available_profile_cannot_expose_objects():
    result = build()
    with pytest.raises(ValueError, match="inactive"):
        replace(
            result,
            status="review_required",
            action="confirm",
            confirmation_required=True,
            profile_id="",
        )


def test_available_profile_requires_objects():
    result = build()
    with pytest.raises(ValueError, match="requires objects"):
        replace(
            result,
            objects=(),
            object_knowledge_available=False,
            confidence=0.0,
            profile_id="",
        )


def test_evidence_rejects_blank_references():
    with pytest.raises(ValueError, match="must not be blank"):
        evidence(evidence_ref=" ")


def test_evidence_rejects_invalid_confidence():
    with pytest.raises(ValueError, match="between zero and one"):
        evidence(confidence=1.1)


def test_evidence_rejects_non_positive_count():
    with pytest.raises(ValueError, match="positive"):
        evidence(count=0)


def test_policy_rejects_invalid_threshold():
    with pytest.raises(ValueError, match="between zero and one"):
        ObjectKnowledgePolicy(minimum_evidence_confidence=-0.1)


def test_policy_rejects_non_positive_limit():
    with pytest.raises(ValueError, match="positive"):
        ObjectKnowledgePolicy(maximum_objects=0)


def test_item_requires_evidence_refs():
    with pytest.raises(ValueError, match="requires evidence"):
        ObjectKnowledgeItem(
            object_ref="obj",
            object_kind="tool",
            label="hammer",
            attributes=(),
            count=1,
            confidence=0.9,
            evidence_refs=(),
        )


def test_identity_rejects_inconsistent_profile_id():
    result = build()
    with pytest.raises(ValueError, match="inconsistent"):
        replace(result, profile_id="wrong")


def test_empty_evidence_requires_review():
    result = build(evidence=())
    assert result.status is ObjectKnowledgeStatus.REVIEW_REQUIRED
    assert result.confirmation_required


def test_rationale_is_stable():
    assert build().rationale == ("object_knowledge_consolidated",)


def test_engine_exposes_policy_and_repository():
    policy = ObjectKnowledgePolicy()
    repository = InMemoryObjectKnowledgeRepository()
    engine = ObjectKnowledgeEngine(policy=policy, repository=repository)
    assert engine.policy is policy
    assert engine.repository is repository


def test_result_collections_are_tuples():
    result = build()
    assert isinstance(result.objects, tuple)
    assert isinstance(result.rationale, tuple)
    assert isinstance(result.objects[0].attributes, tuple)
    assert isinstance(result.objects[0].evidence_refs, tuple)
