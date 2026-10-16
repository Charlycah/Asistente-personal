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
    AmbientObservationResolutionRequest,
    AmbientRepresentationKind,
)
from core.presence_understanding import (
    InMemoryPresenceUnderstandingRepository,
    PresenceEvidence,
    PresenceState,
    PresenceUnderstandingAction,
    PresenceUnderstandingEngine,
    PresenceUnderstandingPolicy,
    PresenceUnderstandingRequest,
    PresenceUnderstandingResult,
    PresenceUnderstandingStatus,
)

NOW = datetime(2026, 7, 11, 22, 0, tzinfo=timezone.utc)


def resolved_observation(
    *, purpose=AmbientObservationPurpose.PRESENCE_CONTEXT, **changes
):
    context = AmbientContextFoundationEngine().establish(
        AmbientContextFoundationRequest(
            owner="Carlos",
            observation=AmbientObservationSignal(
                observation_ref="ambient-001",
                source=AmbientObservationSource.HOME_SYSTEM,
                scope=AmbientScope.ROOM,
                privacy_level=AmbientPrivacyLevel.PERSONAL,
                confidence=0.95,
                observed_at=NOW,
                source_device_id="home-main",
            ),
            explicit_user_consent=True,
        ),
        now=NOW,
    )
    values = dict(
        owner="Carlos",
        ambient_context=context,
        purpose=purpose,
        candidates=(
            AmbientObservationCandidate(
                candidate_ref="snapshot-001",
                observation_ref="ambient-001",
                representation_kind=AmbientRepresentationKind.SNAPSHOT,
                confidence=0.94,
                declared_purposes=(purpose,),
            ),
        ),
    )
    values.update(changes)
    return AmbientObservationResolutionEngine().resolve(
        AmbientObservationResolutionRequest(**values), now=NOW
    )


def evidence(**changes):
    values = dict(
        evidence_ref="presence-001",
        observation_ref="ambient-001",
        presence_state=PresenceState.OCCUPIED,
        confidence=0.92,
        attributes=("stable", "room-level"),
    )
    values.update(changes)
    return PresenceEvidence(**values)


def request(**changes):
    values = dict(
        owner="Carlos",
        resolved_observation=resolved_observation(),
        evidence=(evidence(),),
    )
    values.update(changes)
    return PresenceUnderstandingRequest(**values)


def understand(*, policy=None, **changes):
    return PresenceUnderstandingEngine(policy=policy).understand(
        request(**changes), now=NOW
    )


def test_understands_declared_presence():
    result = understand()
    assert result.status is PresenceUnderstandingStatus.UNDERSTOOD
    assert result.action is PresenceUnderstandingAction.CONSOLIDATE
    assert result.dominant_presence is PresenceState.OCCUPIED
    assert result.presence_understood


@pytest.mark.parametrize("state", list(PresenceState))
def test_supports_each_presence_state(state):
    result = understand(evidence=(evidence(presence_state=state),))
    assert result.dominant_presence is state


def test_preserves_normalized_attributes():
    result = understand()
    assert result.attributes == ("room-level", "stable")


def test_owner_mismatch_is_blocked():
    result = understand(owner="Other")
    assert result.status is PresenceUnderstandingStatus.BLOCKED
    assert result.rationale == ("presence_understanding_owner_mismatch",)


def test_undeclared_understanding_is_not_applicable():
    result = understand(understanding_declared=False)
    assert result.status is PresenceUnderstandingStatus.NOT_APPLICABLE
    assert result.action is PresenceUnderstandingAction.NONE


def test_non_presence_purpose_is_not_applicable():
    result = understand(
        resolved_observation=resolved_observation(
            purpose=AmbientObservationPurpose.ACTIVITY_CONTEXT
        )
    )
    assert result.status is PresenceUnderstandingStatus.NOT_APPLICABLE
    assert result.rationale == ("presence_understanding_not_required",)


def test_unresolved_observation_requires_review():
    resolution = resolved_observation()
    altered = replace(
        resolution,
        status="review_required",
        action="confirm",
        selected_candidate=None,
        observation_resolved=False,
        presence_understanding_required=False,
        rationale=("manual_review",),
        resolution_id="",
    )
    result = understand(resolved_observation=altered)
    assert result.status is PresenceUnderstandingStatus.REVIEW_REQUIRED


def test_wrong_observation_lineage_is_ignored():
    result = understand(evidence=(evidence(observation_ref="other"),))
    assert result.status is PresenceUnderstandingStatus.REVIEW_REQUIRED


