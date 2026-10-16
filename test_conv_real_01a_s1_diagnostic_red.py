"""CONV-REAL-01A-S1: RED contractual; no product changes.

Run inside the certified ROBY project as:
    python -m pytest -q tests/test_conv_real_01a_s1_diagnostic_red.py
"""

from types import SimpleNamespace

from app.conversation_reliability_observability import (
    OfficialConversationReliabilityObservabilityGateway,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineStatus,
)
from tests.test_m166_provider_health_evaluation import NOW
from tests.test_m177_governed_operational_conversation_pipeline import (
    PreparationPort,
    pipeline,
    request,
)


class SuccessfulConversationEvaluation:
    def evaluate_turn(self, request, *, now):
        return SimpleNamespace(reasoning_status=None)


def test_failed_preparation_retains_diagnostic_exception_type_in_official_trace():
    """Expected RED: containment works, but the original error type is lost."""
    observability = OfficialConversationReliabilityObservabilityGateway(
        SuccessfulConversationEvaluation()
    )
    runtime, _, provider = pipeline(
        preparation=PreparationPort(error=RuntimeError("sensitive internal detail")),
        conversation_execution=observability,
    )
    turn = request(session_id="conv-real-01a-s1")

    result = runtime.process(turn, now=NOW)
    traces = observability.traces_for(turn.owner, turn.session_id)

    assert result.status is GovernedConversationPipelineStatus.FAILED
    assert result.platform_mutation_performed is False
    assert provider.calls == []
    assert len(traces) == 1
    assert traces[0].status == "failed"
    assert traces[0].error == "RuntimeError"
    assert "sensitive internal detail" not in result.operational_response.response_text
