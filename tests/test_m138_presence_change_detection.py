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
    InMemoryPresenceChangeDetectionRepository,
    PresenceChangeDetectionAction,
    PresenceChangeDetectionEngine,
    PresenceChangeDetectionPolicy,
    PresenceChangeDetectionRequest,
    PresenceChangeDetectionStatus,
    PresenceChangeKind,
)
from core.presence_continuity import (
    PresenceContinuityEngine,
    PresenceContinuityRequest,
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


def test_continuous_presence_is_suppressed_as_no_change():
    result = detect()
    assert result.status is PresenceChangeDetectionStatus.NO_CHANGE
    assert result.action is PresenceChangeDetectionAction.SUPPRESS
    assert result.change_kind is PresenceChangeKind.NONE
    assert not result.change_detected
    assert not result.change_published


@pytest.mark.parametrize(
    ("states", "kind"),
    [
        (
            (PresenceState.UNOCCUPIED, PresenceState.OCCUPIED),
            PresenceChangeKind.APPEARANCE,
        ),
        (
            (PresenceState.UNOCCUPIED, PresenceState.SINGLE_PRESENCE),
            PresenceChangeKind.APPEARANCE,
        ),
        (
            (PresenceState.OCCUPIED, PresenceState.UNOCCUPIED),
            PresenceChangeKind.DISAPPEARANCE,
        ),
        (
            (PresenceState.MULTIPLE_PRESENCES, PresenceState.UNOCCUPIED),
            PresenceChangeKind.DISAPPEARANCE,
        ),
        (
            (PresenceState.SINGLE_PRESENCE, PresenceState.MULTIPLE_PRESENCES),
            PresenceChangeKind.OCCUPANCY_VARIATION,
        ),
        (
            (PresenceState.OCCUPIED, PresenceState.TRANSIENT),
            PresenceChangeKind.TRANSIENT_VARIATION,
        ),
        (
            (PresenceState.TRANSIENT, PresenceState.OCCUPIED),
            PresenceChangeKind.TRANSIENT_VARIATION,
        ),
        (
            (PresenceState.OCCUPIED, PresenceState.UNKNOWN),
            PresenceChangeKind.UNCERTAIN_VARIATION,
        ),
        (
            (PresenceState.UNKNOWN, PresenceState.OCCUPIED),
            PresenceChangeKind.UNCERTAIN_VARIATION,
        ),
    ],
)
def test_detects_governed_transition_kinds(states, kind):
    source = continuity(states=states)
    result = detect(source)
    assert result.status is PresenceChangeDetectionStatus.DETECTED
    assert result.action is PresenceChangeDetectionAction.PUBLISH
    assert result.change_kind is kind
    assert result.change_detected
    assert result.change_published


def test_detects_continuity_break():
    source = continuity(times=(NOW - timedelta(minutes=40), NOW - timedelta(minutes=5)))
    result = detect(source)
    assert result.change_kind is PresenceChangeKind.CONTINUITY_BREAK
    assert result.continuity_break_detected


@pytest.mark.parametrize("state", list(PresenceState))
def test_same_state_never_becomes_a_change(state):
    result = detect(continuity(states=(state, state)))
    assert result.status is PresenceChangeDetectionStatus.NO_CHANGE


def test_latest_actionable_result_wins():
    old = continuity(
        states=(PresenceState.UNOCCUPIED, PresenceState.OCCUPIED),
        now=NOW - timedelta(minutes=8),
    )
    latest = continuity(
        states=(PresenceState.OCCUPIED, PresenceState.UNOCCUPIED),
        now=NOW - timedelta(minutes=2),
    )
    result = detect(latest, old)
    assert result.source_continuity is latest
    assert result.change_kind is PresenceChangeKind.DISAPPEARANCE


def test_duplicate_results_are_deduplicated():
    source = continuity(states=(PresenceState.UNOCCUPIED, PresenceState.OCCUPIED))
    result = detect(source, source)
    assert result.source_continuity is source


def test_not_declared_is_not_applicable():
    result = detect(detection_declared=False)
    assert result.status is PresenceChangeDetectionStatus.NOT_APPLICABLE
    assert result.action is PresenceChangeDetectionAction.NONE


def test_empty_results_require_review():
    result = PresenceChangeDetectionEngine().detect(
        PresenceChangeDetectionRequest(owner="Carlos", continuity_results=()), now=NOW
    )
    assert result.status is PresenceChangeDetectionStatus.REVIEW_REQUIRED
    assert result.confirmation_required


def test_owner_mismatch_is_blocked():
    result = detect(owner="Other")
    assert result.status is PresenceChangeDetectionStatus.BLOCKED
    assert result.rationale == ("presence_change_owner_mismatch",)


def test_result_limit_is_blocked():
    source = continuity()
    policy = PresenceChangeDetectionPolicy(maximum_results=1)
    result = detect(source, source, policy=policy)
    assert result.status is PresenceChangeDetectionStatus.BLOCKED


def test_stale_result_requires_review():
    source = continuity(now=NOW - timedelta(hours=3))
    result = detect(source)
    assert result.status is PresenceChangeDetectionStatus.REVIEW_REQUIRED


def test_future_result_requires_review():
    source = continuity(now=NOW + timedelta(minutes=1))
    result = detect(source)
    assert result.status is PresenceChangeDetectionStatus.REVIEW_REQUIRED


def test_low_confidence_result_requires_review():
    source = replace(continuity(), confidence=0.4, continuity_id="")
    result = detect(source)
    assert result.status is PresenceChangeDetectionStatus.REVIEW_REQUIRED


def test_context_lineage_mismatch_is_blocked():
    first = continuity(
        states=(PresenceState.UNOCCUPIED, PresenceState.OCCUPIED),
        times=(NOW - timedelta(minutes=14), NOW - timedelta(minutes=10)),
        resolution=resolved_observation(observation_ref="ambient-a"),
        now=NOW - timedelta(minutes=8),
    )
    second = continuity(
        states=(PresenceState.OCCUPIED, PresenceState.UNOCCUPIED),
        times=(NOW - timedelta(minutes=6), NOW - timedelta(minutes=4)),
        resolution=resolved_observation(observation_ref="ambient-b"),
        now=NOW - timedelta(minutes=2),
    )
    result = detect(first, second)
    assert result.status is PresenceChangeDetectionStatus.BLOCKED
    assert result.rationale == ("presence_change_context_lineage_mismatch",)


def test_non_actionable_source_requires_review():
    source = continuity()
    source = replace(
        source,
        status="review_required",
        action="confirm",
        transition_kind="none",
        previous_presence=None,
        current_presence=None,
        accepted_samples=(),
        confidence=0.0,
        continuity_established=False,
        transition_recorded=False,
        interruption_detected=False,
        confirmation_required=True,
        continuity_id="",
    )
    result = detect(source)
    assert result.status is PresenceChangeDetectionStatus.REVIEW_REQUIRED


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
def test_forbidden_capabilities_remain_disabled(field):
    result = detect(
        continuity(states=(PresenceState.UNOCCUPIED, PresenceState.OCCUPIED))
    )
    assert getattr(result, field) is False
    with pytest.raises(ValueError, match="cannot authorize"):
        replace(result, **{field: True}, detection_id="")


def test_models_are_immutable():
    result = detect()
    with pytest.raises(FrozenInstanceError):
        result.confidence = 1.0


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"maximum_results": 0}, "limit"),
        ({"maximum_result_age": timedelta(0)}, "age"),
        ({"minimum_confidence": -0.1}, "confidence"),
        ({"minimum_confidence": 1.1}, "confidence"),
    ],
)
def test_policy_validation(changes, message):
    with pytest.raises(ValueError, match=message):
        PresenceChangeDetectionPolicy(**changes)


