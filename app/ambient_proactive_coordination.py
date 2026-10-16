from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum

from app.conversational_self_analysis import ConversationalSelfAnalysisReport


class AmbientSignalKind(str, Enum):
    CONVERSATION = "conversation"
    TELEVISION = "television"
    MUSIC = "music"
    IMPACT = "impact"
    DISTRESS = "distress"
    VISUAL_UNCERTAINTY = "visual_uncertainty"
    SILENCE = "silence"


class AmbientAction(str, Enum):
    WAIT = "wait"
    COMMENT = "comment"
    REQUEST_VISUAL_CAPTURE = "request_visual_capture"


@dataclass(frozen=True)
class AmbientObservation:
    kind: AmbientSignalKind
    confidence: float
    summary: str
    occurred_at: datetime
    involves_private_speech: bool = False
    visual_confirmation_helpful: bool = False

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("ambient confidence must be between zero and one")
        if not self.summary.strip():
            raise ValueError("ambient summary must not be blank")
        if self.occurred_at.tzinfo is None:
            raise ValueError("ambient observation time must be timezone-aware")


@dataclass(frozen=True)
class AmbientProactivePolicy:
    standing_audio_consent: bool = False
    standing_camera_consent: bool = False
    allow_private_speech_retention: bool = False
    comment_threshold: float = 0.82
    visual_threshold: float = 0.88
    comment_cooldown: timedelta = timedelta(minutes=8)
    camera_cooldown: timedelta = timedelta(minutes=5)

    def __post_init__(self) -> None:
        if not 0.0 <= self.comment_threshold <= 1.0:
            raise ValueError("comment threshold must be between zero and one")
        if not 0.0 <= self.visual_threshold <= 1.0:
            raise ValueError("visual threshold must be between zero and one")
        if self.comment_cooldown.total_seconds() <= 0:
            raise ValueError("comment cooldown must be positive")
        if self.camera_cooldown.total_seconds() <= 0:
            raise ValueError("camera cooldown must be positive")


@dataclass(frozen=True)
class AmbientProactiveDecision:
    action: AmbientAction
    rationale: str
    comment: str | None = None
    camera_reason: str | None = None
    retain_summary: bool = False
    self_analysis_considered: bool = False


@dataclass(frozen=True)
class AmbientProactiveSnapshot:
    observations: int
    comments_proposed: int
    visual_requests: int
    suppressed: int
    last_decision: AmbientProactiveDecision | None


class AmbientProactiveCoordinator:
    """Connect ambient awareness, self-analysis, initiative, and governed vision."""

    def __init__(
        self,
        policy: AmbientProactivePolicy | None = None,
        *,
        executive_presence=None,
    ) -> None:
        self.policy = policy or AmbientProactivePolicy()
        self.executive_presence = executive_presence
        self._observations = 0
        self._comments = 0
        self._visual_requests = 0
        self._suppressed = 0
        self._last_comment_at: datetime | None = None
        self._last_camera_at: datetime | None = None
        self._last_decision: AmbientProactiveDecision | None = None
        self._recent_interventions = 0

    @property
    def snapshot(self) -> AmbientProactiveSnapshot:
        return AmbientProactiveSnapshot(
            observations=self._observations,
            comments_proposed=self._comments,
            visual_requests=self._visual_requests,
            suppressed=self._suppressed,
            last_decision=self._last_decision,
        )

    def evaluate(
        self,
        observation: AmbientObservation,
        *,
        self_analysis: ConversationalSelfAnalysisReport | None = None,
        now: datetime | None = None,
    ) -> AmbientProactiveDecision:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("ambient decision time must be timezone-aware")
        self._observations += 1

        if not self.policy.standing_audio_consent:
            return self._suppress("standing_audio_consent_missing")
        if observation.involves_private_speech:
            return self._suppress("private_household_speech_requires_restraint")

        assessment = None
        if self.executive_presence is not None:
            assessment = self.executive_presence.assess(
                observation,
                self_analysis=self_analysis,
                recent_interventions=self._recent_interventions,
            )

        if self._should_request_vision(observation, timestamp) and (
            assessment is None or assessment.allow_visual_capture
        ):
            decision = AmbientProactiveDecision(
                action=AmbientAction.REQUEST_VISUAL_CAPTURE,
                rationale="visual_confirmation_is_necessary_and_governed",
                camera_reason=observation.summary,
                retain_summary=False,
                self_analysis_considered=self_analysis is not None,
            )
            self._last_camera_at = timestamp
            self._visual_requests += 1
            self._recent_interventions += 1
            self._last_decision = decision
            return decision

        if self._should_comment(observation, timestamp, self_analysis) and (
            assessment is None or assessment.allow_comment
        ):
            decision = AmbientProactiveDecision(
                action=AmbientAction.COMMENT,
                rationale="ambient_event_supports_low_intrusion_comment",
                comment=self._comment_for(observation),
                retain_summary=self._may_retain(observation),
                self_analysis_considered=self_analysis is not None,
            )
            self._last_comment_at = timestamp
            self._comments += 1
            self._recent_interventions += 1
            self._last_decision = decision
            return decision

        if assessment is not None and not assessment.allow_comment:
            return self._suppress(assessment.rationale)
        return self._suppress("restraint_or_insufficient_relevance")

    def _should_request_vision(
        self,
        observation: AmbientObservation,
        now: datetime,
    ) -> bool:
        if not self.policy.standing_camera_consent:
            return False
        if not observation.visual_confirmation_helpful:
            return False
        if observation.confidence < self.policy.visual_threshold:
            return False
        if observation.kind not in {
            AmbientSignalKind.IMPACT,
            AmbientSignalKind.DISTRESS,
            AmbientSignalKind.VISUAL_UNCERTAINTY,
        }:
            return False
        return self._cooldown_elapsed(
            self._last_camera_at,
            self.policy.camera_cooldown,
            now,
        )

    def _should_comment(
        self,
        observation: AmbientObservation,
        now: datetime,
        self_analysis: ConversationalSelfAnalysisReport | None,
    ) -> bool:
        if observation.confidence < self.policy.comment_threshold:
            return False
        if observation.kind not in {
            AmbientSignalKind.IMPACT,
            AmbientSignalKind.DISTRESS,
        }:
            return False
        if self_analysis is not None and any(
            finding.dimension in {"repair", "context"}
            for finding in self_analysis.findings
        ):
            return False
        return self._cooldown_elapsed(
            self._last_comment_at,
            self.policy.comment_cooldown,
            now,
        )

    def _may_retain(self, observation: AmbientObservation) -> bool:
        return (
            self.policy.allow_private_speech_retention
            and not observation.involves_private_speech
        )

    def _suppress(self, rationale: str) -> AmbientProactiveDecision:
        decision = AmbientProactiveDecision(
            action=AmbientAction.WAIT,
            rationale=rationale,
        )
        self._suppressed += 1
        self._last_decision = decision
        return decision

    @staticmethod
    def _comment_for(observation: AmbientObservation) -> str:
        if observation.kind is AmbientSignalKind.DISTRESS:
            return "Escuché algo preocupante. ¿Están bien?"
        return "Escuché un golpe fuerte. ¿Está todo bien?"

    @staticmethod
    def _cooldown_elapsed(
        last_at: datetime | None,
        cooldown: timedelta,
        now: datetime,
    ) -> bool:
        return last_at is None or now - last_at >= cooldown
