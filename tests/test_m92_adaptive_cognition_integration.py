from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from core.adaptive_cognition import (
    AdaptiveCognitionCycle,
    AdaptiveCognitionManager,
    AdaptiveCognitionPolicy,
    AdaptiveCognitionStage,
    AdaptiveCognitionStageRecord,
    AdaptiveCognitionStageStatus,
    InMemoryAdaptiveCognitionCycleRepository,
)

NOW = datetime(2026, 7, 10, 22, 0, tzinfo=timezone.utc)


class EpisodeManagerStub:
    def __init__(self, episode: object | None = None) -> None:
        self.episode = episode or SimpleNamespace(episode_id="episode-1")
        self.calls = 0

    def capture_governed_reasoning(self, *args: object, **kwargs: object) -> object:
        self.calls += 1
        return self.episode


class MetaReasoningStub:
    def __init__(self, *, review: bool = False) -> None:
        self.assessment = SimpleNamespace(
            assessment_id="assessment-1", requires_review=review
        )
        self.calls = 0

    def assess(self, *args: object, **kwargs: object) -> object:
        self.calls += 1
        return self.assessment


class ReflectionStub:
    def __init__(self, *, review: bool = False) -> None:
        self.record = SimpleNamespace(record_id="reflection-1", requires_review=review)
        self.calls = 0

    def reflect(self, *args: object, **kwargs: object) -> object:
        self.calls += 1
        return self.record


def result() -> object:
    return SimpleNamespace(result_id="reasoning-1")


def test_stage_record_normalizes_enums() -> None:
    record = AdaptiveCognitionStageRecord("episodic_memory", "completed")
    assert record.stage is AdaptiveCognitionStage.EPISODIC_MEMORY
    assert record.status is AdaptiveCognitionStageStatus.COMPLETED


def test_stage_record_rejects_duplicate_references() -> None:
    with pytest.raises(ValueError):
        AdaptiveCognitionStageRecord("reflection", "completed", ("a", "a"))


def test_stage_record_rejects_blank_reference() -> None:
    with pytest.raises(ValueError):
        AdaptiveCognitionStageRecord("reflection", "completed", ("",))


def test_cycle_requires_reasoning_result() -> None:
    stage = AdaptiveCognitionStageRecord("reflection", "completed")
    with pytest.raises(ValueError):
        AdaptiveCognitionCycle("", (stage,), created_at=NOW)


def test_cycle_requires_stages() -> None:
    with pytest.raises(ValueError):
        AdaptiveCognitionCycle("reasoning", (), created_at=NOW)


def test_cycle_rejects_naive_timestamp() -> None:
    stage = AdaptiveCognitionStageRecord("reflection", "completed")
    with pytest.raises(ValueError):
        AdaptiveCognitionCycle("reasoning", (stage,), created_at=datetime(2026, 1, 1))


def test_cycle_rejects_duplicate_stages() -> None:
    stage = AdaptiveCognitionStageRecord("reflection", "completed")
    with pytest.raises(ValueError):
        AdaptiveCognitionCycle("reasoning", (stage, stage), created_at=NOW)


def test_cycle_has_stable_identity() -> None:
    stage = AdaptiveCognitionStageRecord("reflection", "completed")
    first = AdaptiveCognitionCycle("reasoning", (stage,), created_at=NOW)
    second = AdaptiveCognitionCycle("reasoning", (stage,), created_at=NOW)
    assert first.cycle_id == second.cycle_id


def test_cycle_detects_review_requirement() -> None:
    stage = AdaptiveCognitionStageRecord("meta_reasoning", "review_required")
    cycle = AdaptiveCognitionCycle("reasoning", (stage,), created_at=NOW)
    assert cycle.requires_review is True


def test_repository_rejects_duplicate_cycle() -> None:
    repository = InMemoryAdaptiveCognitionCycleRepository()
    stage = AdaptiveCognitionStageRecord("reflection", "completed")
    cycle = AdaptiveCognitionCycle("reasoning", (stage,), created_at=NOW)
    repository.add(cycle)
    with pytest.raises(ValueError):
        repository.add(cycle)


def test_policy_forbids_automatic_knowledge_evolution() -> None:
    with pytest.raises(ValueError):
        AdaptiveCognitionPolicy(allow_automatic_knowledge_evolution=True)


def test_policy_forbids_automatic_planning() -> None:
    with pytest.raises(ValueError):
        AdaptiveCognitionPolicy(allow_automatic_executive_planning=True)


def test_policy_forbids_automatic_coordination() -> None:
    with pytest.raises(ValueError):
        AdaptiveCognitionPolicy(allow_automatic_executive_coordination=True)


def test_process_reasoning_runs_safe_automatic_stages() -> None:
    episode = EpisodeManagerStub()
    meta = MetaReasoningStub()
    reflection = ReflectionStub()
    manager = AdaptiveCognitionManager(
        episodic_memory=episode,
        meta_reasoning=meta,
        adaptive_reflection=reflection,
    )
    cycle = manager.process_reasoning("question", result(), now=NOW)
    assert episode.calls == meta.calls == reflection.calls == 1
    assert len(cycle.stages) == 7


def test_process_reasoning_persists_cycle() -> None:
    repository = InMemoryAdaptiveCognitionCycleRepository()
    manager = AdaptiveCognitionManager(repository=repository)
    cycle = manager.process_reasoning("question", result(), now=NOW)
    assert repository.get(cycle.cycle_id) == cycle
    assert manager.last_cycle == cycle


def test_process_reasoning_marks_unconfigured_stages() -> None:
    cycle = AdaptiveCognitionManager().process_reasoning("question", result(), now=NOW)
    assert all(
        stage.status is AdaptiveCognitionStageStatus.NOT_CONFIGURED
        for stage in cycle.stages
    )


def test_review_from_meta_reasoning_propagates() -> None:
    manager = AdaptiveCognitionManager(meta_reasoning=MetaReasoningStub(review=True))
    cycle = manager.process_reasoning("question", result(), now=NOW)
    assert cycle.requires_review is True


def test_reflection_is_skipped_without_assessment() -> None:
    manager = AdaptiveCognitionManager(adaptive_reflection=ReflectionStub())
    cycle = manager.process_reasoning("question", result(), now=NOW)
    reflection = next(
        item for item in cycle.stages if item.stage is AdaptiveCognitionStage.REFLECTION
    )
    assert reflection.status is AdaptiveCognitionStageStatus.SKIPPED


def test_readiness_exposes_all_phase_capabilities() -> None:
    marker = object()
    manager = AdaptiveCognitionManager(
        episodic_memory=marker,
        mental_models=marker,
        meta_reasoning=marker,
        adaptive_reflection=marker,
        knowledge_evolution=marker,
        executive_planning=marker,
        executive_coordination=marker,
    )
    readiness = manager.readiness()
    assert len(readiness) == 7
    assert all(
        item.status is AdaptiveCognitionStageStatus.AVAILABLE for item in readiness
    )


def test_system_prompt_preserves_governance_boundaries() -> None:
    text = " ".join(AdaptiveCognitionManager().system_prompt_lines())
    assert "no equivale a hecho" in text
    assert "No evoluciones conocimiento" in text
    assert "trazable" in text
