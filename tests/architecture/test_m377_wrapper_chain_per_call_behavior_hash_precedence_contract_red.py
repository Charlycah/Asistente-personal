"""M377 RED: existing wrapper-chain per-call transport; no production mutation."""

from __future__ import annotations

import hashlib
import inspect
from pathlib import Path

import pytest

from app.episodic_source_constraint import EpisodicSourceConstraintDesktopComposition
from app.governed_proposal_desktop_review_composition import (
    GovernedProposalDesktopReviewComposition,
)
from app.runtime_ui_adapter import (
    ConversationalPersonalityUIAdapter,
    OptionalServiceGuardUIAdapter,
)
from app.same_turn_governed_visual_result_exposure import (
    SameTurnVisualUIAdapterComposition,
)
from app.ui_adapter import UIResponse

WRAPPERS = (
    ConversationalPersonalityUIAdapter,
    OptionalServiceGuardUIAdapter,
    EpisodicSourceConstraintDesktopComposition,
    GovernedProposalDesktopReviewComposition,
    SameTurnVisualUIAdapterComposition,
)


@pytest.mark.parametrize("wrapper", WRAPPERS)
@pytest.mark.parametrize(
    "operation",
    ("submit_text_with_turn_evidence", "submit_voice_with_turn_evidence"),
)
def test_red_existing_wrapper_exposes_per_call_evidence(
    wrapper: type, operation: str
) -> None:
    """No existing wrapper may silently discard turn evidence."""
    method = getattr(wrapper, operation, None)
    assert callable(method), (
        f"M377 RED: {wrapper.__name__}.{operation} lacks per-call transport"
    )


def test_red_visual_composition_exposes_same_call_visual_evidence() -> None:
    """The explicit visual branch must preserve its own turn and applied result."""
    method = getattr(
        SameTurnVisualUIAdapterComposition,
        "submit_text_with_visual_companion_and_turn_evidence",
        None,
    )
    assert callable(method), (
        "M377 RED: visual composition lacks same-call evidence transport"
    )


def test_protection_historical_wrapper_return_annotations() -> None:
    """Historical text and voice entrypoints retain their UIResponse contract."""
    for wrapper in WRAPPERS:
        for operation in ("submit_text", "submit_voice"):
            signature = inspect.signature(getattr(wrapper, operation))
            annotation = signature.return_annotation
            assert annotation in (UIResponse, "UIResponse"), (
                wrapper.__name__,
                operation,
                annotation,
            )


def test_protection_visual_historical_pair_return() -> None:
    """The visual historical API continues returning the original pair."""
    method = SameTurnVisualUIAdapterComposition.submit_text_with_visual_companion
    annotation = inspect.signature(method).return_annotation
    assert annotation in (
        "tuple[UIResponse, object | None]",
        tuple[UIResponse, object | None],
    )


def test_protection_adapter_sha256_remains_original() -> None:
    """This RED delivery must not change the protected adapter's bytes."""
    root = Path(__file__).resolve().parents[2]
    content = (root / "app" / "runtime_ui_adapter.py").read_bytes()
    assert hashlib.sha256(content).hexdigest() == (
        "2afb8629a78800c64932e289a905a098bb1a32bd5952ec152b204e42924a08e1"
    )
