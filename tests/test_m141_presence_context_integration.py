from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone

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
    AmbientObservationResolutionRequest,
    AmbientRepresentationKind,
)
from core.presence_change_detection import (
    PresenceChangeDetectionEngine,
    PresenceChangeDetectionRequest,
)
from core.presence_context_integration import (
    InMemoryPresenceContextIntegrationRepository,
    PresenceContextDimension,
    PresenceContextIntegrationAction,
    PresenceContextIntegrationEngine,
    PresenceContextIntegrationPolicy,
    PresenceContextIntegrationRequest,
    PresenceContextIntegrationStatus,
)
from core.presence_continuity import (
    PresenceContinuityEngine,
    PresenceContinuityRequest,
)
from core.presence_event_interpretation import (
    PresenceEventInterpretationEngine,
    PresenceEventInterpretationRequest,
)
from core.presence_situation_assessment import (
    PresenceSituationAssessmentEngine,
    PresenceSituationAssessmentRequest,
    PresenceSituationAssessmentStatus,
)
from core.presence_understanding import (
    PresenceEvidence,
    PresenceState,
    PresenceUnderstandingEngine,
    PresenceUnderstandingRequest,
)

NOW = datetime(2026, 7, 11, 23, 0, tzinfo=timezone.utc)


def resolved_observation(*, owner="Carlos", observation_ref="ambient-001", now=NOW):
    context = AmbientContextFoundationEngine().establish(
        AmbientContextFoundationRequest(
            owner=owner,
            observation=AmbientObservationSignal(
                observation_ref=observation_ref,
                source=AmbientObservationSource.HOME_SYSTEM,
                scope=AmbientScope.ROOM,
                privacy_level=AmbientPrivacyLevel.PERSONAL,
                confidence=0.95,
                observed_at=now,
                source_device_id="home-main",
            ),
            explicit_user_consent=True,
        ),
        now=now,
    )
    return AmbientObservationResolutionEngine().resolve(
        AmbientObservationResolutionRequest(
            owner=owner,
            ambient_context=context,
            purpose=AmbientObservationPurpose.PRESENCE_CONTEXT,
            candidates=(
                AmbientObservationCandidate(
                    candidate_ref=f"snapshot-{observation_ref}",
                    observation_ref=observation_ref,
                    representation_kind=AmbientRepresentationKind.SNAPSHOT,
                    confidence=0.94,
                    declared_purposes=(AmbientObservationPurpose.PRESENCE_CONTEXT,),
                ),
            ),
        ),
        now=now,
    )


def understanding(resolution, state, created_at, ref):
    return PresenceUnderstandingEngine().understand(
        PresenceUnderstandingRequest(
            owner=resolution.request.owner,
            resolved_observation=resolution,
            evidence=(
                PresenceEvidence(
                    evidence_ref=ref,
                    observation_ref=resolution.selected_candidate.observation_ref,
                    presence_state=state,
                    confidence=0.92,
                ),
            ),
        ),
        now=created_at,
    )


def continuity(
    *,
    states=(PresenceState.OCCUPIED, PresenceState.OCCUPIED),
    times=(NOW - timedelta(minutes=10), NOW - timedelta(minutes=5)),
    resolution=None,
    owner="Carlos",
    now=NOW - timedelta(minutes=4),
):
    resolution = resolution or resolved_observation(owner=owner)
    samples = tuple(
        understanding(resolution, state, created_at, f"e-{index}-{state.value}")
        for index, (state, created_at) in enumerate(zip(states, times, strict=True))
    )
    return PresenceContinuityEngine().evaluate(
        PresenceContinuityRequest(owner=owner, samples=samples), now=now
    )


def request(*results, owner="Carlos", **changes):
    if not results:
        results = (continuity(),)
    values = {"owner": owner, "continuity_results": results}
    values.update(changes)
    return PresenceChangeDetectionRequest(**values)


def detect(*results, policy=None, now=NOW, owner="Carlos", **changes):
    return PresenceChangeDetectionEngine(policy=policy).detect(
        request(*results, owner=owner, **changes), now=now
    )


def detection(
    *,
    states=(PresenceState.OCCUPIED, PresenceState.OCCUPIED),
    times=None,
    resolution=None,
    owner="Carlos",
    now=NOW - timedelta(minutes=2),
):
    if times is None:
        times = (NOW - timedelta(minutes=10), NOW - timedelta(minutes=5))
    source = continuity(
        states=states,
        times=times,
        resolution=resolution,
        owner=owner,
        now=now - timedelta(minutes=1),
    )
    return PresenceChangeDetectionEngine().detect(
        PresenceChangeDetectionRequest(owner=owner, continuity_results=(source,)),
        now=now,
    )


def interpretation_request(*results, owner="Carlos", **changes):
    if not results:
        results = (detection(),)
    values = {"owner": owner, "detection_results": results}
    values.update(changes)
    return PresenceEventInterpretationRequest(**values)


