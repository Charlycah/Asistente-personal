from __future__ import annotations

from app.unified_experience_layer import UnifiedExperienceLayer
from core.llm_provider import LLMResponse
from tests.test_m166_provider_health_evaluation import NOW
from tests.test_m177_governed_operational_conversation_pipeline import (
    pipeline,
    request,
)


def _run_with_provider_text(text: str):
    runtime, preparation, provider = pipeline(
        experience_layer=UnifiedExperienceLayer()
    )

    provider.response = LLMResponse(
        text=text,
        provider=provider.name,
        model="llama3",
    )

    result = runtime.process(
        request(text="Decime como esta el clima hoy."),
        now=NOW,
    )

    return result, preparation, provider


def test_exp02a_pipeline_preserves_compliant_spanish_response():
    expected = "Hoy esta soleado y hace calor."

    result, preparation, provider = _run_with_provider_text(expected)

    assert result.operational_response.response_text == expected
    assert len(preparation.calls) == 1
    assert len(provider.calls) == 1
    assert result.provider_call_performed
    assert not result.platform_mutation_performed


def test_exp02a_pipeline_does_not_deliver_unrequested_english_unchanged():
    original = "The weather is sunny and warm today."

    result, preparation, provider = _run_with_provider_text(original)

    assert len(preparation.calls) == 1
    assert len(provider.calls) == 1
    assert result.provider_call_performed
    assert not result.platform_mutation_performed

    visible_text = result.operational_response.response_text
    assert visible_text != original, (
        "Unrequested English crossed the canonical pipeline unchanged"
    )
