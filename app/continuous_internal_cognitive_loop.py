from __future__ import annotations

import threading
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum

from app.cognitive_agenda_manager import CognitiveAgendaManager, CognitiveAgendaSnapshot
from app.cognitive_agenda_reasoning import (
    CognitiveAgendaDeliberation,
    CognitiveAgendaReasoner,
)
from app.cognitive_episodic_memory import (
    CognitiveEpisodicMemory,
    CognitiveEpisodicMemorySnapshot,
)
from app.cognitive_hypothesis_workspace import (
    CognitiveHypothesisWorkspace,
    CognitiveHypothesisWorkspaceSnapshot,
)
from app.cognitive_reflection_engine import (
    CognitiveReflection,
    CognitiveReflectionEngine,
)
from app.cognitive_self_model import (
    CognitiveSelfModel,
    CognitiveSelfModelSnapshot,
)
from app.cognitive_thought_stream import (
    CognitiveThoughtStream,
    CognitiveThoughtStreamSnapshot,
)
from app.cognitive_world_model import (
    CognitiveWorldModel,
    CognitiveWorldModelSnapshot,
)
from app.conversational_self_analysis import ConversationalSelfAnalysisReport


class CognitiveFocus(str, Enum):
    IDLE = "idle"
    CONVERSATION_REPAIR = "conversation_repair"
    AMBIENT_AWARENESS = "ambient_awareness"
    OPEN_COMMITMENTS = "open_commitments"
    COGNITIVE_AGENDA = "cognitive_agenda"


class CognitiveLoopStatus(str, Enum):
    STOPPED = "stopped"
    RUNNING = "running"
    DEGRADED = "degraded"
    FAILED = "failed"


@dataclass(frozen=True)
class ContinuousCognitiveLoopPolicy:
    cycle_interval: timedelta = timedelta(seconds=15)
    failure_threshold: int = 3

    def __post_init__(self) -> None:
        if self.cycle_interval.total_seconds() <= 0:
            raise ValueError("cognitive cycle interval must be positive")
        if self.failure_threshold <= 0:
            raise ValueError("failure threshold must be positive")


@dataclass(frozen=True)
class ContinuousCognitiveState:
    focus: CognitiveFocus
    open_commitments: int
    ambient_activity: int
    rationale: str
    updated_at: datetime
    agenda: CognitiveAgendaSnapshot | None = None
    deliberation: CognitiveAgendaDeliberation | None = None
    reflection: CognitiveReflection | None = None
    thought_stream: CognitiveThoughtStreamSnapshot | None = None
    hypothesis_workspace: CognitiveHypothesisWorkspaceSnapshot | None = None
    world_model: CognitiveWorldModelSnapshot | None = None
    episodic_memory: CognitiveEpisodicMemorySnapshot | None = None
    self_model: CognitiveSelfModelSnapshot | None = None


@dataclass(frozen=True)
class ContinuousCognitiveLoopSnapshot:
    cycles: int
    failures: int
    running: bool
    state: ContinuousCognitiveState | None
    status: CognitiveLoopStatus = CognitiveLoopStatus.STOPPED
    last_error: str | None = None


