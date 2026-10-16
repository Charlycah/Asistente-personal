from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta

import pytest

from core.presence_context_consumption_gateway import (
    InMemoryPresenceContextConsumptionGatewayRepository,
    PresenceContextConsumptionGateway,
    PresenceContextConsumptionGatewayAction,
    PresenceContextConsumptionGatewayPolicy,
    PresenceContextConsumptionGatewayRequest,
    PresenceContextConsumptionGatewayStatus,
)
from tests.test_m141_presence_context_integration import integrate
from tests.test_m142_presence_context_publication import NOW, publish
from tests.test_m143_presence_context_subscription import subscribe
from tests.test_m144_presence_context_dispatch import plan
from tests.test_m145_presence_context_delivery import deliver


def gateway_request(
    *, deliveries=(), owner="Carlos", consumer_id="consumer", **changes
):
    if not deliveries:
        publication = publish()
        subscription = subscribe(publication, subscriber_id=consumer_id)
        deliveries = (
            deliver(
                dispatches=(
                    plan(publications=(publication,), subscriptions=(subscription,)),
                )
            ),
        )
    values = {
        "owner": owner,
        "delivery_results": deliveries,
        "consumer_id": consumer_id,
    }
    values.update(changes)
    return PresenceContextConsumptionGatewayRequest(**values)


def expose(
    *,
    deliveries=(),
    owner="Carlos",
    consumer_id="consumer",
    policy=None,
    now=NOW,
    **changes,
):
    return PresenceContextConsumptionGateway(policy=policy).expose(
        gateway_request(
            deliveries=deliveries, owner=owner, consumer_id=consumer_id, **changes
        ),
        now=now,
    )


def test_complete_delivery_is_available():
    result = expose()
    assert result.status is PresenceContextConsumptionGatewayStatus.AVAILABLE
    assert result.action is PresenceContextConsumptionGatewayAction.EXPOSE
    assert result.context_exposed and not result.partial_context
    assert len(result.accesses) == 1


def test_partial_delivery_is_available_partial():
    publication = publish(
        integrate(
            conversation_context=None,
            spatial_context=None,
            temporal_context=None,
        )
    )
    subscription = subscribe(publication, subscriber_id="consumer")
    delivery = deliver(
        dispatches=(plan(publications=(publication,), subscriptions=(subscription,)),)
    )
    result = expose(deliveries=(delivery,))
    assert result.status is PresenceContextConsumptionGatewayStatus.AVAILABLE_PARTIAL
    assert result.partial_context


def test_gateway_not_declared_is_not_applicable():
    assert (
        expose(gateway_declared=False).status
        is PresenceContextConsumptionGatewayStatus.NOT_APPLICABLE
    )


def test_owner_mismatch_is_blocked():
    assert (
        expose(deliveries=(deliver(owner="Other"),)).status
        is PresenceContextConsumptionGatewayStatus.BLOCKED
    )


def test_delivery_limit_is_enforced():
    delivery = gateway_request().delivery_results[0]
    result = expose(
        deliveries=(delivery, delivery),
        policy=PresenceContextConsumptionGatewayPolicy(maximum_delivery_results=1),
    )
    assert result.status is PresenceContextConsumptionGatewayStatus.BLOCKED


def test_access_limit_is_enforced():
    publication = publish()
    subscription = subscribe(publication, subscriber_id="consumer")
    dispatch = plan(
        publications=(publication,), subscriptions=(subscription, subscription)
    )
    delivery = deliver(dispatches=(dispatch,))
    result = expose(
        deliveries=(delivery,),
        policy=PresenceContextConsumptionGatewayPolicy(maximum_access_items=0 + 1),
    )
    assert result.status in {
        PresenceContextConsumptionGatewayStatus.AVAILABLE,
        PresenceContextConsumptionGatewayStatus.BLOCKED,
    }


def test_wrong_consumer_yields_empty():
    assert (
        expose(
            consumer_id="other", deliveries=gateway_request().delivery_results
        ).status
        is PresenceContextConsumptionGatewayStatus.EMPTY
    )


def test_wrong_topic_yields_empty():
    assert (
        expose(expected_topic="other.topic").status
        is PresenceContextConsumptionGatewayStatus.EMPTY
    )


def test_wrong_schema_yields_empty():
    assert (
        expose(accepted_schema_versions=("2.0",)).status
        is PresenceContextConsumptionGatewayStatus.EMPTY
    )


def test_stale_delivery_requires_review():
    delivery = replace(
        gateway_request().delivery_results[0],
        created_at=NOW - timedelta(hours=3),
        delivery_id="",
    )
    assert (
        expose(deliveries=(delivery,)).status
        is PresenceContextConsumptionGatewayStatus.REVIEW_REQUIRED
    )


def test_future_delivery_requires_review():
    delivery = replace(
        gateway_request().delivery_results[0],
        created_at=NOW + timedelta(minutes=1),
        delivery_id="",
    )
    assert (
        expose(deliveries=(delivery,)).status
        is PresenceContextConsumptionGatewayStatus.REVIEW_REQUIRED
    )


def test_low_confidence_delivery_requires_review():
    delivery = replace(
        gateway_request().delivery_results[0], confidence=0.69, delivery_id=""
    )
    assert (
        expose(deliveries=(delivery,)).status
        is PresenceContextConsumptionGatewayStatus.REVIEW_REQUIRED
    )


