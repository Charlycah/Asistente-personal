from dataclasses import FrozenInstanceError, replace
from datetime import timedelta

import pytest

from core.living_conversation_conversation_candidate import (
    InMemoryLivingConversationConversationCandidateRepository,
    LivingConversationConversationCandidate,
    LivingConversationConversationCandidateAction,
    LivingConversationConversationCandidateConfig,
    LivingConversationConversationCandidateRequest,
    LivingConversationConversationCandidateStatus,
)
from tests.test_m142_presence_context_publication import NOW
from tests.test_m154_living_conversation_conversation_eligibility_decision import (
    assess as decision,
)
from tests.test_m154_living_conversation_conversation_eligibility_decision import (
    not_ready,
    partial_readiness,
)


def partial_decision():
    return decision(results=(partial_readiness(),))


def not_eligible_decision():
    return decision(results=(not_ready(),))


def request(*, results=(), owner="Carlos", **changes):
    if not results:
        results = (decision(),)
    values = {"owner": owner, "decision_results": results}
    values.update(changes)
    return LivingConversationConversationCandidateRequest(**values)


def build(*, results=(), owner="Carlos", config=None, now=NOW, **changes):
    return LivingConversationConversationCandidate(config=config).build(
        request(results=results, owner=owner, **changes), now=now
    )


def test_eligible_builds_candidate():
    result = build()
    assert result.status is LivingConversationConversationCandidateStatus.CANDIDATE
    assert (
        result.action is LivingConversationConversationCandidateAction.BUILD_CANDIDATE
    )
    assert result.candidate_available
    assert not result.partial_context
    assert not result.withheld


def test_partial_eligible_builds_partial_candidate():
    result = build(results=(partial_decision(),))
    assert (
        result.status is LivingConversationConversationCandidateStatus.CANDIDATE_PARTIAL
    )
    assert (
        result.action
        is LivingConversationConversationCandidateAction.BUILD_PARTIAL_CANDIDATE
    )
    assert result.candidate_available
    assert result.partial_context


def test_not_eligible_is_withheld():
    result = build(results=(not_eligible_decision(),))
    assert result.status is LivingConversationConversationCandidateStatus.WITHHELD
    assert (
        result.action
        is LivingConversationConversationCandidateAction.WITHHOLD_CANDIDATE
    )
    assert result.withheld
    assert not result.candidate_available


def test_full_beats_partial_and_withheld():
    full = decision()
    result = build(results=(not_eligible_decision(), partial_decision(), full))
    assert result.selected_decision is full


def test_partial_beats_withheld():
    partial = partial_decision()
    assert (
        build(results=(not_eligible_decision(), partial)).selected_decision is partial
    )


def test_confidence_breaks_same_status_tie():
    low = decision()
    high = replace(low, confidence=0.95, decision_id="")
    assert build(results=(low, high)).selected_decision is high


def test_recency_breaks_same_status_and_confidence_tie():
    old = decision()
    new = replace(old, created_at=NOW + timedelta(minutes=1), decision_id="")
    assert (
        build(results=(old, new), now=NOW + timedelta(minutes=2)).selected_decision
        is new
    )


def test_not_requested_is_not_applicable():
    assert (
        build(candidate_requested=False).status
        is LivingConversationConversationCandidateStatus.NOT_APPLICABLE
    )


def test_owner_mismatch_is_blocked():
    assert (
        build(owner="Other").status
        is LivingConversationConversationCandidateStatus.BLOCKED
    )


def test_empty_input_is_not_applicable():
    result = LivingConversationConversationCandidate().build(
        LivingConversationConversationCandidateRequest(
            owner="Carlos", decision_results=()
        ),
        now=NOW,
    )
    assert result.status is LivingConversationConversationCandidateStatus.NOT_APPLICABLE


def test_result_limit_is_enforced():
    source = decision()
    result = build(
        results=(source, source),
        config=LivingConversationConversationCandidateConfig(
            maximum_decision_results=1
        ),
    )
    assert result.status is LivingConversationConversationCandidateStatus.BLOCKED


def test_stale_only_requires_review():
    source = replace(decision(), created_at=NOW - timedelta(hours=3), decision_id="")
    assert (
        build(results=(source,)).status
        is LivingConversationConversationCandidateStatus.REVIEW_REQUIRED
    )


def test_future_only_requires_review():
    source = replace(decision(), created_at=NOW + timedelta(minutes=1), decision_id="")
    assert (
        build(results=(source,)).status
        is LivingConversationConversationCandidateStatus.REVIEW_REQUIRED
    )


