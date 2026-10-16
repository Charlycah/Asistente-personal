from __future__ import annotations

from inspect import getsource

from app.official_conversation_gateway import (
    ConversationOrigin,
    OfficialConversationGateway,
)
from app.unified_brain import UnifiedBrain
from core.cognitive_maturity import (
    CognitiveCycleNodeState,
    TextPerceptionEvidenceAdapter,
)


def _observe(text="mensaje", origin="internal"):
    return TextPerceptionEvidenceAdapter().observe_input(
        text=text,
        origin=origin,
    )


def test_m388_2_internal_text_perception_participates() -> None:
    record = _observe()
    assert record.node_id == "perception_and_evidence"
    assert record.state is CognitiveCycleNodeState.PARTICIPATED
    assert record.evidence_codes == (
        "perception:text_received",
        "perception:origin_declared",
        "perception:interactive_submission",
    )


def test_m388_2_desktop_text_is_a_certified_text_origin() -> None:
    record = _observe(origin=ConversationOrigin.DESKTOP_TEXT)
    assert record.state is CognitiveCycleNodeState.PARTICIPATED
    assert record.reason_codes == ()


def test_m388_2_voice_origin_is_not_certified_as_text_perception() -> None:
    record = _observe(origin=ConversationOrigin.DESKTOP_VOICE)
    assert record.state is CognitiveCycleNodeState.DEGRADED
    assert record.reason_codes == (
        "perception:source_channel_not_certified",
    )


def test_m388_2_retired_console_origin_is_degraded_not_invented() -> None:
    record = _observe(origin=ConversationOrigin.CONSOLE)
    assert record.state is CognitiveCycleNodeState.DEGRADED
    assert "perception:text_received" not in record.evidence_codes


def test_m388_2_android_and_unknown_origins_remain_uncertified() -> None:
    for origin in ("android", "sensor", "unknown"):
        record = _observe(origin=origin)
        assert record.state is CognitiveCycleNodeState.DEGRADED
        assert record.reason_codes == (
            "perception:source_channel_not_certified",
        )


def test_m388_2_empty_text_is_explicitly_degraded() -> None:
    record = _observe(text="   ")
    assert record.state is CognitiveCycleNodeState.DEGRADED
    assert record.reason_codes == ("perception:empty_text",)


def test_m388_2_evidence_contains_no_text_content() -> None:
    private_text = "contenido privado irrepetible"
    record = _observe(text=private_text)
    assert private_text not in repr(record)
    assert all(private_text not in code for code in record.evidence_codes)


def test_m388_2_official_identified_turn_extends_connected_prefix() -> None:
    class Turn:
        response_text = "respuesta"
        response_path = "provider"
        status = "completed"
        session_id = "runtime-session"

    class Runtime:
        def converse(self, text, now=None):
            return Turn()

    gateway = OfficialConversationGateway(Runtime())
    brain = UnifiedBrain(gateway)
    brain.process("Confirmo que soy Carlos", session_id="main")
    diagnostic = gateway.operational_cycle_diagnostic
    assert diagnostic.latest_connected_prefix_node_ids == (
        "conversation_ingress",
        "unified_coordination",
        "identity_and_context",
        "perception_and_evidence",
    )
    assert diagnostic.latest_first_interruption_node_id == "memory_recall"


def test_m388_2_failed_runtime_still_preserves_perception_fact() -> None:
    class Runtime:
        def converse(self, text, now=None):
            raise RuntimeError("failure")

    gateway = OfficialConversationGateway(Runtime())
    try:
        gateway.submit("mensaje")
    except RuntimeError:
        pass
    cycle = gateway.target_cognitive_cycle_evidence.latest_cycle
    assert cycle is not None
    assert cycle.node("perception_and_evidence").state is (
        CognitiveCycleNodeState.PARTICIPATED
    )


def test_m388_2_gateway_observes_perception_before_runtime() -> None:
    source = getsource(OfficialConversationGateway.submit)
    perception_index = source.index("observe_input(")
    runtime_index = source.index("_runtime.converse(")
    assert perception_index < runtime_index


def test_m388_2_adapter_has_no_operational_or_storage_authority() -> None:
    source = getsource(TextPerceptionEvidenceAdapter)
    forbidden = (
        "execute(",
        "persist(",
        "remember(",
        "store(",
        "decide(",
        "open(",
    )
    assert all(item not in source for item in forbidden)


def test_m388_2_preserves_the_canonical_core_constructor_line() -> None:
    path = (
        __import__("pathlib").Path(__file__).resolve().parents[2]
        / "app"
        / "official_conversation_gateway.py"
    )
    assert "CanonicalCognitiveCore(" in path.read_text(
        encoding="utf-8"
    ).splitlines()[51]
