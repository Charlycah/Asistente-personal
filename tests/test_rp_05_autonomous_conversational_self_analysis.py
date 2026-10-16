from app.conversational_self_analysis import (
    AutonomousConversationalSelfAnalysis,
    SelfAnalysisPolicy,
)
from app.unified_experience_layer import UnifiedExperienceLayer
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)


def _request(text: str) -> GovernedConversationPipelineRequest:
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="household-main",
        text=text,
    )


def test_self_analysis_is_autonomous_and_has_no_public_command_dependency():
    analysis = AutonomousConversationalSelfAnalysis(
        SelfAnalysisPolicy(minimum_turns=1, trigger_score=3)
    )
    analysis.observe("Eso no es lo que te dije.", "Entiendo la corrección.")
    report = analysis.snapshot.last_report
    assert report is not None
    assert report.trigger_reason == "user_correction"
    assert report.advisory_only is True


def test_self_analysis_waits_until_a_meaningful_signal_exists():
    analysis = AutonomousConversationalSelfAnalysis(
        SelfAnalysisPolicy(minimum_turns=2, trigger_score=3)
    )
    analysis.observe("hola", "Buen día.")
    analysis.observe("que tengo hoy", "Tenés una reunión.")
    assert analysis.snapshot.analyses_run == 0
    assert analysis.snapshot.last_report is None


def test_self_analysis_detects_repeated_recent_openings():
    analysis = AutonomousConversationalSelfAnalysis(
        SelfAnalysisPolicy(minimum_turns=3, trigger_score=2)
    )
    for response in (
        "Ahora reviso el clima.",
        "Ahora reviso tus recordatorios.",
        "Ahora reviso la agenda.",
    ):
        analysis.observe("continuá", response)
    report = analysis.snapshot.last_report
    assert report is not None
    assert report.trigger_reason == "repeated_opening"
    assert report.findings[0].dimension == "expression_variation"


def test_self_analysis_respects_cooldown():
    analysis = AutonomousConversationalSelfAnalysis(
        SelfAnalysisPolicy(
            minimum_turns=1,
            cooldown_turns=3,
            trigger_score=3,
        )
    )
    analysis.observe("Eso no era.", "Lo corrijo.")
    analysis.observe("Eso no era.", "Lo reviso otra vez.")
    assert analysis.snapshot.analyses_run == 1
    assert analysis.snapshot.skipped_by_cooldown == 1


def test_unified_experience_observes_visible_conversation_automatically():
    analysis = AutonomousConversationalSelfAnalysis(
        SelfAnalysisPolicy(minimum_turns=1, trigger_score=3)
    )
    layer = UnifiedExperienceLayer(self_analysis=analysis)
    result = layer.present(
        GovernedOperationalInterception(response_text="Lo corrijo."),
        request=_request("Eso no es lo que te dije."),
    )
    assert result is not None
    assert analysis.snapshot.observed_turns == 1
    assert analysis.snapshot.analyses_run == 1


def test_report_recommends_context_reuse_without_changing_the_answer():
    analysis = AutonomousConversationalSelfAnalysis(
        SelfAnalysisPolicy(minimum_turns=1, trigger_score=2)
    )
    response = "Voy a usar lo que ya definimos."
    analysis.observe("Como te dije, mantené el voseo.", response)
    report = analysis.snapshot.last_report
    assert report is not None
    assert report.findings[0].dimension == "context"
    assert response == "Voy a usar lo que ya definimos."
