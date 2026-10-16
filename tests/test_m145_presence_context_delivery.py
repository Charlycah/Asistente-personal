from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta

import pytest

from core.presence_context_delivery import (
    InMemoryPresenceContextDeliveryRepository,
    PresenceContextDeliveryAction,
    PresenceContextDeliveryEngine,
    PresenceContextDeliveryItemStatus,
    PresenceContextDeliveryPolicy,
    PresenceContextDeliveryRequest,
    PresenceContextDeliveryStatus,
)
from tests.test_m141_presence_context_integration import integrate
from tests.test_m142_presence_context_publication import NOW, publish
from tests.test_m143_presence_context_subscription import subscribe
from tests.test_m144_presence_context_dispatch import plan


def delivery_request(*, dispatches=(), owner="Carlos", **changes):
    if not dispatches:
        dispatches = (plan(),)
    values = {"owner": owner, "dispatch_results": dispatches}
    values.update(changes)
    return PresenceContextDeliveryRequest(**values)


def deliver(*, dispatches=(), owner="Carlos", policy=None, now=NOW, **changes):
    return PresenceContextDeliveryEngine(policy=policy).deliver(
        delivery_request(dispatches=dispatches, owner=owner, **changes), now=now
    )


def test_complete_dispatch_materializes_delivery():
    result = deliver()
    assert result.status is PresenceContextDeliveryStatus.DELIVERED
    assert result.action is PresenceContextDeliveryAction.MATERIALIZE
    assert result.delivery_materialized
    assert not result.partial_context
    assert len(result.deliveries) == 1


def test_partial_dispatch_materializes_partial_delivery():
    publication = publish(
        integrate(
            conversation_context=None, spatial_context=None, temporal_context=None
        )
    )
    dispatch = plan(
        publications=(publication,), subscriptions=(subscribe(publication),)
    )
    result = deliver(dispatches=(dispatch,))
    assert result.status is PresenceContextDeliveryStatus.DELIVERED_PARTIAL
    assert result.action is PresenceContextDeliveryAction.MATERIALIZE_PARTIAL
    assert result.partial_context
    assert (
        result.deliveries[0].status
        is PresenceContextDeliveryItemStatus.DELIVERED_PARTIAL
    )


def test_multiple_destinations_create_multiple_delivery_items():
    publication = publish()
    dispatch = plan(
        publications=(publication,),
        subscriptions=(
            subscribe(publication, subscriber_id="one"),
            subscribe(publication, subscriber_id="two"),
        ),
    )
    result = deliver(dispatches=(dispatch,))
    assert [item.subscriber_id for item in result.deliveries] == ["one", "two"]


def test_delivery_not_declared_is_not_applicable():
    result = deliver(delivery_declared=False)
    assert result.status is PresenceContextDeliveryStatus.NOT_APPLICABLE


def test_owner_mismatch_is_blocked():
    result = deliver(dispatches=(plan(owner="Other"),))
    assert result.status is PresenceContextDeliveryStatus.BLOCKED


def test_dispatch_limit_is_enforced():
    dispatch = plan()
    result = deliver(
        dispatches=(dispatch, dispatch),
        policy=PresenceContextDeliveryPolicy(maximum_dispatch_results=1),
    )
    assert result.status is PresenceContextDeliveryStatus.BLOCKED


def test_destination_limit_is_enforced():
    publication = publish()
    dispatch = plan(
        publications=(publication,),
        subscriptions=(
            subscribe(publication, subscriber_id="one"),
            subscribe(publication, subscriber_id="two"),
        ),
    )
    result = deliver(
        dispatches=(dispatch,),
        policy=PresenceContextDeliveryPolicy(maximum_destinations=1),
    )
    assert result.status is PresenceContextDeliveryStatus.BLOCKED


def test_stale_dispatch_requires_review():
    dispatch = plan(now=NOW - timedelta(hours=3))
    result = deliver(dispatches=(dispatch,))
    assert result.status is PresenceContextDeliveryStatus.REVIEW_REQUIRED
    assert result.confirmation_required


def test_future_dispatch_requires_review():
    dispatch = plan(now=NOW + timedelta(minutes=1))
    result = deliver(dispatches=(dispatch,))
    assert result.status is PresenceContextDeliveryStatus.REVIEW_REQUIRED


def test_low_confidence_dispatch_requires_review():
    dispatch = replace(plan(), confidence=0.69, dispatch_id="")
    result = deliver(dispatches=(dispatch,))
    assert result.status is PresenceContextDeliveryStatus.REVIEW_REQUIRED


def test_empty_dispatch_requires_review():
    result = deliver(dispatches=())
    assert result.status is PresenceContextDeliveryStatus.DELIVERED


