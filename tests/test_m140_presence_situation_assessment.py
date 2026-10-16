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
    PresenceChangeKind,
)
from core.presence_continuity import (
    PresenceContinuityEngine,
    PresenceContinuityRequest,
)
from core.presence_event_interpretation import (
    PresenceEventInterpretationAction,
    PresenceEventInterpretationEngine,
    PresenceEventInterpretationRequest,
    PresenceEventInterpretationStatus,
    PresenceEventMeaning,
)
from core.presence_situation_assessment import (
    InMemoryPresenceSituationAssessmentRepository,
    PresenceSituationAssessmentAction,
    PresenceSituationAssessmentEngine,
    PresenceSituationAssessmentPolicy,
    PresenceSituationAssessmentRequest,
    PresenceSituationAssessmentStatus,
    PresenceSituationKind,
    PresenceSituationSignal,
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


def test_stable_interpretation_is_suppressed_as_stable_situation():
    result = assess()
    assert result.status is PresenceSituationAssessmentStatus.STABLE
    assert result.action is PresenceSituationAssessmentAction.SUPPRESS
    assert result.situation_kind is PresenceSituationKind.STABLE
    assert result.situation_signal is PresenceSituationSignal.STABLE_PRESENCE
    assert result.situation_assessed
    assert not result.situation_exposed


@pytest.mark.parametrize(
    ("states", "kind", "signal", "meaning"),
    [
        (
            (PresenceState.UNOCCUPIED, PresenceState.OCCUPIED),
            PresenceSituationKind.TRANSITION,
            PresenceSituationSignal.PRESENCE_APPEARED,
            PresenceEventMeaning.PRESENCE_BECAME_OBSERVED,
        ),
        (
            (PresenceState.UNOCCUPIED, PresenceState.SINGLE_PRESENCE),
            PresenceSituationKind.TRANSITION,
            PresenceSituationSignal.PRESENCE_APPEARED,
            PresenceEventMeaning.PRESENCE_BECAME_OBSERVED,
        ),
        (
            (PresenceState.OCCUPIED, PresenceState.UNOCCUPIED),
            PresenceSituationKind.TRANSITION,
            PresenceSituationSignal.PRESENCE_DISAPPEARED,
            PresenceEventMeaning.PRESENCE_BECAME_UNOBSERVED,
        ),
        (
            (PresenceState.MULTIPLE_PRESENCES, PresenceState.UNOCCUPIED),
            PresenceSituationKind.TRANSITION,
            PresenceSituationSignal.PRESENCE_DISAPPEARED,
            PresenceEventMeaning.PRESENCE_BECAME_UNOBSERVED,
        ),
        (
            (PresenceState.SINGLE_PRESENCE, PresenceState.MULTIPLE_PRESENCES),
            PresenceSituationKind.TRANSITION,
            PresenceSituationSignal.OCCUPANCY_CHANGED,
            PresenceEventMeaning.AMBIENT_OCCUPANCY_SHIFTED,
        ),
        (
            (PresenceState.MULTIPLE_PRESENCES, PresenceState.SINGLE_PRESENCE),
            PresenceSituationKind.TRANSITION,
            PresenceSituationSignal.OCCUPANCY_CHANGED,
            PresenceEventMeaning.AMBIENT_OCCUPANCY_SHIFTED,
        ),
        (
            (PresenceState.OCCUPIED, PresenceState.TRANSIENT),
            PresenceSituationKind.TRANSITION,
            PresenceSituationSignal.TRANSIENT_CHANGE,
            PresenceEventMeaning.TRANSIENT_PRESENCE_SIGNAL,
        ),
        (
            (PresenceState.TRANSIENT, PresenceState.OCCUPIED),
            PresenceSituationKind.TRANSITION,
            PresenceSituationSignal.TRANSIENT_CHANGE,
            PresenceEventMeaning.TRANSIENT_PRESENCE_SIGNAL,
        ),
        (
            (PresenceState.OCCUPIED, PresenceState.UNKNOWN),
            PresenceSituationKind.UNCERTAIN,
            PresenceSituationSignal.CERTAINTY_CHANGED,
            PresenceEventMeaning.PRESENCE_CERTAINTY_CHANGED,
        ),
        (
            (PresenceState.UNKNOWN, PresenceState.OCCUPIED),
            PresenceSituationKind.UNCERTAIN,
            PresenceSituationSignal.CERTAINTY_CHANGED,
            PresenceEventMeaning.PRESENCE_CERTAINTY_CHANGED,
        ),
    ],
)
def test_assesses_interpreted_event(states, kind, signal, meaning):
    source = interpret(detection(states=states), now=NOW - timedelta(minutes=1))
    result = assess(source)
    assert result.status is PresenceSituationAssessmentStatus.ASSESSED
    assert result.action is PresenceSituationAssessmentAction.EXPOSE
    assert result.situation_kind is kind
    assert result.situation_signal is signal
    assert result.source_meaning is meaning
    assert result.source_interpretation is source
    assert result.situation_assessed and result.situation_exposed


def test_continuity_loss_is_assessed_as_interrupted():
    source = interpret(
        detection(times=(NOW - timedelta(minutes=40), NOW - timedelta(minutes=5))),
        now=NOW - timedelta(minutes=1),
    )
    result = assess(source)
    assert result.situation_kind is PresenceSituationKind.INTERRUPTED
    assert result.situation_signal is PresenceSituationSignal.CONTINUITY_INTERRUPTED


@pytest.mark.parametrize("state", list(PresenceState))
def test_all_stable_presence_states_remain_stable(state):
    source = interpret(detection(states=(state, state)), now=NOW - timedelta(minutes=1))
    result = assess(source)
    assert result.status is PresenceSituationAssessmentStatus.STABLE
    assert result.previous_presence is state
    assert result.current_presence is state


def test_latest_actionable_interpretation_wins():
    old = interpret(
        detection(
            states=(PresenceState.UNOCCUPIED, PresenceState.OCCUPIED),
            now=NOW - timedelta(minutes=8),
        ),
        now=NOW - timedelta(minutes=7),
    )
    latest = interpret(
        detection(
            states=(PresenceState.OCCUPIED, PresenceState.UNKNOWN),
            now=NOW - timedelta(minutes=3),
        ),
        now=NOW - timedelta(minutes=2),
    )
    result = assess(latest, old)
    assert result.source_interpretation is latest
    assert result.situation_kind is PresenceSituationKind.UNCERTAIN


def test_duplicate_interpretations_are_deduplicated():
    source = interpret(
        detection(states=(PresenceState.UNOCCUPIED, PresenceState.OCCUPIED)),
        now=NOW - timedelta(minutes=1),
    )
    assert assess(source, source).source_interpretation is source


def test_not_declared_is_not_applicable():
    result = assess(assessment_declared=False)
    assert result.status is PresenceSituationAssessmentStatus.NOT_APPLICABLE
    assert result.action is PresenceSituationAssessmentAction.NONE


def test_empty_results_require_review():
    result = PresenceSituationAssessmentEngine().assess(
        PresenceSituationAssessmentRequest(owner="Carlos", interpretation_results=()),
        now=NOW,
    )
    assert result.status is PresenceSituationAssessmentStatus.REVIEW_REQUIRED
    assert result.confirmation_required


def test_owner_mismatch_is_blocked():
    result = assess(owner="Other")
    assert result.status is PresenceSituationAssessmentStatus.BLOCKED
    assert result.rationale == ("presence_situation_owner_mismatch",)


def test_result_limit_is_blocked():
    source = interpret(now=NOW - timedelta(minutes=1))
    result = assess(
        source, source, policy=PresenceSituationAssessmentPolicy(maximum_results=1)
    )
    assert result.status is PresenceSituationAssessmentStatus.BLOCKED


def test_stale_result_requires_review():
    source = interpret(now=NOW - timedelta(hours=3))
    assert assess(source).status is PresenceSituationAssessmentStatus.REVIEW_REQUIRED


def test_future_result_requires_review():
    source = interpret(now=NOW + timedelta(minutes=1))
    assert assess(source).status is PresenceSituationAssessmentStatus.REVIEW_REQUIRED


def test_low_confidence_result_requires_review():
    source = interpret(now=NOW - timedelta(minutes=1))
    weak = replace(source, confidence=0.69, interpretation_id="")
    assert assess(weak).status is PresenceSituationAssessmentStatus.REVIEW_REQUIRED


def test_context_lineage_mismatch_is_blocked():
    first = interpret(
        detection(
            states=(PresenceState.UNOCCUPIED, PresenceState.OCCUPIED),
            resolution=resolved_observation(
                observation_ref="a", now=NOW - timedelta(minutes=10)
            ),
            now=NOW - timedelta(minutes=3),
        ),
        now=NOW - timedelta(minutes=2),
    )
    second = interpret(
        detection(
            states=(PresenceState.OCCUPIED, PresenceState.UNOCCUPIED),
            resolution=resolved_observation(
                observation_ref="b", now=NOW - timedelta(minutes=9)
            ),
            now=NOW - timedelta(minutes=2),
        ),
        now=NOW - timedelta(minutes=1),
    )
    result = assess(first, second)
    assert result.status is PresenceSituationAssessmentStatus.BLOCKED
    assert result.rationale == ("presence_situation_context_lineage_mismatch",)


@pytest.mark.parametrize(
    "status",
    [
        PresenceEventInterpretationStatus.REVIEW_REQUIRED,
        PresenceEventInterpretationStatus.BLOCKED,
        PresenceEventInterpretationStatus.NOT_APPLICABLE,
    ],
)
def test_inactive_interpretation_is_not_assessed(status):
    source = interpret(now=NOW - timedelta(minutes=1))
    inactive = replace(
        source,
        status=status,
        action=(
            PresenceEventInterpretationAction.CONFIRM
            if status is PresenceEventInterpretationStatus.REVIEW_REQUIRED
            else PresenceEventInterpretationAction.WITHHOLD
            if status is PresenceEventInterpretationStatus.BLOCKED
            else PresenceEventInterpretationAction.NONE
        ),
        meaning=PresenceEventMeaning.NONE,
        source_detection=None,
        source_change_kind=PresenceChangeKind.NONE,
        previous_presence=None,
        current_presence=None,
        confidence=0.0,
        event_interpreted=False,
        event_exposed=False,
        confirmation_required=status
        is PresenceEventInterpretationStatus.REVIEW_REQUIRED,
        rationale=("inactive",),
        interpretation_id="",
    )
    assert assess(inactive).status is PresenceSituationAssessmentStatus.REVIEW_REQUIRED


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
        "sensor_access_allowed",
        "automation_allowed",
    ],
)
def test_forbidden_capabilities_remain_false(field):
    result = assess(
        interpret(
            detection(states=(PresenceState.UNOCCUPIED, PresenceState.OCCUPIED)),
            now=NOW - timedelta(minutes=1),
        )
    )
    assert getattr(result, field) is False
    with pytest.raises(ValueError):
        replace(result, **{field: True}, assessment_id="")


