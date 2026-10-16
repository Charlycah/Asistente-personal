from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta

import pytest

from core.living_conversation_opportunity_prioritization import (
    InMemoryLivingConversationOpportunityPrioritizationRepository,
    LivingConversationOpportunityPrioritization,
    LivingConversationOpportunityPrioritizationAction,
    LivingConversationOpportunityPrioritizationConfig,
    LivingConversationOpportunityPrioritizationRequest,
    LivingConversationOpportunityPrioritizationStatus,
    LivingConversationOpportunityPriority,
)
from core.living_conversation_presence_opportunity import (
    LivingConversationPresenceOpportunityStatus,
)
from tests.test_m142_presence_context_publication import NOW
from tests.test_m150_living_conversation_presence_opportunity import (
    assess as opportunity,
)


def request(*, results=(), owner="Carlos", **changes):
    if not results:
        results = (opportunity(),)
    values = {"owner": owner, "opportunity_results": results}
    values.update(changes)
    return LivingConversationOpportunityPrioritizationRequest(**values)


def assess(*, results=(), owner="Carlos", config=None, now=NOW, **changes):
    return LivingConversationOpportunityPrioritization(config=config).evaluate(
        request(results=results, owner=owner, **changes), now=now
    )


def partial_opportunity():
    source = opportunity()
    return replace(
        source,
        status=LivingConversationPresenceOpportunityStatus.AVAILABLE_PARTIAL,
        action="declare_partial",
        kind="available_partial",
        partial_context=True,
        opportunity_id="",
    )


def inhibited_opportunity():
    source = opportunity()
    return replace(
        source,
        status=LivingConversationPresenceOpportunityStatus.INHIBITED,
        action="inhibit",
        kind="inhibited_by_policy",
        opportunity_available=False,
        opportunity_inhibited=True,
        partial_context=False,
        opportunity_id="",
    )


def test_available_opportunity_is_prioritized_high():
    result = assess()
    assert (
        result.status is LivingConversationOpportunityPrioritizationStatus.PRIORITIZED
    )
    assert result.action is LivingConversationOpportunityPrioritizationAction.RANK
    assert result.priority is LivingConversationOpportunityPriority.HIGH
    assert result.selected_opportunity is result.ranked_opportunities[0]


def test_partial_opportunity_is_prioritized_medium():
    result = assess(results=(partial_opportunity(),))
    assert (
        result.status
        is LivingConversationOpportunityPrioritizationStatus.PRIORITIZED_PARTIAL
    )
    assert result.priority is LivingConversationOpportunityPriority.MEDIUM
    assert result.partial_context


def test_inhibited_opportunity_is_deferred():
    result = assess(results=(inhibited_opportunity(),))
    assert result.status is LivingConversationOpportunityPrioritizationStatus.DEFERRED
    assert result.priority is LivingConversationOpportunityPriority.DEFERRED
    assert result.deferred


def test_full_beats_partial_and_inhibited():
    full = opportunity()
    result = assess(results=(inhibited_opportunity(), partial_opportunity(), full))
    assert result.selected_opportunity is full
    assert result.ranked_opportunities[0] is full


def test_partial_beats_inhibited():
    partial = partial_opportunity()
    result = assess(results=(inhibited_opportunity(), partial))
    assert result.selected_opportunity is partial


def test_confidence_breaks_equal_rank():
    low = opportunity()
    high = replace(low, confidence=0.95, opportunity_id="")
    result = assess(results=(low, high))
    assert result.selected_opportunity is high


def test_latest_breaks_equal_rank_and_confidence():
    old = opportunity()
    new = replace(old, created_at=NOW + timedelta(minutes=1), opportunity_id="")
    result = assess(results=(old, new), now=NOW + timedelta(minutes=2))
    assert result.selected_opportunity is new


def test_not_requested_is_not_applicable():
    assert (
        assess(prioritization_requested=False).status
        is LivingConversationOpportunityPrioritizationStatus.NOT_APPLICABLE
    )


def test_owner_mismatch_is_blocked():
    assert (
        assess(owner="Other").status
        is LivingConversationOpportunityPrioritizationStatus.BLOCKED
    )


def test_empty_input_is_not_applicable():
    result = LivingConversationOpportunityPrioritization().evaluate(
        LivingConversationOpportunityPrioritizationRequest(
            owner="Carlos", opportunity_results=()
        ),
        now=NOW,
    )
    assert (
        result.status
        is LivingConversationOpportunityPrioritizationStatus.NOT_APPLICABLE
    )


