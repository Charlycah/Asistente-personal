from __future__ import annotations

import pytest

from app.runtime_root_factory import EnvironmentInferenceRequestPort
from core.conversational_context_continuity import (
    enrich_with_recent_conversation_context,
)
from core.governed_operational_conversation_pipeline import (
    ConversationalContextTurn,
    GovernedConversationPipelineRequest,
)
from core.llm_model_providers import OllamaProvider
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
                "choices": [{"message": {"content": "Carlos"}}],
            },
        )


class RecordingPost:
    def __init__(self) -> None:
        self.payload = None

    def __call__(self, *_args, **kwargs):
        self.payload = kwargs["json_payload"]

        class Response:
            status_code = 200

            @staticmethod
            def json():
                return {"response": "Carlos"}

        return Response()


def test_conversation_message_is_immutable_and_normalized():
    message = ConversationMessage("user", "  Hola ROBY  ")
    assert message.content == "Hola ROBY"
    with pytest.raises(ValueError, match="blank"):
        ConversationMessage("assistant", "   ")


def test_continuity_builds_role_preserving_messages():
    conversation = GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="desktop-main",
        text="¿Cómo me llamo?",
        recent_context=(
            ConversationalContextTurn(
                user_text="Mi nombre es Carlos.",
                assistant_text="Entendido, Carlos.",
            ),
        ),
    )

    built = enrich_with_recent_conversation_context(
        conversation=conversation,
        inference_request=EnvironmentInferenceRequestPort().build(conversation),
    )

    assert built.system_prompt
    assert [(item.role, item.content) for item in built.messages] == [
        ("system", built.system_prompt),
        ("user", "Mi nombre es Carlos."),
        ("assistant", "Entendido, Carlos."),
        ("user", "¿Cómo me llamo?"),
    ]
    assert "Contexto conversacional" in built.prompt


def test_first_turn_is_structured_without_changing_legacy_prompt():
    conversation = GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="desktop-main",
        text="Hola ROBY",
    )

    built = enrich_with_recent_conversation_context(
        conversation=conversation,
        inference_request=EnvironmentInferenceRequestPort().build(conversation),
    )

    assert built.prompt == "Hola ROBY"
    assert built.system_prompt
    assert built.messages == (
        ConversationMessage("system", built.system_prompt),
        ConversationMessage("user", "Hola ROBY"),
    )


def test_openai_compatible_adapter_sends_structured_roles_directly():
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
    request = LLMRequest(
        prompt="legacy fallback",
        messages=(
            ConversationMessage("user", "Mi nombre es Carlos."),
            ConversationMessage("assistant", "Entendido, Carlos."),
            ConversationMessage("user", "¿Cómo me llamo?"),
        ),
    )

    assert provider.generate(request).accepted
    assert transport.calls[0]["payload"]["messages"] == [
        {"role": "user", "content": "Mi nombre es Carlos."},
        {"role": "assistant", "content": "Entendido, Carlos."},
        {"role": "user", "content": "¿Cómo me llamo?"},
    ]


def test_text_only_ollama_provider_serializes_structured_messages_at_boundary():
    post = RecordingPost()
    provider = OllamaProvider(http_post=post)
    request = LLMRequest(
        prompt="legacy fallback",
        messages=(
            ConversationMessage("user", "Mi nombre es Carlos."),
            ConversationMessage("assistant", "Entendido, Carlos."),
            ConversationMessage("user", "¿Cómo me llamo?"),
        ),
    )

    assert provider.generate(request).accepted
    assert post.payload["prompt"] == (
        "Usuario: Mi nombre es Carlos.\n"
        "ROBY: Entendido, Carlos.\n"
        "Usuario: ¿Cómo me llamo?"
    )


def test_openai_compatible_adapter_composes_configured_and_request_system_guidance():
    transport = RecordingTransport()
    provider = LocalProviderRuntimeAdapter(
        LocalProviderRuntimeSettings(
            provider_name="local-openai",
            endpoint="http://127.0.0.1:11434/v1",
            model="llama3:latest",
            system_prompt="Estilo doméstico",
        ),
        transport=transport,
    )
    original_messages = (
        ConversationMessage("user", "Dato"),
        ConversationMessage("assistant", "Entendido"),
        ConversationMessage("user", "Seguimos"),
    )
    request = LLMRequest(
        prompt="legacy fallback",
        system_prompt="Guía cognitiva gobernada",
        messages=original_messages,
    )

    assert provider.generate(request).accepted
    sent = transport.calls[0]["payload"]["messages"]
    assert sent[0] == {
        "role": "system",
        "content": "Estilo doméstico\n\nGuía cognitiva gobernada",
    }
    assert sent[1:] == [
        {"role": item.role, "content": item.content}
        for item in original_messages
    ]


def test_openai_compatible_adapter_preserves_existing_structured_system_message():
    transport = RecordingTransport()
    provider = LocalProviderRuntimeAdapter(
        LocalProviderRuntimeSettings(
            provider_name="local-openai",
            endpoint="http://127.0.0.1:11434/v1",
            model="llama3:latest",
            system_prompt="Estilo doméstico",
        ),
        transport=transport,
    )
    request = LLMRequest(
        prompt="legacy fallback",
        system_prompt="Guía cognitiva gobernada",
        messages=(
            ConversationMessage("system", "Sistema estructurado existente"),
            ConversationMessage("user", "Hola"),
        ),
    )

    assert provider.generate(request).accepted
    sent = transport.calls[0]["payload"]["messages"]
    assert sent == [
        {
            "role": "system",
            "content": "Estilo doméstico\n\nGuía cognitiva gobernada",
        },
        {"role": "system", "content": "Sistema estructurado existente"},
        {"role": "user", "content": "Hola"},
    ]


def test_openai_compatible_adapter_deduplicates_identical_system_sources():
    transport = RecordingTransport()
    provider = LocalProviderRuntimeAdapter(
        LocalProviderRuntimeSettings(
            provider_name="local-openai",
            endpoint="http://127.0.0.1:11434/v1",
            model="llama3:latest",
            system_prompt="Mismo sistema",
        ),
        transport=transport,
    )
    request = LLMRequest(
        prompt="Hola",
        system_prompt="Mismo sistema",
        messages=(ConversationMessage("user", "Hola"),),
    )

    assert provider.generate(request).accepted
    sent = transport.calls[0]["payload"]["messages"]
    assert sent[0] == {"role": "system", "content": "Mismo sistema"}
    assert len([item for item in sent if item["role"] == "system"]) == 1
