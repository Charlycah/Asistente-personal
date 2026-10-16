from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta

import pytest

from core.living_conversation_opportunity_prioritization import (
    LivingConversationOpportunityPrioritizationStatus,
    LivingConversationOpportunityPriority,
)
from core.living_conversation_opportunity_selection import (
    InMemoryLivingConversationOpportunitySelectionRepository,
    LivingConversationOpportunitySelection,
    LivingConversationOpportunitySelectionAction,
    LivingConversationOpportunitySelectionConfig,
    LivingConversationOpportunitySelectionRequest,
    LivingConversationOpportunitySelectionStatus,
)
from tests.test_m142_presence_context_publication import NOW
from tests.test_m151_living_conversation_opportunity_prioritization import (
    assess as prioritization,
)


def request(*, results=(), owner="Carlos", **changes):
    if not results:
        results = (prioritization(),)
    values = {"owner": owner, "prioritization_results": results}
    values.update(changes)
    return LivingConversationOpportunitySelectionRequest(**values)


def assess(*, results=(), owner="Carlos", config=None, now=NOW, **changes):
    return LivingConversationOpportunitySelection(config=config).evaluate(
        request(results=results, owner=owner, **changes), now=now
    )


def partial_prioritization():
    source = prioritization()
    opportunity = replace(
        source.selected_opportunity,
        status="available_partial",
        action="declare_partial",
        kind="available_partial",
        partial_context=True,
        opportunity_id="",
    )
    return replace(
        source,
        status=LivingConversationOpportunityPrioritizationStatus.PRIORITIZED_PARTIAL,
        action="rank_partial",
        priority=LivingConversationOpportunityPriority.MEDIUM,
        selected_opportunity=opportunity,
        ranked_opportunities=(opportunity,),
        partial_context=True,
        prioritization_id="",
    )


def deferred_prioritization():
    source = prioritization()
    opportunity = replace(
        source.selected_opportunity,
        status="inhibited",
        action="inhibit",
        kind="inhibited_by_policy",
        opportunity_available=False,
        opportunity_inhibited=True,
        opportunity_id="",
    )
    return replace(
        source,
        status=LivingConversationOpportunityPrioritizationStatus.DEFERRED,
        action="defer",
        priority=LivingConversationOpportunityPriority.DEFERRED,
        selected_opportunity=opportunity,
        ranked_opportunities=(opportunity,),
        partial_context=False,
        deferred=True,
        prioritization_id="",
    )


def test_high_priority_opportunity_is_selected():
    result = assess()
    assert result.status is LivingConversationOpportunitySelectionStatus.SELECTED
    assert result.action is LivingConversationOpportunitySelectionAction.SELECT
    assert result.selected_prioritization is result.request.prioritization_results[0]
    assert (
        result.selected_opportunity
        is result.selected_prioritization.selected_opportunity
    )


def test_partial_opportunity_is_selected_partial():
    result = assess(results=(partial_prioritization(),))
    assert (
        result.status is LivingConversationOpportunitySelectionStatus.SELECTED_PARTIAL
    )
    assert result.action is LivingConversationOpportunitySelectionAction.SELECT_PARTIAL
    assert result.partial_context


def test_deferred_opportunity_remains_deferred():
    result = assess(results=(deferred_prioritization(),))
    assert result.status is LivingConversationOpportunitySelectionStatus.DEFERRED
    assert result.action is LivingConversationOpportunitySelectionAction.DEFER
    assert result.deferred


def test_high_beats_medium_and_deferred():
    high = prioritization()
    result = assess(results=(deferred_prioritization(), partial_prioritization(), high))
    assert result.selected_prioritization is high


def test_medium_beats_deferred():
    medium = partial_prioritization()
    result = assess(results=(deferred_prioritization(), medium))
    assert result.selected_prioritization is medium


def test_confidence_breaks_equal_priority():
    low = prioritization()
    high = replace(low, confidence=0.95, prioritization_id="")
    result = assess(results=(low, high))
    assert result.selected_prioritization is high


def test_recency_breaks_equal_priority_and_confidence():
    old = prioritization()
    new = replace(old, created_at=NOW + timedelta(minutes=1), prioritization_id="")
    result = assess(results=(old, new), now=NOW + timedelta(minutes=2))
    assert result.selected_prioritization is new


def test_not_requested_is_not_applicable():
    assert (
        assess(selection_requested=False).status
        is LivingConversationOpportunitySelectionStatus.NOT_APPLICABLE
    )


def test_owner_mismatch_is_blocked():
    assert (
        assess(owner="Other").status
        is LivingConversationOpportunitySelectionStatus.BLOCKED
    )


