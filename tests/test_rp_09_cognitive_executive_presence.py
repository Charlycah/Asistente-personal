from datetime import datetime, timezone

from app.ambient_proactive_coordination import (
    AmbientAction,
    AmbientObservation,
    AmbientProactiveCoordinator,
    AmbientProactivePolicy,
    AmbientSignalKind,
)
from app.cognitive_executive_presence import (
    CognitiveExecutivePresence,
    ExecutivePresencePriority,
)
from app.conversational_self_analysis import (
    ConversationalSelfAnalysisReport,
    SelfAnalysisFinding,
)


def _observation(kind: AmbientSignalKind) -> AmbientObservation:
    return AmbientObservation(
        kind=kind,
        confidence=0.99,
        summary="se detectó una señal doméstica",
        occurred_at=datetime.now(timezone.utc),
        visual_confirmation_helpful=True,
    )


def _repair_report() -> ConversationalSelfAnalysisReport:
    return ConversationalSelfAnalysisReport(
        turn=3,
        trigger_reason="repair_signal",
        score=4,
        findings=(
            SelfAnalysisFinding(
                dimension="repair",
                severity="high",
                evidence="el usuario corrigió a ROBY",
                recommendation="priorizar la reparación",
            ),
        ),
    )


def test_routine_signal_yields_to_active_conversation_repair():
    presence = CognitiveExecutivePresence()
    assessment = presence.assess(
        _observation(AmbientSignalKind.IMPACT),
        self_analysis=_repair_report(),
    )
    assert assessment.allow_comment is False
    assert assessment.rationale == "conversation_repair_has_current_executive_priority"


def test_distress_overrides_routine_restraint():
    presence = CognitiveExecutivePresence()
    assessment = presence.assess(
        _observation(AmbientSignalKind.DISTRESS),
        self_analysis=_repair_report(),
        recent_interventions=10,
    )
    assert assessment.priority is ExecutivePresencePriority.URGENT
    assert assessment.allow_comment is True
    assert assessment.allow_visual_capture is True


def test_recent_intervention_budget_prevents_intrusiveness():
    presence = CognitiveExecutivePresence()
    assessment = presence.assess(
        _observation(AmbientSignalKind.IMPACT),
        recent_interventions=2,
    )
    assert assessment.allow_comment is False
    assert assessment.rationale == "recent_intervention_budget_exhausted"


def test_ambient_coordinator_uses_executive_presence_gate():
    coordinator = AmbientProactiveCoordinator(
        AmbientProactivePolicy(
            standing_audio_consent=True,
            standing_camera_consent=False,
        ),
        executive_presence=CognitiveExecutivePresence(),
    )
    decision = coordinator.evaluate(
        _observation(AmbientSignalKind.IMPACT),
        self_analysis=_repair_report(),
    )
    assert decision.action is AmbientAction.WAIT
    assert decision.rationale == "conversation_repair_has_current_executive_priority"
