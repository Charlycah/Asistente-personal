from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from enum import Enum

from app.cognitive_agenda_manager import CognitiveAgendaSnapshot
from app.cognitive_agenda_reasoning import CognitiveAgendaDeliberation
from app.cognitive_reflection_engine import (
    CognitiveReflection,
    CognitiveReflectionOutcome,
)


class CognitiveThoughtThreadStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    WAITING = "waiting"
    COMPLETED = "completed"
    RELEASED = "released"


class CognitiveThoughtTransition(str, Enum):
    NO_CHANGE = "no_change"
    STARTED = "started"
    CONTINUED = "continued"
    PAUSED = "paused"
    RESUMED = "resumed"
    WAITING = "waiting"
    COMPLETED = "completed"
    RELEASED = "released"


@dataclass(frozen=True)
class CognitiveThoughtStreamPolicy:
    max_threads: int = 8
    release_after: timedelta = timedelta(hours=6)
    completion_cycles: int = 4

    def __post_init__(self) -> None:
        if self.max_threads <= 0:
            raise ValueError("thought stream max threads must be positive")
        if self.release_after.total_seconds() < 0:
            raise ValueError("thought stream release interval must not be negative")
        if self.completion_cycles <= 0:
            raise ValueError("thought stream completion cycles must be positive")


@dataclass(frozen=True)
class CognitiveThoughtThread:
    key: str
    title: str
    status: CognitiveThoughtThreadStatus
    started_at: datetime
    updated_at: datetime
    cycles: int
    confidence: float
    evidence_sources: tuple[str, ...]
    last_disposition: str
    last_reflection: str
    summary: str


@dataclass(frozen=True)
class CognitiveThoughtStreamSnapshot:
    generated_at: datetime
    active_key: str | None
    transition: CognitiveThoughtTransition
    threads: tuple[CognitiveThoughtThread, ...]
    summary: str
    rationale: str
    requires_user_authorization: bool = False


