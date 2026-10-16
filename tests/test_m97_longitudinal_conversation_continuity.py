from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone

import pytest

from core.living_conversation import (
    ContinuityAssessment,
    ContinuityRecommendation,
    ConversationEpisode,
    ConversationOpportunityKind,
    ConversationThread,
    ConversationThreadStatus,
    InMemoryContinuityAssessmentRepository,
    InMemoryConversationThreadRepository,
    LivingConversationContext,
    LongitudinalContinuityPolicy,
    LongitudinalConversationContinuity,
)

NOW = datetime(2026, 7, 15, 15, 0, tzinfo=timezone.utc)
PAST = NOW - timedelta(days=7)


def episode(**changes: object) -> ConversationEpisode:
    base = ConversationEpisode(
        owner="Carlos",
        topic_key="paciencia-inteligencia",
        summary="La paciencia puede ser una forma de inteligencia práctica.",
        source_reference_ids=("memory:42",),
        occurred_at=PAST,
        reflection_id="reflection:96",
    )
    return replace(base, episode_id="", **changes)


def context(**changes: object) -> LivingConversationContext:
    base = LivingConversationContext(owner="Carlos", mode="home")
    return replace(base, **changes)


def thread() -> ConversationThread:
    return LongitudinalConversationContinuity().record(
        episode(), title="Paciencia e inteligencia"
    )


def test_episode_has_deterministic_identifier() -> None:
    assert episode().episode_id == episode().episode_id


def test_episode_requires_timezone() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        episode(occurred_at=datetime(2026, 7, 8, 15, 0))


def test_episode_requires_source() -> None:
    with pytest.raises(ValueError, match="at least one source"):
        episode(source_reference_ids=())


def test_episode_rejects_duplicate_sources() -> None:
    with pytest.raises(ValueError, match="unique"):
        episode(source_reference_ids=("memory:42", "memory:42"))


def test_content_fingerprint_normalizes_case_and_space() -> None:
    first = episode(summary="Una Idea   Importante")
    second = episode(summary=" una idea importante ")
    assert first.content_fingerprint == second.content_fingerprint


def test_record_creates_open_thread() -> None:
    item = thread()
    assert item.status is ConversationThreadStatus.OPEN
    assert item.latest_episode == episode()
    assert item.title == "Paciencia e inteligencia"


def test_thread_identifier_is_owner_and_topic_stable() -> None:
    first = thread()
    second = ConversationThread(
        owner=first.owner,
        topic_key=first.topic_key,
        title="Otro título",
        status="dormant",
        episodes=first.episodes,
        opened_at=first.opened_at,
        updated_at=first.updated_at,
    )
    assert first.thread_id == second.thread_id


def test_record_appends_episode_chronologically() -> None:
    service = LongitudinalConversationContinuity()
    first = service.record(episode())
    second_episode = episode(
        summary="Esperar también permite observar mejor.",
        occurred_at=PAST + timedelta(days=1),
        source_reference_ids=("conversation:7",),
    )
    updated = service.record(second_episode)
    assert updated.thread_id == first.thread_id
    assert updated.episodes == (episode(), second_episode)


def test_record_rejects_older_episode() -> None:
    service = LongitudinalConversationContinuity()
    service.record(episode())
    with pytest.raises(ValueError, match="precede"):
        service.record(episode(occurred_at=PAST - timedelta(seconds=1)))


def test_record_rejects_exact_duplicate() -> None:
    service = LongitudinalConversationContinuity()
    service.record(episode())
    with pytest.raises(ValueError, match="already exists"):
        service.record(episode())


def test_record_rejects_repeated_latest_content() -> None:
    service = LongitudinalConversationContinuity()
    service.record(episode())
    with pytest.raises(ValueError, match="repeats latest content"):
        service.record(
            episode(
                summary=" la paciencia puede ser una forma de inteligencia práctica. ",
                occurred_at=PAST + timedelta(days=1),
                source_reference_ids=("conversation:8",),
            )
        )


