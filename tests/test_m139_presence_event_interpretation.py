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
    PresenceChangeDetectionAction,
    PresenceChangeDetectionEngine,
    PresenceChangeDetectionRequest,
    PresenceChangeDetectionStatus,
    PresenceChangeKind,
)
from core.presence_continuity import (
    PresenceContinuityEngine,
    PresenceContinuityRequest,
)
from core.presence_event_interpretation import (
    InMemoryPresenceEventInterpretationRepository,
    PresenceEventInterpretationAction,
    PresenceEventInterpretationEngine,
    PresenceEventInterpretationPolicy,
    PresenceEventInterpretationRequest,
    PresenceEventInterpretationStatus,
    PresenceEventMeaning,
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


def test_no_change_is_suppressed_as_no_event():
    result = interpret()
    assert result.status is PresenceEventInterpretationStatus.NO_EVENT
    assert result.action is PresenceEventInterpretationAction.SUPPRESS
    assert result.meaning is PresenceEventMeaning.NONE
    assert not result.event_interpreted
    assert not result.event_exposed


@pytest.mark.parametrize(
    ("states", "meaning", "kind"),
    [
        (
            (PresenceState.UNOCCUPIED, PresenceState.OCCUPIED),
            PresenceEventMeaning.PRESENCE_BECAME_OBSERVED,
            PresenceChangeKind.APPEARANCE,
        ),
        (
            (PresenceState.UNOCCUPIED, PresenceState.SINGLE_PRESENCE),
            PresenceEventMeaning.PRESENCE_BECAME_OBSERVED,
            PresenceChangeKind.APPEARANCE,
        ),
        (
            (PresenceState.OCCUPIED, PresenceState.UNOCCUPIED),
            PresenceEventMeaning.PRESENCE_BECAME_UNOBSERVED,
            PresenceChangeKind.DISAPPEARANCE,
        ),
        (
            (PresenceState.MULTIPLE_PRESENCES, PresenceState.UNOCCUPIED),
            PresenceEventMeaning.PRESENCE_BECAME_UNOBSERVED,
            PresenceChangeKind.DISAPPEARANCE,
        ),
        (
            (PresenceState.SINGLE_PRESENCE, PresenceState.MULTIPLE_PRESENCES),
            PresenceEventMeaning.AMBIENT_OCCUPANCY_SHIFTED,
            PresenceChangeKind.OCCUPANCY_VARIATION,
        ),
        (
            (PresenceState.MULTIPLE_PRESENCES, PresenceState.SINGLE_PRESENCE),
            PresenceEventMeaning.AMBIENT_OCCUPANCY_SHIFTED,
            PresenceChangeKind.OCCUPANCY_VARIATION,
        ),
        (
            (PresenceState.OCCUPIED, PresenceState.TRANSIENT),
            PresenceEventMeaning.TRANSIENT_PRESENCE_SIGNAL,
            PresenceChangeKind.TRANSIENT_VARIATION,
        ),
        (
            (PresenceState.TRANSIENT, PresenceState.OCCUPIED),
            PresenceEventMeaning.TRANSIENT_PRESENCE_SIGNAL,
            PresenceChangeKind.TRANSIENT_VARIATION,
        ),
        (
            (PresenceState.OCCUPIED, PresenceState.UNKNOWN),
            PresenceEventMeaning.PRESENCE_CERTAINTY_CHANGED,
            PresenceChangeKind.UNCERTAIN_VARIATION,
        ),
        (
            (PresenceState.UNKNOWN, PresenceState.OCCUPIED),
            PresenceEventMeaning.PRESENCE_CERTAINTY_CHANGED,
            PresenceChangeKind.UNCERTAIN_VARIATION,
        ),
    ],
)
def test_interprets_detected_change_semantics(states, meaning, kind):
    result = interpret(detection(states=states))
    assert result.status is PresenceEventInterpretationStatus.INTERPRETED
    assert result.action is PresenceEventInterpretationAction.EXPOSE
    assert result.meaning is meaning
    assert result.source_change_kind is kind
    assert result.event_interpreted
    assert result.event_exposed


def test_interprets_continuity_break_without_inventing_activity():
    source = detection(times=(NOW - timedelta(minutes=40), NOW - timedelta(minutes=5)))
    result = interpret(source)
    assert result.meaning is PresenceEventMeaning.PRESENCE_CONTINUITY_LOST
    assert result.source_change_kind is PresenceChangeKind.CONTINUITY_BREAK
    assert not result.activity_inference_allowed
    assert not result.intent_inference_allowed


@pytest.mark.parametrize("state", list(PresenceState))
def test_stable_states_never_gain_event_semantics(state):
    result = interpret(detection(states=(state, state)))
    assert result.status is PresenceEventInterpretationStatus.NO_EVENT
    assert result.meaning is PresenceEventMeaning.NONE


def test_latest_actionable_detection_wins():
    old = detection(
        states=(PresenceState.UNOCCUPIED, PresenceState.OCCUPIED),
        now=NOW - timedelta(minutes=8),
    )
    latest = detection(
        states=(PresenceState.OCCUPIED, PresenceState.UNOCCUPIED),
        now=NOW - timedelta(minutes=2),
    )
    result = interpret(latest, old)
    assert result.source_detection is latest
    assert result.meaning is PresenceEventMeaning.PRESENCE_BECAME_UNOBSERVED


def test_duplicate_detections_are_deduplicated():
    source = detection(states=(PresenceState.UNOCCUPIED, PresenceState.OCCUPIED))
    result = interpret(source, source)
    assert result.source_detection is source


def test_not_declared_is_not_applicable():
    result = interpret(interpretation_declared=False)
    assert result.status is PresenceEventInterpretationStatus.NOT_APPLICABLE
    assert result.action is PresenceEventInterpretationAction.NONE


def test_empty_results_require_review():
    result = PresenceEventInterpretationEngine().interpret(
        PresenceEventInterpretationRequest(owner="Carlos", detection_results=()),
        now=NOW,
    )
    assert result.status is PresenceEventInterpretationStatus.REVIEW_REQUIRED
    assert result.confirmation_required


def test_owner_mismatch_is_blocked():
    result = interpret(owner="Other")
    assert result.status is PresenceEventInterpretationStatus.BLOCKED
    assert result.rationale == ("presence_event_owner_mismatch",)


def test_result_limit_is_blocked():
    source = detection()
    result = interpret(
        source, source, policy=PresenceEventInterpretationPolicy(maximum_results=1)
    )
    assert result.status is PresenceEventInterpretationStatus.BLOCKED


def test_stale_result_requires_review():
    source = detection(now=NOW - timedelta(hours=3))
    result = interpret(source)
    assert result.status is PresenceEventInterpretationStatus.REVIEW_REQUIRED


def test_future_result_requires_review():
    source = detection(now=NOW + timedelta(minutes=1))
    result = interpret(source)
    assert result.status is PresenceEventInterpretationStatus.REVIEW_REQUIRED


def test_low_confidence_result_requires_review():
    source = detection()
    weak = replace(source, confidence=0.69, detection_id="")
    result = interpret(weak)
    assert result.status is PresenceEventInterpretationStatus.REVIEW_REQUIRED


def test_context_lineage_mismatch_is_blocked():
    first = detection(
        states=(PresenceState.UNOCCUPIED, PresenceState.OCCUPIED),
        resolution=resolved_observation(observation_ref="a"),
        now=NOW - timedelta(minutes=4),
    )
    second = detection(
        states=(PresenceState.OCCUPIED, PresenceState.UNOCCUPIED),
        resolution=resolved_observation(observation_ref="b"),
        now=NOW - timedelta(minutes=2),
    )
    result = interpret(first, second)
    assert result.status is PresenceEventInterpretationStatus.BLOCKED
    assert result.rationale == ("presence_event_context_lineage_mismatch",)


@pytest.mark.parametrize(
    "status",
    [
        PresenceChangeDetectionStatus.REVIEW_REQUIRED,
        PresenceChangeDetectionStatus.BLOCKED,
        PresenceChangeDetectionStatus.NOT_APPLICABLE,
    ],
)
def test_non_actionable_detection_is_not_reinterpreted(status):
    source = detection()
    inactive = replace(
        source,
        status=status,
        action=(
            PresenceChangeDetectionAction.CONFIRM
            if status is PresenceChangeDetectionStatus.REVIEW_REQUIRED
            else PresenceChangeDetectionAction.WITHHOLD
            if status is PresenceChangeDetectionStatus.BLOCKED
            else PresenceChangeDetectionAction.NONE
        ),
        change_kind=PresenceChangeKind.NONE,
        source_continuity=None,
        previous_presence=None,
        current_presence=None,
        confidence=0.0,
        change_detected=False,
        change_published=False,
        continuity_break_detected=False,
        confirmation_required=status is PresenceChangeDetectionStatus.REVIEW_REQUIRED,
        rationale=("inactive",),
        detection_id="",
    )
    result = interpret(inactive)
    assert result.status is PresenceEventInterpretationStatus.REVIEW_REQUIRED


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
        "sensor_access_allowed",
        "automation_allowed",
    ],
)
def test_forbidden_capabilities_remain_false(field):
    result = interpret(
        detection(states=(PresenceState.UNOCCUPIED, PresenceState.OCCUPIED))
    )
    assert getattr(result, field) is False
    with pytest.raises(ValueError):
        replace(result, **{field: True}, interpretation_id="")


