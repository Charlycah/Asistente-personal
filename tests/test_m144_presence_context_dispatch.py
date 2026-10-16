from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta

import pytest

from core.presence_context_dispatch import (
    InMemoryPresenceContextDispatchRepository,
    PresenceContextDispatchAction,
    PresenceContextDispatchEngine,
    PresenceContextDispatchPolicy,
    PresenceContextDispatchRequest,
    PresenceContextDispatchStatus,
)
from core.presence_context_subscription import (
    PresenceContextSubscriptionFilter,
    PresenceContextSubscriptionLifecycle,
)
from tests.test_m141_presence_context_integration import integrate
from tests.test_m142_presence_context_publication import NOW, publish
from tests.test_m143_presence_context_subscription import subscribe


def dispatch_request(*, publications=(), subscriptions=(), owner="Carlos", **changes):
    if not publications:
        publications = (publish(),)
    if not subscriptions:
        subscriptions = (subscribe(publications[0]),)
    values = {
        "owner": owner,
        "publication_results": publications,
        "subscription_results": subscriptions,
    }
    values.update(changes)
    return PresenceContextDispatchRequest(**values)


def plan(
    *,
    publications=(),
    subscriptions=(),
    owner="Carlos",
    policy=None,
    now=NOW,
    **changes,
):
    return PresenceContextDispatchEngine(policy=policy).plan(
        dispatch_request(
            publications=publications,
            subscriptions=subscriptions,
            owner=owner,
            **changes,
        ),
        now=now,
    )


def test_complete_publication_builds_dispatch_plan():
    result = plan()
    assert result.status is PresenceContextDispatchStatus.PLANNED
    assert result.action is PresenceContextDispatchAction.PLAN
    assert result.dispatch_planned
    assert not result.partial_context
    assert len(result.destinations) == 1


def test_partial_publication_builds_partial_dispatch_plan():
    publication = publish(
        integrate(
            conversation_context=None, spatial_context=None, temporal_context=None
        )
    )
    subscription = subscribe(publication)
    result = plan(publications=(publication,), subscriptions=(subscription,))
    assert result.status is PresenceContextDispatchStatus.PLANNED_PARTIAL
    assert result.action is PresenceContextDispatchAction.PLAN_PARTIAL
    assert result.partial_context
    assert result.destinations[0].partial_context


def test_complete_only_subscription_excludes_partial_publication():
    publication = publish(
        integrate(
            conversation_context=None, spatial_context=None, temporal_context=None
        )
    )
    subscription = subscribe(
        publication, filter_mode=PresenceContextSubscriptionFilter.COMPLETE_ONLY
    )
    result = plan(publications=(publication,), subscriptions=(subscription,))
    assert result.status is PresenceContextDispatchStatus.EMPTY
    assert result.action is PresenceContextDispatchAction.NONE


def test_multiple_compatible_subscriptions_are_planned():
    publication = publish()
    first = subscribe(publication, subscriber_id="living-conversation")
    second = subscribe(publication, subscriber_id="executive-context")
    result = plan(publications=(publication,), subscriptions=(second, first))
    assert [item.subscriber_id for item in result.destinations] == [
        "executive-context",
        "living-conversation",
    ]


def test_duplicate_subscription_is_deduplicated():
    publication = publish()
    subscription = subscribe(publication)
    result = plan(
        publications=(publication,), subscriptions=(subscription, subscription)
    )
    assert len(result.destinations) == 1


def test_duplicate_subscriber_id_is_deduplicated():
    publication = publish()
    first = subscribe(publication, subscriber_id="consumer")
    second = replace(
        first,
        created_at=NOW + timedelta(seconds=1),
        subscription_id="",
    )
    result = plan(
        publications=(publication,),
        subscriptions=(second, first),
        now=NOW + timedelta(minutes=1),
    )
    assert len(result.destinations) == 1
    assert result.destinations[0].subscriber_id == "consumer"


def test_paused_subscription_is_excluded():
    publication = publish()
    subscription = subscribe(
        publication, lifecycle=PresenceContextSubscriptionLifecycle.PAUSED
    )
    result = plan(publications=(publication,), subscriptions=(subscription,))
    assert result.status is PresenceContextDispatchStatus.EMPTY


