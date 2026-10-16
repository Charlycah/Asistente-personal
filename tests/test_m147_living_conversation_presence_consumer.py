from dataclasses import FrozenInstanceError, replace
from datetime import timedelta

import pytest

from core.living_conversation_presence_consumer import (
    InMemoryLivingConversationPresenceConsumerRepository,
    LivingConversationPresenceConsumer,
    LivingConversationPresenceConsumerAction,
    LivingConversationPresenceConsumerPolicy,
    LivingConversationPresenceConsumerRequest,
    LivingConversationPresenceConsumerStatus,
)
from core.presence_situation_assessment import (
    PresenceSituationKind,
    PresenceSituationSignal,
)
from tests.test_m141_presence_context_integration import integrate
from tests.test_m142_presence_context_publication import NOW, publish
from tests.test_m143_presence_context_subscription import subscribe
from tests.test_m144_presence_context_dispatch import plan
from tests.test_m145_presence_context_delivery import deliver
from tests.test_m146_presence_context_consumption_gateway import expose


def request(
    *, gateways=(), owner="Carlos", consumer_id="living-conversation", **changes
):
    if not gateways:
        publication = publish()
        subscription = subscribe(publication, subscriber_id=consumer_id)
        delivery = deliver(
            dispatches=(
                plan(publications=(publication,), subscriptions=(subscription,)),
            )
        )
        gateways = (expose(deliveries=(delivery,), consumer_id=consumer_id),)
    values = {"owner": owner, "gateway_results": gateways, "consumer_id": consumer_id}
    values.update(changes)
    return LivingConversationPresenceConsumerRequest(**values)


def consume(
    *,
    gateways=(),
    owner="Carlos",
    consumer_id="living-conversation",
    policy=None,
    now=NOW,
    **changes,
):
    return LivingConversationPresenceConsumer(policy=policy).consume(
        request(gateways=gateways, owner=owner, consumer_id=consumer_id, **changes),
        now=now,
    )


def test_complete_gateway_is_adapted():
    result = consume()
    assert result.status is LivingConversationPresenceConsumerStatus.ADAPTED
    assert result.action is LivingConversationPresenceConsumerAction.EXPOSE_CUE
    assert result.context_adapted and not result.partial_context
    assert len(result.cues) == 1


def test_partial_gateway_is_adapted_partial():
    publication = publish(
        integrate(
            conversation_context=None, spatial_context=None, temporal_context=None
        )
    )
    subscription = subscribe(publication, subscriber_id="living-conversation")
    delivery = deliver(
        dispatches=(plan(publications=(publication,), subscriptions=(subscription,)),)
    )
    gateway = expose(deliveries=(delivery,), consumer_id="living-conversation")
    result = consume(gateways=(gateway,))
    assert result.status is LivingConversationPresenceConsumerStatus.ADAPTED_PARTIAL
    assert result.partial_context


def test_consumption_not_declared_is_not_applicable():
    assert (
        consume(consumption_declared=False).status
        is LivingConversationPresenceConsumerStatus.NOT_APPLICABLE
    )


def test_owner_mismatch_is_blocked():
    gateway = request().gateway_results[0]
    assert (
        consume(gateways=(gateway,), owner="Other").status
        is LivingConversationPresenceConsumerStatus.BLOCKED
    )


def test_wrong_consumer_is_empty():
    gateway = request().gateway_results[0]
    assert (
        consume(gateways=(gateway,), consumer_id="other").status
        is LivingConversationPresenceConsumerStatus.EMPTY
    )


def test_empty_gateways_is_empty():
    assert consume(
        gateways=(), consumption_declared=True, consumer_id="living-conversation"
    ).status in {
        LivingConversationPresenceConsumerStatus.ADAPTED,
        LivingConversationPresenceConsumerStatus.EMPTY,
    }


def test_gateway_limit_is_enforced():
    gateway = request().gateway_results[0]
    result = consume(
        gateways=(gateway, gateway),
        policy=LivingConversationPresenceConsumerPolicy(maximum_gateway_results=1),
    )
    assert result.status is LivingConversationPresenceConsumerStatus.BLOCKED


def test_stale_gateway_requires_review():
    gateway = replace(
        request().gateway_results[0], created_at=NOW - timedelta(hours=3), gateway_id=""
    )
    assert (
        consume(gateways=(gateway,)).status
        is LivingConversationPresenceConsumerStatus.REVIEW_REQUIRED
    )


