from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timezone

import pytest

from core.living_conversation import (
    ConversationActivityState,
    ConversationalFeedbackLoop,
    ConversationalFeedbackRequest,
    ConversationalFeedbackSignal,
    ConversationalPresenceEngine,
    ConversationalPresenceRequest,
    ConversationalRealizationLayer,
    ConversationalRealizationRequest,
    ConversationalRhythmRegulator,
    ConversationalRhythmRequest,
    ConversationOpportunity,
    ConversationTimingContext,
    ConversationTimingEngine,
    InMemoryIntellectualCuriosityRepository,
    IntellectualCompanionLayer,
    IntellectualCompanionRequest,
    IntellectualCuriosityEngine,
    IntellectualCuriosityKind,
    IntellectualCuriosityPlan,
    IntellectualCuriosityPolicy,
    IntellectualCuriosityPrompt,
    IntellectualCuriosityRequest,
    IntellectualCuriosityStatus,
    IntellectualInterestEvidence,
    LivingConversationContext,
    LivingConversationManager,
    ReflectionGenerator,
    SharedIntellectualInterests,
    SharedIntellectualInterestsRequest,
)

NOW = datetime(2026, 7, 11, 18, 0, tzinfo=timezone.utc)


def interest_assessment(*topics, confidence=0.9, feedback_kind="acceptance"):
    opportunity = ConversationOpportunity(
        kind="reflect",
        reason="shared inquiry",
        value_score=0.94,
        relevance_score=0.93,
        confidence=0.95,
        content_hint="ideas",
        source_reference_ids=("source:root",),
    )
    context = LivingConversationContext(owner="Carlos")
    governance = LivingConversationManager().evaluate(context, opportunity, now=NOW)
    timing = ConversationTimingEngine().evaluate(
        ConversationTimingContext(
            conversation=context,
            activity=ConversationActivityState.AVAILABLE,
            cognitive_load=0.1,
            local_hour=18,
        ),
        opportunity,
        now=NOW,
    )
    reflection = ReflectionGenerator().generate(governance, timing, now=NOW)
    contribution = IntellectualCompanionLayer().compose(
        IntellectualCompanionRequest(
            governance=governance,
            timing=timing,
            reflection=reflection,
            domain="literature",
            thesis="Ideas invite inquiry.",
            concepts=("time",),
            requested_at=NOW,
        ),
        now=NOW,
    )
    realization = ConversationalRealizationLayer().realize(
        ConversationalRealizationRequest(
            contribution=contribution,
            owner="Carlos",
            requested_at=NOW,
        ),
        now=NOW,
    )
    presence = ConversationalPresenceEngine().compose(
        ConversationalPresenceRequest(
            realization=realization,
            owner="Carlos",
            requested_at=NOW,
        ),
        now=NOW,
    )
    feedback = ConversationalFeedbackLoop().assess(
        ConversationalFeedbackRequest(
            presence=presence,
            owner="Carlos",
            signals=(
                ConversationalFeedbackSignal(
                    kind=feedback_kind,
                    origin="explicit",
                    confidence=confidence,
                    evidence="signal",
                ),
            ),
            requested_at=NOW,
        ),
        now=NOW,
    )
    rhythm = ConversationalRhythmRegulator().regulate(
        ConversationalRhythmRequest(
            feedback=feedback,
            owner="Carlos",
            requested_at=NOW,
        ),
        now=NOW,
    )
    evidence = tuple(
        IntellectualInterestEvidence(
            topic=topic,
            kind="explicit",
            confidence=confidence,
            source_reference_id=f"turn:{index}",
        )
        for index, topic in enumerate(topics or ("Borges",), 1)
    )
    return SharedIntellectualInterests().assess(
        SharedIntellectualInterestsRequest(
            rhythm=rhythm,
            owner="Carlos",
            evidence=evidence,
            requested_at=NOW,
        ),
        now=NOW,
    )


def request(*topics, **kwargs):
    return IntellectualCuriosityRequest(
        interests=interest_assessment(*topics),
        owner="Carlos",
        requested_at=NOW,
        **kwargs,
    )


def test_generates_curiosity_plan():
    result = IntellectualCuriosityEngine().generate(request("Borges"), now=NOW)
    assert result.status is IntellectualCuriosityStatus.GENERATED
    assert result.prompts


@pytest.mark.parametrize("kind", list(IntellectualCuriosityKind))
def test_requested_kind_is_generated(kind):
    topics = (
        ("Borges", "Memory")
        if kind is IntellectualCuriosityKind.CONNECTION
        else ("Borges",)
    )
    result = IntellectualCuriosityEngine().generate(
        request(*topics, requested_kinds=(kind,)),
        now=NOW,
    )
    assert result.prompts[0].kind is kind


