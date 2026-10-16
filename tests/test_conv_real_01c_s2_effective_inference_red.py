"""CONV-REAL-01C-S2: RED for effective inference propagation.

Tests only. Do not change production or weaken ADR_224_4 curation.
The repetition notice wording is provisional; the behavior is contractual.
"""

from core.conversational_context_continuity import (
    enrich_with_recent_conversation_context,
)
from core.governed_operational_conversation_pipeline import (
    ConversationalContextTurn,
    GovernedConversationPipelineRequest,
)
from core.llm_model_providers import _build_prompt, _chat_messages
from core.llm_provider import LLMRequest


def _build(question: str, history_question: str):
    bad_answer = "RESPUESTA_HISTORICA_INCORRECTA_NO_REINTRODUCIR"
    conversation = GovernedConversationPipelineRequest(
        owner="owner-a",
        session_id="session-a",
        text=question,
        recent_context=(
            ConversationalContextTurn(
                user_text=history_question,
                assistant_text=bad_answer,
            ),
        ),
    )
    original = conversation.recent_context
    result = enrich_with_recent_conversation_context(
        conversation=conversation,
        inference_request=LLMRequest(prompt=question),
    )
    assert conversation.recent_context == original
    return result, bad_answer


def _effective_text(request: LLMRequest) -> str:
    chat = "\n".join(message["content"] for message in _chat_messages(request))
    return _build_prompt(request) + "\n" + chat


def test_repetition_reaches_effective_provider_content_without_bad_anchor():
    question = "Si una respuesta era incorrecta, ¿cómo la corregirías?"
    result, bad_answer = _build(question, question)
    effective = _effective_text(result)

    # ADR_224_4: a discarded incorrect answer must stay out of inference.
    assert bad_answer not in result.prompt
    assert bad_answer not in effective
    assert all(bad_answer not in message.content for message in result.messages)

    # RED: metadata alone is not consumed by these provider payload builders.
    # The model must receive a bounded, explicit indication of repetition.
    assert "pregunta equivalente" in effective.casefold()


def test_new_question_does_not_invent_repetition_notice():
    result, _ = _build("Pregunta nueva", "Pregunta distinta")
    assert "pregunta equivalente" not in _effective_text(result).casefold()


def test_equivalent_normalized_question_reaches_provider_content():
    result, bad_answer = _build(
        "¿CÓMO CORREGIRÍAS UN ERROR?",
        "como corregirias un error",
    )
    effective = _effective_text(result)
    assert bad_answer not in effective
    assert "pregunta equivalente" in effective.casefold()
