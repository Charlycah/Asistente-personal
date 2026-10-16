from dataclasses import FrozenInstanceError, replace
from datetime import timedelta

import pytest

from core.living_conversation_presence_awareness import (
    InMemoryLivingConversationPresenceAwarenessRepository,
    LivingConversationPresenceAwareness,
    LivingConversationPresenceAwarenessAction,
    LivingConversationPresenceAwarenessKind,
    LivingConversationPresenceAwarenessPolicy,
    LivingConversationPresenceAwarenessRequest,
    LivingConversationPresenceAwarenessStatus,
)
from core.living_conversation_presence_consumer import (
    LivingConversationPresenceConsumerStatus,
)
from core.presence_situation_assessment import PresenceSituationKind
from tests.test_m142_presence_context_publication import NOW
from tests.test_m147_living_conversation_presence_consumer import consume


def request(*, results=(), owner="Carlos", **changes):
    if not results:
        results = (consume(),)
    values = {"owner": owner, "consumer_results": results}
    values.update(changes)
    return LivingConversationPresenceAwarenessRequest(**values)


def assess(*, results=(), owner="Carlos", policy=None, now=NOW, **changes):
    return LivingConversationPresenceAwareness(policy=policy).assess(
        request(results=results, owner=owner, **changes), now=now
    )


def consumer_with_kind(kind: PresenceSituationKind):
    result = consume()
    cue = replace(result.cues[0], situation_kind=kind, cue_id="")
    return replace(result, cues=(cue,), consumption_id="")


def test_complete_consumer_result_becomes_awareness():
    result = assess()
    assert result.status is LivingConversationPresenceAwarenessStatus.AWARE
    assert result.action is LivingConversationPresenceAwarenessAction.EXPOSE_AWARENESS
    assert result.presence_awareness_available
    assert not result.partial_context
    assert len(result.states) == 1


def test_partial_consumer_result_becomes_partial_awareness():
    source = consume()
    source = replace(
        source,
        status=LivingConversationPresenceConsumerStatus.ADAPTED_PARTIAL,
        partial_context=True,
        cues=(replace(source.cues[0], partial_context=True, cue_id=""),),
        consumption_id="",
    )
    result = assess(results=(source,))
    assert result.status is LivingConversationPresenceAwarenessStatus.AWARE_PARTIAL
    assert (
        result.action
        is LivingConversationPresenceAwarenessAction.EXPOSE_PARTIAL_AWARENESS
    )
    assert result.partial_context


@pytest.mark.parametrize(
    ("kind", "expected"),
    [
        (PresenceSituationKind.STABLE, LivingConversationPresenceAwarenessKind.STABLE),
        (
            PresenceSituationKind.TRANSITION,
            LivingConversationPresenceAwarenessKind.TRANSITIONAL,
        ),
        (
            PresenceSituationKind.UNCERTAIN,
            LivingConversationPresenceAwarenessKind.UNCERTAIN,
        ),
        (
            PresenceSituationKind.INTERRUPTED,
            LivingConversationPresenceAwarenessKind.INTERRUPTED,
        ),
        (PresenceSituationKind.NONE, LivingConversationPresenceAwarenessKind.UNCERTAIN),
    ],
)
def test_situation_kind_maps_to_awareness(kind, expected):
    assert (
        assess(results=(consumer_with_kind(kind),)).states[0].awareness_kind is expected
    )


def test_stable_state_flags_are_consistent():
    state = assess(results=(consumer_with_kind(PresenceSituationKind.STABLE),)).states[
        0
    ]
    assert state.stable_presence
    assert not state.transition_present
    assert not state.uncertainty_present
    assert not state.continuity_interrupted


def test_transition_state_flags_are_consistent():
    state = assess(
        results=(consumer_with_kind(PresenceSituationKind.TRANSITION),)
    ).states[0]
    assert state.transition_present
    assert not state.stable_presence


def test_uncertain_state_flags_are_consistent():
    state = assess(
        results=(consumer_with_kind(PresenceSituationKind.UNCERTAIN),)
    ).states[0]
    assert state.uncertainty_present
    assert not state.stable_presence


def test_interrupted_state_flags_are_consistent():
    state = assess(
        results=(consumer_with_kind(PresenceSituationKind.INTERRUPTED),)
    ).states[0]
    assert state.continuity_interrupted
    assert not state.stable_presence


def test_awareness_not_declared_is_not_applicable():
    assert (
        assess(awareness_declared=False).status
        is LivingConversationPresenceAwarenessStatus.NOT_APPLICABLE
    )


def test_owner_mismatch_is_blocked():
    assert (
        assess(owner="Other").status
        is LivingConversationPresenceAwarenessStatus.BLOCKED
    )


def test_empty_results_are_empty():
    req = LivingConversationPresenceAwarenessRequest(
        owner="Carlos", consumer_results=()
    )
    result = LivingConversationPresenceAwareness().assess(req, now=NOW)
    assert result.status is LivingConversationPresenceAwarenessStatus.EMPTY


