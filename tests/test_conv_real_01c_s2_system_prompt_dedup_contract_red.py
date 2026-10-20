from __future__ import annotations

from app.runtime_root_factory import EnvironmentInferenceRequestPort
from core.conversational_context_continuity import (
    enrich_with_recent_conversation_context,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)
from core.llm_provider import ConversationMessage, LLMRequest
from core.local_provider_runtime_adapter import (
    LocalProviderRuntimeAdapter,
    LocalProviderRuntimeSettings,
    TransportResponse,
)


class RecordingTransport:
    def __init__(self) -> None:
        self.calls = []

    def request(self, **kwargs):
        self.calls.append(kwargs)
        return TransportResponse(
            200,
            {
                "model": "llama3:latest",
                "choices": [{"message": {"content": "Respuesta"}}],
            },
        )


def test_productive_system_prompt_is_not_duplicated():
    conversation = GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="desktop-main",
        text="Hola ROBY",
    )

    inference_request = EnvironmentInferenceRequestPort().build(
        conversation
    )
    enriched = enrich_with_recent_conversation_context(
        conversation=conversation,
        inference_request=inference_request,
    )

    transport = RecordingTransport()
    provider = LocalProviderRuntimeAdapter(
        LocalProviderRuntimeSettings(
            provider_name="local-openai",
            endpoint="http://127.0.0.1:11434/v1",
            model="llama3:latest",
            system_prompt="",
        ),
        transport=transport,
    )

    result = provider.generate(enriched)

    assert result.accepted

    sent = transport.calls[0]["payload"]["messages"]

    assert sent == [
        {
            "role": "system",
            "content": inference_request.system_prompt,
        },
        {
            "role": "user",
            "content": "Hola ROBY",
        },
    ]



def test_composed_system_guidance_is_not_repeated():

    provider = LocalProviderRuntimeAdapter(
        LocalProviderRuntimeSettings(
            provider_name="local-openai",
            endpoint="http://127.0.0.1:11434/v1",
            model="llama3:latest",
            system_prompt="Estilo configurado",
        )
    )
    request = LLMRequest(
        prompt="Hola",
        system_prompt="Guia gobernada",
        messages=(
            ConversationMessage("system", "Guia gobernada"),
            ConversationMessage("user", "Hola"),
        ),
    )

    sent = provider._messages(request)

    assert sent == [
        {"role": "system", "content": "Estilo configurado"},
        {"role": "system", "content": "Guia gobernada"},
        {"role": "user", "content": "Hola"},
    ]


def test_configured_and_governed_system_messages_are_not_duplicated():

    adapter = LocalProviderRuntimeAdapter(
        LocalProviderRuntimeSettings(
            provider_name="local-openai",
            endpoint="http://127.0.0.1:11434/v1",
            model="llama3:latest",
            system_prompt="Estilo configurado",
        )
    )

    request = LLMRequest(
        prompt="Hola",
        system_prompt="Guia gobernada",
        messages=(
            ConversationMessage("system", "Estilo configurado"),
            ConversationMessage("system", "Guia gobernada"),
            ConversationMessage("user", "Hola"),
        ),
    )

    assert adapter._messages(request) == [
        {"role": "system", "content": "Estilo configurado"},
        {"role": "system", "content": "Guia gobernada"},
        {"role": "user", "content": "Hola"},
    ]


def test_configured_system_message_is_not_repeated_in_composed_guidance():

    adapter = LocalProviderRuntimeAdapter(
        LocalProviderRuntimeSettings(
            provider_name="local-openai",
            endpoint="http://127.0.0.1:11434/v1",
            model="llama3:latest",
            system_prompt="Estilo configurado",
        )
    )

    request = LLMRequest(
        prompt="Hola",
        system_prompt="Guia gobernada",
        messages=(
            ConversationMessage("system", "Estilo configurado"),
            ConversationMessage("user", "Hola"),
        ),
    )

    assert adapter._messages(request) == [
        {"role": "system", "content": "Estilo configurado"},
        {"role": "system", "content": "Guia gobernada"},
        {"role": "user", "content": "Hola"},
    ]
