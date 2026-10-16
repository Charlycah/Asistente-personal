from __future__ import annotations

from app.household_conversation_style import (
    DEFAULT_HOUSEHOLD_CONVERSATION_STYLE,
)
from app.runtime_environment_ports import (
    EnvironmentInferenceRequestPort,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)


def _inference_for(text: str):
    request = GovernedConversationPipelineRequest(
        owner="test-owner",
        session_id="exp02a-language-delimiter",
        text=text,
    )
    return EnvironmentInferenceRequestPort().build(request)


def test_exp02a_explicit_english_colon_is_recognized():
    inference = _inference_for(
        "Respondé en inglés: explicá qué es una variable."
    )

    assert inference.system_prompt == (
        DEFAULT_HOUSEHOLD_CONVERSATION_STYLE
        .system_prompt_for_language("en")
    )


def test_exp02a_technical_terms_remain_spanish_default():
    inference = _inference_for(
        "Explicame qué es un endpoint de una API."
    )

    assert inference.system_prompt == (
        DEFAULT_HOUSEHOLD_CONVERSATION_STYLE.system_prompt
    )
