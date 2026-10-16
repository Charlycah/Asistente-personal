from __future__ import annotations

from app.runtime_root_factory import EnvironmentInferenceRequestPort
from core.conversation_context_curation import (
    curate_recent_conversation_context,
    normalize_conversational_text,
)
from core.conversational_context_continuity import (
    enrich_with_recent_conversation_context,
)
from core.governed_operational_conversation_pipeline import (
    ConversationalContextTurn,
    GovernedConversationPipelineRequest,
)


def turn(user: str, assistant: str) -> ConversationalContextTurn:
    return ConversationalContextTurn(user_text=user, assistant_text=assistant)


def test_normalization_ignores_case_accents_and_punctuation():
    assert normalize_conversational_text("¿Cómo me llamo?") == "como me llamo"
    assert normalize_conversational_text("COMO me llamo !!!") == "como me llamo"


def test_curator_drops_previous_versions_of_current_question():
    context = (
        turn("Mi nombre es Carlos.", "Entendido, Carlos."),
        turn("como me llamo ?", "No tengo un nombre propio."),
    )

    curated = curate_recent_conversation_context(
        current_text="¿Cómo me llamo?",
        recent_context=context,
    )

    assert curated == (context[0],)


def test_curator_keeps_latest_duplicate_statement_only():
    context = (
        turn("mi nombre es Carlos", "Hola, Carlos."),
        turn("Mi nombre es Carlos.", "Entendido, Carlos."),
    )

    curated = curate_recent_conversation_context(
        current_text="¿Cómo me llamo?",
        recent_context=context,
    )

    assert curated == (context[1],)


def test_enrichment_reports_curation_lineage_and_excludes_bad_anchor():
    request = GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="desktop-main",
        text="¿Cómo me llamo?",
        recent_context=(
            turn("Mi nombre es Carlos.", "Entendido, Carlos."),
            turn("como me llamo ?", "No tengo un nombre propio."),
        ),
    )

    built = enrich_with_recent_conversation_context(
        conversation=request,
        inference_request=EnvironmentInferenceRequestPort().build(request),
    )

    assert "Mi nombre es Carlos." in built.prompt
    assert "No tengo un nombre propio." not in built.prompt
    assert built.metadata["conversation_context_input_turns"] == "2"
    assert built.metadata["conversation_context_turns"] == "1"
    assert built.metadata["conversation_context_dropped_turns"] == "1"
