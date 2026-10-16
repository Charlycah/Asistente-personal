from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone

import pytest

from core.visual_observation_resolution import (
    InMemoryVisualObservationResolutionRepository,
    VisualObservationCandidate,
    VisualObservationPurpose,
    VisualObservationResolutionEngine,
    VisualObservationResolutionPolicy,
    VisualObservationResolutionRequest,
    VisualRepresentationKind,
    VisualResolutionAction,
    VisualResolutionStatus,
)
from core.visual_understanding_foundation import (
    VisualMediaType,
    VisualObservationSignal,
    VisualObservationSource,
    VisualPrivacyLevel,
    VisualUnderstandingFoundationEngine,
    VisualUnderstandingFoundationRequest,
)

NOW = datetime(2026, 7, 11, 23, 0, tzinfo=timezone.utc)


def visual_context(**changes):
    values = dict(
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
    values.update(changes)
    return VisualUnderstandingFoundationEngine().establish(
        VisualUnderstandingFoundationRequest(**values), now=NOW
    )


def candidate(**changes):
    values = dict(
        candidate_ref="candidate-original",
        observation_ref="obs-001",
        representation_kind=VisualRepresentationKind.ORIGINAL,
        confidence=0.95,
        declared_purposes=(VisualObservationPurpose.GENERAL_CONTEXT,),
    )
    values.update(changes)
    return VisualObservationCandidate(**values)


def request(**changes):
    values = dict(owner="Carlos", visual_context=visual_context())
    values.update(changes)
    return VisualObservationResolutionRequest(**values)


def resolve(*, policy=None, **changes):
    return VisualObservationResolutionEngine(policy=policy).resolve(
        request(**changes), now=NOW
    )


def test_default_resolution_uses_original_observation():
    result = resolve()
    assert result.status is VisualResolutionStatus.RESOLVED
    assert result.action is VisualResolutionAction.SELECT
    assert result.selected_candidate is not None
    assert (
        result.selected_candidate.representation_kind
        is VisualRepresentationKind.ORIGINAL
    )


def test_default_resolution_requires_scene_understanding_for_general_context():
    result = resolve()
    assert result.scene_understanding_required
    assert not result.object_understanding_required


@pytest.mark.parametrize(
    ("purpose", "field"),
    [
        (VisualObservationPurpose.SCENE_CONTEXT, "scene_understanding_required"),
        (VisualObservationPurpose.OBJECT_CONTEXT, "object_understanding_required"),
        (VisualObservationPurpose.TEXT_CONTEXT, "text_understanding_required"),
        (VisualObservationPurpose.PRODUCT_CONTEXT, "product_understanding_required"),
        (VisualObservationPurpose.PLACE_CONTEXT, "place_understanding_required"),
    ],
)
def test_each_specialized_purpose_sets_only_its_requirement(purpose, field):
    item = candidate(declared_purposes=(purpose,))
    result = resolve(purpose=purpose, candidates=(item,))
    assert getattr(result, field)


def test_never_authorizes_pixel_access():
    assert not resolve().pixel_access_allowed


def test_never_authorizes_biometrics():
    assert not resolve().biometric_analysis_allowed


def test_owner_mismatch_is_blocked():
    result = resolve(owner="Other")
    assert result.status is VisualResolutionStatus.BLOCKED
    assert result.rationale == ("visual_resolution_owner_mismatch",)


def test_resolution_not_declared_is_not_applicable():
    result = resolve(resolution_declared=False)
    assert result.status is VisualResolutionStatus.NOT_APPLICABLE
    assert result.action is VisualResolutionAction.NONE


def test_non_ready_context_requires_review():
    context = visual_context(explicit_user_consent=False)
    result = resolve(visual_context=context)
    assert result.status is VisualResolutionStatus.REVIEW_REQUIRED


def test_blocked_context_is_blocked():
    observation = VisualObservationSignal(
        "obs-001",
        VisualObservationSource.MOBILE_CAMERA,
        VisualMediaType.PHOTO,
        VisualPrivacyLevel.RESTRICTED,
        0.95,
        NOW,
    )
    context = visual_context(observation=observation)
    result = resolve(visual_context=context)
    assert result.status is VisualResolutionStatus.BLOCKED


def test_candidate_with_wrong_observation_lineage_is_ignored():
    result = resolve(candidates=(candidate(observation_ref="other"),))
    assert result.status is VisualResolutionStatus.REVIEW_REQUIRED


def test_low_confidence_candidate_is_ignored():
    result = resolve(candidates=(candidate(confidence=0.69),))
    assert result.status is VisualResolutionStatus.REVIEW_REQUIRED


def test_confidence_threshold_is_inclusive():
    result = resolve(candidates=(candidate(confidence=0.7),))
    assert result.status is VisualResolutionStatus.RESOLVED


def test_external_candidate_is_rejected_by_default():
    result = resolve(candidates=(candidate(externally_supplied=True),))
    assert result.status is VisualResolutionStatus.REVIEW_REQUIRED


def test_policy_can_allow_external_candidate():
    policy = VisualObservationResolutionPolicy(allow_external_candidates=True)
    result = resolve(policy=policy, candidates=(candidate(externally_supplied=True),))
    assert result.status is VisualResolutionStatus.RESOLVED


def test_candidate_limit_is_blocked():
    policy = VisualObservationResolutionPolicy(maximum_candidates=1)
    items = (candidate(candidate_ref="a"), candidate(candidate_ref="b"))
    result = resolve(policy=policy, candidates=items)
    assert result.status is VisualResolutionStatus.BLOCKED


def test_too_long_candidate_reference_is_ignored():
    policy = VisualObservationResolutionPolicy(maximum_reference_length=3)
    result = resolve(policy=policy, candidates=(candidate(candidate_ref="long"),))
    assert result.status is VisualResolutionStatus.REVIEW_REQUIRED


def test_duplicate_candidate_references_are_deduplicated():
    low = candidate(candidate_ref="same", confidence=0.8)
    high = candidate(candidate_ref="same", confidence=0.9)
    result = resolve(candidates=(low, high))
    assert result.status is VisualResolutionStatus.RESOLVED
    assert result.selected_candidate == low


def test_original_is_preferred_when_policy_says_so():
    preview = candidate(
        candidate_ref="preview",
        representation_kind=VisualRepresentationKind.PREVIEW,
        confidence=0.99,
    )
    original = candidate(candidate_ref="original", confidence=0.8)
    result = resolve(candidates=(preview, original))
    assert result.selected_candidate == original


def test_highest_confidence_wins_when_original_preference_disabled():
    policy = VisualObservationResolutionPolicy(prefer_original_representation=False)
    preview = candidate(
        candidate_ref="preview",
        representation_kind=VisualRepresentationKind.PREVIEW,
        confidence=0.99,
    )
    original = candidate(candidate_ref="original", confidence=0.8)
    result = resolve(policy=policy, candidates=(preview, original))
    assert result.selected_candidate == preview


def test_tie_breaker_is_candidate_reference():
    b = candidate(
        candidate_ref="b", representation_kind=VisualRepresentationKind.PREVIEW
    )
    a = candidate(
        candidate_ref="a", representation_kind=VisualRepresentationKind.PREVIEW
    )
    result = resolve(candidates=(b, a))
    assert result.selected_candidate == a


def test_specialized_purpose_falls_back_to_general_candidate():
    result = resolve(
        purpose=VisualObservationPurpose.OBJECT_CONTEXT,
        candidates=(candidate(),),
    )
    assert result.status is VisualResolutionStatus.RESOLVED
    assert result.object_understanding_required


def test_non_matching_candidate_requires_review():
    item = candidate(declared_purposes=(VisualObservationPurpose.TEXT_CONTEXT,))
    result = resolve(
        purpose=VisualObservationPurpose.OBJECT_CONTEXT,
        candidates=(item,),
    )
    assert result.status is VisualResolutionStatus.REVIEW_REQUIRED


@pytest.mark.parametrize("kind", list(VisualRepresentationKind))
def test_all_representation_kinds_are_modeled(kind):
    item = candidate(representation_kind=kind)
    assert item.representation_kind is kind


@pytest.mark.parametrize("purpose", list(VisualObservationPurpose))
def test_all_purposes_are_modeled(purpose):
    item = candidate(declared_purposes=(purpose,))
    assert item.declared_purposes == (purpose,)


def test_string_enums_are_normalized():
    item = VisualObservationCandidate("c", "obs-001", "preview", 0.9, ("text_context",))
    req = VisualObservationResolutionRequest(
        "Carlos", visual_context(), "text_context", (item,)
    )
    assert item.representation_kind is VisualRepresentationKind.PREVIEW
    assert req.purpose is VisualObservationPurpose.TEXT_CONTEXT


def test_candidate_references_are_trimmed():
    item = candidate(candidate_ref="  c  ", observation_ref="  obs-001  ")
    assert item.candidate_ref == "c"
    assert item.observation_ref == "obs-001"


def test_owner_is_trimmed():
    assert request(owner="  Carlos  ").owner == "Carlos"


def test_blank_owner_rejected():
    with pytest.raises(ValueError):
        request(owner="   ")


def test_blank_candidate_reference_rejected():
    with pytest.raises(ValueError):
        candidate(candidate_ref="   ")


def test_blank_observation_reference_rejected():
    with pytest.raises(ValueError):
        candidate(observation_ref="   ")


def test_invalid_candidate_confidence_rejected():
    with pytest.raises(ValueError):
        candidate(confidence=1.1)


def test_empty_candidate_purposes_rejected():
    with pytest.raises(ValueError):
        candidate(declared_purposes=())


def test_duplicate_candidate_purposes_rejected():
    with pytest.raises(ValueError):
        candidate(
            declared_purposes=(
                VisualObservationPurpose.GENERAL_CONTEXT,
                VisualObservationPurpose.GENERAL_CONTEXT,
            )
        )


def test_invalid_policy_confidence_rejected():
    with pytest.raises(ValueError):
        VisualObservationResolutionPolicy(minimum_candidate_confidence=-0.1)


def test_invalid_policy_candidate_limit_rejected():
    with pytest.raises(ValueError):
        VisualObservationResolutionPolicy(maximum_candidates=0)


def test_invalid_policy_reference_limit_rejected():
    with pytest.raises(ValueError):
        VisualObservationResolutionPolicy(maximum_reference_length=0)


def test_request_candidates_are_tuple_normalized():
    req = VisualObservationResolutionRequest(
        "Carlos", visual_context(), candidates=[candidate()]
    )
    assert isinstance(req.candidates, tuple)


def test_resolution_is_immutable():
    result = resolve()
    with pytest.raises(FrozenInstanceError):
        result.observation_resolved = False


def test_request_is_immutable():
    req = request()
    with pytest.raises(FrozenInstanceError):
        req.owner = "Other"


def test_candidate_is_immutable():
    item = candidate()
    with pytest.raises(FrozenInstanceError):
        item.confidence = 0.1


def test_resolution_id_is_deterministic():
    first = resolve()
    second = VisualObservationResolutionEngine().resolve(first.request, now=NOW)
    assert first.resolution_id == second.resolution_id


def test_candidate_order_does_not_change_resolution_id():
    a = candidate(candidate_ref="a", confidence=0.8)
    b = candidate(candidate_ref="b", confidence=0.9)
    first = resolve(candidates=(a, b))
    second = resolve(candidates=(b, a))
    assert first.resolution_id == second.resolution_id


def test_inconsistent_resolution_id_rejected():
    result = resolve()
    with pytest.raises(ValueError):
        replace(result, resolution_id="wrong")


def test_naive_resolution_timestamp_rejected():
    with pytest.raises(ValueError):
        VisualObservationResolutionEngine().resolve(request(), now=datetime(2026, 1, 1))


def test_repository_add_get_and_list():
    repository = InMemoryVisualObservationResolutionRepository()
    engine = VisualObservationResolutionEngine(repository=repository)
    result = engine.resolve(request(), now=NOW)
    assert repository.get(result.resolution_id) == result
    assert repository.list_all() == (result,)


def test_repository_rejects_duplicate():
    repository = InMemoryVisualObservationResolutionRepository()
    result = VisualObservationResolutionEngine(repository=repository).resolve(
        request(), now=NOW
    )
    with pytest.raises(ValueError):
        repository.add(result)


def test_non_resolved_result_exposes_no_candidate():
    result = resolve(owner="Other")
    assert result.selected_candidate is None
    assert not result.observation_resolved


def test_resolved_result_preserves_visual_context_lineage():
    context = visual_context()
    result = resolve(visual_context=context)
    assert result.request.visual_context.context_id == context.context_id


def test_engine_does_not_mutate_request_candidates():
    items = (candidate(),)
    req = request(candidates=items)
    VisualObservationResolutionEngine().resolve(req, now=NOW)
    assert req.candidates == items
