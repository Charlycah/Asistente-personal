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
from core.presence_continuity import (
    InMemoryPresenceContinuityRepository,
    PresenceContinuityAction,
    PresenceContinuityEngine,
    PresenceContinuityPolicy,
    PresenceContinuityRequest,
    PresenceContinuityStatus,
    PresenceTransitionKind,
)
from core.presence_understanding import (
    PresenceEvidence,
    PresenceState,
    PresenceUnderstandingEngine,
    PresenceUnderstandingRequest,
)

NOW = datetime(2026, 7, 11, 22, 0, tzinfo=timezone.utc)


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


def sample(
    resolution,
    *,
    state=PresenceState.OCCUPIED,
    confidence=0.92,
    created_at=NOW - timedelta(minutes=5),
    evidence_ref=None,
):
    evidence_ref = evidence_ref or f"evidence-{state.value}-{created_at.timestamp()}"
    return PresenceUnderstandingEngine().understand(
        PresenceUnderstandingRequest(
            owner=resolution.request.owner,
            resolved_observation=resolution,
            evidence=(
                PresenceEvidence(
                    evidence_ref=evidence_ref,
                    observation_ref=resolution.selected_candidate.observation_ref,
                    presence_state=state,
                    confidence=confidence,
                ),
            ),
        ),
        now=created_at,
    )


def request(*, states=(PresenceState.OCCUPIED, PresenceState.OCCUPIED), **changes):
    resolution = changes.pop("resolution", resolved_observation())
    times = changes.pop(
        "times", (NOW - timedelta(minutes=10), NOW - timedelta(minutes=5))
    )
    samples = tuple(
        sample(
            resolution, state=state, created_at=created_at, evidence_ref=f"e-{index}"
        )
        for index, (state, created_at) in enumerate(zip(states, times, strict=True))
    )
    values = {"owner": "Carlos", "samples": samples}
    values.update(changes)
    return PresenceContinuityRequest(**values)


def evaluate(*, policy=None, now=NOW, **changes):
    return PresenceContinuityEngine(policy=policy).evaluate(request(**changes), now=now)


def test_establishes_continuity_for_same_state():
    result = evaluate()
    assert result.status is PresenceContinuityStatus.CONTINUOUS
    assert result.action is PresenceContinuityAction.PRESERVE
    assert result.transition_kind is PresenceTransitionKind.NONE
    assert result.continuity_established


@pytest.mark.parametrize("state", list(PresenceState))
def test_supports_continuity_for_each_presence_state(state):
    result = evaluate(states=(state, state))
    assert result.previous_presence is state
    assert result.current_presence is state


@pytest.mark.parametrize(
    ("previous", "current", "kind"),
    [
        (
            PresenceState.UNOCCUPIED,
            PresenceState.OCCUPIED,
            PresenceTransitionKind.ARRIVAL,
        ),
        (
            PresenceState.UNOCCUPIED,
            PresenceState.SINGLE_PRESENCE,
            PresenceTransitionKind.ARRIVAL,
        ),
        (
            PresenceState.OCCUPIED,
            PresenceState.UNOCCUPIED,
            PresenceTransitionKind.DEPARTURE,
        ),
        (
            PresenceState.MULTIPLE_PRESENCES,
            PresenceState.UNOCCUPIED,
            PresenceTransitionKind.DEPARTURE,
        ),
        (
            PresenceState.SINGLE_PRESENCE,
            PresenceState.MULTIPLE_PRESENCES,
            PresenceTransitionKind.OCCUPANCY_CHANGE,
        ),
        (
            PresenceState.OCCUPIED,
            PresenceState.TRANSIENT,
            PresenceTransitionKind.TRANSIENT_CHANGE,
        ),
        (
            PresenceState.TRANSIENT,
            PresenceState.OCCUPIED,
            PresenceTransitionKind.TRANSIENT_CHANGE,
        ),
        (
            PresenceState.OCCUPIED,
            PresenceState.UNKNOWN,
            PresenceTransitionKind.UNCERTAIN_CHANGE,
        ),
        (
            PresenceState.UNKNOWN,
            PresenceState.OCCUPIED,
            PresenceTransitionKind.UNCERTAIN_CHANGE,
        ),
    ],
)
def test_classifies_transitions(previous, current, kind):
    result = evaluate(states=(previous, current))
    assert result.status is PresenceContinuityStatus.TRANSITION
    assert result.action is PresenceContinuityAction.RECORD_TRANSITION
    assert result.transition_kind is kind
    assert result.transition_recorded


