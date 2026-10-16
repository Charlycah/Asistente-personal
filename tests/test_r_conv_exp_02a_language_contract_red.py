from __future__ import annotations

from dataclasses import dataclass

from app.unified_experience_layer import UnifiedExperienceLayer
from core.governed_operational_conversation_pipeline import (
    GovernedOperationalInterception,
)


@dataclass(frozen=True)
class _Request:
    text: str


def _present(request_text: str, response_text: str):
    return UnifiedExperienceLayer().present(
        GovernedOperationalInterception(
            response_text=response_text,
            rationale="exp02a_language_contract",
        ),
        request=_Request(text=request_text),
    )


def test_exp02a_preserves_ordinary_spanish_response():
    response = "Hoy esta soleado y hace calor."

    result = _present(
        "Decime como esta el clima hoy.",
        response,
    )

    assert result is not None
    assert result.response_text == response


def test_exp02a_does_not_expose_unrequested_english_as_final_answer():
    response = "The weather is sunny and warm today."

    result = _present(
        "Decime como esta el clima hoy.",
        response,
    )

    assert result is not None
    assert result.response_text != response
    assert result.response_text.strip()
    assert "soleado" in result.response_text.lower()
    assert "calor" in result.response_text.lower()
    assert result.rationale == "exp02a_language_contract"


def test_exp02a_preserves_explicit_english_request():
    response = "The weather is sunny today."

    result = _present(
        "Responde en ingles: como esta el clima?",
        response,
    )

    assert result is not None
    assert result.response_text == response


def test_exp02a_preserves_spanish_with_english_technical_term():
    response = "El endpoint responde correctamente."

    result = _present(
        "Decime si funciona el endpoint.",
        response,
    )

    assert result is not None
    assert result.response_text == response


def test_exp02a_preserves_spanish_with_protected_code():
    response = "Ejecuta `python -m pytest -q` para comprobarlo."

    result = _present(
        "Como compruebo las pruebas?",
        response,
    )

    assert result is not None
    assert result.response_text == response


def test_exp02a_preserves_spanish_with_english_quotation():
    response = 'El mensaje recibido dice "The operation completed".'

    result = _present(
        "Que dice el mensaje recibido?",
        response,
    )

    assert result is not None
    assert result.response_text == response
