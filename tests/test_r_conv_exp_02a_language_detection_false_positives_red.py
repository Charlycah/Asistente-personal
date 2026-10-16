import pytest

from app.household_conversation_style import (
    DEFAULT_HOUSEHOLD_CONVERSATION_STYLE,
)
from app.runtime_environment_ports import (
    EnvironmentInferenceRequestPort,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)


@pytest.mark.parametrize(
    "message",
    [
        "Please answer in English.",
        "Respond in English, please.",
        "Respondé en inglés, por favor.",
        "Por favor, respondé en inglés.",
        "Please answer in English and explain the result.",
    ],
)
def test_exp02a_explicit_english_instruction_is_preserved(message):
    request = GovernedConversationPipelineRequest(
        owner="test-owner",
        session_id="desktop-main",
        text=message,
    )

    built = EnvironmentInferenceRequestPort().build(request)

    assert built.system_prompt is not None
    assert "Respond in English" in built.system_prompt
    assert built.prompt == message
    assert built.metadata == {
        "owner": "test-owner",
        "session": "desktop-main",
    }


@pytest.mark.parametrize(
    "message",
    [
        "No respondas en inglés.",
        'Explicame qué significa "respond in English".',
        "Mostrame la frase respond in English en un ejemplo.",
        "Decime cómo funciona un endpoint.",
        "No, please answer in English.",
        "¿Qué significa respond in English?",
    ],
)
def test_exp02a_english_mentions_do_not_change_response_language(
    message,
):
    request = GovernedConversationPipelineRequest(
        owner="test-owner",
        session_id="desktop-main",
        text=message,
    )

    built = EnvironmentInferenceRequestPort().build(request)

    assert built.system_prompt == (
        DEFAULT_HOUSEHOLD_CONVERSATION_STYLE.system_prompt
    )
    assert built.prompt == message
    assert built.metadata == {
        "owner": "test-owner",
        "session": "desktop-main",
    }