def test_gap_interrupts_continuity():
    result = evaluate(times=(NOW - timedelta(minutes=40), NOW - timedelta(minutes=5)))
    assert result.status is PresenceContinuityStatus.INTERRUPTED
    assert result.action is PresenceContinuityAction.CLOSE
    assert result.interruption_detected


def test_gap_threshold_is_inclusive():
    policy = PresenceContinuityPolicy(maximum_gap=timedelta(minutes=20))
    result = evaluate(
        policy=policy,
        times=(NOW - timedelta(minutes=25), NOW - timedelta(minutes=5)),
    )
    assert result.status is PresenceContinuityStatus.CONTINUOUS


def test_continuity_not_declared_is_not_applicable():
    result = evaluate(continuity_declared=False)
    assert result.status is PresenceContinuityStatus.NOT_APPLICABLE
    assert result.action is PresenceContinuityAction.NONE


def test_owner_mismatch_is_blocked():
    result = evaluate(owner="Other")
    assert result.status is PresenceContinuityStatus.BLOCKED
    assert result.rationale == ("presence_continuity_owner_mismatch",)


def test_sample_limit_is_blocked():
    policy = PresenceContinuityPolicy(maximum_samples=2)
    resolution = resolved_observation()
    samples = tuple(
        sample(
            resolution,
            created_at=NOW - timedelta(minutes=minutes),
            evidence_ref=f"e-{minutes}",
        )
        for minutes in (15, 10, 5)
    )
    result = PresenceContinuityEngine(policy=policy).evaluate(
        PresenceContinuityRequest(owner="Carlos", samples=samples), now=NOW
    )
    assert result.status is PresenceContinuityStatus.BLOCKED


def test_single_sample_requires_review():
    resolution = resolved_observation()
    only = sample(resolution)
    result = PresenceContinuityEngine().evaluate(
        PresenceContinuityRequest(owner="Carlos", samples=(only,)), now=NOW
    )
    assert result.status is PresenceContinuityStatus.REVIEW_REQUIRED
    assert result.confirmation_required


def test_empty_samples_require_review():
    result = PresenceContinuityEngine().evaluate(
        PresenceContinuityRequest(owner="Carlos", samples=()), now=NOW
    )
    assert result.status is PresenceContinuityStatus.REVIEW_REQUIRED


def test_stale_samples_are_ignored():
    result = evaluate(times=(NOW - timedelta(hours=3), NOW - timedelta(minutes=5)))
    assert result.status is PresenceContinuityStatus.REVIEW_REQUIRED


def test_future_samples_are_ignored():
    result = evaluate(times=(NOW - timedelta(minutes=5), NOW + timedelta(minutes=1)))
    assert result.status is PresenceContinuityStatus.REVIEW_REQUIRED


def test_low_confidence_samples_are_ignored():
    resolution = resolved_observation()
    samples = (
        sample(
            resolution,
            confidence=0.69,
            created_at=NOW - timedelta(minutes=10),
            evidence_ref="a",
        ),
        sample(
            resolution,
            confidence=0.92,
            created_at=NOW - timedelta(minutes=5),
            evidence_ref="b",
        ),
    )
    result = PresenceContinuityEngine().evaluate(
        PresenceContinuityRequest(owner="Carlos", samples=samples), now=NOW
    )
    assert result.status is PresenceContinuityStatus.REVIEW_REQUIRED


def test_confidence_threshold_is_inclusive():
    resolution = resolved_observation()
    samples = (
        sample(
            resolution,
            confidence=0.7,
            created_at=NOW - timedelta(minutes=10),
            evidence_ref="a",
        ),
        sample(
            resolution,
            confidence=0.7,
            created_at=NOW - timedelta(minutes=5),
            evidence_ref="b",
        ),
    )
    result = PresenceContinuityEngine().evaluate(
        PresenceContinuityRequest(owner="Carlos", samples=samples), now=NOW
    )
    assert result.status is PresenceContinuityStatus.CONTINUOUS


def test_confidence_uses_weakest_recent_sample():
    resolution = resolved_observation()
    samples = (
        sample(
            resolution,
            confidence=0.84,
            created_at=NOW - timedelta(minutes=10),
            evidence_ref="a",
        ),
        sample(
            resolution,
            confidence=0.91,
            created_at=NOW - timedelta(minutes=5),
            evidence_ref="b",
        ),
    )
    result = PresenceContinuityEngine().evaluate(
        PresenceContinuityRequest(owner="Carlos", samples=samples), now=NOW
    )
    assert result.confidence == 0.84