def test_empty_input_is_not_applicable():
    result = LivingConversationOpportunitySelection().evaluate(
        LivingConversationOpportunitySelectionRequest(
            owner="Carlos", prioritization_results=()
        ),
        now=NOW,
    )
    assert result.status is LivingConversationOpportunitySelectionStatus.NOT_APPLICABLE


def test_result_limit_is_enforced():
    source = prioritization()
    result = assess(
        results=(source, source),
        config=LivingConversationOpportunitySelectionConfig(
            maximum_prioritization_results=1
        ),
    )
    assert result.status is LivingConversationOpportunitySelectionStatus.BLOCKED


def test_stale_only_requires_review():
    source = replace(
        prioritization(), created_at=NOW - timedelta(hours=3), prioritization_id=""
    )
    assert (
        assess(results=(source,)).status
        is LivingConversationOpportunitySelectionStatus.REVIEW_REQUIRED
    )


def test_future_only_requires_review():
    source = replace(
        prioritization(), created_at=NOW + timedelta(minutes=1), prioritization_id=""
    )
    assert (
        assess(results=(source,)).status
        is LivingConversationOpportunitySelectionStatus.REVIEW_REQUIRED
    )


def test_low_confidence_only_requires_review():
    source = replace(prioritization(), confidence=0.69, prioritization_id="")
    assert (
        assess(results=(source,)).status
        is LivingConversationOpportunitySelectionStatus.REVIEW_REQUIRED
    )


def test_partial_can_require_review():
    result = assess(
        results=(partial_prioritization(),),
        config=LivingConversationOpportunitySelectionConfig(
            allow_partial_context=False
        ),
    )
    assert result.status is LivingConversationOpportunitySelectionStatus.REVIEW_REQUIRED


def test_duplicate_is_deduplicated():
    source = prioritization()
    result = assess(results=(source, source))
    assert result.selected_prioritization is source


def test_sources_are_preserved_exactly():
    source = prioritization()
    result = assess(results=(source,))
    assert result.selected_prioritization is source
    assert result.selected_opportunity is source.selected_opportunity


def test_confidence_is_selected_source_confidence():
    result = assess()
    assert result.confidence == result.selected_prioritization.confidence


def test_id_is_deterministic():
    req = request()
    first = LivingConversationOpportunitySelection().evaluate(req, now=NOW)
    second = LivingConversationOpportunitySelection().evaluate(req, now=NOW)
    assert first.selection_id == second.selection_id


def test_repository_round_trip():
    repository = InMemoryLivingConversationOpportunitySelectionRepository()
    result = LivingConversationOpportunitySelection(repository=repository).evaluate(
        request(), now=NOW
    )
    assert repository.get(result.selection_id) is result
    assert repository.list_all() == (result,)


def test_repository_rejects_duplicate():
    repository = InMemoryLivingConversationOpportunitySelectionRepository()
    result = LivingConversationOpportunitySelection(repository=repository).evaluate(
        request(), now=NOW
    )
    with pytest.raises(ValueError):
        repository.add(result)


def test_request_normalizes_owner_and_tuple():
    source = prioritization()
    req = LivingConversationOpportunitySelectionRequest(
        owner=" Carlos ", prioritization_results=[source]
    )
    assert req.owner == "Carlos"
    assert req.prioritization_results == (source,)


def test_request_rejects_blank_owner():
    with pytest.raises(ValueError):
        LivingConversationOpportunitySelectionRequest(
            owner=" ", prioritization_results=()
        )


@pytest.mark.parametrize(
    "changes",
    [
        {"maximum_prioritization_results": 0},
        {"maximum_result_age": timedelta(0)},
        {"minimum_confidence": -0.1},
        {"minimum_confidence": 1.1},
    ],
)
def test_invalid_config_is_rejected(changes):
    with pytest.raises(ValueError):
        LivingConversationOpportunitySelectionConfig(**changes)


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
    source = replace(prioritization(), confidence=0.1, prioritization_id="")
    result = assess(results=(source,))
    assert result.selected_prioritization is None
    assert result.selected_opportunity is None
    assert result.confidence == 0
    assert result.confirmation_required


def test_selection_is_deterministic_across_input_order():
    high = prioritization()
    medium = partial_prioritization()
    first = assess(results=(medium, high))
    second = assess(results=(high, medium))
    assert (
        first.selected_prioritization.prioritization_id
        == second.selected_prioritization.prioritization_id
    )


def test_deferred_selection_does_not_activate_conversation():
    result = assess(results=(deferred_prioritization(),))
    assert result.deferred
    assert not result.conversation_decision_allowed
    assert not result.conversational_activation_allowed