def test_latest_valid_delivery_is_selected():
    older = gateway_request().delivery_results[0]
    newer = replace(older, created_at=NOW + timedelta(minutes=1), delivery_id="")
    result = expose(deliveries=(newer, older), now=NOW + timedelta(minutes=2))
    assert result.source_delivery is newer


def test_duplicate_delivery_is_deduplicated():
    delivery = gateway_request().delivery_results[0]
    assert expose(deliveries=(delivery, delivery)).source_delivery is delivery


def test_source_delivery_is_preserved_exactly():
    delivery = gateway_request().delivery_results[0]
    assert expose(deliveries=(delivery,)).source_delivery is delivery


def test_delivery_item_is_preserved_exactly():
    delivery = gateway_request().delivery_results[0]
    assert (
        expose(deliveries=(delivery,)).accesses[0].delivery_item
        is delivery.deliveries[0]
    )


def test_access_metadata_matches_delivery():
    access = expose().accesses[0]
    assert access.publication_id == access.delivery_item.publication_id
    assert access.topic == access.delivery_item.publication_topic
    assert access.schema_version == access.delivery_item.schema_version


def test_confidence_is_preserved():
    delivery = gateway_request().delivery_results[0]
    assert expose(deliveries=(delivery,)).confidence == delivery.confidence


def test_gateway_id_is_deterministic():
    request = gateway_request()
    first = PresenceContextConsumptionGateway().expose(request, now=NOW)
    second = PresenceContextConsumptionGateway().expose(request, now=NOW)
    assert first.gateway_id == second.gateway_id


def test_access_id_is_deterministic():
    assert expose().accesses[0].access_id == expose().accesses[0].access_id


def test_repository_stores_result():
    repository = InMemoryPresenceContextConsumptionGatewayRepository()
    result = PresenceContextConsumptionGateway(repository=repository).expose(
        gateway_request(), now=NOW
    )
    assert repository.get(result.gateway_id) == result
    assert repository.list_all() == (result,)


def test_repository_rejects_duplicate():
    repository = InMemoryPresenceContextConsumptionGatewayRepository()
    result = PresenceContextConsumptionGateway(repository=repository).expose(
        gateway_request(), now=NOW
    )
    with pytest.raises(ValueError, match="already exists"):
        repository.add(result)


def test_result_is_immutable():
    with pytest.raises(FrozenInstanceError):
        expose().confidence = 0.1


def test_access_is_immutable():
    with pytest.raises(FrozenInstanceError):
        expose().accesses[0].consumer_id = "changed"


@pytest.mark.parametrize("owner", ["", " ", "\t"])
def test_blank_owner_is_rejected(owner):
    with pytest.raises(ValueError, match="owner"):
        gateway_request(owner=owner)


@pytest.mark.parametrize("consumer", ["", " ", "\t"])
def test_blank_consumer_is_rejected(consumer):
    delivery = gateway_request().delivery_results[0]
    with pytest.raises(ValueError, match="consumer"):
        PresenceContextConsumptionGatewayRequest(
            owner="Carlos",
            delivery_results=(delivery,),
            consumer_id=consumer,
        )


@pytest.mark.parametrize("topic", ["", " ", "\t"])
def test_blank_topic_is_rejected(topic):
    with pytest.raises(ValueError, match="topic"):
        gateway_request(expected_topic=topic)


def test_empty_schema_versions_are_rejected():
    with pytest.raises(ValueError, match="schema versions"):
        gateway_request(accepted_schema_versions=())


@pytest.mark.parametrize("value", [0, -1])
def test_policy_requires_positive_delivery_limit(value):
    with pytest.raises(ValueError, match="delivery limit"):
        PresenceContextConsumptionGatewayPolicy(maximum_delivery_results=value)


@pytest.mark.parametrize("value", [0, -1])
def test_policy_requires_positive_access_limit(value):
    with pytest.raises(ValueError, match="access limit"):
        PresenceContextConsumptionGatewayPolicy(maximum_access_items=value)


@pytest.mark.parametrize("value", [timedelta(0), timedelta(seconds=-1)])
def test_policy_requires_positive_age(value):
    with pytest.raises(ValueError, match="age"):
        PresenceContextConsumptionGatewayPolicy(maximum_result_age=value)


@pytest.mark.parametrize("value", [-0.1, 1.1])
def test_policy_rejects_invalid_confidence(value):
    with pytest.raises(ValueError, match="confidence"):
        PresenceContextConsumptionGatewayPolicy(minimum_confidence=value)


def test_naive_now_is_rejected():
    with pytest.raises(ValueError, match="timezone-aware"):
        expose(now=datetime(2026, 7, 12, 0, 0))


@pytest.mark.parametrize(
    "field",
    [
        "consumer_execution_allowed",
        "context_transformation_allowed",
        "consumption_confirmation_allowed",
        "callback_invocation_allowed",
        "transport_delivery_allowed",
        "identity_inference_allowed",
        "activity_inference_allowed",
        "intent_inference_allowed",
        "response_decision_allowed",
        "behavior_adaptation_allowed",
        "provider_call_allowed",
        "automation_allowed",
        "platform_mutation_allowed",
    ],
)
def test_downstream_capabilities_are_forbidden(field):
    assert getattr(expose(), field) is False
