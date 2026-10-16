from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import Enum

from app.cognitive_agenda_reasoning import CognitiveAgendaDeliberation
from app.cognitive_reflection_engine import CognitiveReflection
from app.cognitive_thought_stream import CognitiveThoughtStreamSnapshot


class CognitiveHypothesisStatus(str, Enum):
    CANDIDATE = "candidate"
    SUPPORTED = "supported"
    CROBYLENGED = "challenged"
    SUSPENDED = "suspended"
    REJECTED = "rejected"


class CognitiveHypothesisTransition(str, Enum):
    NO_CHANGE = "no_change"
    CREATED = "created"
    UPDATED = "updated"
    REORDERED = "reordered"
    SUSPENDED = "suspended"
    CLEARED = "cleared"


@dataclass(frozen=True)
class CognitiveHypothesisWorkspacePolicy:
    max_hypotheses: int = 4
    support_threshold: float = 0.7
    challenge_threshold: float = 0.4
    confidence_step: float = 0.08

    def __post_init__(self) -> None:
        if self.max_hypotheses <= 0:
            raise ValueError("hypothesis workspace max hypotheses must be positive")
        for name, value in (
            ("support threshold", self.support_threshold),
            ("challenge threshold", self.challenge_threshold),
            ("confidence step", self.confidence_step),
        ):
            if not 0 <= value <= 1:
                raise ValueError(f"hypothesis {name} must be between zero and one")
        if self.challenge_threshold > self.support_threshold:
            raise ValueError("challenge threshold must not exceed support threshold")


@dataclass(frozen=True)
class CognitiveHypothesis:
    key: str
    thread_key: str
    proposition: str
    status: CognitiveHypothesisStatus
    confidence: float
    evidence_sources: tuple[str, ...]
    created_at: datetime
    updated_at: datetime
    revisions: int
    summary: str


@dataclass(frozen=True)
class CognitiveHypothesisWorkspaceSnapshot:
    generated_at: datetime
    active_thread_key: str | None
    leading_key: str | None
    transition: CognitiveHypothesisTransition
    hypotheses: tuple[CognitiveHypothesis, ...]
    summary: str
    rationale: str
    requires_user_authorization: bool = False