def test_low_confidence_only_requires_review():
    source = replace(decision(), confidence=0.69, decision_id="")
    assert (
        build(results=(source,)).status
        is LivingConversationConversationCandidateStatus.REVIEW_REQUIRED
    )


def test_partial_can_require_review():
    result = build(
        results=(partial_decision(),),
        config=LivingConversationConversationCandidateConfig(
            allow_partial_context=False
        ),
    )
    assert (
        result.status is LivingConversationConversationCandidateStatus.REVIEW_REQUIRED
    )


def test_duplicate_is_deduplicated():
    source = decision()
    assert build(results=(source, source)).selected_decision is source


def test_sources_are_preserved_exactly():
    source = decision()
    result = build(results=(source,))
    assert result.selected_decision is source
    assert result.selected_opportunity is source.selected_opportunity


def test_confidence_is_source_confidence():
    result = build()
    assert result.confidence == result.selected_decision.confidence


def test_id_is_deterministic():
    req = request()
    first = LivingConversationConversationCandidate().build(req, now=NOW)
    second = LivingConversationConversationCandidate().build(req, now=NOW)
    assert first.candidate_id == second.candidate_id


def test_repository_round_trip():
    repository = InMemoryLivingConversationConversationCandidateRepository()
    result = LivingConversationConversationCandidate(repository=repository).build(
        request(), now=NOW
    )
    assert repository.get(result.candidate_id) is result
    assert repository.list_all() == (result,)


def test_repository_rejects_duplicate():
    repository = InMemoryLivingConversationConversationCandidateRepository()
    result = LivingConversationConversationCandidate(repository=repository).build(
        request(), now=NOW
    )
    with pytest.raises(ValueError, match="already exists"):
        repository.add(result)


def test_result_is_immutable():
    with pytest.raises(FrozenInstanceError):
        build().confidence = 0.1


def test_request_normalizes_owner_and_tuple():
    source = decision()
    req = LivingConversationConversationCandidateRequest(
        owner="  Carlos  ", decision_results=[source]
    )
    assert req.owner == "Carlos"
    assert req.decision_results == (source,)


@pytest.mark.parametrize("owner", ["", "   "])
def test_blank_owner_is_rejected(owner):
    with pytest.raises(ValueError, match="owner"):
        LivingConversationConversationCandidateRequest(owner=owner, decision_results=())


@pytest.mark.parametrize(
    "changes",
    [
        {"maximum_decision_results": 0},
        {"maximum_result_age": timedelta(0)},
        {"minimum_confidence": -0.1},
        {"minimum_confidence": 1.1},
    ],
)
def test_invalid_config_is_rejected(changes):
    with pytest.raises(ValueError):
        LivingConversationConversationCandidateConfig(**changes)


def test_naive_now_is_rejected():
    with pytest.raises(ValueError, match="timezone-aware"):
        LivingConversationConversationCandidate().build(
            request(), now=NOW.replace(tzinfo=None)
        )


def test_review_requires_confirmation():
    source = replace(decision(), confidence=0.1, decision_id="")
    assert build(results=(source,)).confirmation_required


@pytest.mark.parametrize(
    "field",
    [
        "conversation_start_allowed",
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
    assert getattr(build(), field) is False


def test_result_rejects_capability_authorization():
    result = build()
    with pytest.raises(ValueError, match="cannot authorize"):
        replace(result, conversation_start_allowed=True, candidate_id="")


def test_result_rejects_wrong_candidate_id():
    with pytest.raises(ValueError, match="id is inconsistent"):
        replace(build(), candidate_id="wrong")


def test_active_result_requires_sources():
    result = build()
    with pytest.raises(ValueError, match="requires source"):
        replace(result, selected_decision=None, candidate_id="")


def test_active_result_requires_matching_opportunity():
    result = build()
    other = partial_decision().selected_opportunity
    with pytest.raises(ValueError, match="must come from"):
        replace(result, selected_opportunity=other, candidate_id="")


def test_inactive_result_cannot_expose_active_values():
    inactive = build(candidate_requested=False)
    with pytest.raises(ValueError, match="inactive candidate"):
        replace(inactive, confidence=0.8, candidate_id="")


def test_rationale_is_non_empty():
    assert all(item.strip() for item in build().rationale)


def test_decision_request_is_preserved():
    req = request()
    assert LivingConversationConversationCandidate().build(req, now=NOW).request is req
