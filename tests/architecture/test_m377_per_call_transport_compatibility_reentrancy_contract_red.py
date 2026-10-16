"""M377 per-call transport RED: no production or protected contract mutation."""

import inspect
from dataclasses import is_dataclass

import pytest

from app.runtime_ui_adapter import LocalConversationUIAdapter
from app.ui_adapter import UIResponse


@pytest.mark.parametrize(
    "method_name,required_argument",
    [
        ("submit_text_with_turn_evidence", "integrated_visual_context"),
        ("submit_voice_with_turn_evidence", "text"),
    ],
)
def test_red_per_call_entrypoint_exposes_correlated_result(
    method_name: str, required_argument: str
) -> None:
    """A per-call operation must expose evidence without lateral last-turn state."""
    method = getattr(LocalConversationUIAdapter, method_name, None)
    assert callable(method), (
        f"M377 RED: no per-call correlated operation {method_name}"
    )
    assert required_argument in inspect.signature(method).parameters


def test_red_per_call_result_is_immutable_pair() -> None:
    """The adapter module must provide a frozen response/turn value carrier."""
    import app.runtime_ui_adapter as adapter_module

    result_type = getattr(adapter_module, "TurnBoundUIResult", None)
    assert result_type is not None, "M377 RED: missing per-call result value"
    assert is_dataclass(result_type)
    assert result_type.__dataclass_params__.frozen
    assert {"response", "turn"}.issubset(result_type.__dataclass_fields__)


def test_protection_historical_text_and_voice_return_annotations() -> None:
    """The public historical methods must retain UIResponse return contracts."""
    for method_name in ("submit_text", "submit_voice"):
        method = getattr(LocalConversationUIAdapter, method_name)
        assert inspect.signature(method).return_annotation in (
            "UIResponse", UIResponse
        )


def test_protection_historical_text_visual_keyword_arguments() -> None:
    """Visual and explicit-evidence keywords remain in historical submit_text."""
    signature = inspect.signature(LocalConversationUIAdapter.submit_text)
    for name in (
        "explicit_document_ids",
        "explicit_sources",
        "explicit_evidence_references",
        "integrated_visual_context",
    ):
        assert name in signature.parameters
        assert signature.parameters[name].kind is inspect.Parameter.KEYWORD_ONLY
