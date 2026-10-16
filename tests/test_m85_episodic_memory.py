from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone

import pytest

from core.adaptive_cognition import (
    Episode,
    EpisodeEvent,
    EpisodeEventKind,
    EpisodeRecallQuery,
    EpisodeReference,
    EpisodeSensitivity,
    EpisodeStatus,
    EpisodicMemoryManager,
    EpisodicMemoryPolicy,
    InMemoryEpisodeRepository,
)
from core.governed_reasoning import (
    Claim,
    ClaimCondition,
    ClaimConfidence,
    ClaimOrigin,
    ClaimRegistryManager,
    ClaimStatus,
    ClaimType,
    ConflictResolutionManager,
    DecisionRecordManager,
    EvidenceRegistry,
    GovernedContextAssembler,
    GovernedInferenceEngine,
    GovernedReasoningOrchestrator,
    InferenceRule,
    InMemoryDecisionRecordRepository,
    InMemoryInferenceRuleRegistry,
    ReasoningQuery,
)
from core.scope_guard import ScopeDomain

NOW = datetime(2026, 7, 10, 12, 0, tzinfo=timezone.utc)


def _event(content="Carlos completed the task", *, at=NOW):
    return EpisodeEvent(
        EpisodeEventKind.OUTCOME,
        content,
        occurred_at=at,
        source="test",
    )


def _closed_episode(
    title="Morning task",
    *,
    owner="Carlos",
    importance=5,
    sensitivity=EpisodeSensitivity.PERSONAL,
    tags=("task",),
    started_at=NOW,
):
    manager = EpisodicMemoryManager()
    episode = manager.start(
        title,
        owner=owner,
        tags=tags,
        importance=importance,
        sensitivity=sensitivity,
        started_at=started_at,
    )
    manager.append(episode.episode_id, _event(at=started_at))
    return manager.close(
        episode.episode_id,
        status=EpisodeStatus.COMPLETED,
        outcome="task completed",
        ended_at=started_at,
    )


def _reasoning_result(*, review=False):
    claims = ClaimRegistryManager()
    claims.register(
        Claim(
            "task",
            "status",
            "pending",
            ClaimType.ASSUMPTION,
            ClaimOrigin.HUMAN,
            ClaimStatus.REVIEW_REQUIRED if review else ClaimStatus.PROPOSED,
            confidence=ClaimConfidence(0.8, "confirmed"),
            owner="shared",
            created_at=NOW,
            claim_id="claim-task-status",
        )
    )
    assembler = GovernedContextAssembler(
        claim_registry=claims,
        evidence_registry=EvidenceRegistry(),
    )
    rules = InMemoryInferenceRuleRegistry()
    rules.register(
        InferenceRule(
            "task.pending",
            "1.0.0",
            "identify pending task",
            (ClaimCondition("status", values=("pending",)),),
            "task",
            "is_pending",
            "true",
            base_confidence=0.7,
        )
    )
    orchestrator = GovernedReasoningOrchestrator(
        context_assembler=assembler,
        inference_engine=GovernedInferenceEngine(rules),
        conflict_manager=ConflictResolutionManager(),
        decision_manager=DecisionRecordManager(InMemoryDecisionRecordRepository()),
    )
    return orchestrator.reason(
        ReasoningQuery(
            "task status",
            domains=(ScopeDomain.PERSONAL_OPERATIONS,),
            as_of=NOW,
        ),
        now=NOW,
    )


def test_episode_event_is_immutable_and_has_stable_identity():
    event = _event()
    same = _event()
    assert event.event_id == same.event_id
    with pytest.raises(FrozenInstanceError):
        event.content = "changed"  # type: ignore[misc]


def test_episode_reference_validates_fingerprint():
    with pytest.raises(ValueError):
        EpisodeReference("decision", "id", "bad")


def test_open_episode_cannot_have_end_timestamp():
    with pytest.raises(ValueError):
        Episode(
            "title",
            "Carlos",
            (ScopeDomain.PERSONAL_OPERATIONS,),
            ended_at=NOW,
            started_at=NOW,
        )


def test_completed_episode_requires_outcome():
    with pytest.raises(ValueError):
        Episode(
            "title",
            "Carlos",
            (ScopeDomain.PERSONAL_OPERATIONS,),
            status=EpisodeStatus.COMPLETED,
            ended_at=NOW,
            started_at=NOW,
        )


def test_manager_builds_append_only_revision_history():
    repository = InMemoryEpisodeRepository()
    manager = EpisodicMemoryManager(repository)
    episode = manager.start("task", owner="Carlos", started_at=NOW)
    manager.append(episode.episode_id, _event())
    closed = manager.close(
        episode.episode_id,
        status=EpisodeStatus.COMPLETED,
        outcome="done",
        ended_at=NOW,
    )
    history = repository.history(episode.episode_id)
    assert [item.revision for item in history] == [1, 2, 3]
    assert closed.supersedes_revision == 2


def test_closed_episode_rejects_new_events():
    episode = _closed_episode()
    with pytest.raises(ValueError):
        episode.append(_event("late event"))


def test_repository_rejects_non_contiguous_revision():
    repository = InMemoryEpisodeRepository()
    episode = Episode(
        "task",
        "Carlos",
        (ScopeDomain.PERSONAL_OPERATIONS,),
        started_at=NOW,
        revision=2,
        supersedes_revision=1,
    )
    with pytest.raises(ValueError):
        repository.save(episode)


