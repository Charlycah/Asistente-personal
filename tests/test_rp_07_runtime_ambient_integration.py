from __future__ import annotations

from datetime import datetime, timezone

from app.ambient_proactive_coordination import (
    AmbientObservation,
    AmbientProactiveCoordinator,
    AmbientProactivePolicy,
    AmbientSignalKind,
)
from app.ambient_proactive_runtime import AmbientProactiveRuntime
from app.desktop_bootstrap import DesktopPersonalRuntime

NOW = datetime(2026, 7, 16, tzinfo=timezone.utc)


class Source:
    def __init__(self, observation=None):
        self.observation = observation

    def observe(self):
        item = self.observation
        self.observation = None
        return item


class LifecyclePart:
    def __init__(self):
        self.started = 0
        self.stopped = 0

    def start(self):
        self.started += 1

    def stop(self):
        self.stopped += 1


class AmbientPart(LifecyclePart):
    pass


def observation(kind, *, visual=False, private=False):
    return AmbientObservation(
        kind=kind,
        confidence=0.99,
        summary="evento doméstico relevante",
        occurred_at=NOW,
        involves_private_speech=private,
        visual_confirmation_helpful=visual,
    )


def test_resident_runtime_delivers_governed_ambient_comment():
    messages = []
    runtime = AmbientProactiveRuntime(
        Source(observation(AmbientSignalKind.IMPACT)),
        AmbientProactiveCoordinator(
            AmbientProactivePolicy(standing_audio_consent=True)
        ),
        notify=messages.append,
    )

    runtime.tick(now=NOW)

    assert messages == ["Escuché un golpe fuerte. ¿Está todo bien?"]
    assert runtime.snapshot.comments_delivered == 1


def test_resident_runtime_requests_registered_visual_capture():
    reasons = []
    runtime = AmbientProactiveRuntime(
        Source(observation(AmbientSignalKind.DISTRESS, visual=True)),
        AmbientProactiveCoordinator(
            AmbientProactivePolicy(
                standing_audio_consent=True,
                standing_camera_consent=True,
            )
        ),
        notify=lambda message: None,
        request_visual_capture=reasons.append,
    )

    runtime.tick(now=NOW)

    assert reasons == ["evento doméstico relevante"]
    assert runtime.snapshot.visual_captures_requested == 1


def test_private_household_speech_is_not_delivered():
    messages = []
    runtime = AmbientProactiveRuntime(
        Source(
            observation(
                AmbientSignalKind.CONVERSATION,
                private=True,
            )
        ),
        AmbientProactiveCoordinator(
            AmbientProactivePolicy(standing_audio_consent=True)
        ),
        notify=messages.append,
    )

    runtime.tick(now=NOW)

    assert messages == []
    assert runtime.snapshot.observations == 1


def test_desktop_personal_runtime_owns_ambient_lifecycle():
    lifecycle = LifecyclePart()
    supervisor = LifecyclePart()
    ambient = AmbientPart()
    runtime = DesktopPersonalRuntime(
        lifecycle=lifecycle,
        supervisor=supervisor,
        ambient_proactive_runtime=ambient,
    )

    runtime.start()
    runtime.stop()

    assert ambient.started == 1
    assert ambient.stopped == 1
    assert lifecycle.started == 1
    assert lifecycle.stopped == 1