def interpret(*results, owner="Carlos", policy=None, now=NOW, **changes):
    return PresenceEventInterpretationEngine(policy=policy).interpret(
        interpretation_request(*results, owner=owner, **changes), now=now
    )


def situation_request(*results, owner="Carlos", **changes):
    if not results:
        results = (interpret(),)
    values = {"owner": owner, "interpretation_results": results}
    values.update(changes)
    return PresenceSituationAssessmentRequest(**values)


def assess(*results, owner="Carlos", policy=None, now=NOW, **changes):
    return PresenceSituationAssessmentEngine(policy=policy).assess(
        situation_request(*results, owner=owner, **changes), now=now
    )


def integration_request(*results, owner="Carlos", **changes):
    if not results:
        results = (assess(),)
    values = {
        "owner": owner,
        "assessment_results": results,
        "device_context": "mobile-primary",
        "conversation_context": "active-session",
        "spatial_context": "home-room",
        "temporal_context": "evening",
    }
    values.update(changes)
    return PresenceContextIntegrationRequest(**values)


def integrate(*results, owner="Carlos", policy=None, now=NOW, **changes):
    return PresenceContextIntegrationEngine(policy=policy).integrate(
        integration_request(*results, owner=owner, **changes), now=now
    )


def test_all_declared_dimensions_are_integrated():
    result = integrate()
    assert result.status is PresenceContextIntegrationStatus.INTEGRATED
    assert result.action is PresenceContextIntegrationAction.EXPOSE
    assert result.integrated_dimensions == tuple(PresenceContextDimension)
    assert result.context_integrated and result.context_exposed


@pytest.mark.parametrize(
    ("field", "dimension"),
    [
        ("device_context", PresenceContextDimension.DEVICE),
        ("conversation_context", PresenceContextDimension.CONVERSATION),
        ("spatial_context", PresenceContextDimension.SPATIAL),
        ("temporal_context", PresenceContextDimension.TEMPORAL),
    ],
)
def test_single_dimension_is_exposed_as_partial(field, dimension):
    changes = {
        name: None
        for name in (
            "device_context",
            "conversation_context",
            "spatial_context",
            "temporal_context",
        )
    }
    changes[field] = "declared-value"
    result = integrate(**changes)
    assert result.status is PresenceContextIntegrationStatus.PARTIAL
    assert result.action is PresenceContextIntegrationAction.EXPOSE_PARTIAL
    assert result.integrated_dimensions == (dimension,)


@pytest.mark.parametrize(
    "missing",
    ["device_context", "conversation_context", "spatial_context", "temporal_context"],
)
def test_three_dimensions_remain_fully_integrated(missing):
    result = integrate(**{missing: None})
    assert result.status is PresenceContextIntegrationStatus.INTEGRATED
    assert len(result.integrated_dimensions) == 3


def test_no_declared_dimension_requires_review():
    result = integrate(
        device_context=None,
        conversation_context=None,
        spatial_context=None,
        temporal_context=None,
    )
    assert result.status is PresenceContextIntegrationStatus.REVIEW_REQUIRED
    assert result.action is PresenceContextIntegrationAction.CONFIRM
    assert result.confirmation_required


def test_integration_not_declared_is_not_applicable():
    result = integrate(integration_declared=False)
    assert result.status is PresenceContextIntegrationStatus.NOT_APPLICABLE
    assert result.action is PresenceContextIntegrationAction.NONE


def test_owner_mismatch_is_blocked():
    result = integrate(assess(owner="Other"), owner="Carlos")
    assert result.status is PresenceContextIntegrationStatus.BLOCKED
    assert result.action is PresenceContextIntegrationAction.WITHHOLD


def test_result_limit_is_enforced():
    source = assess()
    result = integrate(
        source, source, policy=PresenceContextIntegrationPolicy(maximum_results=1)
    )
    assert result.status is PresenceContextIntegrationStatus.BLOCKED


def test_stale_source_requires_review():
    source = assess(now=NOW - timedelta(hours=3))
    result = integrate(source)
    assert result.status is PresenceContextIntegrationStatus.REVIEW_REQUIRED


def test_future_source_requires_review():
    source = assess(now=NOW + timedelta(minutes=1))
    result = integrate(source)
    assert result.status is PresenceContextIntegrationStatus.REVIEW_REQUIRED


def test_low_confidence_source_requires_review():
    source = replace(assess(), confidence=0.69, assessment_id="")
    result = integrate(source)
    assert result.status is PresenceContextIntegrationStatus.REVIEW_REQUIRED


def test_latest_valid_assessment_is_selected():
    older = assess(now=NOW)
    newer = replace(older, created_at=NOW + timedelta(minutes=1), assessment_id="")
    result = integrate(newer, older, now=NOW + timedelta(minutes=2))
    assert result.source_assessment == newer