def test_non_actionable_dispatch_requires_review():
    publication = publish()
    empty = plan(
        publications=(publication,),
        subscriptions=(subscribe(publication, accepted_schema_versions=("2.0",)),),
    )
    result = deliver(dispatches=(empty,))
    assert result.status is PresenceContextDeliveryStatus.REVIEW_REQUIRED


def test_latest_valid_dispatch_is_selected():
    older = plan(now=NOW)
    newer = replace(older, created_at=NOW + timedelta(minutes=1), dispatch_id="")
    result = deliver(dispatches=(newer, older), now=NOW + timedelta(minutes=2))
    assert result.source_dispatch is newer


def test_duplicate_dispatch_is_deduplicated():
    dispatch = plan()
    result = deliver(dispatches=(dispatch, dispatch))
    assert result.source_dispatch is dispatch


def test_source_dispatch_is_preserved_exactly():
    dispatch = plan()
    assert deliver(dispatches=(dispatch,)).source_dispatch is dispatch


def test_destination_is_preserved_exactly():
    dispatch = plan()
    assert (
        deliver(dispatches=(dispatch,)).deliveries[0].destination
        is dispatch.destinations[0]
    )


def test_delivery_item_metadata_matches_dispatch():
    dispatch = plan()
    item = deliver(dispatches=(dispatch,)).deliveries[0]
    assert item.publication_id == dispatch.source_publication.publication_id
    assert item.publication_topic == dispatch.destinations[0].publication_topic
    assert item.schema_version == dispatch.destinations[0].schema_version


def test_confidence_is_preserved_from_dispatch():
    dispatch = plan()
    assert deliver(dispatches=(dispatch,)).confidence == dispatch.confidence


def test_delivery_id_is_deterministic():
    request = delivery_request()
    first = PresenceContextDeliveryEngine().deliver(request, now=NOW)
    second = PresenceContextDeliveryEngine().deliver(request, now=NOW)
    assert first.delivery_id == second.delivery_id


def test_delivery_item_id_is_deterministic():
    dispatch = plan()
    first = deliver(dispatches=(dispatch,)).deliveries[0]
    second = deliver(dispatches=(dispatch,)).deliveries[0]
    assert first.delivery_item_id == second.delivery_item_id


def test_repository_stores_result():
    repository = InMemoryPresenceContextDeliveryRepository()
    result = PresenceContextDeliveryEngine(repository=repository).deliver(
        delivery_request(), now=NOW
    )
    assert repository.get(result.delivery_id) == result
    assert repository.list_all() == (result,)


def test_repository_rejects_duplicate():
    repository = InMemoryPresenceContextDeliveryRepository()
    result = PresenceContextDeliveryEngine(repository=repository).deliver(
        delivery_request(), now=NOW
    )
    with pytest.raises(ValueError, match="already exists"):
        repository.add(result)


def test_result_is_immutable():
    with pytest.raises(FrozenInstanceError):
        deliver().confidence = 0.1


def test_delivery_item_is_immutable():
    with pytest.raises(FrozenInstanceError):
        deliver().deliveries[0].subscriber_id = "changed"


@pytest.mark.parametrize("owner", ["", " ", "\t"])
def test_blank_owner_is_rejected(owner):
    with pytest.raises(ValueError, match="owner"):
        delivery_request(owner=owner)


@pytest.mark.parametrize("value", [0, -1])
def test_policy_requires_positive_dispatch_limit(value):
    with pytest.raises(ValueError, match="dispatch limit"):
        PresenceContextDeliveryPolicy(maximum_dispatch_results=value)


@pytest.mark.parametrize("value", [0, -1])
def test_policy_requires_positive_destination_limit(value):
    with pytest.raises(ValueError, match="destination limit"):
        PresenceContextDeliveryPolicy(maximum_destinations=value)


@pytest.mark.parametrize("value", [timedelta(0), timedelta(seconds=-1)])
def test_policy_requires_positive_age(value):
    with pytest.raises(ValueError, match="age"):
        PresenceContextDeliveryPolicy(maximum_result_age=value)


@pytest.mark.parametrize("value", [-0.1, 1.1])
def test_policy_rejects_invalid_confidence(value):
    with pytest.raises(ValueError, match="confidence"):
        PresenceContextDeliveryPolicy(minimum_confidence=value)


def test_naive_now_is_rejected():
    with pytest.raises(ValueError, match="timezone-aware"):
        deliver(now=datetime(2026, 7, 12, 0, 0))


@pytest.mark.parametrize(
    "field",
    [
        "transport_delivery_allowed",
        "callback_invocation_allowed",
        "consumer_processing_allowed",
        "routing_execution_allowed",
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
def test_all_downstream_capabilities_are_forbidden(field):
    result = deliver()
    assert getattr(result, field) is False
    with pytest.raises(ValueError, match="cannot authorize"):
        replace(result, **{field: True}, delivery_id="")