def test_request_normalizes_owner_and_tuple():
    source = detection()
    request = PresenceEventInterpretationRequest(
        owner="  Carlos  ", detection_results=[source]
    )
    assert request.owner == "Carlos"
    assert request.detection_results == (source,)


def test_blank_owner_is_rejected():
    with pytest.raises(ValueError):
        PresenceEventInterpretationRequest(owner=" ", detection_results=())


@pytest.mark.parametrize(
    "changes",
    [
        {"maximum_results": 0},
        {"maximum_result_age": timedelta(0)},
        {"minimum_confidence": -0.1},
        {"minimum_confidence": 1.1},
    ],
)
def test_invalid_policy_is_rejected(changes):
    with pytest.raises(ValueError):
        PresenceEventInterpretationPolicy(**changes)


def test_naive_now_is_rejected():
    with pytest.raises(ValueError):
        interpret(now=datetime(2026, 7, 11, 23, 0))


def test_result_is_immutable():
    result = interpret()
    with pytest.raises(FrozenInstanceError):
        result.confidence = 0.2


def test_repository_protocol_and_storage():
    repository = InMemoryPresenceEventInterpretationRepository()
    engine = PresenceEventInterpretationEngine(repository=repository)
    result = engine.interpret(interpretation_request(), now=NOW)
    assert repository.get(result.interpretation_id) is result
    assert repository.list_all() == (result,)


