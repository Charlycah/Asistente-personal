from datetime import datetime, timezone

import pytest

from core.conversational_grounding_intelligence import (
    ConversationalGroundingIntelligence,
    ConversationalGroundingRuntimeContributor,
)
from core.llm_provider import LLMRequest

NOW = datetime(2026, 8, 16, 12, 0, tzinfo=timezone.utc)
GUIDANCE_PREFIX = "Grounding epistémico:"


def _epistemic_line(text: str) -> str:
    contribution = ConversationalGroundingRuntimeContributor(
        ConversationalGroundingIntelligence()
    ).contribute(
        owner="Carlos",
        session_id="main",
        text=text,
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    lines = tuple(
        line for line in contribution.prompt_lines if line.startswith(GUIDANCE_PREFIX)
    )
    assert len(lines) == 1
    return lines[0].casefold()


@pytest.mark.parametrize(
    "text",
    (
        "Hoy Juan está en Rosario.",
        "Ana estaba con Pedro en la estación.",
        "Luis usó el auto esta mañana.",
        "La cámara muestra a una persona golpeando la ventana.",
    ),
)
def test_epistemic_guidance_forbids_unsupported_semantic_strengthening(
    text: str,
) -> None:
    line = _epistemic_line(text)

    assert "no fortalecer" in line
    assert "semántic" in line
    assert "sin evidencia" in line or "sin soporte" in line


def test_semantic_strength_contract_remains_general_not_example_specific() -> None:
    line = _epistemic_line("Hoy Juan está en Rosario.")

    for forbidden in (
        "juan",
        "rosario",
        "residencia",
        "ana",
        "pedro",
        "auto",
        "propiedad",
        "ventana",
    ):
        assert forbidden not in line


def test_semantic_strength_contract_preserves_inference_escape_hatch() -> None:
    line = _epistemic_line("La cámara muestra a una persona golpeando la ventana.")

    assert "inferencia" in line or "posibilidad" in line


def test_unknown_required_condition_is_not_treated_as_satisfied() -> None:
    line = _epistemic_line(
        "Un recurso falló y no sabemos si existe una alternativa."
    )

    assert "condición necesaria desconocida" in line
    assert "no cuenta como satisfecha" in line


def test_absence_of_evidence_does_not_become_evidence_of_absence() -> None:
    line = _epistemic_line(
        "No sabemos si existe otra fuente disponible."
    )

    assert "ausencia de evidencia" in line
    assert "no demuestra ausencia" in line


def test_unknown_precondition_guidance_remains_domain_general() -> None:
    line = _epistemic_line(
        "No sabemos si existe otra copia del registro."
    )

    for forbidden in (
        "sensor",
        "temperatura",
        "neral",
        "registro",
        "copia",
    ):
        assert forbidden not in line
