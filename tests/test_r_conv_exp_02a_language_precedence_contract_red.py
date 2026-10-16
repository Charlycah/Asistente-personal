from app.household_conversation_style import (
    DEFAULT_HOUSEHOLD_CONVERSATION_STYLE,
)
from app.runtime_environment_ports import (
    EnvironmentInferenceRequestPort,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)
from core.llm_service import LLMRequest
from core.local_provider_runtime_adapter import (
    LocalProviderRuntimeAdapter,
    LocalProviderRuntimeSettings,
)


def test_exp02a_explicit_english_has_no_conflicting_spanish_guidance():
    provider = LocalProviderRuntimeAdapter(
        LocalProviderRuntimeSettings(
            provider_name="local-openai",
            model="llama3",
            system_prompt=(
                DEFAULT_HOUSEHOLD_CONVERSATION_STYLE.system_prompt
            ),
        )
    )
    request = LLMRequest(
        prompt="Please answer in English.",
        system_prompt=(
            DEFAULT_HOUSEHOLD_CONVERSATION_STYLE
            .system_prompt_for_language("en")
        ),
    )

    effective = provider._effective_system_prompt(request)

    assert "Respond in English" in effective
    assert (
        DEFAULT_HOUSEHOLD_CONVERSATION_STYLE.system_prompt
        not in effective
    )
    assert "Sos Roby" in effective


def test_exp02a_explicit_english_reaches_inference_request():
    request = GovernedConversationPipelineRequest(
        owner="test-owner",
        session_id="desktop-main",
        text="Please answer in English.",
    )

    built = EnvironmentInferenceRequestPort().build(request)

    assert built.system_prompt is not None
    assert "Respond in English" in built.system_prompt
    assert built.prompt == request.text
    assert built.metadata == {
        "owner": "test-owner",
        "session": "desktop-main",
    }
