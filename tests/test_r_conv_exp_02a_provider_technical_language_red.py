from __future__ import annotations

from app.household_conversation_style import (
    DEFAULT_HOUSEHOLD_CONVERSATION_STYLE,
)
from app.local_provider_factory import (
    build_local_provider_from_environment,
)
from app.runtime_environment_ports import (
    EnvironmentInferenceRequestPort,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)


def _messages_for(text: str) -> list[dict[str, str]]:
    request = GovernedConversationPipelineRequest(
        owner="test-owner",
        session_id="exp02a-provider-language",
        text=text,
    )
    inference = EnvironmentInferenceRequestPort().build(request)
    provider = build_local_provider_from_environment()
    return provider._messages(inference)


def test_exp02a_technical_terms_do_not_switch_language():
    messages = _messages_for(
        "Explicame qué es un endpoint de una API."
    )

    assert messages[0]["role"] == "system"
    assert messages[-1]["role"] == "user"

    system_text = messages[0]["content"].casefold()

    assert "español" in system_text or "espanol" in system_text
    assert "términos técnicos" in system_text or (
        "terminos tecnicos" in system_text
    )
    assert "inglés" in system_text or "ingles" in system_text
    assert "no" in system_text and (
        "cambiar" in system_text
        or "cambio" in system_text
    )


def test_exp02a_explicit_english_preserves_precedence():
    messages = _messages_for(
        "Respondé en inglés: explicá qué es una variable."
    )

    assert messages[0]["role"] == "system"

    system_text = messages[0]["content"]

    assert (
        DEFAULT_HOUSEHOLD_CONVERSATION_STYLE
        .system_prompt_for_language("en")
        in system_text
    )
    assert (
        DEFAULT_HOUSEHOLD_CONVERSATION_STYLE.system_prompt
        not in system_text
    )