def test_topic_mismatch_is_excluded():
    publication = publish()
    subscription = subscribe(publication, accepted_topic="other.topic")
    assert not subscription.subscription_registered
    result = plan(publications=(publication,), subscriptions=(subscription,))
    assert result.status is PresenceContextDispatchStatus.EMPTY


def test_schema_mismatch_is_excluded():
    publication = publish()
    subscription = subscribe(publication, accepted_schema_versions=("2.0",))
    result = plan(publications=(publication,), subscriptions=(subscription,))
    assert result.status is PresenceContextDispatchStatus.EMPTY


def test_dispatch_not_declared_is_not_applicable():
    result = plan(dispatch_declared=False)
    assert result.status is PresenceContextDispatchStatus.NOT_APPLICABLE


def test_publication_owner_mismatch_is_blocked():
    result = plan(publications=(publish(owner="Other"),), subscriptions=())
    assert result.status is PresenceContextDispatchStatus.BLOCKED


def test_subscription_owner_mismatch_is_blocked():
    publication = publish()
    subscription = subscribe(publish(owner="Other"), owner="Other")
    result = plan(publications=(publication,), subscriptions=(subscription,))
    assert result.status is PresenceContextDispatchStatus.BLOCKED


def test_publication_limit_is_enforced():
    publication = publish()
    result = plan(
        publications=(publication, publication),
        policy=PresenceContextDispatchPolicy(maximum_publication_results=1),
    )
    assert result.status is PresenceContextDispatchStatus.BLOCKED


def test_subscription_limit_is_enforced():
    publication = publish()
    subscription = subscribe(publication)
    result = plan(
        publications=(publication,),
        subscriptions=(subscription, subscription),
        policy=PresenceContextDispatchPolicy(maximum_subscription_results=1),
    )
    assert result.status is PresenceContextDispatchStatus.BLOCKED


def test_stale_publication_requires_review():
    publication = publish(now=NOW - timedelta(hours=3))
    subscription = subscribe(publication, now=NOW - timedelta(hours=3))
    result = plan(publications=(publication,), subscriptions=(subscription,))
    assert result.status is PresenceContextDispatchStatus.REVIEW_REQUIRED
    assert result.confirmation_required


def test_future_publication_requires_review():
    publication = publish(now=NOW + timedelta(minutes=1))
    subscription = subscribe(publication, now=NOW + timedelta(minutes=1))
    result = plan(publications=(publication,), subscriptions=(subscription,))
    assert result.status is PresenceContextDispatchStatus.REVIEW_REQUIRED


def test_low_confidence_publication_requires_review():
    publication = replace(publish(), confidence=0.69, publication_id="")
    subscription = subscribe(publication)
    result = plan(publications=(publication,), subscriptions=(subscription,))
    assert result.status is PresenceContextDispatchStatus.REVIEW_REQUIRED


def test_stale_subscription_is_excluded():
    publication = publish()
    subscription = subscribe(publication, now=NOW - timedelta(hours=3))
    result = plan(publications=(publication,), subscriptions=(subscription,))
    assert result.status is PresenceContextDispatchStatus.EMPTY


def test_future_subscription_is_excluded():
    publication = publish()
    subscription = subscribe(publication, now=NOW + timedelta(minutes=1))
    result = plan(publications=(publication,), subscriptions=(subscription,))
    assert result.status is PresenceContextDispatchStatus.EMPTY


def test_low_confidence_subscription_is_excluded():
    publication = publish()
    subscription = replace(subscribe(publication), confidence=0.69, subscription_id="")
    result = plan(publications=(publication,), subscriptions=(subscription,))
    assert result.status is PresenceContextDispatchStatus.EMPTY


def test_latest_valid_publication_is_selected():
    older = publish(now=NOW)
    newer = replace(older, created_at=NOW + timedelta(minutes=1), publication_id="")
    subscription = subscribe(older)
    result = plan(
        publications=(newer, older),
        subscriptions=(subscription,),
        now=NOW + timedelta(minutes=2),
    )
    assert result.source_publication is newer