def test_request_normalizes_owner_and_tuple():
    source = interpret(now=NOW - timedelta(minutes=1))
    request = PresenceSituationAssessmentRequest(
        owner="  Carlos  ", interpretation_results=[source]
    )
    assert request.owner == "Carlos"
    assert request.interpretation_results == (source,)


def test_blank_owner_is_rejected():
    with pytest.raises(ValueError):
        PresenceSituationAssessmentRequest(owner=" ", interpretation_results=())


@pytest.mark.parametrize(
    "values",
    [
        {"maximum_results": 0},
        {"maximum_result_age": timedelta(0)},
        {"minimum_confidence": -0.1},
        {"minimum_confidence": 1.1},
    ],
)
def test_invalid_policy_is_rejected(values):
    with pytest.raises(ValueError):
        PresenceSituationAssessmentPolicy(**values)


def test_naive_timestamp_is_rejected():
    with pytest.raises(ValueError):
        assess(now=datetime(2026, 7, 11, 23, 0))


def test_result_is_immutable():
    result = assess()
    with pytest.raises(FrozenInstanceError):
        result.confidence = 0.1


def test_repository_round_trip_and_duplicate_guard():
    repository = InMemoryPresenceSituationAssessmentRepository()
    engine = PresenceSituationAssessmentEngine(repository=repository)
    result = engine.assess(situation_request(), now=NOW)
    assert repository.get(result.assessment_id) is result
    assert repository.list_all() == (result,)
    with pytest.raises(ValueError):
        repository.add(result)


