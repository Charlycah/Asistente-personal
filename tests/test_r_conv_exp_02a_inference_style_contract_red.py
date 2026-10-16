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


def test_exp02a_inference_port_uses_canonical_spanish_style():
    request = GovernedConversationPipelineRequest(
        owner="test-owner",
        session_id="desktop-main",
        text="Decime como funciona.",
    )

    built = EnvironmentInferenceRequestPort().build(request)

    assert built.system_prompt == (
        DEFAULT_HOUSEHOLD_CONVERSATION_STYLE.system_prompt
    )


def test_exp02a_inference_style_preserves_original_request():
    request = GovernedConversationPipelineRequest(
        owner="test-owner",
        session_id="desktop-main",
        text="Explicame el resultado.",
    )

    built = EnvironmentInferenceRequestPort().build(request)

    assert built.prompt == request.text
    assert built.metadata == {
        "owner": "test-owner",
        "session": "desktop-main",
    }
