from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone

import pytest

from core.ambient_context_foundation import (
    AmbientContextFoundationEngine,
    AmbientContextFoundationRequest,
    AmbientObservationSignal,
    AmbientObservationSource,
    AmbientPrivacyLevel,
    AmbientScope,
)
from core.ambient_observation_resolution import (
    AmbientObservationCandidate,
    AmbientObservationPurpose,
    AmbientObservationResolutionEngine,
    AmbientObservationResolutionPolicy,
    AmbientObservationResolutionRequest,
    AmbientRepresentationKind,
    AmbientResolutionAction,
    AmbientResolutionStatus,
    InMemoryAmbientObservationResolutionRepository,
)

NOW = datetime(2026, 7, 11, 23, 30, tzinfo=timezone.utc)


def context(*, owner="Carlos"):
    signal = AmbientObservationSignal(
        "ambient-001",
        AmbientObservationSource.MOBILE_DEVICE,
        AmbientScope.PERSONAL,
        AmbientPrivacyLevel.PERSONAL,
        0.95,
        NOW,
        "phone-main",
    )
    request = AmbientContextFoundationRequest(
        owner=owner, observation=signal, explicit_user_consent=True
    )
    return AmbientContextFoundationEngine().establish(request, now=NOW)


def candidate(**changes):
    values = dict(
        candidate_ref="ambient-candidate-001",
        observation_ref="ambient-001",
        representation_kind=AmbientRepresentationKind.SNAPSHOT,
        confidence=0.95,
        declared_purposes=(AmbientObservationPurpose.GENERAL_CONTEXT,),
    )
    values.update(changes)
    return AmbientObservationCandidate(**values)


def request(**changes):
    values = dict(owner="Carlos", ambient_context=context(), candidates=(candidate(),))
    values.update(changes)
    return AmbientObservationResolutionRequest(**values)


def resolve(*, policy=None, repository=None, **changes):
    return AmbientObservationResolutionEngine(
        policy=policy, repository=repository
    ).resolve(request(**changes), now=NOW)


def test_resolves_governed_candidate():
    result = resolve()
    assert result.status is AmbientResolutionStatus.RESOLVED
    assert result.action is AmbientResolutionAction.SELECT
    assert result.observation_resolved


def test_selected_candidate_is_preserved():
    item = candidate()
    assert resolve(candidates=(item,)).selected_candidate == item


def test_general_context_sets_no_special_requirement():
    result = resolve()
    assert not any(
        (
            result.presence_understanding_required,
            result.activity_understanding_required,
            result.acoustic_understanding_required,
            result.environmental_condition_understanding_required,
            result.spatial_understanding_required,
        )
    )


@pytest.mark.parametrize(
    ("purpose", "field"),
    [
        (AmbientObservationPurpose.PRESENCE_CONTEXT, "presence_understanding_required"),
        (AmbientObservationPurpose.ACTIVITY_CONTEXT, "activity_understanding_required"),
        (AmbientObservationPurpose.ACOUSTIC_CONTEXT, "acoustic_understanding_required"),
        (
            AmbientObservationPurpose.ENVIRONMENTAL_CONDITION_CONTEXT,
            "environmental_condition_understanding_required",
        ),
        (AmbientObservationPurpose.SPATIAL_CONTEXT, "spatial_understanding_required"),
    ],
)
def test_purpose_sets_matching_future_requirement(purpose, field):
    item = candidate(declared_purposes=(purpose,))
    result = resolve(purpose=purpose, candidates=(item,))
    assert getattr(result, field)


def test_never_allows_sensor_access():
    assert not resolve().sensor_access_allowed


def test_never_allows_automation():
    assert not resolve().automation_allowed


def test_resolution_not_declared_is_not_applicable():
    result = resolve(resolution_declared=False)
    assert result.status is AmbientResolutionStatus.NOT_APPLICABLE


def test_owner_mismatch_is_blocked():
    result = resolve(owner="Other")
    assert result.status is AmbientResolutionStatus.BLOCKED


def test_non_ready_context_is_blocked():
    bad = AmbientContextFoundationEngine().establish(
        AmbientContextFoundationRequest(
            owner="Carlos", observation=None, explicit_user_consent=True
        ),
        now=NOW,
    )
    assert resolve(ambient_context=bad).status is AmbientResolutionStatus.BLOCKED


def test_missing_candidates_requires_review():
    result = resolve(candidates=())
    assert result.status is AmbientResolutionStatus.REVIEW_REQUIRED
    assert result.action is AmbientResolutionAction.CONFIRM


