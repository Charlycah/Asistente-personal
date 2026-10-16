from __future__ import annotations

import pytest

from app.companion_expression_policy import CompanionExpressionPolicy


@pytest.mark.parametrize(
    ("original", "expected"),
    [
        (
            "Vos! Un endpoint es una direccion URL.",
            "Un endpoint es una direccion URL.",
        ),
        (
            "¡Vos! En Python, una funcion reutiliza codigo.",
            "En Python, una funcion reutiliza codigo.",
        ),
        (
            "Vos! Podes definir una funcion.",
            "Podes definir una funcion.",
        ),
        (
            "Vos podes definir una funcion.",
            "Vos podes definir una funcion.",
        ),
        (
            "Si vos queres, revisamos el codigo.",
            "Si vos queres, revisamos el codigo.",
        ),
        (
            'La expresion "Vos!" aparece en el texto.',
            'La expresion "Vos!" aparece en el texto.',
        ),
        (
            "`Vos!` es el contenido literal.",
            "`Vos!` es el contenido literal.",
        ),
        (
            "```text\nVos!\n```\nExplicacion.",
            "```text\nVos!\n```\nExplicacion.",
        ),
        (
            "En Python, una funcion permite reutilizar codigo.",
            "En Python, una funcion permite reutilizar codigo.",
        ),
    ],
)
def test_exp02c_vos_opening_presentation_contract(
    original: str,
    expected: str,
) -> None:
    policy = CompanionExpressionPolicy()

    assert policy.apply(original) == expected
