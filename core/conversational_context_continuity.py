from __future__ import annotations

from core.conversation_context_curation import (
    curate_recent_conversation_context,
    normalize_conversational_text,
)
from core.conversation_history_sanitization import sanitize_conversation_history
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)
from core.llm_provider import ConversationMessage, LLMRequest


def enrich_with_recent_conversation_context(
    *,
    conversation: GovernedConversationPipelineRequest,
    inference_request: LLMRequest,
) -> LLMRequest:
    """Prepend curated, bounded, session-scoped context to inference."""
    sanitized = sanitize_conversation_history(conversation.recent_context)
    normalized_current = normalize_conversational_text(conversation.text)
    repeat_count = sum(
        1
        for turn in sanitized.context
        if normalized_current
        and normalize_conversational_text(turn.user_text)
        == normalized_current
    )
    curated_context = curate_recent_conversation_context(
        current_text=conversation.text,
        recent_context=sanitized.context,
    )
    messages: list[ConversationMessage] = []
    if inference_request.system_prompt:
        messages.append(ConversationMessage("system", inference_request.system_prompt))
    if repeat_count:
        messages.append(
            ConversationMessage(
                "system",
                "Contexto de esta sesión: el usuario ya formuló una "
                "pregunta equivalente. La respuesta anterior se excluyó "
                "por curación. No presupongas que fue correcta, que "
                "hubo insatisfacción ni que se completó una respuesta.",
            )
        )
    for turn in curated_context:
        messages.extend(
            (
                ConversationMessage("user", turn.user_text),
                ConversationMessage("assistant", turn.assistant_text),
            )
        )
    messages.append(ConversationMessage("user", inference_request.prompt))
    metadata = dict(inference_request.metadata)
    if repeat_count:
        metadata["conversation_current_question_repeated"] = "true"
        metadata["conversation_current_question_repeat_count"] = str(
            repeat_count
        )
    if conversation.recent_context:
        metadata["conversation_context_input_turns"] = str(
            len(conversation.recent_context)
        )
        metadata["conversation_context_sanitized_turns"] = str(len(sanitized.context))
        metadata["conversation_context_reserved_removed_turns"] = str(
            sanitized.removed_turns
        )
        metadata["conversation_context_turns"] = str(len(curated_context))
        metadata["conversation_context_dropped_turns"] = str(
            len(conversation.recent_context) - len(curated_context)
        )
        metadata["conversation_context_curation_dropped_turns"] = str(
            len(sanitized.context) - len(curated_context)
        )
        metadata["conversation_context_characters"] = str(
            sum(
                len(turn.user_text) + len(turn.assistant_text)
                for turn in curated_context
            )
        )
        metadata["conversation_context_scope"] = "owner_session"
        metadata["conversation_context_sanitization"] = "reserved_prefixes"
        metadata["conversation_context_curation"] = "duplicate_question_and_statement"
    if not curated_context:
        return LLMRequest(
            prompt=inference_request.prompt,
            system_prompt=inference_request.system_prompt,
            model=inference_request.model,
            max_tokens=inference_request.max_tokens,
            temperature=inference_request.temperature,
            metadata=metadata,
            messages=tuple(messages),
        )

    lines = ["Contexto conversacional reciente de esta misma sesión:"]
    for turn in curated_context:
        lines.extend((f"Usuario: {turn.user_text}", f"ROBY: {turn.assistant_text}"))
    lines.extend(("", f"Usuario: {inference_request.prompt.strip()}", "ROBY:"))
    prompt = "\n".join(lines) if curated_context else inference_request.prompt
    return LLMRequest(
        prompt=prompt,
        system_prompt=inference_request.system_prompt,
        model=inference_request.model,
        max_tokens=inference_request.max_tokens,
        temperature=inference_request.temperature,
        metadata=metadata,
        messages=tuple(messages),
    )
