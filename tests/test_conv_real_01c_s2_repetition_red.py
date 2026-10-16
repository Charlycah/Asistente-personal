"""CONV-REAL-01C-S2: contractual RED; no production changes.

Expected RED: the existing curation removes the historical answer, but does not
expose an explicit, safe repetition signal in the inference request.
"""

from core.conversational_context_continuity import (
    enrich_with_recent_conversation_context,
)
from core.governed_operational_conversation_pipeline import (
    ConversationalContextTurn,
    GovernedConversationPipelineRequest,
)
from core.llm_provider import LLMRequest


def test_repetition_is_signaled_without_reintroducing_bad_anchor():
    question = "Si una respuesta era incorrecta, ¿cómo la corregirías?"
    bad_answer = "RESPUESTA_HISTORICA_INCORRECTA_NO_REINTRODUCIR"
    request = GovernedConversationPipelineRequest(
        owner="owner-a",
        session_id="session-a",
        text=question,
        recent_context=(
            ConversationalContextTurn(
                user_text=question,
                assistant_text=bad_answer,
            ),
        ),
    )
    original_context = request.recent_context

    built = enrich_with_recent_conversation_context(
        conversation=request,
        inference_request=LLMRequest(prompt=question),
    )

    # Existing protection: these assertions must stay GREEN.
    assert bad_answer not in built.prompt
    assert all(bad_answer not in message.content for message in built.messages)
    assert request.recent_context == original_context

    # New contract: an explicit, bounded repetition signal reaches inference.
    # Exact metadata key is a proposed contract, not yet a canonical API.
    assert built.metadata.get("conversation_current_question_repeated") == "true"
    assert built.metadata.get("conversation_current_question_repeat_count") == "1"


def test_new_question_does_not_claim_repetition():
    request = GovernedConversationPipelineRequest(
        owner="owner-a",
        session_id="session-a",
        text="Pregunta nueva",
        recent_context=(
            ConversationalContextTurn(
                user_text="Pregunta distinta",
                assistant_text="Respuesta anterior",
            ),
        ),
    )
    built = enrich_with_recent_conversation_context(
        conversation=request,
        inference_request=LLMRequest(prompt=request.text),
    )
    assert built.metadata.get("conversation_current_question_repeated") != "true"