def test_duplicate_assessment_is_deduplicated():
    source = assess()
    result = integrate(source, source)
    assert result.source_assessment == source


def test_repository_stores_result():
    repository = InMemoryPresenceContextIntegrationRepository()
    engine = PresenceContextIntegrationEngine(repository=repository)
    result = engine.integrate(integration_request(), now=NOW)
    assert repository.get(result.integration_id) == result
    assert repository.list_all() == (result,)


def test_repository_rejects_duplicate():
    repository = InMemoryPresenceContextIntegrationRepository()
    result = PresenceContextIntegrationEngine(repository=repository).integrate(
        integration_request(), now=NOW
    )
    with pytest.raises(ValueError, match="already exists"):
        repository.add(result)


def test_result_is_immutable():
    with pytest.raises(FrozenInstanceError):
        integrate().confidence = 0.1


@pytest.mark.parametrize("owner", ["", " ", "\t"])
def test_blank_owner_is_rejected(owner):
    with pytest.raises(ValueError, match="owner"):
        integration_request(owner=owner)


@pytest.mark.parametrize(
    "field",
    ["device_context", "conversation_context", "spatial_context", "temporal_context"],
)
def test_blank_declared_context_is_rejected(field):
    with pytest.raises(ValueError, match=field):
        integration_request(**{field: " "})


@pytest.mark.parametrize("value", [0, -1])
def test_policy_requires_positive_result_limit(value):
    with pytest.raises(ValueError, match="limit"):
        PresenceContextIntegrationPolicy(maximum_results=value)


@pytest.mark.parametrize("value", [timedelta(0), timedelta(seconds=-1)])
def test_policy_requires_positive_age(value):
    with pytest.raises(ValueError, match="age"):
        PresenceContextIntegrationPolicy(maximum_result_age=value)


@pytest.mark.parametrize("value", [-0.1, 1.1])
def test_policy_rejects_invalid_confidence(value):
    with pytest.raises(ValueError, match="confidence"):
        PresenceContextIntegrationPolicy(minimum_confidence=value)


@pytest.mark.parametrize("value", [0, 5])
def test_policy_rejects_invalid_dimension_threshold(value):
    with pytest.raises(ValueError, match="dimension"):
        PresenceContextIntegrationPolicy(minimum_dimensions_for_integrated=value)


def test_custom_dimension_threshold_controls_partial_status():
    policy = PresenceContextIntegrationPolicy(minimum_dimensions_for_integrated=4)
    result = integrate(policy=policy, temporal_context=None)
    assert result.status is PresenceContextIntegrationStatus.PARTIAL


def test_naive_now_is_rejected():
    with pytest.raises(ValueError, match="timezone-aware"):
        integrate(now=datetime(2026, 7, 11, 23, 0))


@pytest.mark.parametrize(
    "field",
    [
        "identity_inference_allowed",
        "biometric_analysis_allowed",
        "precise_person_counting_allowed",
        "activity_inference_allowed",
        "intent_inference_allowed",
        "individual_tracking_allowed",
        "movement_tracking_allowed",
        "response_decision_allowed",
        "behavior_adaptation_allowed",
        "sensor_access_allowed",
        "automation_allowed",
    ],
)
def test_all_downstream_capabilities_are_forbidden(field):
    result = integrate()
    assert getattr(result, field) is False
    with pytest.raises(ValueError, match="cannot authorize"):
        replace(result, **{field: True}, integration_id="")


def test_source_assessment_is_preserved_exactly():
    source = assess()
    result = integrate(source)
    assert result.source_assessment is source


def test_context_values_are_preserved_exactly():
    result = integrate()
    assert result.device_context == "mobile-primary"
    assert result.conversation_context == "active-session"
    assert result.spatial_context == "home-room"
    assert result.temporal_context == "evening"


def test_stable_assessment_can_be_integrated_without_reinterpretation():
    source = assess()
    assert source.status is PresenceSituationAssessmentStatus.STABLE
    result = integrate(source)
    assert result.status is PresenceContextIntegrationStatus.INTEGRATED
    assert result.source_assessment is source


def test_transition_assessment_can_be_integrated_without_decision():
    source = assess(
        interpret(detection(states=(PresenceState.UNOCCUPIED, PresenceState.OCCUPIED)))
    )
    result = integrate(source)
    assert result.status is PresenceContextIntegrationStatus.INTEGRATED
    assert not result.response_decision_allowed
    assert not result.behavior_adaptation_allowed


def test_id_is_deterministic_for_same_result():
    first = integrate()
    second = PresenceContextIntegrationEngine().integrate(first.request, now=NOW)
    assert first.integration_id == second.integration_id


def test_tampered_id_is_rejected():
    with pytest.raises(ValueError, match="id is inconsistent"):
        replace(integrate(), integration_id="tampered")
