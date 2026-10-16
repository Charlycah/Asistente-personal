from datetime import UTC, datetime, timedelta
from pathlib import Path

from core.cognitive_intent import CognitiveIntentAnalyzer
from core.cognitive_memory import LearningAction, LearningCandidate, LearningCategory
from core.cognitive_memory_integration import CognitiveMemoryIntegration
from core.cognitive_memory_recall import (
    CognitiveMemoryRecall,
    CognitiveMemoryRecallRequest,
    SessionContinuityReason,
)
from core.cognitive_memory_store import (
    CognitiveMemorySearch,
    CognitiveMemoryStore,
    CognitiveMemoryStoreConfig,
)
from core.conversation_strategy import ConversationStrategyPlanner
from core.personal_identity_and_session_profiles.models import RuntimeSessionProfile


def _store(tmp_path: Path) -> CognitiveMemoryStore:
    return CognitiveMemoryStore(
        CognitiveMemoryStoreConfig(db_path=tmp_path / "brain.sqlite3")
    )


def _session(session_id: str, profile_id: str = "carlos") -> RuntimeSessionProfile:
    now = datetime.now(UTC)
    return RuntimeSessionProfile(
        session_id=session_id,
        profile_id=profile_id,
        created_at=now - timedelta(minutes=5),
        last_active_at=now,
    )


def _candidate(
    content: str,
    *,
    session_id: str | None = None,
    profile_id: str | None = None,
) -> LearningCandidate:
    metadata = {"source": "test"}
    if session_id is not None:
        metadata["session_id"] = session_id
    if profile_id is not None:
        metadata["profile_id"] = profile_id
    return LearningCandidate(
        content=content,
        category=LearningCategory.PROJECT_CONVENTION,
        action=LearningAction.STORE,
        confidence=0.8,
        reason="project_convention_is_reusable",
        tags=("project_convention", "project_work", "project_focused"),
        metadata=metadata,
    )


def _request(text: str, session: RuntimeSessionProfile):
    intent = CognitiveIntentAnalyzer().analyze(text)
    strategy = ConversationStrategyPlanner().plan(intent)
    return CognitiveMemoryRecallRequest(
        text=text,
        intent_result=intent,
        strategy=strategy,
        session_profile=session,
    )


def test_integration_records_canonical_session_provenance(tmp_path):
    store = _store(tmp_path)
    session = _session("session-a")

    result = CognitiveMemoryIntegration(store).process_turn(
        "En ROBY usamos Ruff y pytest antes del commit",
        session_profile=session,
    )

    assert result.session_profile is session
    assert result.stored_memory_ids
    memory = store.search(CognitiveMemorySearch(query="ruff"))[0]
    assert memory.metadata["session_id"] == "session-a"
    assert memory.metadata["profile_id"] == "carlos"


def test_relevant_memory_continues_across_sessions_of_same_profile(tmp_path):
    store = _store(tmp_path)
    integration = CognitiveMemoryIntegration(store)
    first = _session("session-a")
    second = _session("session-b")
    integration.process_turn(
        "En ROBY usamos Ruff y pytest antes del commit",
        session_profile=first,
    )

    result = integration.process_turn(
        "Recordemos Ruff y pytest para el milestone",
        session_profile=second,
        enable_learning=False,
    )

    decision = result.recall_result.continuity_decision
    assert result.recall_result.should_use_memory is True
    assert decision is not None
    assert decision.reason is SessionContinuityReason.CROSS_SESSION_MEMORY
    assert decision.cross_session_count == 1
    assert decision.continued_from_previous_session is True


def test_memory_from_another_profile_is_not_recalled(tmp_path):
    store = _store(tmp_path)
    store.store_candidate(
        _candidate(
            "ROBY usa Ruff y pytest antes del commit",
            session_id="session-a",
            profile_id="otro",
        )
    )

    result = CognitiveMemoryRecall(store).recall(
        _request("Recordemos Ruff y pytest", _session("session-b"))
    )

    decision = result.continuity_decision
    assert result.should_use_memory is False
    assert decision is not None
    assert decision.filtered_profile_count == 1
    assert decision.cross_session_count == 0


def test_legacy_memory_without_session_remains_compatible(tmp_path):
    store = _store(tmp_path)
    store.store_candidate(_candidate("ROBY usa Ruff y pytest antes del commit"))

    result = CognitiveMemoryRecall(store).recall(
        _request("Recordemos Ruff y pytest", _session("session-b"))
    )

    decision = result.continuity_decision
    assert result.should_use_memory is True
    assert decision is not None
    assert decision.reason is SessionContinuityReason.LEGACY_MEMORY
    assert decision.legacy_count == 1


def test_same_session_memory_is_reported_without_false_cross_session(tmp_path):
    store = _store(tmp_path)
    session = _session("session-a")
    integration = CognitiveMemoryIntegration(store)
    integration.process_turn(
        "En ROBY usamos Ruff y pytest antes del commit",
        session_profile=session,
    )

    result = integration.process_turn(
        "Recordemos Ruff y pytest",
        session_profile=session,
        enable_learning=False,
    )

    decision = result.recall_result.continuity_decision
    assert decision is not None
    assert decision.reason is SessionContinuityReason.CURRENT_SESSION_MEMORY
    assert decision.current_session_count == 1
    assert decision.cross_session_count == 0


def test_continuity_serialization_excludes_memory_content(tmp_path):
    store = _store(tmp_path)
    integration = CognitiveMemoryIntegration(store)
    integration.process_turn(
        "En ROBY usamos Ruff y pytest antes del commit",
        session_profile=_session("session-a"),
    )
    result = integration.process_turn(
        "Recordemos Ruff y pytest",
        session_profile=_session("session-b"),
        enable_learning=False,
    )

    decision = result.recall_result.continuity_decision
    assert decision is not None
    serialized = decision.as_dict()
    assert serialized["continued_from_previous_session"] is True
    assert "content" not in serialized
    assert "memory" not in serialized