def test_large_confidence_variation_requires_review():
    policy = PresenceContinuityPolicy(confidence_variation_limit=0.1)
    resolution = resolved_observation()
    samples = (
        sample(
            resolution,
            confidence=0.75,
            created_at=NOW - timedelta(minutes=10),
            evidence_ref="a",
        ),
        sample(
            resolution,
            confidence=0.92,
            created_at=NOW - timedelta(minutes=5),
            evidence_ref="b",
        ),
    )
    result = PresenceContinuityEngine(policy=policy).evaluate(
        PresenceContinuityRequest(owner="Carlos", samples=samples), now=NOW
    )
    assert result.status is PresenceContinuityStatus.REVIEW_REQUIRED
    assert result.rationale == ("presence_continuity_confidence_variation",)


def test_duplicate_samples_are_deduplicated():
    resolution = resolved_observation()
    first = sample(resolution, created_at=NOW - timedelta(minutes=10), evidence_ref="a")
    second = sample(resolution, created_at=NOW - timedelta(minutes=5), evidence_ref="b")
    result = PresenceContinuityEngine().evaluate(
        PresenceContinuityRequest(owner="Carlos", samples=(first, first, second)),
        now=NOW,
    )
    assert result.accepted_samples == (first, second)


def test_samples_are_sorted_chronologically():
    resolution = resolved_observation()
    first = sample(resolution, created_at=NOW - timedelta(minutes=10), evidence_ref="a")
    second = sample(resolution, created_at=NOW - timedelta(minutes=5), evidence_ref="b")
    result = PresenceContinuityEngine().evaluate(
        PresenceContinuityRequest(owner="Carlos", samples=(second, first)), now=NOW
    )
    assert result.accepted_samples == (first, second)


def test_only_two_most_recent_samples_define_transition():
    resolution = resolved_observation()
    samples = (
        sample(
            resolution,
            state=PresenceState.UNOCCUPIED,
            created_at=NOW - timedelta(minutes=15),
            evidence_ref="a",
        ),
        sample(
            resolution,
            state=PresenceState.OCCUPIED,
            created_at=NOW - timedelta(minutes=10),
            evidence_ref="b",
        ),
        sample(
            resolution,
            state=PresenceState.OCCUPIED,
            created_at=NOW - timedelta(minutes=5),
            evidence_ref="c",
        ),
    )
    result = PresenceContinuityEngine().evaluate(
        PresenceContinuityRequest(owner="Carlos", samples=samples), now=NOW
    )
    assert result.status is PresenceContinuityStatus.CONTINUOUS
    assert len(result.accepted_samples) == 3


def test_context_lineage_mismatch_is_blocked():
    first_resolution = resolved_observation(observation_ref="ambient-a")
    second_resolution = resolved_observation(observation_ref="ambient-b")
    samples = (
        sample(
            first_resolution, created_at=NOW - timedelta(minutes=10), evidence_ref="a"
        ),
        sample(
            second_resolution, created_at=NOW - timedelta(minutes=5), evidence_ref="b"
        ),
    )
    result = PresenceContinuityEngine().evaluate(
        PresenceContinuityRequest(owner="Carlos", samples=samples), now=NOW
    )
    assert result.status is PresenceContinuityStatus.BLOCKED
    assert result.rationale == ("presence_continuity_context_lineage_mismatch",)


def test_non_understood_sample_is_ignored():
    resolution = resolved_observation()
    understood = sample(
        resolution, created_at=NOW - timedelta(minutes=5), evidence_ref="a"
    )
    review = replace(
        understood,
        status="review_required",
        action="confirm",
        dominant_presence=None,
        accepted_evidence=(),
        attributes=(),
        confidence=0,
        presence_understood=False,
        confirmation_required=True,
        rationale=("manual_review",),
        understanding_id="",
    )
    result = PresenceContinuityEngine().evaluate(
        PresenceContinuityRequest(owner="Carlos", samples=(review, understood)), now=NOW
    )
    assert result.status is PresenceContinuityStatus.REVIEW_REQUIRED


def test_naive_evaluation_timestamp_is_rejected():
    with pytest.raises(ValueError, match="timezone-aware"):
        PresenceContinuityEngine().evaluate(request(), now=datetime(2026, 7, 11))


def test_request_normalizes_owner_and_samples():
    original = request()
    normalized = PresenceContinuityRequest(
        owner=" Carlos ", samples=list(original.samples)
    )
    assert normalized.owner == "Carlos"
    assert isinstance(normalized.samples, tuple)


