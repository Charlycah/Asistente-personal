from __future__ import annotations

from core.llm_provider import LLMRequest
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
                "model": "llama3",
                "choices": [
                    {
                        "message": {
                            "content": "The weather is sunny today."
                        }
                    }
                ],
            },
        )


def test_exp02a_explicit_english_does_not_conflict_with_default_spanish():
    transport = RecordingTransport()
    provider = LocalProviderRuntimeAdapter(
        LocalProviderRuntimeSettings(
            provider_name="local-openai",
            model="llama3",
            system_prompt=(
                "Respond? siempre en espa?ol argentino."
            ),
        ),
        transport=transport,
    )

    result = provider.generate(
        LLMRequest(
            prompt="Respond? en ingl?s: ?c?mo est? el clima?",
            system_prompt="Respond in English.",
        )
    )

    assert result.accepted
    assert len(transport.calls) == 1

    messages = transport.calls[0]["payload"]["messages"]
    system_text = " ".join(
        message["content"]
        for message in messages
        if message["role"] == "system"
    )

    assert "Respond in English." in system_text
    assert "Respond? siempre en espa?ol argentino." not in system_text