def test_connection_has_related_topic():
    result = IntellectualCuriosityEngine().generate(
        request("Borges", "Memory", requested_kinds=("connection",)),
        now=NOW,
    )
    assert result.prompts[0].related_topic == "Memory"


def test_connection_combines_sources():
    result = IntellectualCuriosityEngine().generate(
        request("Borges", "Memory", requested_kinds=("connection",)),
        now=NOW,
    )
    assert result.prompts[0].source_reference_ids == ("turn:1", "turn:2")


def test_single_interest_cannot_generate_connection():
    result = IntellectualCuriosityEngine().generate(
        request("Borges", requested_kinds=("connection",)),
        now=NOW,
    )
    assert result.status is IntellectualCuriosityStatus.INSUFFICIENT


def test_excluded_topic_is_not_used():
    result = IntellectualCuriosityEngine().generate(
        request("Borges", excluded_topics=("borges",)),
        now=NOW,
    )
    assert result.status is IntellectualCuriosityStatus.INSUFFICIENT


def test_exclusions_are_case_insensitive():
    result = IntellectualCuriosityEngine().generate(
        request("BORGES", excluded_topics=("Borges",)),
        now=NOW,
    )
    assert result.prompts == ()


def test_maximum_prompt_limit_is_applied():
    engine = IntellectualCuriosityEngine(
        policy=IntellectualCuriosityPolicy(maximum_prompts=1)
    )
    result = engine.generate(request("Borges", "Memory"), now=NOW)
    assert len(result.prompts) == 1
    assert "curiosity_limit_applied" in result.rationale


def test_counterpoints_can_be_disabled():
    engine = IntellectualCuriosityEngine(
        policy=IntellectualCuriosityPolicy(allow_counterpoints=False)
    )
    result = engine.generate(
        request("Borges", requested_kinds=("counterpoint",)),
        now=NOW,
    )
    assert result.status is IntellectualCuriosityStatus.INSUFFICIENT


def test_explicit_interest_receives_bonus():
    result = IntellectualCuriosityEngine().generate(
        request("Borges", requested_kinds=("question",)),
        now=NOW,
    )
    assert result.prompts[0].score > result.request.interests.interests[0].score


def test_scores_are_clamped():
    result = IntellectualCuriosityEngine(
        policy=IntellectualCuriosityPolicy(explicit_bonus=1.0, core_bonus=1.0)
    ).generate(request("Borges"), now=NOW)
    assert result.prompts[0].score == 1.0


def test_prompts_are_sorted_by_score():
    result = IntellectualCuriosityEngine().generate(
        request("Borges", "Memory"), now=NOW
    )
    scores = [item.score for item in result.prompts]
    assert scores == sorted(scores, reverse=True)


def test_low_interest_score_is_insufficient():
    assessment = interest_assessment("Borges", confidence=0.5)
    result = IntellectualCuriosityEngine(
        policy=IntellectualCuriosityPolicy(minimum_interest_score=0.8, review_score=0.8)
    ).generate(
        IntellectualCuriosityRequest(assessment, "Carlos", requested_at=NOW), now=NOW
    )
    assert result.status is IntellectualCuriosityStatus.INSUFFICIENT


def test_review_interests_propagate_review():
    assessment = interest_assessment("Borges", confidence=0.5)
    result = IntellectualCuriosityEngine().generate(
        IntellectualCuriosityRequest(assessment, "Carlos", requested_at=NOW),
        now=NOW,
    )
    assert result.status is IntellectualCuriosityStatus.REVIEW_REQUIRED


@pytest.mark.parametrize("feedback_kind", ["rejection", "disengagement"])
def test_non_actionable_interests_produce_not_applicable(feedback_kind):
    assessment = interest_assessment(
        "Borges", confidence=0.2, feedback_kind=feedback_kind
    )
    result = IntellectualCuriosityEngine().generate(
        IntellectualCuriosityRequest(assessment, "Carlos", requested_at=NOW),
        now=NOW,
    )
    assert result.status is IntellectualCuriosityStatus.NOT_APPLICABLE


def test_closing_rhythm_is_recorded_without_erasing_curiosity():
    assessment = interest_assessment("Borges", feedback_kind="rejection")
    result = IntellectualCuriosityEngine().generate(
        IntellectualCuriosityRequest(assessment, "Carlos", requested_at=NOW),
        now=NOW,
    )
    assert result.prompts
    assert "rhythm_discourages_immediate_activation" in result.rationale