class CognitiveHypothesisWorkspace:
    """Track concise alternative interpretations without hidden reasoning."""

    def __init__(
        self,
        *,
        policy: CognitiveHypothesisWorkspacePolicy | None = None,
    ) -> None:
        self.policy = policy or CognitiveHypothesisWorkspacePolicy()
        self._hypotheses: dict[str, CognitiveHypothesis] = {}
        self._active_thread_key: str | None = None
        self._leading_key: str | None = None

    def evaluate(
        self,
        thought_stream: CognitiveThoughtStreamSnapshot | None,
        deliberation: CognitiveAgendaDeliberation | None,
        reflection: CognitiveReflection | None,
        *,
        now: datetime | None = None,
    ) -> CognitiveHypothesisWorkspaceSnapshot:
        timestamp = now or datetime.now(timezone.utc)
        thread = self._active_thread(thought_stream)
        if thread is None or deliberation is None or reflection is None:
            transition = self._suspend_active(timestamp)
        else:
            transition = self._evaluate_thread(
                thread=thread,
                deliberation=deliberation,
                reflection=reflection,
                now=timestamp,
            )
        hypotheses = self._ordered_hypotheses()
        leading = self._hypotheses.get(self._leading_key or "")
        return CognitiveHypothesisWorkspaceSnapshot(
            generated_at=timestamp,
            active_thread_key=self._active_thread_key,
            leading_key=self._leading_key,
            transition=transition,
            hypotheses=hypotheses,
            summary=(
                leading.summary
                if leading is not None
                else "No hay una hipótesis cognitiva activa"
            ),
            rationale=self._rationale(transition, leading),
        )

    @staticmethod
    def _active_thread(thought_stream):
        if thought_stream is None or thought_stream.active_key is None:
            return None
        return next(
            (
                thread
                for thread in thought_stream.threads
                if thread.key == thought_stream.active_key
            ),
            None,
        )

    def _evaluate_thread(self, *, thread, deliberation, reflection, now):
        previous_leading = self._leading_key
        self._active_thread_key = thread.key
        primary_key = f"{thread.key}:continuity"
        alternative_key = f"{thread.key}:reassessment"
        created = primary_key not in self._hypotheses
        self._upsert(
            key=primary_key,
            thread=thread,
            proposition=f"Conviene sostener el foco {thread.title}",
            confidence=deliberation.confidence,
            evidence=thread.evidence_sources,
            now=now,
        )
        if reflection.outcome.value in {
            "reassess_priority",
            "seek_more_evidence",
            "release_stale_focus",
        }:
            self._upsert(
                key=alternative_key,
                thread=thread,
                proposition=f"Conviene revisar el foco {thread.title}",
                confidence=1 - deliberation.confidence,
                evidence=thread.evidence_sources,
                now=now,
            )
        self._suspend_other_threads(thread.key, now)
        self._trim()
        self._leading_key = self._select_leading(thread.key)
        if created:
            return CognitiveHypothesisTransition.CREATED
        if previous_leading != self._leading_key:
            return CognitiveHypothesisTransition.REORDERED
        return CognitiveHypothesisTransition.UPDATED

    def _upsert(self, *, key, thread, proposition, confidence, evidence, now):
        existing = self._hypotheses.get(key)
        normalized = max(0.0, min(1.0, round(confidence, 6)))
        status = self._status(normalized)
        if existing is None:
            revisions = 1
            created_at = now
            blended = normalized
        else:
            revisions = existing.revisions + 1
            created_at = existing.created_at
            direction = normalized - existing.confidence
            step = max(
                -self.policy.confidence_step,
                min(self.policy.confidence_step, direction),
            )
            blended = round(existing.confidence + step, 6)
            status = self._status(blended)
        self._hypotheses[key] = CognitiveHypothesis(
            key=key,
            thread_key=thread.key,
            proposition=proposition,
            status=status,
            confidence=blended,
            evidence_sources=tuple(dict.fromkeys(evidence)),
            created_at=created_at,
            updated_at=now,
            revisions=revisions,
            summary=f"{proposition}; confianza {blended:.2f}; estado {status.value}",
        )

    def _status(self, confidence: float) -> CognitiveHypothesisStatus:
        if confidence >= self.policy.support_threshold:
            return CognitiveHypothesisStatus.SUPPORTED
        if confidence <= self.policy.challenge_threshold:
            return CognitiveHypothesisStatus.CROBYLENGED
        return CognitiveHypothesisStatus.CANDIDATE

    def _suspend_other_threads(self, active_key: str, now: datetime) -> None:
        for key, hypothesis in tuple(self._hypotheses.items()):
            if hypothesis.thread_key != active_key and hypothesis.status not in {
                CognitiveHypothesisStatus.REJECTED,
                CognitiveHypothesisStatus.SUSPENDED,
            }:
                self._hypotheses[key] = replace(
                    hypothesis,
                    status=CognitiveHypothesisStatus.SUSPENDED,
                    updated_at=now,
                )

    def _suspend_active(self, now: datetime) -> CognitiveHypothesisTransition:
        if self._active_thread_key is None:
            return CognitiveHypothesisTransition.NO_CHANGE
        for key, hypothesis in tuple(self._hypotheses.items()):
            if hypothesis.thread_key == self._active_thread_key:
                self._hypotheses[key] = replace(
                    hypothesis,
                    status=CognitiveHypothesisStatus.SUSPENDED,
                    updated_at=now,
                )
        self._active_thread_key = None
        self._leading_key = None
        return CognitiveHypothesisTransition.SUSPENDED

    def _select_leading(self, thread_key: str) -> str | None:
        eligible = [
            hypothesis
            for hypothesis in self._hypotheses.values()
            if hypothesis.thread_key == thread_key
            and hypothesis.status is not CognitiveHypothesisStatus.SUSPENDED
        ]
        if not eligible:
            return None
        return max(eligible, key=lambda item: (item.confidence, item.key)).key

    def _ordered_hypotheses(self) -> tuple[CognitiveHypothesis, ...]:
        return tuple(
            sorted(
                self._hypotheses.values(),
                key=lambda item: (item.confidence, item.updated_at),
                reverse=True,
            )[: self.policy.max_hypotheses]
        )

    def _trim(self) -> None:
        if len(self._hypotheses) <= self.policy.max_hypotheses:
            return
        ordered = sorted(
            self._hypotheses.values(),
            key=lambda item: (
                item.status is not CognitiveHypothesisStatus.SUSPENDED,
                item.updated_at,
            ),
        )
        for hypothesis in ordered[: len(self._hypotheses) - self.policy.max_hypotheses]:
            if hypothesis.key != self._leading_key:
                self._hypotheses.pop(hypothesis.key, None)

    @staticmethod
    def _rationale(transition, leading):
        key = leading.key if leading is not None else "none"
        return f"hypothesis_workspace:{transition.value}:{key}"