@pytest.mark.parametrize("owner", ["", " ", "\t"])
def test_request_rejects_blank_owner(owner):
    with pytest.raises(ValueError, match="owner"):
        PresenceChangeDetectionRequest(owner=owner, continuity_results=())


def test_request_normalizes_owner_and_results():
    source = continuity()
    result = PresenceChangeDetectionRequest(
        owner=" Carlos ", continuity_results=[source]
    )
    assert result.owner == "Carlos"
    assert result.continuity_results == (source,)


def test_detect_rejects_naive_timestamp():
    with pytest.raises(ValueError, match="timezone-aware"):
        PresenceChangeDetectionEngine().detect(
            request(), now=datetime(2026, 7, 11, 23, 0)
        )


def test_result_rejects_naive_timestamp():
    result = detect()
    with pytest.raises(ValueError, match="timezone-aware"):
        replace(result, created_at=datetime(2026, 7, 11), detection_id="")


def test_result_rejects_invalid_confidence():
    result = detect()
    with pytest.raises(ValueError, match="confidence"):
        replace(result, confidence=1.1, detection_id="")


def test_result_requires_rationale():
    result = detect()
    with pytest.raises(ValueError, match="rationale"):
        replace(result, rationale=(), detection_id="")


def test_result_rejects_inconsistent_id():
    result = detect()
    with pytest.raises(ValueError, match="id is inconsistent"):
        replace(result, detection_id="not-valid")


def test_detection_id_is_deterministic():
    source = continuity(states=(PresenceState.UNOCCUPIED, PresenceState.OCCUPIED))
    engine = PresenceChangeDetectionEngine()
    first = engine.detect(request(source), now=NOW)
    second = PresenceChangeDetectionEngine().detect(request(source), now=NOW)
    assert first.detection_id == second.detection_id


def test_detection_id_changes_with_timestamp():
    source = continuity(states=(PresenceState.UNOCCUPIED, PresenceState.OCCUPIED))
    first = detect(source, now=NOW)
    second = detect(source, now=NOW + timedelta(seconds=1))
    assert first.detection_id != second.detection_id


def test_repository_round_trip():
    repository = InMemoryPresenceChangeDetectionRepository()
    engine = PresenceChangeDetectionEngine(repository=repository)
    result = engine.detect(request(), now=NOW)
    assert repository.get(result.detection_id) is result
    assert repository.list_all() == (result,)