def test_blank_owner_is_rejected():
    with pytest.raises(ValueError, match="must not be blank"):
        PresenceContinuityRequest(owner=" ", samples=())


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("maximum_samples", 0, "sample limit"),
        ("maximum_sample_age", timedelta(0), "sample age"),
        ("maximum_gap", timedelta(0), "gap"),
        ("minimum_samples_for_continuity", 1, "at least two"),
        ("minimum_confidence", -0.1, "between zero and one"),
        ("minimum_confidence", 1.1, "between zero and one"),
        ("confidence_variation_limit", -0.1, "between zero and one"),
        ("confidence_variation_limit", 1.1, "between zero and one"),
    ],
)
def test_policy_rejects_invalid_values(field, value, message):
    with pytest.raises(ValueError, match=message):
        PresenceContinuityPolicy(**{field: value})


def test_policy_rejects_minimum_above_maximum():
    with pytest.raises(ValueError, match="exceeds"):
        PresenceContinuityPolicy(maximum_samples=2, minimum_samples_for_continuity=3)


def test_result_is_immutable():
    result = evaluate()
    with pytest.raises(FrozenInstanceError):
        result.confidence = 0.1


def test_repository_round_trip():
    repository = InMemoryPresenceContinuityRepository()
    engine = PresenceContinuityEngine(repository=repository)
    result = engine.evaluate(request(), now=NOW)
    assert repository.get(result.continuity_id) is result
    assert repository.list_all() == (result,)


def test_repository_rejects_duplicate_result():
    repository = InMemoryPresenceContinuityRepository()
    result = PresenceContinuityEngine(repository=repository).evaluate(
        request(), now=NOW
    )
    with pytest.raises(ValueError, match="already exists"):
        repository.add(result)


def test_continuity_id_is_deterministic():
    first = PresenceContinuityEngine().evaluate(request(), now=NOW)
    second = PresenceContinuityEngine().evaluate(request(), now=NOW)
    assert first.continuity_id == second.continuity_id


def test_inconsistent_continuity_id_is_rejected():
    result = evaluate()
    with pytest.raises(ValueError, match="id is inconsistent"):
        replace(result, continuity_id="wrong")


def test_forbidden_capabilities_remain_false():
    result = evaluate()
    assert not result.identity_inference_allowed
    assert not result.biometric_analysis_allowed
    assert not result.precise_person_counting_allowed
    assert not result.activity_inference_allowed
    assert not result.individual_tracking_allowed
    assert not result.movement_tracking_allowed
    assert not result.sensor_access_allowed
    assert not result.automation_allowed


@pytest.mark.parametrize(
    "field",
    [
        "identity_inference_allowed",
        "biometric_analysis_allowed",
        "precise_person_counting_allowed",
        "activity_inference_allowed",
        "individual_tracking_allowed",
        "movement_tracking_allowed",
        "sensor_access_allowed",
        "automation_allowed",
    ],
)
def test_result_rejects_authorized_forbidden_capability(field):
    result = evaluate()
    with pytest.raises(ValueError, match="cannot authorize"):
        replace(result, **{field: True}, continuity_id="")


def test_inactive_result_cannot_expose_presence_state():
    result = evaluate(continuity_declared=False)
    with pytest.raises(ValueError, match="cannot expose presence states"):
        replace(result, previous_presence=PresenceState.OCCUPIED, continuity_id="")


def test_continuous_result_requires_none_transition():
    result = evaluate()
    with pytest.raises(ValueError, match="cannot expose a transition"):
        replace(
            result, transition_kind=PresenceTransitionKind.ARRIVAL, continuity_id=""
        )


def test_transition_result_requires_transition_kind():
    result = evaluate(states=(PresenceState.UNOCCUPIED, PresenceState.OCCUPIED))
    with pytest.raises(ValueError, match="requires a transition kind"):
        replace(result, transition_kind=PresenceTransitionKind.NONE, continuity_id="")


def test_result_rejects_naive_timestamp():
    result = evaluate()
    with pytest.raises(ValueError, match="timezone-aware"):
        replace(result, created_at=datetime(2026, 7, 11), continuity_id="")


def test_result_rejects_empty_rationale():
    result = evaluate()
    with pytest.raises(ValueError, match="must not be empty"):
        replace(result, rationale=(), continuity_id="")


def test_result_rejects_invalid_confidence():
    result = evaluate()
    with pytest.raises(ValueError, match="between zero and one"):
        replace(result, confidence=1.1, continuity_id="")


def test_repository_protocol_is_runtime_checkable():
    repository = InMemoryPresenceContinuityRepository()
    from core.presence_continuity import PresenceContinuityRepository

    assert isinstance(repository, PresenceContinuityRepository)


def test_domain_exposes_no_sensor_or_provider_dependency():
    import core.presence_continuity.engine as engine_module

    source_names = set(engine_module.__dict__)
    assert not {"camera", "microphone", "provider", "sensor", "requests"} & source_names