def test_candidate_lineage_mismatch_is_blocked():
    result = resolve(candidates=(candidate(observation_ref="other"),))
    assert result.status is AmbientResolutionStatus.BLOCKED


def test_external_candidate_blocked_by_default():
    result = resolve(candidates=(candidate(externally_supplied=True),))
    assert result.status is AmbientResolutionStatus.BLOCKED


def test_policy_can_allow_external_candidate():
    policy = AmbientObservationResolutionPolicy(allow_external_candidates=True)
    result = resolve(policy=policy, candidates=(candidate(externally_supplied=True),))
    assert result.status is AmbientResolutionStatus.RESOLVED


def test_low_confidence_candidate_is_ignored():
    result = resolve(candidates=(candidate(confidence=0.69),))
    assert result.status is AmbientResolutionStatus.REVIEW_REQUIRED


def test_confidence_at_threshold_is_accepted():
    policy = AmbientObservationResolutionPolicy(minimum_candidate_confidence=0.7)
    assert resolve(
        policy=policy, candidates=(candidate(confidence=0.7),)
    ).observation_resolved


def test_candidate_without_requested_purpose_is_ignored():
    result = resolve(purpose=AmbientObservationPurpose.ACTIVITY_CONTEXT)
    assert result.status is AmbientResolutionStatus.REVIEW_REQUIRED


def test_candidate_limit_is_enforced():
    policy = AmbientObservationResolutionPolicy(maximum_candidates=1)
    items = (candidate(candidate_ref="a"), candidate(candidate_ref="b"))
    assert (
        resolve(policy=policy, candidates=items).status
        is AmbientResolutionStatus.BLOCKED
    )


def test_reference_limit_is_enforced():
    policy = AmbientObservationResolutionPolicy(maximum_reference_length=3)
    assert resolve(policy=policy).status is AmbientResolutionStatus.BLOCKED


def test_observation_reference_limit_is_enforced():
    policy = AmbientObservationResolutionPolicy(maximum_reference_length=5)
    item = candidate(candidate_ref="a", observation_ref="ambient-001")
    assert (
        resolve(policy=policy, candidates=(item,)).status
        is AmbientResolutionStatus.BLOCKED
    )


def test_prefers_snapshot_by_default():
    items = (
        candidate(
            candidate_ref="raw",
            representation_kind=AmbientRepresentationKind.RAW_SIGNAL,
            confidence=1.0,
        ),
        candidate(
            candidate_ref="snap",
            representation_kind=AmbientRepresentationKind.SNAPSHOT,
            confidence=0.8,
        ),
    )
    assert resolve(candidates=items).selected_candidate.candidate_ref == "snap"


def test_policy_can_disable_snapshot_preference():
    policy = AmbientObservationResolutionPolicy(prefer_snapshot_representation=False)
    items = (
        candidate(
            candidate_ref="raw",
            representation_kind=AmbientRepresentationKind.RAW_SIGNAL,
            confidence=1.0,
        ),
        candidate(
            candidate_ref="snap",
            representation_kind=AmbientRepresentationKind.SNAPSHOT,
            confidence=0.8,
        ),
    )
    assert (
        resolve(policy=policy, candidates=items).selected_candidate.candidate_ref
        == "raw"
    )


def test_deduplicates_and_keeps_higher_confidence():
    items = (candidate(confidence=0.8), candidate(confidence=0.95))
    assert resolve(candidates=items).selected_candidate.confidence == 0.95


def test_deterministic_tie_breaker_uses_reference():
    items = (candidate(candidate_ref="b"), candidate(candidate_ref="a"))
    assert resolve(candidates=items).selected_candidate.candidate_ref == "a"


@pytest.mark.parametrize("kind", list(AmbientRepresentationKind))
def test_all_representation_kinds_supported(kind):
    result = resolve(candidates=(candidate(representation_kind=kind),))
    assert result.status is AmbientResolutionStatus.RESOLVED


@pytest.mark.parametrize("purpose", list(AmbientObservationPurpose))
def test_all_purposes_supported(purpose):
    item = candidate(declared_purposes=(purpose,))
    assert resolve(purpose=purpose, candidates=(item,)).observation_resolved


def test_string_enums_are_normalized():
    item = AmbientObservationCandidate(
        "c", "ambient-001", "snapshot", 0.9, ("general_context",)
    )
    assert item.representation_kind is AmbientRepresentationKind.SNAPSHOT
    assert item.declared_purposes == (AmbientObservationPurpose.GENERAL_CONTEXT,)