def test_repository_rejects_duplicate_result():
    repository = InMemoryPresenceChangeDetectionRepository()
    result = detect()
    repository.add(result)
    with pytest.raises(ValueError, match="already exists"):
        repository.add(result)


def test_repository_returns_none_for_unknown_id():
    assert InMemoryPresenceChangeDetectionRepository().get("missing") is None


def test_custom_repository_is_used():
    repository = InMemoryPresenceChangeDetectionRepository()
    engine = PresenceChangeDetectionEngine(repository=repository)
    assert engine.repository is repository


def test_custom_policy_is_used():
    policy = PresenceChangeDetectionPolicy(minimum_confidence=0.8)
    engine = PresenceChangeDetectionEngine(policy=policy)
    assert engine.policy is policy


def test_result_preserves_exact_m137_source():
    source = continuity(states=(PresenceState.UNOCCUPIED, PresenceState.OCCUPIED))
    result = detect(source)
    assert result.source_continuity is source
    assert result.previous_presence is PresenceState.UNOCCUPIED
    assert result.current_presence is PresenceState.OCCUPIED
    assert result.confidence == source.confidence


def test_detection_does_not_mutate_source():
    source = continuity(states=(PresenceState.UNOCCUPIED, PresenceState.OCCUPIED))
    before = source
    detect(source)
    assert source == before


def test_public_api_exports_expected_symbols():
    from core import presence_change_detection as api

    expected = {
        "InMemoryPresenceChangeDetectionRepository",
        "PresenceChangeDetectionAction",
        "PresenceChangeDetectionEngine",
        "PresenceChangeDetectionPolicy",
        "PresenceChangeDetectionRepository",
        "PresenceChangeDetectionRequest",
        "PresenceChangeDetectionResult",
        "PresenceChangeDetectionStatus",
        "PresenceChangeKind",
    }
    assert expected <= set(api.__all__)


def test_protocol_is_runtime_checkable():
    from core.presence_change_detection import PresenceChangeDetectionRepository

    assert isinstance(
        InMemoryPresenceChangeDetectionRepository(),
        PresenceChangeDetectionRepository,
    )


@pytest.mark.parametrize(
    ("status", "action"),
    [
        (
            PresenceChangeDetectionStatus.DETECTED,
            PresenceChangeDetectionAction.PUBLISH,
        ),
        (
            PresenceChangeDetectionStatus.NO_CHANGE,
            PresenceChangeDetectionAction.SUPPRESS,
        ),
        (
            PresenceChangeDetectionStatus.REVIEW_REQUIRED,
            PresenceChangeDetectionAction.CONFIRM,
        ),
        (
            PresenceChangeDetectionStatus.BLOCKED,
            PresenceChangeDetectionAction.WITHHOLD,
        ),
        (
            PresenceChangeDetectionStatus.NOT_APPLICABLE,
            PresenceChangeDetectionAction.NONE,
        ),
    ],
)
def test_status_and_action_are_string_enums(status, action):
    assert isinstance(status.value, str)
    assert isinstance(action.value, str)


@pytest.mark.parametrize("kind", list(PresenceChangeKind))
def test_change_kinds_are_string_enums(kind):
    assert isinstance(kind.value, str)


def test_result_accepts_string_enums():
    result = detect()
    rebuilt = replace(
        result,
        status=result.status.value,
        action=result.action.value,
        change_kind=result.change_kind.value,
        detection_id="",
    )
    assert rebuilt.status is result.status
    assert rebuilt.action is result.action
    assert rebuilt.change_kind is result.change_kind


def test_detected_result_rejects_none_kind():
    result = detect(
        continuity(states=(PresenceState.UNOCCUPIED, PresenceState.OCCUPIED))
    )
    with pytest.raises(ValueError, match="change kind"):
        replace(result, change_kind=PresenceChangeKind.NONE, detection_id="")


def test_no_change_rejects_detected_flag():
    result = detect()
    with pytest.raises(ValueError, match="flags"):
        replace(result, change_detected=True, detection_id="")


def test_review_requires_confirmation():
    result = PresenceChangeDetectionEngine().detect(
        PresenceChangeDetectionRequest(owner="Carlos", continuity_results=()), now=NOW
    )
    with pytest.raises(ValueError, match="confirmation"):
        replace(result, confirmation_required=False, detection_id="")


def test_continuity_break_flag_only_for_break_kind():
    result = detect(
        continuity(states=(PresenceState.UNOCCUPIED, PresenceState.OCCUPIED))
    )
    with pytest.raises(ValueError, match="continuity-break"):
        replace(result, continuity_break_detected=True, detection_id="")


def test_detection_is_provider_neutral_and_side_effect_free():
    result = detect(
        continuity(states=(PresenceState.UNOCCUPIED, PresenceState.OCCUPIED))
    )
    assert result.sensor_access_allowed is False
    assert result.automation_allowed is False
    assert not hasattr(result, "provider")
    assert not hasattr(result, "execute")