def test_duplicate_publication_is_deduplicated():
    publication = publish()
    subscription = subscribe(publication)
    result = plan(
        publications=(publication, publication), subscriptions=(subscription,)
    )
    assert result.source_publication is publication


def test_source_publication_is_preserved_exactly():
    publication = publish()
    subscription = subscribe(publication)
    result = plan(publications=(publication,), subscriptions=(subscription,))
    assert result.source_publication is publication


def test_source_subscription_is_preserved_exactly():
    publication = publish()
    subscription = subscribe(publication)
    result = plan(publications=(publication,), subscriptions=(subscription,))
    assert result.destinations[0].subscription is subscription


def test_destination_metadata_matches_publication():
    publication = publish()
    subscription = subscribe(publication)
    destination = plan(
        publications=(publication,), subscriptions=(subscription,)
    ).destinations[0]
    assert destination.publication_topic == publication.publication_topic
    assert destination.schema_version == publication.schema_version


def test_confidence_is_minimum_of_publication_and_subscriptions():
    publication = publish()
    first = replace(subscribe(publication), confidence=0.91, subscription_id="")
    second = replace(
        subscribe(publication, subscriber_id="other"),
        confidence=0.82,
        subscription_id="",
    )
    result = plan(publications=(publication,), subscriptions=(first, second))
    assert result.confidence == 0.82


def test_dispatch_id_is_deterministic():
    request = dispatch_request()
    first = PresenceContextDispatchEngine().plan(request, now=NOW)
    second = PresenceContextDispatchEngine().plan(request, now=NOW)
    assert first.dispatch_id == second.dispatch_id


def test_repository_stores_result():
    repository = InMemoryPresenceContextDispatchRepository()
    result = PresenceContextDispatchEngine(repository=repository).plan(
        dispatch_request(), now=NOW
    )
    assert repository.get(result.dispatch_id) == result
    assert repository.list_all() == (result,)


def test_repository_rejects_duplicate():
    repository = InMemoryPresenceContextDispatchRepository()
    result = PresenceContextDispatchEngine(repository=repository).plan(
        dispatch_request(), now=NOW
    )
    with pytest.raises(ValueError, match="already exists"):
        repository.add(result)


def test_result_is_immutable():
    with pytest.raises(FrozenInstanceError):
        plan().confidence = 0.1


def test_destination_is_immutable():
    with pytest.raises(FrozenInstanceError):
        plan().destinations[0].subscriber_id = "changed"


@pytest.mark.parametrize("owner", ["", " ", "\t"])
def test_blank_owner_is_rejected(owner):
    with pytest.raises(ValueError, match="owner"):
        dispatch_request(owner=owner)


@pytest.mark.parametrize("value", [0, -1])
def test_policy_requires_positive_publication_limit(value):
    with pytest.raises(ValueError, match="publication limit"):
        PresenceContextDispatchPolicy(maximum_publication_results=value)


@pytest.mark.parametrize("value", [0, -1])
def test_policy_requires_positive_subscription_limit(value):
    with pytest.raises(ValueError, match="subscription limit"):
        PresenceContextDispatchPolicy(maximum_subscription_results=value)


@pytest.mark.parametrize("value", [timedelta(0), timedelta(seconds=-1)])
def test_policy_requires_positive_age(value):
    with pytest.raises(ValueError, match="age"):
        PresenceContextDispatchPolicy(maximum_result_age=value)


@pytest.mark.parametrize("value", [-0.1, 1.1])
def test_policy_rejects_invalid_confidence(value):
    with pytest.raises(ValueError, match="confidence"):
        PresenceContextDispatchPolicy(minimum_confidence=value)


def test_naive_now_is_rejected():
    with pytest.raises(ValueError, match="timezone-aware"):
        plan(now=datetime(2026, 7, 11, 23, 45))


@pytest.mark.parametrize(
    "field",
    [
        "delivery_allowed",
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
    result = plan()
    assert getattr(result, field) is False
    with pytest.raises(ValueError, match="cannot authorize"):
        replace(result, **{field: True}, dispatch_id="")
