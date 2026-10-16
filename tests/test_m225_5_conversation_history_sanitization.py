from __future__ import annotations

from app.runtime_root_factory import EnvironmentInferenceRequestPort
from core.conversation_history_sanitization import (
    has_reserved_conversation_prefix,
    sanitize_conversation_history,
)
from core.conversational_context_continuity import (
    enrich_with_recent_conversation_context,
)
from core.development_console_observability import DevelopmentConsoleRenderer
from core.development_console_observability.models import TurnObservation
from core.governed_operational_conversation_pipeline import (
    ConversationalContextTurn,
    GovernedConversationPipelineRequest,
)


def turn(user: str, assistant: str) -> ConversationalContextTurn:
    return ConversationalContextTurn(user_text=user, assistant_text=assistant)


def test_reserved_prefix_detection_is_case_insensitive_and_trimmed():
    assert has_reserved_conversation_prefix("  OBS> provider_payload")
    assert has_reserved_conversation_prefix("assistant: synthetic")
    assert not has_reserved_conversation_prefix("Observé un problema")


def test_sanitizer_removes_whole_turn_when_either_side_is_reserved():
    context = (
        turn("Mi nombre es Carlos", "Entendido, Carlos"),
        turn("OBS> provider_payload", "Respuesta contaminada"),
        turn("Pregunta normal", "TRACE> internal output"),
    )

    result = sanitize_conversation_history(context)

    assert result.context == (context[0],)
    assert result.removed_turns == 2


def test_enrichment_excludes_reserved_history_from_prompt_and_messages():
    request = GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="desktop-main",
        text="Hola ROBY",
        recent_context=(
            turn("Mi nombre es Carlos", "Entendido, Carlos"),
            turn("OBS> provider_payload transport=messages", "Ruido"),
        ),
    )

    built = enrich_with_recent_conversation_context(
        conversation=request,
        inference_request=EnvironmentInferenceRequestPort().build(request),
    )

    assert "Mi nombre es Carlos" in built.prompt
    assert "OBS>" not in built.prompt
    assert all("OBS>" not in message.content for message in built.messages)
    assert built.metadata["conversation_context_input_turns"] == "2"
    assert built.metadata["conversation_context_sanitized_turns"] == "1"
    assert built.metadata["conversation_context_reserved_removed_turns"] == "1"
    assert built.metadata["conversation_context_curation_dropped_turns"] == "0"


def test_all_reserved_history_yields_current_message_only():
    request = GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="desktop-main",
        text="Hola ROBY",
        recent_context=(turn("OBS> copied trace", "Ruido"),),
    )

    built = enrich_with_recent_conversation_context(
        conversation=request,
        inference_request=EnvironmentInferenceRequestPort().build(request),
    )

    assert built.prompt == "Hola ROBY"
    assert tuple((item.role, item.content) for item in built.messages) == (
        ("user", "Hola ROBY"),
    )
    assert built.metadata["conversation_context_reserved_removed_turns"] == "1"
    assert built.metadata["conversation_context_turns"] == "0"


def test_observation_renders_sanitizer_counts():
    lines = DevelopmentConsoleRenderer().render_turn(
        TurnObservation(
            sequence=1,
            status="completed",
            turn_id="turn",
            trace_id="trace",
            pipeline_result_id="pipeline",
            operational_response_id="response",
            modules=(),
            provider_call_performed=True,
            retrieval_performed=False,
            network_access_performed=False,
            platform_mutation_performed=False,
            event_count=1,
            terminal_event="turn_persisted",
            context_turns=1,
            context_input_turns=3,
            context_sanitized_turns=2,
            context_reserved_removed_turns=1,
            context_curation_dropped_turns=1,
        )
    )

    assert (
        "context_sanitizer input=3 sanitized=2 reserved_removed=1 curation_removed=1"
    ) in lines