def test_low_confidence_evidence_is_ignored():
    result = understand(evidence=(evidence(confidence=0.69),))
    assert result.status is PresenceUnderstandingStatus.REVIEW_REQUIRED


def test_confidence_threshold_is_inclusive():
    result = understand(evidence=(evidence(confidence=0.7),))
    assert result.status is PresenceUnderstandingStatus.UNDERSTOOD


def test_external_evidence_is_rejected_by_default():
    result = understand(evidence=(evidence(externally_supplied=True),))
    assert result.status is PresenceUnderstandingStatus.REVIEW_REQUIRED


def test_policy_can_allow_external_evidence():
    policy = PresenceUnderstandingPolicy(allow_external_evidence=True)
    result = understand(policy=policy, evidence=(evidence(externally_supplied=True),))
    assert result.status is PresenceUnderstandingStatus.UNDERSTOOD


def test_evidence_limit_is_blocked():
    policy = PresenceUnderstandingPolicy(maximum_evidence_items=1)
    result = understand(
        policy=policy,
        evidence=(evidence(evidence_ref="a"), evidence(evidence_ref="b")),
    )
    assert result.status is PresenceUnderstandingStatus.BLOCKED


def test_long_reference_is_filtered():
    policy = PresenceUnderstandingPolicy(maximum_reference_length=3)
    result = understand(policy=policy, evidence=(evidence(evidence_ref="long"),))
    assert result.status is PresenceUnderstandingStatus.REVIEW_REQUIRED


def test_highest_confidence_presence_wins():
    result = understand(
        evidence=(
            evidence(
                evidence_ref="empty",
                presence_state=PresenceState.UNOCCUPIED,
                confidence=0.8,
            ),
            evidence(
                evidence_ref="occupied",
                presence_state=PresenceState.OCCUPIED,
                confidence=0.95,
            ),
        )
    )
    assert result.dominant_presence is PresenceState.OCCUPIED


def test_close_competing_states_require_review():
    result = understand(
        evidence=(
            evidence(
                evidence_ref="a",
                presence_state=PresenceState.OCCUPIED,
                confidence=0.9,
            ),
            evidence(
                evidence_ref="b",
                presence_state=PresenceState.UNOCCUPIED,
                confidence=0.86,
            ),
        )
    )
    assert result.status is PresenceUnderstandingStatus.REVIEW_REQUIRED
    assert result.rationale == ("presence_evidence_conflict",)


def test_policy_controls_ambiguity_margin():
    policy = PresenceUnderstandingPolicy(ambiguity_margin=0.01)
    result = understand(
        policy=policy,
        evidence=(
            evidence(
                evidence_ref="a",
                presence_state=PresenceState.OCCUPIED,
                confidence=0.9,
            ),
            evidence(
                evidence_ref="b",
                presence_state=PresenceState.UNOCCUPIED,
                confidence=0.86,
            ),
        ),
    )
    assert result.status is PresenceUnderstandingStatus.UNDERSTOOD


def test_same_state_evidence_is_consolidated():
    result = understand(
        evidence=(
            evidence(evidence_ref="a", attributes=("stable",)),
            evidence(evidence_ref="b", confidence=0.85, attributes=("recent",)),
        )
    )
    assert len(result.accepted_evidence) == 2
    assert result.attributes == ("recent", "stable")


def test_duplicate_reference_keeps_highest_confidence_deterministically():
    low = evidence(
        evidence_ref="same",
        confidence=0.8,
        presence_state=PresenceState.UNOCCUPIED,
    )
    high = evidence(
        evidence_ref="same",
        confidence=0.95,
        presence_state=PresenceState.OCCUPIED,
    )
    result = understand(evidence=(low, high))
    assert result.dominant_presence is PresenceState.OCCUPIED
    assert result.accepted_evidence == (high,)


def test_attribute_limit_is_enforced():
    policy = PresenceUnderstandingPolicy(maximum_attributes=2)
    result = understand(policy=policy, evidence=(evidence(attributes=("c", "a", "b")),))
    assert result.attributes == ("a", "b")


