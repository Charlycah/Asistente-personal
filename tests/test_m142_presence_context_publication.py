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
    PresenceContextIntegrationEngine,
    PresenceContextIntegrationRequest,
)
from core.presence_context_publication import (
    InMemoryPresenceContextPublicationRepository,
    PresenceContextPublicationAction,
    PresenceContextPublicationEngine,
    PresenceContextPublicationPolicy,
    PresenceContextPublicationRequest,
    PresenceContextPublicationStatus,
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


def publication_request(*results, owner="Carlos", **changes):
    if not results:
        results = (integrate(),)
    values = {
        "owner": owner,
        "integration_results": results,
        "publication_topic": "roby.ambient.presence.context",
        "schema_version": "1.0",
    }
    values.update(changes)
    return PresenceContextPublicationRequest(**values)


def publish(*results, owner="Carlos", policy=None, now=NOW, **changes):
    return PresenceContextPublicationEngine(policy=policy).publish(
        publication_request(*results, owner=owner, **changes), now=now
    )


def test_integrated_context_is_published_canonically():
    result = publish()
    assert result.status is PresenceContextPublicationStatus.PUBLISHED
    assert result.action is PresenceContextPublicationAction.PUBLISH
    assert result.context_published
    assert not result.partial_context_published


def test_partial_context_is_published_explicitly():
    source = integrate(
        conversation_context=None, spatial_context=None, temporal_context=None
    )
    result = publish(source)
    assert result.status is PresenceContextPublicationStatus.PUBLISHED_PARTIAL
    assert result.action is PresenceContextPublicationAction.PUBLISH_PARTIAL
    assert result.partial_context_published


def test_partial_publication_can_require_review_by_policy():
    source = integrate(
        conversation_context=None, spatial_context=None, temporal_context=None
    )
    result = publish(
        source, policy=PresenceContextPublicationPolicy(allow_partial_publication=False)
    )
    assert result.status is PresenceContextPublicationStatus.REVIEW_REQUIRED
    assert result.confirmation_required


def test_publication_not_declared_is_not_applicable():
    result = publish(publication_declared=False)
    assert result.status is PresenceContextPublicationStatus.NOT_APPLICABLE
    assert result.action is PresenceContextPublicationAction.NONE


def test_owner_mismatch_is_blocked():
    result = publish(integrate(owner="Other"), owner="Carlos")
    assert result.status is PresenceContextPublicationStatus.BLOCKED
    assert result.action is PresenceContextPublicationAction.WITHHOLD


def test_result_limit_is_enforced():
    source = integrate()
    result = publish(
        source, source, policy=PresenceContextPublicationPolicy(maximum_results=1)
    )
    assert result.status is PresenceContextPublicationStatus.BLOCKED


def test_stale_source_requires_review():
    source = integrate(now=NOW - timedelta(hours=3))
    result = publish(source)
    assert result.status is PresenceContextPublicationStatus.REVIEW_REQUIRED


def test_future_source_requires_review():
    source = integrate(now=NOW + timedelta(minutes=1))
    result = publish(source)
    assert result.status is PresenceContextPublicationStatus.REVIEW_REQUIRED


def test_low_confidence_source_requires_review():
    source = replace(integrate(), confidence=0.69, integration_id="")
    result = publish(source)
    assert result.status is PresenceContextPublicationStatus.REVIEW_REQUIRED


def test_latest_valid_integration_is_selected():
    older = integrate(now=NOW)
    newer = replace(older, created_at=NOW + timedelta(minutes=1), integration_id="")
    result = publish(newer, older, now=NOW + timedelta(minutes=2))
    assert result.source_integration == newer


def test_duplicate_integration_is_deduplicated():
    source = integrate()
    result = publish(source, source)
    assert result.source_integration == source


def test_source_integration_is_preserved_exactly():
    source = integrate()
    result = publish(source)
    assert result.source_integration is source


def test_topic_and_schema_are_preserved_exactly():
    result = publish(publication_topic="custom.topic", schema_version="2.1")
    assert result.publication_topic == "custom.topic"
    assert result.schema_version == "2.1"


def test_payload_digest_is_deterministic():
    first = publish()
    second = PresenceContextPublicationEngine().publish(first.request, now=NOW)
    assert first.payload_digest == second.payload_digest
    assert first.publication_id == second.publication_id


def test_payload_digest_changes_with_schema():
    first = publish(schema_version="1.0")
    second = publish(schema_version="2.0")
    assert first.payload_digest != second.payload_digest


def test_repository_stores_result():
    repository = InMemoryPresenceContextPublicationRepository()
    engine = PresenceContextPublicationEngine(repository=repository)
    result = engine.publish(publication_request(), now=NOW)
    assert repository.get(result.publication_id) == result
    assert repository.list_all() == (result,)


def test_repository_rejects_duplicate():
    repository = InMemoryPresenceContextPublicationRepository()
    result = PresenceContextPublicationEngine(repository=repository).publish(
        publication_request(), now=NOW
    )
    with pytest.raises(ValueError, match="already exists"):
        repository.add(result)


def test_result_is_immutable():
    with pytest.raises(FrozenInstanceError):
        publish().confidence = 0.1


@pytest.mark.parametrize("owner", ["", " ", "\t"])
def test_blank_owner_is_rejected(owner):
    with pytest.raises(ValueError, match="owner"):
        publication_request(owner=owner)


@pytest.mark.parametrize("field", ["publication_topic", "schema_version"])
def test_blank_publication_metadata_is_rejected(field):
    with pytest.raises(ValueError, match="blank"):
        publication_request(**{field: " "})


@pytest.mark.parametrize("value", [0, -1])
def test_policy_requires_positive_result_limit(value):
    with pytest.raises(ValueError, match="limit"):
        PresenceContextPublicationPolicy(maximum_results=value)


@pytest.mark.parametrize("value", [timedelta(0), timedelta(seconds=-1)])
def test_policy_requires_positive_age(value):
    with pytest.raises(ValueError, match="age"):
        PresenceContextPublicationPolicy(maximum_result_age=value)


@pytest.mark.parametrize("value", [-0.1, 1.1])
def test_policy_rejects_invalid_confidence(value):
    with pytest.raises(ValueError, match="confidence"):
        PresenceContextPublicationPolicy(minimum_confidence=value)


def test_naive_now_is_rejected():
    with pytest.raises(ValueError, match="timezone-aware"):
        publish(now=datetime(2026, 7, 11, 23, 0))


@pytest.mark.parametrize(
    "field",
    [
        "consumer_invocation_allowed",
        "identity_inference_allowed",
        "activity_inference_allowed",
        "intent_inference_allowed",
        "individual_tracking_allowed",
        "response_decision_allowed",
        "behavior_adaptation_allowed",
        "sensor_access_allowed",
        "provider_call_allowed",
        "automation_allowed",
        "platform_mutation_allowed",
    ],
)
def test_all_downstream_capabilities_are_forbidden(field):
    result = publish()
    assert getattr(result, field) is False
    with pytest.raises(ValueError, match="cannot authorize"):
        replace(result, **{field: True}, publication_id="")


def test_publication_does_not_mutate_source_context():
    source = integrate()
    before = source.integration_id
    result = publish(source)
    assert source.integration_id == before
    assert result.source_integration is source


def test_publication_does_not_invoke_consumers():
    result = publish()
    assert not result.consumer_invocation_allowed
    assert result.action is PresenceContextPublicationAction.PUBLISH


def test_inactive_result_exposes_no_canonical_metadata():
    result = publish(publication_declared=False)
    assert result.publication_topic is None
    assert result.schema_version is None
    assert result.payload_digest is None
    assert result.source_integration is None


def test_tampered_id_is_rejected():
    with pytest.raises(ValueError, match="id is inconsistent"):
        replace(publish(), publication_id="tampered")