def test_assessment_id_is_deterministic_for_equal_result():
    result = assess()
    clone = replace(result, assessment_id="")
    assert clone.assessment_id == result.assessment_id


def test_inconsistent_assessment_id_is_rejected():
    with pytest.raises(ValueError):
        replace(assess(), assessment_id="wrong")


@pytest.mark.parametrize(
    "field,value",
    [
        ("confidence", -0.1),
        ("confidence", 1.1),
        ("rationale", ()),
    ],
)
def test_invalid_result_values_are_rejected(field, value):
    with pytest.raises(ValueError):
        replace(assess(), **{field: value}, assessment_id="")


def test_source_states_and_confidence_are_preserved_exactly():
    source = interpret(
        detection(states=(PresenceState.UNOCCUPIED, PresenceState.OCCUPIED)),
        now=NOW - timedelta(minutes=1),
    )
    result = assess(source)
    assert result.previous_presence is source.previous_presence
    assert result.current_presence is source.current_presence
    assert result.confidence == source.confidence


def test_assessment_does_not_mutate_source_interpretation():
    source = interpret(
        detection(states=(PresenceState.UNOCCUPIED, PresenceState.OCCUPIED)),
        now=NOW - timedelta(minutes=1),
    )
    source_id = source.interpretation_id
    assess(source)
    assert source.interpretation_id == source_id


def test_repository_protocol_is_runtime_checkable():
    repository = InMemoryPresenceSituationAssessmentRepository()
    from core.presence_situation_assessment import PresenceSituationAssessmentRepository

    assert isinstance(repository, PresenceSituationAssessmentRepository)
