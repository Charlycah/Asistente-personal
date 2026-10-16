from datetime import datetime, timedelta, timezone

from app.continuous_internal_cognitive_loop import (
    CognitiveFocus,
    ContinuousCognitiveLoopPolicy,
    ContinuousInternalCognitiveLoop,
)
from app.conversational_self_analysis import (
    ConversationalSelfAnalysisReport,
    SelfAnalysisFinding,
)


def test_idle_state_when_there_is_no_current_demand():
    loop = ContinuousInternalCognitiveLoop()
    state = loop.tick(now=datetime.now(timezone.utc))
    assert state.focus is CognitiveFocus.IDLE
    assert loop.snapshot.cycles == 1


def test_open_commitments_keep_continuity_focus():
    loop = ContinuousInternalCognitiveLoop(open_commitments=lambda: 2)
    assert loop.tick().focus is CognitiveFocus.OPEN_COMMITMENTS


def test_ambient_activity_has_priority_over_commitments():
    loop = ContinuousInternalCognitiveLoop(
        open_commitments=lambda: 3,
        ambient_activity=lambda: 1,
    )
    assert loop.tick().focus is CognitiveFocus.AMBIENT_AWARENESS


def test_conversation_repair_has_highest_non_urgent_focus():
    report = ConversationalSelfAnalysisReport(
        turn=4,
        trigger_reason="user_correction",
        score=3,
        findings=(
            SelfAnalysisFinding(
                dimension="repair",
                severity="high",
                evidence="user correction",
                recommendation="repair context",
            ),
        ),
    )
    loop = ContinuousInternalCognitiveLoop(
        latest_self_analysis=lambda: report,
        open_commitments=lambda: 2,
        ambient_activity=lambda: 1,
    )
    assert loop.tick().focus is CognitiveFocus.CONVERSATION_REPAIR


def test_policy_rejects_non_positive_interval():
    try:
        ContinuousCognitiveLoopPolicy(cycle_interval=timedelta(seconds=0))
    except ValueError as error:
        assert "positive" in str(error)
    else:
        raise AssertionError("expected ValueError")


def test_snapshot_reports_thread_liveness_instead_of_stale_running_flag():
    loop = ContinuousInternalCognitiveLoop()
    loop._running = True
    snapshot = loop.snapshot
    assert snapshot.running is False
    assert snapshot.status.value == "failed"


def test_tick_publishes_state_through_direct_read_only_properties():
    loop = ContinuousInternalCognitiveLoop()
    state = loop.tick()
    assert loop.current_state is state
    assert loop.snapshot.cycles == 1


def test_unexpected_resident_failure_is_recorded_and_degrades_loop():
    loop = ContinuousInternalCognitiveLoop(
        latest_self_analysis=lambda: (_ for _ in ()).throw(KeyboardInterrupt())
    )
    try:
        loop.tick()
    except KeyboardInterrupt:
        pass
    else:
        raise AssertionError("direct tick must preserve process-level interrupts")

    loop._record_failure(RuntimeError("broken dependency"))
    snapshot = loop.snapshot
    assert snapshot.failures == 1
    assert snapshot.status.value == "degraded"
    assert snapshot.last_error == "RuntimeError: broken dependency"


def test_policy_rejects_non_positive_failure_threshold():
    try:
        ContinuousCognitiveLoopPolicy(failure_threshold=0)
    except ValueError as error:
        assert "failure threshold" in str(error)
    else:
        raise AssertionError("expected ValueError")