class CognitiveThoughtStream:
    """Maintain concise cognitive continuity without storing hidden reasoning."""

    def __init__(
        self,
        *,
        policy: CognitiveThoughtStreamPolicy | None = None,
    ) -> None:
        self.policy = policy or CognitiveThoughtStreamPolicy()
        self._threads: dict[str, CognitiveThoughtThread] = {}
        self._active_key: str | None = None

    def advance(
        self,
        agenda: CognitiveAgendaSnapshot | None,
        deliberation: CognitiveAgendaDeliberation | None,
        reflection: CognitiveReflection | None,
        *,
        now: datetime | None = None,
    ) -> CognitiveThoughtStreamSnapshot:
        timestamp = now or datetime.now(timezone.utc)
        self._release_expired(timestamp)
        item = agenda.effective_focus if agenda is not None else None
        transition = self._advance_focus(
            item=item,
            deliberation=deliberation,
            reflection=reflection,
            now=timestamp,
        )
        threads = tuple(
            sorted(
                self._threads.values(),
                key=lambda thread: thread.updated_at,
                reverse=True,
            )[: self.policy.max_threads]
        )
        active = self._threads.get(self._active_key or "")
        return CognitiveThoughtStreamSnapshot(
            generated_at=timestamp,
            active_key=self._active_key,
            transition=transition,
            threads=threads,
            summary=(
                active.summary
                if active is not None
                else "No hay un hilo cognitivo activo"
            ),
            rationale=self._rationale(active, transition),
        )

    def _advance_focus(
        self,
        *,
        item,
        deliberation: CognitiveAgendaDeliberation | None,
        reflection: CognitiveReflection | None,
        now: datetime,
    ) -> CognitiveThoughtTransition:
        if item is None or deliberation is None or reflection is None:
            return self._pause_active(now)
        previous_key = self._active_key
        if previous_key is not None and previous_key != item.key:
            self._pause_thread(previous_key, now)
        thread = self._threads.get(item.key)
        if thread is None:
            thread = self._new_thread(item, deliberation, reflection, now)
            transition = CognitiveThoughtTransition.STARTED
        else:
            transition = (
                CognitiveThoughtTransition.RESUMED
                if thread.status is CognitiveThoughtThreadStatus.PAUSED
                else CognitiveThoughtTransition.CONTINUED
            )
            thread = self._update_thread(
                thread,
                item,
                deliberation,
                reflection,
                now,
            )
        thread, transition = self._apply_reflection(thread, reflection, transition)
        self._threads[item.key] = thread
        self._active_key = (
            item.key if thread.status is CognitiveThoughtThreadStatus.ACTIVE else None
        )
        self._trim_threads()
        return transition

    def _new_thread(self, item, deliberation, reflection, now):
        return CognitiveThoughtThread(
            key=item.key,
            title=item.title,
            status=CognitiveThoughtThreadStatus.ACTIVE,
            started_at=now,
            updated_at=now,
            cycles=1,
            confidence=deliberation.confidence,
            evidence_sources=tuple(item.sources),
            last_disposition=deliberation.disposition.value,
            last_reflection=reflection.outcome.value,
            summary=self._summary(item.title, deliberation, reflection, 1),
        )

    def _update_thread(self, thread, item, deliberation, reflection, now):
        cycles = thread.cycles + 1
        sources = tuple(dict.fromkeys((*thread.evidence_sources, *item.sources)))
        return replace(
            thread,
            title=item.title,
            status=CognitiveThoughtThreadStatus.ACTIVE,
            updated_at=now,
            cycles=cycles,
            confidence=round((thread.confidence + deliberation.confidence) / 2, 6),
            evidence_sources=sources,
            last_disposition=deliberation.disposition.value,
            last_reflection=reflection.outcome.value,
            summary=self._summary(item.title, deliberation, reflection, cycles),
        )

    def _apply_reflection(self, thread, reflection, transition):
        if reflection.outcome is CognitiveReflectionOutcome.WAIT_FOR_CHANGE:
            return (
                replace(thread, status=CognitiveThoughtThreadStatus.WAITING),
                CognitiveThoughtTransition.WAITING,
            )
        if reflection.outcome is CognitiveReflectionOutcome.RELEASE_STALE_FOCUS:
            return (
                replace(thread, status=CognitiveThoughtThreadStatus.RELEASED),
                CognitiveThoughtTransition.RELEASED,
            )
        if (
            reflection.outcome is CognitiveReflectionOutcome.AFFIRM_FOCUS
            and thread.cycles >= self.policy.completion_cycles
            and thread.last_disposition == "observe"
        ):
            return (
                replace(thread, status=CognitiveThoughtThreadStatus.COMPLETED),
                CognitiveThoughtTransition.COMPLETED,
            )
        return thread, transition

    def _pause_active(self, now: datetime) -> CognitiveThoughtTransition:
        if self._active_key is None:
            return CognitiveThoughtTransition.NO_CHANGE
        self._pause_thread(self._active_key, now)
        self._active_key = None
        return CognitiveThoughtTransition.PAUSED

    def _pause_thread(self, key: str, now: datetime) -> None:
        thread = self._threads.get(key)
        if thread is not None and thread.status is CognitiveThoughtThreadStatus.ACTIVE:
            self._threads[key] = replace(
                thread,
                status=CognitiveThoughtThreadStatus.PAUSED,
                updated_at=now,
            )

    def _release_expired(self, now: datetime) -> None:
        for key, thread in tuple(self._threads.items()):
            if (
                thread.status
                in {
                    CognitiveThoughtThreadStatus.PAUSED,
                    CognitiveThoughtThreadStatus.WAITING,
                }
                and now - thread.updated_at > self.policy.release_after
            ):
                self._threads[key] = replace(
                    thread,
                    status=CognitiveThoughtThreadStatus.RELEASED,
                    updated_at=now,
                )

    def _trim_threads(self) -> None:
        if len(self._threads) <= self.policy.max_threads:
            return
        ordered = sorted(self._threads.values(), key=lambda item: item.updated_at)
        for thread in ordered[: len(self._threads) - self.policy.max_threads]:
            if thread.key != self._active_key:
                self._threads.pop(thread.key, None)

    @staticmethod
    def _summary(title, deliberation, reflection, cycles):
        return (
            f"{title}; ciclo {cycles}; disposición "
            f"{deliberation.disposition.value}; reflexión {reflection.outcome.value}"
        )

    @staticmethod
    def _rationale(active, transition):
        key = active.key if active is not None else "none"
        cycles = active.cycles if active is not None else 0
        return f"thought_stream:{transition.value}:{key}:cycles={cycles}"
