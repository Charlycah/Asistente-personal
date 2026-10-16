from __future__ import annotations

from dataclasses import dataclass

from app.unified_experience_layer import UnifiedExperienceLayer
from core.governed_operational_conversation_pipeline import (
    GovernedOperationalInterception,
)


@dataclass(frozen=True)
class _Request:
    text: str


def test_exp02a_unrequested_english_requires_governed_handling():
    original = "The weather is sunny and warm today."
    result = UnifiedExperienceLayer().present(
        GovernedOperationalInterception(
            response_text=original,
            rationale="exp02a_governed_language_boundary",
        ),
        request=_Request(text="Decime como esta el clima hoy."),
    )

    assert result is not None

    assert (
        result.response_text != original
        or result.rationale != "exp02a_governed_language_boundary"
    ), "Unrequested English crossed the governed presentation boundary"



def test_exp02a_metadata_only_change_cannot_satisfy_language_contract():
    original = "The weather is sunny and warm today."

    result = UnifiedExperienceLayer().present(
        GovernedOperationalInterception(
            response_text=original,
            rationale="exp02a_metadata_preservation",
        ),
        request=_Request(text="Decime como esta el clima hoy."),
    )

    assert result is not None
    assert result.response_text != original, (
        "Changing rationale alone does not resolve unrequested English"
    )