def test_result_limit_is_enforced():
    source = opportunity()
    result = assess(
        results=(source, source),
        config=LivingConversationOpportunityPrioritizationConfig(
            maximum_opportunity_results=1
        ),
    )
    assert result.status is LivingConversationOpportunityPrioritizationStatus.BLOCKED


def test_stale_only_requires_review():
    source = replace(
        opportunity(), created_at=NOW - timedelta(hours=3), opportunity_id=""
    )
    assert (
        assess(results=(source,)).status
        is LivingConversationOpportunityPrioritizationStatus.REVIEW_REQUIRED
    )


def test_future_only_requires_review():
    source = replace(
        opportunity(), created_at=NOW + timedelta(minutes=1), opportunity_id=""
    )
    assert (
        assess(results=(source,)).status
        is LivingConversationOpportunityPrioritizationStatus.REVIEW_REQUIRED
    )


def test_low_confidence_only_requires_review():
    source = replace(opportunity(), confidence=0.69, opportunity_id="")
    assert (
        assess(results=(source,)).status
        is LivingConversationOpportunityPrioritizationStatus.REVIEW_REQUIRED
    )


def test_partial_can_require_review():
    result = assess(
        results=(partial_opportunity(),),
        config=LivingConversationOpportunityPrioritizationConfig(
            allow_partial_context=False
        ),
    )
    assert (
        result.status
        is LivingConversationOpportunityPrioritizationStatus.REVIEW_REQUIRED
    )


def test_duplicate_is_deduplicated():
    source = opportunity()
    result = assess(results=(source, source))
    assert result.ranked_opportunities == (source,)


def test_source_is_preserved_exactly():
    source = opportunity()
    assert assess(results=(source,)).selected_opportunity is source


def test_confidence_is_source_confidence():
    result = assess()
    assert result.confidence == result.selected_opportunity.confidence


def test_id_is_deterministic():
    req = request()
    first = LivingConversationOpportunityPrioritization().evaluate(req, now=NOW)
    second = LivingConversationOpportunityPrioritization().evaluate(req, now=NOW)
    assert first.prioritization_id == second.prioritization_id


def test_repository_round_trip():
    repository = InMemoryLivingConversationOpportunityPrioritizationRepository()
    result = LivingConversationOpportunityPrioritization(
        repository=repository
    ).evaluate(request(), now=NOW)
    assert repository.get(result.prioritization_id) is result
    assert repository.list_all() == (result,)


def test_repository_rejects_duplicate():
    repository = InMemoryLivingConversationOpportunityPrioritizationRepository()
    result = LivingConversationOpportunityPrioritization(
        repository=repository
    ).evaluate(request(), now=NOW)
    with pytest.raises(ValueError):
        repository.add(result)


def test_request_normalizes_owner_and_tuple():
    source = opportunity()
    req = LivingConversationOpportunityPrioritizationRequest(
        owner=" Carlos ", opportunity_results=[source]
    )
    assert req.owner == "Carlos"
    assert req.opportunity_results == (source,)


def test_request_rejects_blank_owner():
    with pytest.raises(ValueError):
        LivingConversationOpportunityPrioritizationRequest(
            owner=" ", opportunity_results=()
        )


@pytest.mark.parametrize(
    "changes",
    [
        {"maximum_opportunity_results": 0},
        {"maximum_result_age": timedelta(0)},
        {"minimum_confidence": -0.1},
        {"minimum_confidence": 1.1},
    ],
)
def test_invalid_config_is_rejected(changes):
    with pytest.raises(ValueError):
        LivingConversationOpportunityPrioritizationConfig(**changes)


def test_naive_now_is_rejected():
    with pytest.raises(ValueError):
        assess(now=datetime(2026, 7, 11))


def test_result_is_frozen():
    with pytest.raises(FrozenInstanceError):
        assess().confidence = 0.1


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


def test_review_has_no_active_values():
    source = replace(opportunity(), confidence=0.1, opportunity_id="")
    result = assess(results=(source,))
    assert result.selected_opportunity is None
    assert result.ranked_opportunities == ()
    assert result.priority is None
    assert result.confirmation_required


def test_sorting_is_deterministic_across_input_order():
    full = opportunity()
    partial = partial_opportunity()
    first = assess(results=(partial, full))
    second = assess(results=(full, partial))
    assert [x.opportunity_id for x in first.ranked_opportunities] == [
        x.opportunity_id for x in second.ranked_opportunities
    ]
