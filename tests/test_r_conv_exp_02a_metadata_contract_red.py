from __future__ import annotations

from dataclasses import dataclass

from app.unified_experience_layer import UnifiedExperienceLayer
from core.governed_operational_conversation_pipeline import (
    GovernedOperationalInterception,
)


@dataclass(frozen=True)
class _Request:
    text: str


def test_exp02a_presentation_preserves_network_provenance():
    original = GovernedOperationalInterception(
        response_text="Hola, hola. Te puedo ayudar.",
        rationale="exp02a_metadata_preservation",
        network_access_performed=True,
    )

    presented = UnifiedExperienceLayer().present(
        original,
        request=_Request(text="Necesito ayuda."),
    )

    assert presented is not None
    assert presented.response_text != original.response_text
    assert presented.rationale == original.rationale
    assert presented.origin == original.origin
    assert (
        presented.network_access_performed
        == original.network_access_performed
    )