def test_non_adapted_result_is_empty():
    source = consume(consumption_declared=False)
    assert (
        assess(results=(source,)).status
        is LivingConversationPresenceAwarenessStatus.EMPTY
    )


def test_result_limit_is_enforced():
    source = consume()
    result = assess(
        results=(source, source),
        policy=LivingConversationPresenceAwarenessPolicy(maximum_consumer_results=1),
    )
    assert result.status is LivingConversationPresenceAwarenessStatus.BLOCKED


def test_stale_result_requires_review():
    source = replace(consume(), created_at=NOW - timedelta(hours=3), consumption_id="")
    assert (
        assess(results=(source,)).status
        is LivingConversationPresenceAwarenessStatus.REVIEW_REQUIRED
    )


def test_future_result_requires_review():
    source = replace(
        consume(), created_at=NOW + timedelta(minutes=1), consumption_id=""
    )
    assert (
        assess(results=(source,)).status
        is LivingConversationPresenceAwarenessStatus.REVIEW_REQUIRED
    )


def test_low_confidence_requires_review():
    source = replace(consume(), confidence=0.69, consumption_id="")
    assert (
        assess(results=(source,)).status
        is LivingConversationPresenceAwarenessStatus.REVIEW_REQUIRED
    )


def test_latest_result_is_selected():
    old = consume()
    new = replace(old, created_at=NOW + timedelta(minutes=1), consumption_id="")
    result = assess(results=(old, new), now=NOW + timedelta(minutes=2))
    assert result.source_consumer is new


def test_duplicate_result_is_deduplicated():
    source = consume()
    assert assess(results=(source, source)).source_consumer is source


def test_source_consumer_is_preserved_exactly():
    source = consume()
    assert assess(results=(source,)).source_consumer is source


def test_source_cue_is_preserved_exactly():
    source = consume()
    assert assess(results=(source,)).states[0].source_cue is source.cues[0]


def test_confidence_is_bounded_by_source():
    result = assess()
    assert result.confidence <= result.source_consumer.confidence


def test_awareness_id_is_deterministic():
    req = request()
    first = LivingConversationPresenceAwareness().assess(req, now=NOW)
    second = LivingConversationPresenceAwareness().assess(req, now=NOW)
    assert first.awareness_id == second.awareness_id


def test_state_id_is_deterministic():
    assert assess().states[0].state_id == assess().states[0].state_id


def test_repository_stores_result():
    repository = InMemoryLivingConversationPresenceAwarenessRepository()
    result = LivingConversationPresenceAwareness(repository=repository).assess(
        request(), now=NOW
    )
    assert repository.get(result.awareness_id) == result
    assert repository.list_all() == (result,)


def test_repository_rejects_duplicate():
    repository = InMemoryLivingConversationPresenceAwarenessRepository()
    result = LivingConversationPresenceAwareness(repository=repository).assess(
        request(), now=NOW
    )
    with pytest.raises(ValueError, match="already exists"):
        repository.add(result)


def test_result_is_immutable():
    with pytest.raises(FrozenInstanceError):
        assess().confidence = 0.1


def test_state_is_immutable():
    with pytest.raises(FrozenInstanceError):
        assess().states[0].confidence = 0.1


@pytest.mark.parametrize("owner", ["", " ", "\t"])
def test_blank_owner_is_rejected(owner):
    with pytest.raises(ValueError, match="owner"):
        request(owner=owner)


def test_naive_timestamp_is_rejected():
    with pytest.raises(ValueError, match="timezone-aware"):
        LivingConversationPresenceAwareness().assess(
            request(), now=NOW.replace(tzinfo=None)
        )


@pytest.mark.parametrize("value", [-0.1, 1.1])
def test_invalid_confidence_policy_is_rejected(value):
    with pytest.raises(ValueError, match="confidence"):
        LivingConversationPresenceAwarenessPolicy(minimum_confidence=value)


def test_non_positive_limit_is_rejected():
    with pytest.raises(ValueError, match="limit"):
        LivingConversationPresenceAwarenessPolicy(maximum_consumer_results=0)


def test_non_positive_age_is_rejected():
    with pytest.raises(ValueError, match="age"):
        LivingConversationPresenceAwarenessPolicy(maximum_result_age=timedelta(0))


@pytest.mark.parametrize(
    "field",
    [
        "conversation_decision_allowed",
        "conversational_activation_allowed",
        "timing_selection_allowed",
        "prompt_generation_allowed",
        "response_realization_allowed",
        "identity_inference_allowed",
        "activity_inference_allowed",
        "intent_inference_allowed",
        "behavior_adaptation_allowed",
        "provider_call_allowed",
        "automation_allowed",
        "platform_mutation_allowed",
    ],
)
def test_downstream_capabilities_are_forbidden(field):
    assert getattr(assess(), field) is False