def test_attributes_are_casefolded_and_deduplicated():
    item = evidence(attributes=("Stable", "stable", "Room"))
    assert item.attributes == ("stable", "room")


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("evidence_ref", " ", "presence evidence references"),
        ("observation_ref", " ", "presence evidence references"),
        ("confidence", -0.1, "presence evidence confidence"),
        ("confidence", 1.1, "presence evidence confidence"),
        ("attributes", ("",), "presence evidence attributes"),
    ],
)
def test_evidence_validation(field, value, message):
    with pytest.raises(ValueError, match=message):
        evidence(**{field: value})


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"minimum_evidence_confidence": -0.1}, "presence confidence threshold"),
        ({"minimum_evidence_confidence": 1.1}, "presence confidence threshold"),
        ({"ambiguity_margin": -0.1}, "presence ambiguity margin"),
        ({"ambiguity_margin": 1.1}, "presence ambiguity margin"),
        ({"maximum_evidence_items": 0}, "presence evidence limit"),
        ({"maximum_reference_length": 0}, "presence reference limit"),
        ({"maximum_attributes": 0}, "presence attribute limit"),
    ],
)
def test_policy_validation(changes, message):
    with pytest.raises(ValueError, match=message):
        PresenceUnderstandingPolicy(**changes)


def test_request_owner_must_not_be_blank():
    with pytest.raises(ValueError, match="presence understanding owner"):
        request(owner=" ")


def test_result_is_immutable():
    result = understand()
    with pytest.raises(FrozenInstanceError):
        result.confidence = 0.1


def test_repository_contract_and_duplicate_protection():
    repository = InMemoryPresenceUnderstandingRepository()
    engine = PresenceUnderstandingEngine(repository=repository)
    result = engine.understand(request(), now=NOW)
    assert repository.get(result.understanding_id) is result
    assert repository.list_all() == (result,)
    with pytest.raises(ValueError, match="already exists"):
        repository.add(result)


def test_identity_is_deterministic_for_same_input_and_timestamp():
    first = understand()
    second = understand()
    assert first.understanding_id == second.understanding_id


def test_identity_changes_with_semantic_input():
    first = understand()
    second = understand(evidence=(evidence(confidence=0.91),))
    assert first.understanding_id != second.understanding_id


def test_naive_timestamp_is_rejected():
    with pytest.raises(ValueError, match="timezone-aware"):
        PresenceUnderstandingEngine().understand(
            request(), now=datetime(2026, 7, 11, 22, 0)
        )


def test_non_understood_result_cannot_expose_presence():
    with pytest.raises(ValueError, match="non-understood presence"):
        PresenceUnderstandingResult(
            request=request(),
            status=PresenceUnderstandingStatus.REVIEW_REQUIRED,
            action=PresenceUnderstandingAction.CONFIRM,
            dominant_presence=PresenceState.OCCUPIED,
            accepted_evidence=(),
            attributes=(),
            confidence=0.0,
            presence_understood=False,
            confirmation_required=True,
            identity_inference_allowed=False,
            biometric_analysis_allowed=False,
            precise_person_counting_allowed=False,
            activity_inference_allowed=False,
            movement_tracking_allowed=False,
            sensor_access_allowed=False,
            automation_allowed=False,
            rationale=("manual_review",),
            created_at=NOW,
        )


@pytest.mark.parametrize(
    "field",
    [
        "identity_inference_allowed",
        "biometric_analysis_allowed",
        "precise_person_counting_allowed",
        "activity_inference_allowed",
        "movement_tracking_allowed",
        "sensor_access_allowed",
        "automation_allowed",
    ],
)
def test_forbidden_capabilities_are_rejected(field):
    values = dict(
        request=request(),
        status=PresenceUnderstandingStatus.UNDERSTOOD,
        action=PresenceUnderstandingAction.CONSOLIDATE,
        dominant_presence=PresenceState.OCCUPIED,
        accepted_evidence=(evidence(),),
        attributes=(),
        confidence=0.9,
        presence_understood=True,
        confirmation_required=False,
        identity_inference_allowed=False,
        biometric_analysis_allowed=False,
        precise_person_counting_allowed=False,
        activity_inference_allowed=False,
        movement_tracking_allowed=False,
        sensor_access_allowed=False,
        automation_allowed=False,
        rationale=("presence_understood",),
        created_at=NOW,
    )
    values[field] = True
    with pytest.raises(ValueError, match="cannot authorize"):
        PresenceUnderstandingResult(**values)


def test_engine_never_exposes_forbidden_capabilities():
    result = understand()
    assert not result.identity_inference_allowed
    assert not result.biometric_analysis_allowed
    assert not result.precise_person_counting_allowed
    assert not result.activity_inference_allowed
    assert not result.movement_tracking_allowed
    assert not result.sensor_access_allowed
    assert not result.automation_allowed
