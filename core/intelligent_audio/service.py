from __future__ import annotations

from collections import deque
from datetime import datetime, timezone

from .models import (
    AudioEvent,
    AudioEventType,
    AudioFrame,
    AudioMode,
    AudioPolicy,
    AudioSnapshot,
)


class IntelligentAudioService:
    """Governed local audio control plane; it never opens a microphone itself."""

    def __init__(self, policy: AudioPolicy | None = None) -> None:
        self.policy = policy or AudioPolicy()
        self._active = False
        self._activated_at: datetime | None = None
        self._expires_at: datetime | None = None
        self._queue: deque[str] = deque(maxlen=self.policy.queue_limit)
        self._events: list[AudioEvent] = []

    @property
    def snapshot(self) -> AudioSnapshot:
        return AudioSnapshot(
            active=self._active,
            activated_at=self._activated_at,
            expires_at=self._expires_at,
            queued_utterances=tuple(self._queue),
            events=tuple(self._events),
        )

    def process(self, frame: AudioFrame) -> AudioEvent:
        self._expire_if_needed(frame.observed_at)
        rejected = self._permission_rejection(frame)
        if rejected is not None:
            return self._record(AudioEventType.REJECTED, frame, rejected)
        if self.policy.mode is AudioMode.DISABLED:
            return self._record(
                AudioEventType.REJECTED,
                frame,
                ("audio is disabled by policy",),
            )
        if not frame.speech_detected:
            return self._record(
                AudioEventType.SILENCE,
                frame,
                ("voice activity was not detected",),
            )
        if frame.voice_confidence < self.policy.minimum_voice_confidence:
            return self._record(
                AudioEventType.SPEECH_IGNORED,
                frame,
                ("voice confidence is below policy threshold",),
            )
        if frame.duration_seconds > self.policy.max_utterance_seconds:
            return self._record(
                AudioEventType.REJECTED,
                frame,
                ("utterance exceeds maximum authorized duration",),
            )
        if not self._active:
            activation = self._activation_reason(frame)
            if activation is None:
                return self._record(
                    AudioEventType.SPEECH_IGNORED,
                    frame,
                    ("speech did not satisfy the activation policy",),
                )
            self._active = True
            self._activated_at = frame.observed_at
            self._expires_at = frame.observed_at + self.policy.session_timeout
            remaining = self._remove_wake_word(frame.transcript)
            if remaining:
                self._queue.append(remaining)
                return self._record(
                    AudioEventType.UTTERANCE_READY,
                    frame,
                    (activation, "authorized utterance queued"),
                    transcript=remaining,
                )
            return self._record(
                AudioEventType.ACTIVATED,
                frame,
                (activation,),
            )
        self._expires_at = frame.observed_at + self.policy.session_timeout
        if not frame.transcript:
            return self._record(
                AudioEventType.SPEECH_IGNORED,
                frame,
                ("active session received no transcript",),
            )
        self._queue.append(frame.transcript)
        return self._record(
            AudioEventType.UTTERANCE_READY,
            frame,
            ("authorized audio session is active", "utterance queued"),
        )

    def pop_utterance(self) -> str | None:
        return self._queue.popleft() if self._queue else None

    def deactivate(self, *, now: datetime | None = None) -> AudioEvent:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("audio deactivation time must be timezone-aware")
        self._active = False
        self._activated_at = None
        self._expires_at = None
        frame = AudioFrame(observed_at=timestamp)
        return self._record(
            AudioEventType.SESSION_EXPIRED,
            frame,
            ("audio session was deactivated",),
        )

    def _permission_rejection(self, frame: AudioFrame) -> tuple[str, ...] | None:
        reasons: list[str] = []
        if (
            self.policy.require_microphone_permission
            and not frame.microphone_permission
        ):
            reasons.append("microphone permission is missing")
        if self.policy.require_explicit_consent and not frame.explicit_user_consent:
            reasons.append("explicit audio consent is missing")
        return tuple(reasons) or None

    def _activation_reason(self, frame: AudioFrame) -> str | None:
        if self.policy.mode is AudioMode.AUTHORIZED_CONTINUOUS:
            return "authorized continuous mode accepted speech"
        if self.policy.mode is AudioMode.PUSH_TO_TALK and frame.push_to_talk:
            return "push-to-talk activation was present"
        if self.policy.mode is AudioMode.WAKE_WORD:
            normalized = frame.transcript.casefold()
            if any(word in normalized.split() for word in self.policy.wake_words):
                return "authorized wake word was detected"
        return None

    def _remove_wake_word(self, transcript: str) -> str:
        words = transcript.split()
        for index, word in enumerate(words):
            cleaned = word.casefold().strip("¿?¡!.,:;")
            if cleaned in self.policy.wake_words:
                return " ".join(words[index + 1 :]).strip()
        return transcript.strip()

    def _expire_if_needed(self, observed_at: datetime) -> None:
        if self._expires_at is None or observed_at <= self._expires_at:
            return
        self._active = False
        self._activated_at = None
        self._expires_at = None
        frame = AudioFrame(observed_at=observed_at)
        self._record(
            AudioEventType.SESSION_EXPIRED,
            frame,
            ("audio session expired after inactivity",),
        )

    def _record(
        self,
        event_type: AudioEventType,
        frame: AudioFrame,
        rationale: tuple[str, ...],
        *,
        transcript: str | None = None,
    ) -> AudioEvent:
        event = AudioEvent(
            event_type=event_type,
            observed_at=frame.observed_at,
            transcript=frame.transcript if transcript is None else transcript,
            rationale=rationale,
        )
        self._events.append(event)
        return event
