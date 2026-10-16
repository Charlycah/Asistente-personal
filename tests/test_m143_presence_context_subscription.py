from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta

import pytest

from core.presence_context_publication import PresenceContextPublicationStatus
from core.presence_context_subscription import (
    InMemoryPresenceContextSubscriptionRepository,
    PresenceContextSubscriptionAction,
    PresenceContextSubscriptionEngine,
    PresenceContextSubscriptionFilter,
    PresenceContextSubscriptionLifecycle,
    PresenceContextSubscriptionPolicy,
    PresenceContextSubscriptionRequest,
    PresenceContextSubscriptionStatus,
)
from tests.test_m142_presence_context_publication import NOW, integrate, publish


def subscription_request(*results, owner="Carlos", **changes):
    if not results:
        results = (publish(),)
    values = {
        "owner": owner,
        "publication_results": results,
        "subscriber_id": "living-conversation",
        "accepted_topic": "roby.ambient.presence.context",
        "accepted_schema_versions": ("1.0",),
    }
    values.update(changes)
    return PresenceContextSubscriptionRequest(**values)


def subscribe(*results, owner="Carlos", policy=None, now=NOW, **changes):
    return PresenceContextSubscriptionEngine(policy=policy).subscribe(
        subscription_request(*results, owner=owner, **changes), now=now
    )


def test_complete_publication_registers_active_subscription():
    result = subscribe()
    assert result.status is PresenceContextSubscriptionStatus.ACTIVE
    assert result.action is PresenceContextSubscriptionAction.REGISTER
    assert result.subscription_registered
    assert result.context_eligible


def test_partial_publication_is_eligible_when_filter_includes_partial():
    partial = publish(
        integrate(
            conversation_context=None, spatial_context=None, temporal_context=None
        )
    )
    assert partial.status is PresenceContextPublicationStatus.PUBLISHED_PARTIAL
    result = subscribe(partial)
    assert result.status is PresenceContextSubscriptionStatus.ACTIVE
    assert result.source_publication is partial


def test_partial_publication_is_filtered_for_complete_only_subscription():
    partial = publish(
        integrate(
            conversation_context=None, spatial_context=None, temporal_context=None
        )
    )
    result = subscribe(
        partial, filter_mode=PresenceContextSubscriptionFilter.COMPLETE_ONLY
    )
    assert result.status is PresenceContextSubscriptionStatus.NOT_APPLICABLE
    assert result.action is PresenceContextSubscriptionAction.NONE


def test_paused_lifecycle_registers_paused_subscription():
    result = subscribe(lifecycle=PresenceContextSubscriptionLifecycle.PAUSED)
    assert result.status is PresenceContextSubscriptionStatus.PAUSED
    assert result.action is PresenceContextSubscriptionAction.PAUSE
    assert result.subscription_registered
    assert not result.context_eligible


def test_subscription_not_declared_is_not_applicable():
    result = subscribe(subscription_declared=False)
    assert result.status is PresenceContextSubscriptionStatus.NOT_APPLICABLE


def test_owner_mismatch_is_blocked():
    result = subscribe(publish(owner="Other"), owner="Carlos")
    assert result.status is PresenceContextSubscriptionStatus.BLOCKED


def test_result_limit_is_enforced():
    source = publish()
    result = subscribe(
        source, source, policy=PresenceContextSubscriptionPolicy(maximum_results=1)
    )
    assert result.status is PresenceContextSubscriptionStatus.BLOCKED


def test_stale_publication_requires_review():
    source = publish(now=NOW - timedelta(hours=3))
    result = subscribe(source)
    assert result.status is PresenceContextSubscriptionStatus.REVIEW_REQUIRED


def test_future_publication_requires_review():
    source = publish(now=NOW + timedelta(minutes=1))
    result = subscribe(source)
    assert result.status is PresenceContextSubscriptionStatus.REVIEW_REQUIRED


def test_low_confidence_publication_requires_review():
    source = replace(publish(), confidence=0.69, publication_id="")
    result = subscribe(source)
    assert result.status is PresenceContextSubscriptionStatus.REVIEW_REQUIRED


def test_topic_mismatch_is_blocked():
    result = subscribe(accepted_topic="other.topic")
    assert result.status is PresenceContextSubscriptionStatus.BLOCKED


def test_unsupported_schema_requires_review():
    result = subscribe(accepted_schema_versions=("2.0",))
    assert result.status is PresenceContextSubscriptionStatus.REVIEW_REQUIRED
    assert result.confirmation_required


def test_multiple_accepted_versions_allow_source_schema():
    result = subscribe(accepted_schema_versions=("2.0", "1.0"))
    assert result.status is PresenceContextSubscriptionStatus.ACTIVE