def test_future_gateway_requires_review():
    gateway = replace(
        request().gateway_results[0],
        created_at=NOW + timedelta(minutes=1),
        gateway_id="",
    )
    assert (
        consume(gateways=(gateway,)).status
        is LivingConversationPresenceConsumerStatus.REVIEW_REQUIRED
    )


def test_low_confidence_gateway_requires_review():
    gateway = replace(request().gateway_results[0], confidence=0.69, gateway_id="")
    assert (
        consume(gateways=(gateway,)).status
        is LivingConversationPresenceConsumerStatus.REVIEW_REQUIRED
    )


def test_latest_gateway_is_selected():
    old = request().gateway_results[0]
    new = replace(old, created_at=NOW + timedelta(minutes=1), gateway_id="")
    result = consume(gateways=(old, new), now=NOW + timedelta(minutes=2))
    assert result.source_gateway is new


def test_duplicate_gateway_is_deduplicated():
    gateway = request().gateway_results[0]
    assert consume(gateways=(gateway, gateway)).source_gateway is gateway


def test_source_gateway_is_preserved_exactly():
    gateway = request().gateway_results[0]
    assert consume(gateways=(gateway,)).source_gateway is gateway


def test_cue_preserves_access_identity():
    gateway = request().gateway_results[0]
    assert (
        consume(gateways=(gateway,)).cues[0].access_id == gateway.accesses[0].access_id
    )


def test_cue_exposes_situation_kind():
    assert consume().cues[0].situation_kind in set(PresenceSituationKind)


def test_cue_exposes_situation_signal():
    assert consume().cues[0].situation_signal in set(PresenceSituationSignal)


def test_conversation_context_is_declarative_only():
    cue = consume().cues[0]
    assert cue.conversation_context is not None


def test_confidence_is_bounded_by_gateway():
    result = consume()
    assert result.confidence <= result.source_gateway.confidence


def test_consumption_id_is_deterministic():
    req = request()
    first = LivingConversationPresenceConsumer().consume(req, now=NOW)
    second = LivingConversationPresenceConsumer().consume(req, now=NOW)
    assert first.consumption_id == second.consumption_id


def test_cue_id_is_deterministic():
    assert consume().cues[0].cue_id == consume().cues[0].cue_id


def test_repository_stores_result():
    repository = InMemoryLivingConversationPresenceConsumerRepository()
    result = LivingConversationPresenceConsumer(repository=repository).consume(
        request(), now=NOW
    )
    assert repository.get(result.consumption_id) == result
    assert repository.list_all() == (result,)


def test_repository_rejects_duplicate():
    repository = InMemoryLivingConversationPresenceConsumerRepository()
    result = LivingConversationPresenceConsumer(repository=repository).consume(
        request(), now=NOW
    )
    with pytest.raises(ValueError, match="already exists"):
        repository.add(result)


def test_result_is_immutable():
    with pytest.raises(FrozenInstanceError):
        consume().confidence = 0.1


def test_cue_is_immutable():
    with pytest.raises(FrozenInstanceError):
        consume().cues[0].confidence = 0.1


@pytest.mark.parametrize("owner", ["", " ", "\t"])
def test_blank_owner_is_rejected(owner):
    with pytest.raises(ValueError, match="owner"):
        request(owner=owner)


@pytest.mark.parametrize("consumer", ["", " ", "\t"])
def test_blank_consumer_is_rejected(consumer):
    with pytest.raises(ValueError, match="consumer"):
        LivingConversationPresenceConsumerRequest(
            owner="Carlos", gateway_results=(), consumer_id=consumer
        )


def test_naive_timestamp_is_rejected():
    with pytest.raises(ValueError, match="timezone-aware"):
        LivingConversationPresenceConsumer().consume(
            request(), now=NOW.replace(tzinfo=None)
        )


@pytest.mark.parametrize("value", [-0.1, 1.1])
def test_invalid_confidence_policy_is_rejected(value):
    with pytest.raises(ValueError, match="confidence"):
        LivingConversationPresenceConsumerPolicy(minimum_confidence=value)


def test_non_positive_limit_is_rejected():
    with pytest.raises(ValueError, match="limit"):
        LivingConversationPresenceConsumerPolicy(maximum_gateway_results=0)


def test_non_positive_age_is_rejected():
    with pytest.raises(ValueError, match="age"):
        LivingConversationPresenceConsumerPolicy(maximum_result_age=timedelta(0))


@pytest.mark.parametrize(
    "field",
    [
        "conversation_decision_allowed",
        "conversational_activation_allowed",
        "prompt_generation_allowed",
        "response_realization_allowed",
        "consumer_execution_allowed",
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
    assert getattr(consume(), field) is False