def test_repository_stores_plan():
    repository = InMemoryIntellectualCuriosityRepository()
    engine = IntellectualCuriosityEngine(repository=repository)
    result = engine.generate(request("Borges"), now=NOW)
    assert repository.get(result.plan_id) == result
    assert engine.last_plan == result


def test_duplicate_plan_is_rejected():
    repository = InMemoryIntellectualCuriosityRepository()
    engine = IntellectualCuriosityEngine(repository=repository)
    req = request("Borges")
    engine.generate(req, now=NOW)
    with pytest.raises(ValueError, match="already exists"):
        engine.generate(req, now=NOW)


def test_repository_lists_in_insertion_order():
    repository = InMemoryIntellectualCuriosityRepository()
    engine = IntellectualCuriosityEngine(repository=repository)
    first = engine.generate(request("Borges"), now=NOW)
    second = engine.generate(request("Memory"), now=NOW.replace(second=1))
    assert repository.list_all() == (first, second)


def test_result_is_immutable():
    result = IntellectualCuriosityEngine().generate(request("Borges"), now=NOW)
    with pytest.raises(FrozenInstanceError):
        result.status = "insufficient"


def test_prompt_is_immutable():
    prompt = (
        IntellectualCuriosityEngine().generate(request("Borges"), now=NOW).prompts[0]
    )
    with pytest.raises(FrozenInstanceError):
        prompt.score = 0.0


def test_generation_is_deterministic():
    req = request("Borges")
    first = IntellectualCuriosityEngine().generate(req, now=NOW)
    second = IntellectualCuriosityEngine().generate(req, now=NOW)
    assert first == second


def test_plan_id_detects_tampering():
    result = IntellectualCuriosityEngine().generate(request("Borges"), now=NOW)
    with pytest.raises(ValueError, match="inconsistent"):
        replace(result, plan_id="bad")


def test_owner_must_match_interests():
    with pytest.raises(ValueError, match="must match"):
        IntellectualCuriosityRequest(
            interest_assessment("Borges"), "Cristina", requested_at=NOW
        )


def test_owner_must_not_be_blank():
    with pytest.raises(ValueError, match="must not be blank"):
        IntellectualCuriosityRequest(
            interest_assessment("Borges"), " ", requested_at=NOW
        )


def test_request_timestamp_must_be_aware():
    with pytest.raises(ValueError, match="aware"):
        IntellectualCuriosityRequest(
            interest_assessment("Borges"),
            "Carlos",
            requested_at=NOW.replace(tzinfo=None),
        )


def test_generation_timestamp_must_be_aware():
    with pytest.raises(ValueError, match="aware"):
        IntellectualCuriosityEngine().generate(
            request("Borges"), now=NOW.replace(tzinfo=None)
        )


def test_requested_kinds_must_be_unique():
    with pytest.raises(ValueError, match="unique"):
        request("Borges", requested_kinds=("question", "question"))


def test_excluded_topics_must_not_be_blank():
    with pytest.raises(ValueError, match="must not be blank"):
        request("Borges", excluded_topics=(" ",))


def test_policy_rejects_invalid_ranges():
    with pytest.raises(ValueError, match="between zero and one"):
        IntellectualCuriosityPolicy(minimum_interest_score=1.1)


def test_policy_rejects_review_below_minimum():
    with pytest.raises(ValueError, match="cannot be below"):
        IntellectualCuriosityPolicy(minimum_interest_score=0.8, review_score=0.7)


def test_policy_requires_positive_limit():
    with pytest.raises(ValueError, match="positive"):
        IntellectualCuriosityPolicy(maximum_prompts=0)


def test_prompt_requires_sources():
    with pytest.raises(ValueError, match="sources"):
        IntellectualCuriosityPrompt("Borges", "question", "Why?", 0.8, ())


def test_prompt_rejects_blank_related_topic():
    with pytest.raises(ValueError, match="related"):
        IntellectualCuriosityPrompt(
            "Borges", "connection", "Connect", 0.8, ("turn:1",), related_topic=" "
        )


def test_plan_rejects_duplicate_topic_kind():
    req = request("Borges")
    prompt = IntellectualCuriosityEngine().generate(req, now=NOW).prompts[0]
    with pytest.raises(ValueError, match="unique"):
        IntellectualCuriosityPlan(
            req, "generated", (prompt, prompt), ("reason",), created_at=NOW
        )
