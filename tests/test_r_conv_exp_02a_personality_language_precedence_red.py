from app.household_conversation_style import (
    DEFAULT_HOUSEHOLD_CONVERSATION_STYLE,
)
from core.llm_provider import LLMRequest
from core.local_provider_runtime_adapter import (
    LocalProviderRuntimeAdapter,
    LocalProviderRuntimeSettings,
)


def test_exp02a_english_precedence_preserves_personality_expression():
    style = DEFAULT_HOUSEHOLD_CONVERSATION_STYLE
    english = style.system_prompt_for_language("en")

    personality = (
        "[CANONICAL STABLE PERSONALITY EXPRESSION]\n"
        "- Delivery tone: sober\n"
        "- Response detail: concise\n"
        "- Response structure: natural"
    )

    provider = LocalProviderRuntimeAdapter(
        LocalProviderRuntimeSettings(
            provider_name="local-openai",
            model="llama3",
            system_prompt=style.system_prompt,
        )
    )

    request = LLMRequest(
        prompt="Please answer in English.",
        system_prompt=f"{english}\n\n{personality}",
    )

    effective = provider._effective_system_prompt(request)

    assert "Respond in English" in effective
    assert personality in effective
    assert style.system_prompt not in effective
    assert provider.settings.system_prompt == style.system_prompt
