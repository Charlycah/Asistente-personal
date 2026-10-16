from app.cognitive_analysis_authority import CognitiveAnalysisStatus
from app.official_conversation_gateway import OfficialConversationGateway
from app.unified_brain import UnifiedBrain


class _Turn:
    response_text = "respuesta preservada"
    response_path = "provider"
    status = "completed"
    session_id = "runtime-session"
    provider_call_performed = True
    retrieval_performed = False
    network_access_performed = False
    degradation_reason = "not_applicable"


class _Runtime:
    bootstrap = object()
    history = ()
    traces = ()

    def converse(self, text: str):
        return _Turn()


class _FailingAnalysis:
    def analyze(self, dossier):
        raise RuntimeError("controlled analysis failure")


def test_m389_1_analysis_failure_cannot_change_or_fail_turn() -> None:
    brain = UnifiedBrain(
        OfficialConversationGateway(_Runtime()),
        cognitive_analysis=_FailingAnalysis(),
    )
    turn = brain.process("mensaje")
    assert turn.response_text == "respuesta preservada"
    assert brain.cognitive_analysis.status is CognitiveAnalysisStatus.DEGRADED
    assert brain.cognitive_analysis.report is None
    assert brain.cognitive_analysis.failure_code == "analysis:internal_failure"
    assert brain.cognitive_analysis.affects_turn_result is False