def test_repository_rejects_duplicate_identity():
    repository = InMemoryPresenceEventInterpretationRepository()
    result = PresenceEventInterpretationEngine(repository=repository).interpret(
        interpretation_request(), now=NOW
    )
    with pytest.raises(ValueError):
        repository.add(result)


def test_identity_is_deterministic_for_same_payload():
    request = interpretation_request()
    first = PresenceEventInterpretationEngine().interpret(request, now=NOW)
    second = PresenceEventInterpretationEngine().interpret(request, now=NOW)
    assert first.interpretation_id == second.interpretation_id


def test_tampered_identity_is_rejected():
    result = interpret()
    with pytest.raises(ValueError):
        replace(result, interpretation_id="tampered")


def test_result_rationale_cannot_be_empty():
    result = interpret()
    with pytest.raises(ValueError):
        replace(result, rationale=(), interpretation_id="")


def test_result_timestamp_must_be_timezone_aware():
    result = interpret()
    with pytest.raises(ValueError):
        replace(
            result,
            created_at=result.created_at.replace(tzinfo=None),
            interpretation_id="",
        )


def test_interpreted_result_requires_source():
    result = interpret(
        detection(states=(PresenceState.UNOCCUPIED, PresenceState.OCCUPIED))
    )
    with pytest.raises(ValueError):
        replace(result, source_detection=None, interpretation_id="")


def test_no_event_cannot_expose_meaning():
    result = interpret()
    with pytest.raises(ValueError):
        replace(
            result,
            meaning=PresenceEventMeaning.PRESENCE_BECAME_OBSERVED,
            interpretation_id="",
        )


def test_inactive_result_cannot_expose_confidence():
    result = interpret(interpretation_declared=False)
    with pytest.raises(ValueError):
        replace(result, confidence=0.5, interpretation_id="")


def test_exact_m138_source_is_preserved():
    source = detection(states=(PresenceState.UNOCCUPIED, PresenceState.OCCUPIED))
    result = interpret(source)
    assert result.source_detection is source
    assert result.previous_presence is source.previous_presence
    assert result.current_presence is source.current_presence


def test_m139_does_not_mutate_source_detection():
    source = detection(states=(PresenceState.UNOCCUPIED, PresenceState.OCCUPIED))
    before = source.detection_id
    interpret(source)
    assert source.detection_id == before


def test_semantics_are_architectural_not_personal():
    result = interpret(
        detection(states=(PresenceState.UNOCCUPIED, PresenceState.OCCUPIED))
    )
    assert "person" not in result.meaning.value
    assert "identity" not in result.meaning.value
    assert "activity" not in result.meaning.value


@pytest.mark.parametrize(
    "meaning",
    [item for item in PresenceEventMeaning if item is not PresenceEventMeaning.NONE],
)
def test_meaning_vocabulary_contains_no_action_verbs(meaning):
    forbidden = {"notify", "execute", "open", "close", "call", "send", "track"}
    assert not forbidden.intersection(meaning.value.split("_"))


@pytest.mark.parametrize(
    "kind", [item for item in PresenceChangeKind if item is not PresenceChangeKind.NONE]
)
def test_every_m138_change_kind_has_exactly_one_semantic_mapping(kind):
    assert (
        PresenceEventInterpretationEngine._meaning(kind)
        is not PresenceEventMeaning.NONE
    )


def test_unknown_change_kind_is_not_silently_interpreted():
    with pytest.raises(KeyError):
        PresenceEventInterpretationEngine._meaning(PresenceChangeKind.NONE)
