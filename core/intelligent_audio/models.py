from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from hashlib import sha256


class AudioMode(str, Enum):
    DISABLED = "disabled"
    PUSH_TO_TALK = "push_to_talk"
    WAKE_WORD = "wake_word"
    AUTHORIZED_CONTINUOUS = "authorized_continuous"


class AudioEventType(str, Enum):
    SILENCE = "silence"
    SPEECH_IGNORED = "speech_ignored"
    ACTIVATED = "activated"
    UTTERANCE_READY = "utterance_ready"
    REJECTED = "rejected"
    SESSION_EXPIRED = "session_expired"


@dataclass(frozen=True)
class AudioPolicy:
    mode: AudioMode | str = AudioMode.PUSH_TO_TALK
    wake_words: tuple[str, ...] = ("roby",)
    require_microphone_permission: bool = True
    require_explicit_consent: bool = True
    minimum_voice_confidence: float = 0.65
    session_timeout: timedelta = timedelta(seconds=20)
    max_utterance_seconds: float = 30.0
    queue_limit: int = 8

    def __post_init__(self) -> None:
        mode = AudioMode(self.mode)
        words = tuple(word.strip().casefold() for word in self.wake_words)
        if mode is AudioMode.WAKE_WORD and not words:
            raise ValueError("wake-word mode requires at least one wake word")
        if any(not word for word in words) or len(words) != len(set(words)):
            raise ValueError("wake words must be non-empty and unique")
        if not 0 <= self.minimum_voice_confidence <= 1:
            raise ValueError("voice confidence must be between zero and one")
        if self.session_timeout.total_seconds() <= 0:
            raise ValueError("audio session timeout must be positive")
        if self.max_utterance_seconds <= 0:
            raise ValueError("maximum utterance duration must be positive")
        if self.queue_limit <= 0:
            raise ValueError("audio queue limit must be positive")
        object.__setattr__(self, "mode", mode)
        object.__setattr__(self, "wake_words", words)


@dataclass(frozen=True)
class AudioFrame:
    observed_at: datetime
    transcript: str = ""
    speech_detected: bool = False
    voice_confidence: float = 0.0
    duration_seconds: float = 0.0
    push_to_talk: bool = False
    microphone_permission: bool = False
    explicit_user_consent: bool = False

    def __post_init__(self) -> None:
        if self.observed_at.tzinfo is None:
            raise ValueError("audio frame timestamp must be timezone-aware")
        if not 0 <= self.voice_confidence <= 1:
            raise ValueError("voice confidence must be between zero and one")
        if self.duration_seconds < 0:
            raise ValueError("audio duration must not be negative")
        object.__setattr__(self, "transcript", self.transcript.strip())


@dataclass(frozen=True)
class AudioEvent:
    event_type: AudioEventType | str
    observed_at: datetime
    rationale: tuple[str, ...]
    transcript: str = ""
    event_id: str = ""

    def __post_init__(self) -> None:
        event_type = AudioEventType(self.event_type)
        if self.observed_at.tzinfo is None:
            raise ValueError("audio event timestamp must be timezone-aware")
        if not self.rationale or any(not item.strip() for item in self.rationale):
            raise ValueError("audio event rationale must not be empty")
        normalized = self.transcript.strip()
        expected = sha256(
            "|".join(
                (
                    event_type.value,
                    self.observed_at.isoformat(),
                    normalized,
                    ";".join(self.rationale),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.event_id and self.event_id != expected:
            raise ValueError("audio event id is inconsistent")
        object.__setattr__(self, "event_type", event_type)
        object.__setattr__(self, "transcript", normalized)
        object.__setattr__(self, "event_id", expected)


@dataclass(frozen=True)
class AudioSnapshot:
    active: bool
    activated_at: datetime | None
    expires_at: datetime | None
    queued_utterances: tuple[str, ...]
    events: tuple[AudioEvent, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        for value in (self.activated_at, self.expires_at):
            if value is not None and value.tzinfo is None:
                raise ValueError("audio snapshot times must be timezone-aware")
        if self.active != (self.expires_at is not None):
            raise ValueError("active audio snapshots require an expiration")
