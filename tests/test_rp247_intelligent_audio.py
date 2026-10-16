from datetime import datetime, timedelta, timezone

import pytest

from core.intelligent_audio import (
    AudioEventType,
    AudioFrame,
    AudioMode,
    AudioPolicy,
    IntelligentAudioService,
)

NOW = datetime(2026, 7, 20, 15, 0, tzinfo=timezone.utc)


def frame(**changes):
    values = {
        "observed_at": NOW,
        "transcript": "Roby recordame llamar a Cristi",
        "speech_detected": True,
        "voice_confidence": 0.9,
        "duration_seconds": 3.0,
        "microphone_permission": True,
        "explicit_user_consent": True,
    }
    values.update(changes)
    return AudioFrame(**values)


def test_wake_word_queues_remaining_utterance():
    service = IntelligentAudioService(AudioPolicy(mode=AudioMode.WAKE_WORD))

    event = service.process(frame())

    assert event.event_type is AudioEventType.UTTERANCE_READY
    assert service.pop_utterance() == "recordame llamar a Cristi"
    assert service.snapshot.active


def test_wake_word_mode_ignores_unaddressed_speech():
    service = IntelligentAudioService(AudioPolicy(mode=AudioMode.WAKE_WORD))

    event = service.process(frame(transcript="Hoy hace frío"))

    assert event.event_type is AudioEventType.SPEECH_IGNORED
    assert service.pop_utterance() is None


def test_push_to_talk_requires_activation_signal():
    service = IntelligentAudioService(AudioPolicy(mode=AudioMode.PUSH_TO_TALK))

    ignored = service.process(frame(push_to_talk=False))
    accepted = service.process(frame(push_to_talk=True))

    assert ignored.event_type is AudioEventType.SPEECH_IGNORED
    assert accepted.event_type is AudioEventType.UTTERANCE_READY


def test_missing_permission_or_consent_is_rejected():
    service = IntelligentAudioService(AudioPolicy(mode=AudioMode.WAKE_WORD))

    event = service.process(
        frame(microphone_permission=False, explicit_user_consent=False)
    )

    assert event.event_type is AudioEventType.REJECTED
    assert len(event.rationale) == 2


def test_vad_and_confidence_gate_audio():
    service = IntelligentAudioService(AudioPolicy(mode=AudioMode.WAKE_WORD))

    silence = service.process(frame(speech_detected=False))
    uncertain = service.process(frame(voice_confidence=0.2))

    assert silence.event_type is AudioEventType.SILENCE
    assert uncertain.event_type is AudioEventType.SPEECH_IGNORED


def test_active_session_accepts_follow_up_without_wake_word():
    service = IntelligentAudioService(AudioPolicy(mode=AudioMode.WAKE_WORD))
    service.process(frame(transcript="Roby"))

    event = service.process(
        frame(observed_at=NOW + timedelta(seconds=5), transcript="qué hora es")
    )

    assert event.event_type is AudioEventType.UTTERANCE_READY
    assert service.pop_utterance() == "qué hora es"


def test_session_expires_after_inactivity():
    policy = AudioPolicy(
        mode=AudioMode.WAKE_WORD,
        session_timeout=timedelta(seconds=10),
    )
    service = IntelligentAudioService(policy)
    service.process(frame(transcript="Roby"))

    event = service.process(
        frame(observed_at=NOW + timedelta(seconds=11), transcript="hola")
    )

    assert event.event_type is AudioEventType.SPEECH_IGNORED
    assert any(
        item.event_type is AudioEventType.SESSION_EXPIRED
        for item in service.snapshot.events
    )


def test_queue_is_bounded_and_discards_oldest():
    policy = AudioPolicy(mode=AudioMode.AUTHORIZED_CONTINUOUS, queue_limit=2)
    service = IntelligentAudioService(policy)

    for index in range(3):
        service.process(frame(transcript=f"mensaje {index}"))

    assert service.snapshot.queued_utterances == ("mensaje 1", "mensaje 2")


def test_overlong_utterance_is_rejected():
    service = IntelligentAudioService(AudioPolicy(mode=AudioMode.AUTHORIZED_CONTINUOUS))

    event = service.process(frame(duration_seconds=31.0))

    assert event.event_type is AudioEventType.REJECTED


def test_policy_and_frames_reject_invalid_values():
    with pytest.raises(ValueError):
        AudioPolicy(minimum_voice_confidence=1.1)
    with pytest.raises(ValueError):
        AudioFrame(observed_at=NOW.replace(tzinfo=None))