def test_closed_thread_rejects_new_episode() -> None:
    service = LongitudinalConversationContinuity()
    closed = service.transition(service.record(episode()), "closed")
    assert closed.status is ConversationThreadStatus.CLOSED
    with pytest.raises(ValueError, match="cannot receive"):
        service.record(
            episode(
                summary="Nueva observación.",
                occurred_at=PAST + timedelta(days=1),
            )
        )


def test_episode_capacity_keeps_recent_history() -> None:
    service = LongitudinalConversationContinuity(
        policy=LongitudinalContinuityPolicy(maximum_episodes=2)
    )
    service.record(episode(summary="Uno"))
    service.record(episode(summary="Dos", occurred_at=PAST + timedelta(days=1)))
    updated = service.record(
        episode(summary="Tres", occurred_at=PAST + timedelta(days=2))
    )
    assert tuple(item.summary for item in updated.episodes) == ("Dos", "Tres")


def test_assess_produces_resume_opportunity() -> None:
    assessment = LongitudinalConversationContinuity().assess(
        thread(), context(), now=NOW
    )
    assert assessment.recommendation is ContinuityRecommendation.RESUME
    assert assessment.opportunity is not None
    assert assessment.opportunity.kind is ConversationOpportunityKind.RESUME
    assert assessment.opportunity.content_hint == thread().latest_episode.summary


def test_resume_preserves_latest_sources() -> None:
    item = thread()
    assessment = LongitudinalConversationContinuity().assess(item, context(), now=NOW)
    assert assessment.opportunity is not None
    assert assessment.opportunity.source_reference_ids == (
        item.latest_episode.source_reference_ids
    )


def test_too_recent_thread_is_held() -> None:
    item = LongitudinalConversationContinuity().record(
        episode(occurred_at=NOW - timedelta(hours=4))
    )
    assessment = LongitudinalConversationContinuity().assess(item, context(), now=NOW)
    assert assessment.recommendation is ContinuityRecommendation.HOLD
    assert assessment.opportunity is None


def test_expired_thread_is_not_resumed() -> None:
    item = LongitudinalConversationContinuity().record(
        episode(occurred_at=NOW - timedelta(days=121))
    )
    assessment = LongitudinalConversationContinuity().assess(item, context(), now=NOW)
    assert assessment.recommendation is ContinuityRecommendation.DO_NOT_RESUME


@pytest.mark.parametrize("status", ["resolved", "closed"])
def test_terminal_thread_is_not_resumed(status: str) -> None:
    service = LongitudinalConversationContinuity()
    item = service.transition(service.record(episode()), status)
    result = service.assess(item, context(), now=NOW)
    assert result.recommendation is ContinuityRecommendation.DO_NOT_RESUME


@pytest.mark.parametrize(
    "changes",
    [
        {"do_not_disturb": True},
        {"user_present": False},
        {"guests_present": True, "mode": "guests"},
    ],
)
def test_presence_or_guests_hold_resume(changes: dict[str, object]) -> None:
    result = LongitudinalConversationContinuity().assess(
        thread(), context(**changes), now=NOW
    )
    assert result.recommendation is ContinuityRecommendation.HOLD
    assert result.opportunity is None


def test_sensitive_context_requires_review() -> None:
    result = LongitudinalConversationContinuity().assess(
        thread(), context(sensitive_context=True), now=NOW
    )
    assert result.recommendation is ContinuityRecommendation.REVIEW_REQUIRED
    assert result.opportunity is None


def test_same_episode_is_not_proposed_twice() -> None:
    service = LongitudinalConversationContinuity()
    item = service.record(episode())
    first = service.assess(item, context(), now=NOW)
    second = service.assess(item, context(), now=NOW + timedelta(minutes=1))
    assert first.recommendation is ContinuityRecommendation.RESUME
    assert second.recommendation is ContinuityRecommendation.ALREADY_PROPOSED