def test_latest_valid_publication_is_selected():
    older = publish(now=NOW)
    newer = replace(older, created_at=NOW + timedelta(minutes=1), publication_id="")
    result = subscribe(newer, older, now=NOW + timedelta(minutes=2))
    assert result.source_publication is newer


def test_duplicate_publication_is_deduplicated():
    source = publish()
    result = subscribe(source, source)
    assert result.source_publication is source


def test_source_publication_is_preserved_exactly():
    source = publish()
    result = subscribe(source)
    assert result.source_publication is source


def test_subscription_metadata_is_preserved_exactly():
    result = subscribe(
        subscriber_id="executive-context",
        accepted_schema_versions=("1.0", "1.1"),
        filter_mode=PresenceContextSubscriptionFilter.COMPLETE_ONLY,
    )
    assert result.subscriber_id == "executive-context"
    assert result.accepted_schema_versions == ("1.0", "1.1")
    assert result.filter_mode is PresenceContextSubscriptionFilter.COMPLETE_ONLY


def test_subscription_id_is_deterministic():
    request = subscription_request()
    first = PresenceContextSubscriptionEngine().subscribe(request, now=NOW)
    second = PresenceContextSubscriptionEngine().subscribe(request, now=NOW)
    assert first.subscription_id == second.subscription_id


def test_repository_stores_result():
    repository = InMemoryPresenceContextSubscriptionRepository()
    result = PresenceContextSubscriptionEngine(repository=repository).subscribe(
        subscription_request(), now=NOW
    )
    assert repository.get(result.subscription_id) == result
    assert repository.list_all() == (result,)


def test_repository_rejects_duplicate():
    repository = InMemoryPresenceContextSubscriptionRepository()
    result = PresenceContextSubscriptionEngine(repository=repository).subscribe(
        subscription_request(), now=NOW
    )
    with pytest.raises(ValueError, match="already exists"):
        repository.add(result)


def test_result_is_immutable():
    with pytest.raises(FrozenInstanceError):
        subscribe().confidence = 0.1


@pytest.mark.parametrize("owner", ["", " ", "\t"])
def test_blank_owner_is_rejected(owner):
    with pytest.raises(ValueError, match="owner"):
        subscription_request(owner=owner)


@pytest.mark.parametrize("subscriber", ["", " ", "\t"])
def test_blank_subscriber_is_rejected(subscriber):
    with pytest.raises(ValueError, match="subscriber"):
        subscription_request(subscriber_id=subscriber)


def test_blank_topic_is_rejected():
    with pytest.raises(ValueError, match="topic"):
        subscription_request(accepted_topic=" ")


@pytest.mark.parametrize("versions", [(), ("",), ("1.0", " ")])
def test_blank_schema_versions_are_rejected(versions):
    with pytest.raises(ValueError, match="schema versions"):
        subscription_request(accepted_schema_versions=versions)


@pytest.mark.parametrize("value", [0, -1])
def test_policy_requires_positive_result_limit(value):
    with pytest.raises(ValueError, match="limit"):
        PresenceContextSubscriptionPolicy(maximum_results=value)


@pytest.mark.parametrize("value", [timedelta(0), timedelta(seconds=-1)])
def test_policy_requires_positive_age(value):
    with pytest.raises(ValueError, match="age"):
        PresenceContextSubscriptionPolicy(maximum_result_age=value)


@pytest.mark.parametrize("value", [-0.1, 1.1])
def test_policy_rejects_invalid_confidence(value):
    with pytest.raises(ValueError, match="confidence"):
        PresenceContextSubscriptionPolicy(minimum_confidence=value)


def test_naive_now_is_rejected():
    with pytest.raises(ValueError, match="timezone-aware"):
        subscribe(now=datetime(2026, 7, 11, 23, 0))


@pytest.mark.parametrize(
    "field",
    [
        "delivery_allowed",
        "callback_invocation_allowed",
        "consumer_processing_allowed",
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
    result = subscribe()
    assert getattr(result, field) is False
    with pytest.raises(ValueError, match="cannot authorize"):
        replace(result, **{field: True}, subscription_id="")


def test_subscription_does_not_mutate_source_publication():
    source = publish()
    before = source.publication_id
    result = subscribe(source)
    assert source.publication_id == before
    assert result.source_publication is source


def test_subscription_does_not_deliver_or_process_context():
    result = subscribe()
    assert not result.delivery_allowed
    assert not result.callback_invocation_allowed
    assert not result.consumer_processing_allowed


def test_inactive_result_exposes_no_subscription_metadata():
    result = subscribe(subscription_declared=False)
    assert result.source_publication is None
    assert result.subscriber_id is None
    assert result.accepted_topic is None
    assert result.accepted_schema_versions == ()
    assert result.filter_mode is None
    assert result.lifecycle is None


def test_tampered_id_is_rejected():
    with pytest.raises(ValueError, match="id is inconsistent"):
        replace(subscribe(), subscription_id="tampered")