def test_request_owner_is_trimmed():
    assert request(owner="  Carlos  ").owner == "Carlos"


def test_candidate_references_are_trimmed():
    item = candidate(candidate_ref="  c  ", observation_ref="  ambient-001  ")
    assert item.candidate_ref == "c"
    assert item.observation_ref == "ambient-001"


@pytest.mark.parametrize("field", ["candidate_ref", "observation_ref"])
def test_blank_candidate_references_rejected(field):
    with pytest.raises(ValueError):
        candidate(**{field: "   "})


def test_blank_owner_rejected():
    with pytest.raises(ValueError):
        request(owner="   ")


@pytest.mark.parametrize("confidence", [-0.01, 1.01])
def test_invalid_candidate_confidence_rejected(confidence):
    with pytest.raises(ValueError):
        candidate(confidence=confidence)


def test_empty_purposes_rejected():
    with pytest.raises(ValueError):
        candidate(declared_purposes=())


def test_duplicate_purposes_rejected():
    with pytest.raises(ValueError):
        candidate(declared_purposes=(AmbientObservationPurpose.GENERAL_CONTEXT,) * 2)


@pytest.mark.parametrize(
    "changes",
    [
        {"minimum_candidate_confidence": -0.1},
        {"minimum_candidate_confidence": 1.1},
        {"maximum_candidates": 0},
        {"maximum_reference_length": 0},
    ],
)
def test_invalid_policy_rejected(changes):
    with pytest.raises(ValueError):
        AmbientObservationResolutionPolicy(**changes)


def test_naive_resolution_timestamp_rejected():
    with pytest.raises(ValueError):
        AmbientObservationResolutionEngine().resolve(
            request(), now=datetime(2026, 7, 11)
        )


def test_result_is_immutable():
    with pytest.raises(FrozenInstanceError):
        resolve().status = AmbientResolutionStatus.BLOCKED


def test_request_and_candidate_are_immutable():
    with pytest.raises(FrozenInstanceError):
        request().owner = "Other"
    with pytest.raises(FrozenInstanceError):
        candidate().confidence = 0.1


def test_repository_stores_and_returns_result():
    repository = InMemoryAmbientObservationResolutionRepository()
    result = resolve(repository=repository)
    assert repository.get(result.resolution_id) == result
    assert repository.list_all() == (result,)


def test_repository_rejects_duplicate_id():
    repository = InMemoryAmbientObservationResolutionRepository()
    result = resolve(repository=repository)
    with pytest.raises(ValueError):
        repository.add(result)


def test_same_input_and_time_produce_same_id():
    first = AmbientObservationResolutionEngine().resolve(request(), now=NOW)
    second = AmbientObservationResolutionEngine().resolve(request(), now=NOW)
    assert first.resolution_id == second.resolution_id


def test_candidate_order_does_not_change_id():
    a = candidate(candidate_ref="a")
    b = candidate(candidate_ref="b", confidence=0.8)
    first = AmbientObservationResolutionEngine().resolve(
        request(candidates=(a, b)), now=NOW
    )
    second = AmbientObservationResolutionEngine().resolve(
        request(candidates=(b, a)), now=NOW
    )
    assert first.resolution_id == second.resolution_id


def test_inconsistent_resolution_id_rejected():
    result = resolve()
    with pytest.raises(ValueError):
        replace(result, resolution_id="wrong")


def test_manual_sensor_authorization_rejected():
    result = resolve()
    with pytest.raises(ValueError):
        replace(result, sensor_access_allowed=True, resolution_id="")


def test_manual_automation_authorization_rejected():
    result = resolve()
    with pytest.raises(ValueError):
        replace(result, automation_allowed=True, resolution_id="")


def test_non_resolved_result_cannot_expose_candidate():
    result = resolve()
    with pytest.raises(ValueError):
        replace(result, status=AmbientResolutionStatus.BLOCKED, resolution_id="")


def test_result_rationale_is_non_empty():
    assert resolve().rationale == ("ambient_observation_resolved",)


def test_result_preserves_context_lineage():
    result = resolve()
    assert (
        result.request.ambient_context.context_id
        == request().ambient_context.context_id
    )


def test_module_does_not_expose_forbidden_capabilities():
    result = resolve()
    for name in (
        "presence_inference_allowed",
        "activity_inference_allowed",
        "acoustic_analysis_allowed",
        "environmental_condition_analysis_allowed",
        "spatial_inference_allowed",
    ):
        assert not hasattr(result, name)