def test_new_episode_allows_new_resume_assessment() -> None:
    service = LongitudinalConversationContinuity()
    item = service.record(episode())
    service.assess(item, context(), now=NOW)
    updated = service.record(
        episode(
            summary="Una semana después, la idea se conectó con una decisión.",
            source_reference_ids=("conversation:9",),
            occurred_at=NOW + timedelta(days=1),
        )
    )
    result = service.assess(updated, context(), now=NOW + timedelta(days=4))
    assert result.recommendation is ContinuityRecommendation.RESUME


def test_resume_budget_is_enforced() -> None:
    policy = LongitudinalContinuityPolicy(maximum_resume_count=1)
    service = LongitudinalConversationContinuity(policy=policy)
    item = service.mark_resumed(service.record(episode()))
    result = service.assess(item, context(), now=NOW)
    assert result.recommendation is ContinuityRecommendation.DO_NOT_RESUME
    assert result.rationale == ("thread_resume_budget_exhausted",)


def test_mark_resumed_increments_counter() -> None:
    service = LongitudinalConversationContinuity()
    item = service.record(episode())
    updated = service.mark_resumed(item)
    assert updated.resume_count == 1
    assert service.thread_repository.get(item.thread_id) == updated


def test_context_owner_must_match() -> None:
    with pytest.raises(ValueError, match="owner must match"):
        LongitudinalConversationContinuity().assess(
            thread(), LivingConversationContext(owner="Cristina"), now=NOW
        )


def test_future_thread_cannot_be_assessed() -> None:
    item = LongitudinalConversationContinuity().record(
        episode(occurred_at=NOW + timedelta(days=1))
    )
    with pytest.raises(ValueError, match="before latest episode"):
        LongitudinalConversationContinuity().assess(item, context(), now=NOW)


def test_naive_assessment_time_is_rejected() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        LongitudinalConversationContinuity().assess(
            thread(), context(), now=datetime(2026, 7, 15, 15, 0)
        )


def test_assessment_repository_persists_result() -> None:
    repository = InMemoryContinuityAssessmentRepository()
    service = LongitudinalConversationContinuity(assessment_repository=repository)
    item = service.record(episode())
    assessment = service.assess(item, context(), now=NOW)
    assert repository.list_for_thread(item.thread_id) == (assessment,)


def test_thread_repository_rejects_backward_revision() -> None:
    repository = InMemoryConversationThreadRepository()
    current = thread()
    repository.save(current)
    older_episode = episode(occurred_at=PAST - timedelta(days=1))
    older = ConversationThread(
        owner=current.owner,
        topic_key=current.topic_key,
        title=current.title,
        status=current.status,
        episodes=(older_episode,),
        opened_at=older_episode.occurred_at,
        updated_at=older_episode.occurred_at,
    )
    with pytest.raises(ValueError, match="move backwards"):
        repository.save(older)


def test_assessment_is_immutable() -> None:
    result = LongitudinalConversationContinuity().assess(thread(), context(), now=NOW)
    with pytest.raises(FrozenInstanceError):
        result.rationale = ("changed",)  # type: ignore[misc]


def test_non_resume_assessment_cannot_contain_opportunity() -> None:
    item = thread()
    resume = LongitudinalConversationContinuity().assess(item, context(), now=NOW)
    assert resume.opportunity is not None
    with pytest.raises(ValueError, match="non-resume"):
        ContinuityAssessment(
            thread=item,
            context=context(),
            recommendation="hold",
            rationale=("test",),
            opportunity=resume.opportunity,
            latest_episode_id=item.latest_episode.episode_id,
            assessed_at=NOW,
        )


def test_policy_requires_ordered_gaps() -> None:
    with pytest.raises(ValueError, match="must exceed"):
        LongitudinalContinuityPolicy(
            minimum_resume_gap=timedelta(days=2),
            maximum_resume_gap=timedelta(days=2),
        )


def test_system_prompt_preserves_non_execution_boundary() -> None:
    lines = LongitudinalConversationContinuity.system_prompt_lines()
    assert any("sin hablar" in line for line in lines)
    assert any("No inventa contexto" in line for line in lines)
    assert any("M93" in line and "M96" in line for line in lines)