class ContinuousInternalCognitiveLoop:
    """Own ROBY's resident, governed RP.10-RP.18 cognitive state."""

    def __init__(
        self,
        *,
        latest_self_analysis: Callable[[], ConversationalSelfAnalysisReport | None]
        | None = None,
        open_commitments: Callable[[], int] | None = None,
        ambient_activity: Callable[[], int] | None = None,
        policy: ContinuousCognitiveLoopPolicy | None = None,
        agenda_manager: CognitiveAgendaManager | None = None,
        agenda_reasoner: CognitiveAgendaReasoner | None = None,
        reflection_engine: CognitiveReflectionEngine | None = None,
        thought_stream: CognitiveThoughtStream | None = None,
        hypothesis_workspace: CognitiveHypothesisWorkspace | None = None,
        world_model: CognitiveWorldModel | None = None,
        episodic_memory: CognitiveEpisodicMemory | None = None,
        self_model: CognitiveSelfModel | None = None,
        agenda_context: Callable[[], Iterable[str]] | None = None,
    ) -> None:
        self.latest_self_analysis = latest_self_analysis or (lambda: None)
        self.open_commitments = open_commitments or (lambda: 0)
        self.ambient_activity = ambient_activity or (lambda: 0)
        self.policy = policy or ContinuousCognitiveLoopPolicy()
        self.agenda_manager = agenda_manager
        self.agenda_reasoner = agenda_reasoner or CognitiveAgendaReasoner()
        self.reflection_engine = reflection_engine or CognitiveReflectionEngine()
        self.thought_stream = thought_stream or CognitiveThoughtStream()
        self.hypothesis_workspace = (
            hypothesis_workspace or CognitiveHypothesisWorkspace()
        )
        self.world_model = world_model or CognitiveWorldModel()
        self.episodic_memory = episodic_memory or CognitiveEpisodicMemory()
        self.self_model = self_model or CognitiveSelfModel()
        self.agenda_context = agenda_context or (lambda: ())
        self._cycles = 0
        self._failures = 0
        self._consecutive_failures = 0
        self._running = False
        self._status = CognitiveLoopStatus.STOPPED
        self._last_error: str | None = None
        self._state: ContinuousCognitiveState | None = None
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._lock = threading.RLock()

    @property
    def snapshot(self) -> ContinuousCognitiveLoopSnapshot:
        with self._lock:
            thread_alive = self._thread is not None and self._thread.is_alive()
            running = self._running and thread_alive
            status = self._status
            if self._running and not thread_alive:
                status = CognitiveLoopStatus.FAILED
            return ContinuousCognitiveLoopSnapshot(
                cycles=self._cycles,
                failures=self._failures,
                running=running,
                state=self._state,
                status=status,
                last_error=self._last_error,
            )

    @property
    def current_state(self) -> ContinuousCognitiveState | None:
        """Return the immutable state published by the last completed cycle."""
        return self.snapshot.state

    def start(self) -> None:
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                return
            self._stop.clear()
            self._running = True
            self._status = CognitiveLoopStatus.RUNNING
            self._last_error = None
            self._thread = threading.Thread(
                target=self._run,
                name="roby-continuous-cognitive-loop",
                daemon=True,
            )
            self._thread.start()

    def stop(self) -> None:
        with self._lock:
            thread = self._thread
            if not self._running and thread is None:
                return
            self._stop.set()
        if thread is not None:
            thread.join(
                timeout=max(1.0, self.policy.cycle_interval.total_seconds() * 2)
            )
        with self._lock:
            self._thread = None
            self._running = False
            self._status = CognitiveLoopStatus.STOPPED

    def tick(self, *, now: datetime | None = None) -> ContinuousCognitiveState:
        timestamp = now or datetime.now(timezone.utc)
        if isinstance(self.agenda_manager, CognitiveAgendaManager):
            agenda = self.agenda_manager.refresh(
                now=timestamp, context_facts=self._agenda_context_facts()
            )
        elif self.agenda_manager is not None:
            agenda = self.agenda_manager.refresh(now=timestamp)
        else:
            agenda = None
        report = self.latest_self_analysis()
        commitments = max(0, int(self.open_commitments()))
        ambient = max(0, int(self.ambient_activity()))
        deliberation = (
            self.agenda_reasoner.deliberate(agenda, now=timestamp)
            if agenda is not None
            else None
        )
        reflection = self.reflection_engine.reflect(agenda, deliberation, now=timestamp)
        thought_stream = self.thought_stream.advance(
            agenda, deliberation, reflection, now=timestamp
        )
        hypothesis_workspace = self.hypothesis_workspace.evaluate(
            thought_stream, deliberation, reflection, now=timestamp
        )
        world_model = self.world_model.update(
            thought_stream, hypothesis_workspace, now=timestamp
        )
        episodic_memory = self.episodic_memory.remember(world_model, now=timestamp)
        if agenda is not None and agenda.effective_focus is not None:
            focus = CognitiveFocus.COGNITIVE_AGENDA
            rationale = f"agenda:{agenda.effective_focus.key}"
        else:
            focus, rationale = self._select_focus(report, commitments, ambient)
        self_model = self.self_model.assess(
            world_model,
            episodic_memory,
            deliberation,
            reflection,
            now=timestamp,
        )
        state = ContinuousCognitiveState(
            focus=focus,
            open_commitments=commitments,
            ambient_activity=ambient,
            rationale=rationale,
            updated_at=timestamp,
            agenda=agenda,
            deliberation=deliberation,
            reflection=reflection,
            thought_stream=thought_stream,
            hypothesis_workspace=hypothesis_workspace,
            world_model=world_model,
            episodic_memory=episodic_memory,
            self_model=self_model,
        )
        with self._lock:
            self._state = state
            self._cycles += 1
            self._consecutive_failures = 0
            self._last_error = None
            if self._running:
                self._status = CognitiveLoopStatus.RUNNING
        return state

    def _agenda_context_facts(self) -> tuple[str, ...]:
        facts = list(self.agenda_context())
        previous = self._state.world_model if self._state is not None else None
        if previous is not None:
            if previous.active_focus_key:
                facts.append(f"world:focus:{previous.active_focus_key}")
            if previous.leading_hypothesis_key:
                facts.append(f"world:hypothesis:{previous.leading_hypothesis_key}")
            facts.extend(
                f"world:entity:{entity.key}:{entity.status.value}"
                for entity in previous.entities
            )
        return tuple(dict.fromkeys(facts))

    @staticmethod
    def _select_focus(
        report: ConversationalSelfAnalysisReport | None,
        commitments: int,
        ambient: int,
    ) -> tuple[CognitiveFocus, str]:
        if report is not None and any(
            finding.dimension in {"repair", "context"} for finding in report.findings
        ):
            return (
                CognitiveFocus.CONVERSATION_REPAIR,
                "recent_self_analysis_requires_conversation_repair",
            )
        if ambient > 0:
            return CognitiveFocus.AMBIENT_AWARENESS, "ambient_activity_is_current"
        if commitments > 0:
            return (
                CognitiveFocus.OPEN_COMMITMENTS,
                "open_commitments_require_continuity",
            )
        return CognitiveFocus.IDLE, "no_current_cognitive_demand"

    def _record_failure(self, error: BaseException) -> None:
        with self._lock:
            self._failures += 1
            self._consecutive_failures += 1
            self._last_error = f"{type(error).__name__}: {error}"
            self._status = (
                CognitiveLoopStatus.FAILED
                if self._consecutive_failures >= self.policy.failure_threshold
                else CognitiveLoopStatus.DEGRADED
            )

    def _run(self) -> None:
        interval = self.policy.cycle_interval.total_seconds()
        try:
            while not self._stop.is_set():
                try:
                    self.tick(now=datetime.now(timezone.utc))
                except Exception as error:  # noqa: BLE001 - resident boundary isolation
                    self._record_failure(error)
                self._stop.wait(interval)
        finally:
            with self._lock:
                self._running = False
                if self._status is not CognitiveLoopStatus.STOPPED:
                    self._status = CognitiveLoopStatus.FAILED