def test_manager_enforces_event_capacity():
    manager = EpisodicMemoryManager(
        policy=EpisodicMemoryPolicy(max_events_per_episode=1)
    )
    episode = manager.start("task", started_at=NOW)
    manager.append(episode.episode_id, _event())
    with pytest.raises(ValueError):
        manager.append(episode.episode_id, _event("second"))


def test_recall_filters_owner_and_shared_visibility():
    repository = InMemoryEpisodeRepository()
    manager = EpisodicMemoryManager(repository)
    for owner in ("Carlos", "shared", "Cristina"):
        episode = manager.start(owner, owner=owner, started_at=NOW)
        manager.close(
            episode.episode_id,
            status=EpisodeStatus.COMPLETED,
            outcome="done",
            ended_at=NOW,
        )
    result = manager.recall(EpisodeRecallQuery(owner="Carlos"))
    assert {item.owner for item in result.episodes} == {"Carlos", "shared"}


def test_recall_excludes_sensitive_by_default():
    repository = InMemoryEpisodeRepository()
    manager = EpisodicMemoryManager(repository)
    episode = manager.start(
        "private",
        owner="Carlos",
        sensitivity=EpisodeSensitivity.SENSITIVE,
        started_at=NOW,
    )
    manager.close(
        episode.episode_id,
        status=EpisodeStatus.COMPLETED,
        outcome="done",
        ended_at=NOW,
    )
    assert not manager.recall(EpisodeRecallQuery(owner="Carlos")).episodes
    assert manager.recall(
        EpisodeRecallQuery(owner="Carlos", include_sensitive=True)
    ).episodes


def test_recall_filters_domain_status_tags_time_and_importance():
    repository = InMemoryEpisodeRepository()
    manager = EpisodicMemoryManager(repository)
    episode = manager.start(
        "important task",
        owner="Carlos",
        tags=("task", "morning"),
        importance=9,
        started_at=NOW,
    )
    manager.close(
        episode.episode_id,
        status=EpisodeStatus.COMPLETED,
        outcome="done",
        ended_at=NOW,
    )
    query = EpisodeRecallQuery(
        "task",
        owner="Carlos",
        domains=(ScopeDomain.PERSONAL_OPERATIONS,),
        tags=("task",),
        since=NOW - timedelta(minutes=1),
        until=NOW + timedelta(minutes=1),
        min_importance=8,
    )
    assert manager.recall(query).episodes[0].episode_id == episode.episode_id


def test_recall_ranks_relevance_before_importance():
    repository = InMemoryEpisodeRepository()
    manager = EpisodicMemoryManager(repository)
    relevant = manager.start("dentist appointment", importance=5, started_at=NOW)
    manager.close(
        relevant.episode_id,
        status=EpisodeStatus.COMPLETED,
        outcome="dentist booked",
        ended_at=NOW,
    )
    other = manager.start(
        "important groceries", importance=10, started_at=NOW + timedelta(seconds=1)
    )
    manager.close(
        other.episode_id,
        status=EpisodeStatus.COMPLETED,
        outcome="done",
        ended_at=NOW + timedelta(seconds=1),
    )
    result = manager.recall(EpisodeRecallQuery("dentist"))
    assert result.episodes[0].episode_id == relevant.episode_id


def test_capture_governed_reasoning_preserves_traceability():
    manager = EpisodicMemoryManager()
    result = _reasoning_result()
    episode = manager.capture_governed_reasoning("task status", result)
    assert episode is not None
    assert episode.normalized_status is EpisodeStatus.COMPLETED
    assert episode.outcome == result.decision.conclusion
    decision_event = episode.events[-1]
    reference_types = {item.reference_type for item in decision_event.references}
    assert reference_types == {
        "reasoning_result",
        "context",
        "decision",
        "explanation",
    }


def test_capture_review_required_preserves_governance():
    episode = EpisodicMemoryManager().capture_governed_reasoning(
        "task status", _reasoning_result(review=True)
    )
    assert episode is not None
    assert episode.normalized_status is EpisodeStatus.REVIEW_REQUIRED


def test_policy_can_disable_abstention_capture():
    manager = EpisodicMemoryManager(
        policy=EpisodicMemoryPolicy(capture_abstentions=False)
    )
    result = _reasoning_result()
    object.__setattr__(result, "status", "abstained")
    assert manager.capture_governed_reasoning("unknown", result) is None


def test_prompt_lines_explicitly_separate_episode_from_fact():
    lines = EpisodicMemoryManager().system_prompt_lines()
    assert any("no hechos" in line for line in lines)
    assert any("no prueban" in line for line in lines)


def test_episode_snapshot_contains_fingerprint_not_mutable_repository_state():
    episode = _closed_episode()
    snapshot = episode.to_dict()
    assert snapshot["fingerprint"] == episode.fingerprint
    assert snapshot["status"] == "completed"
    assert "repository" not in snapshot


def test_recall_query_rejects_naive_time_and_invalid_bounds():
    with pytest.raises(ValueError):
        EpisodeRecallQuery(since=datetime(2026, 7, 10, 12, 0))
    with pytest.raises(ValueError):
        EpisodeRecallQuery(min_importance=0)


def test_episode_exposes_no_learning_or_external_action():
    episode = _closed_episode()
    assert not hasattr(episode, "learn")
    assert not hasattr(episode, "execute")
    assert not hasattr(episode, "tool_call")
