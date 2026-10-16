from datetime import datetime, timedelta, timezone

from app.ambient_proactive_coordination import (
    AmbientAction,
    AmbientObservation,
    AmbientProactiveCoordinator,
    AmbientProactivePolicy,
    AmbientSignalKind,
)
from app.conversational_self_analysis import (
    ConversationalSelfAnalysisReport,
    SelfAnalysisFinding,
)

NOW = datetime(2026, 7, 16, 18, 0, tzinfo=timezone.utc)


def _observation(kind, **changes):
    values = {
        "kind": kind,
        "confidence": 0.95,
        "summary": "Se detectó un evento ambiental relevante.",
        "occurred_at": NOW,
    }
    values.update(changes)
    return AmbientObservation(**values)


def test_audio_observation_requires_standing_consent():
    coordinator = AmbientProactiveCoordinator()
    decision = coordinator.evaluate(_observation(AmbientSignalKind.IMPACT), now=NOW)
    assert decision.action is AmbientAction.WAIT
    assert decision.rationale == "standing_audio_consent_missing"


def test_private_household_conversation_does_not_trigger_comment():
    coordinator = AmbientProactiveCoordinator(
        AmbientProactivePolicy(standing_audio_consent=True)
    )
    decision = coordinator.evaluate(
        _observation(
            AmbientSignalKind.CONVERSATION,
            involves_private_speech=True,
        ),
        now=NOW,
    )
    assert decision.action is AmbientAction.WAIT
    assert decision.rationale == "private_household_speech_requires_restraint"


def test_strong_impact_can_produce_a_low_intrusion_check_in():
    coordinator = AmbientProactiveCoordinator(
        AmbientProactivePolicy(standing_audio_consent=True)
    )
    decision = coordinator.evaluate(_observation(AmbientSignalKind.IMPACT), now=NOW)
    assert decision.action is AmbientAction.COMMENT
    assert decision.comment == "Escuché un golpe fuerte. ¿Está todo bien?"
    assert decision.retain_summary is False


def test_roby_can_request_camera_when_visual_confirmation_is_needed():
    coordinator = AmbientProactiveCoordinator(
        AmbientProactivePolicy(
            standing_audio_consent=True,
            standing_camera_consent=True,
        )
    )
    decision = coordinator.evaluate(
        _observation(
            AmbientSignalKind.VISUAL_UNCERTAINTY,
            visual_confirmation_helpful=True,
        ),
        now=NOW,
    )
    assert decision.action is AmbientAction.REQUEST_VISUAL_CAPTURE
    assert decision.camera_reason is not None


def test_camera_is_not_activated_without_standing_camera_consent():
    coordinator = AmbientProactiveCoordinator(
        AmbientProactivePolicy(standing_audio_consent=True)
    )
    decision = coordinator.evaluate(
        _observation(
            AmbientSignalKind.VISUAL_UNCERTAINTY,
            visual_confirmation_helpful=True,
        ),
        now=NOW,
    )
    assert decision.action is AmbientAction.WAIT


def test_self_analysis_can_restrain_nonurgent_proactive_comment():
    coordinator = AmbientProactiveCoordinator(
        AmbientProactivePolicy(standing_audio_consent=True)
    )
    report = ConversationalSelfAnalysisReport(
        turn=4,
        trigger_reason="context_reuse_risk",
        score=3,
        findings=(
            SelfAnalysisFinding(
                dimension="context",
                severity="medium",
                evidence="Context was missed.",
                recommendation="Use the available context.",
            ),
        ),
    )
    decision = coordinator.evaluate(
        _observation(AmbientSignalKind.IMPACT),
        self_analysis=report,
        now=NOW,
    )
    assert decision.action is AmbientAction.WAIT


def test_comment_and_camera_cooldowns_prevent_repeated_intrusion():
    coordinator = AmbientProactiveCoordinator(
        AmbientProactivePolicy(
            standing_audio_consent=True,
            standing_camera_consent=True,
            comment_cooldown=timedelta(minutes=10),
            camera_cooldown=timedelta(minutes=10),
        )
    )
    impact = _observation(AmbientSignalKind.IMPACT)
    assert coordinator.evaluate(impact, now=NOW).action is AmbientAction.COMMENT
    assert (
        coordinator.evaluate(
            impact,
            now=NOW + timedelta(minutes=1),
        ).action
        is AmbientAction.WAIT
    )
