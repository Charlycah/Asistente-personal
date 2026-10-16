from __future__ import annotations

import hashlib
import inspect
from pathlib import Path

from app import desktop_bootstrap
from app.governed_proposal_executive_notification_runtime import (
    GovernedProposalExecutiveNotificationRuntime,
)

ROOT = Path(__file__).resolve().parents[2]
PROTECTED_RUNTIME_UI_ADAPTER_SHA256 = (
    "2afb8629a78800c64932e289a905a098bb1a32bd5952ec152b204e42924a08e1"
)


def test_red_certified_proposal_review_transport_desktop_composition_contract() -> None:
    """RED: compose S1-B outside both protected conversational surfaces."""
    runtime_ui_adapter = ROOT / "app" / "runtime_ui_adapter.py"

    assert hashlib.sha256(runtime_ui_adapter.read_bytes()).hexdigest() == (
        PROTECTED_RUNTIME_UI_ADAPTER_SHA256
    )

    bootstrap_source = inspect.getsource(desktop_bootstrap.build_unified_desktop_app)
    notification_source = inspect.getsource(
        GovernedProposalExecutiveNotificationRuntime
    )

    # S1-C remains a composition obligation. The protected UI adapter must not own
    # proposal-review semantics or state. A bounded exterior composition seam must
    # reuse the two already-certified S1-A/S1-B components.
    assert "GovernedProposalHumanReviewProjection" in bootstrap_source, (
        "RED: Composition Root does not construct the certified S1-A human-review "
        "projection"
    )
    assert "GovernedPresentedProposalReviewTransport" in bootstrap_source, (
        "RED: Composition Root does not construct the certified S1-B exact-reference "
        "review transport"
    )
    assert "GovernedProposalDesktopReviewComposition" in bootstrap_source, (
        "RED: no bounded exterior desktop composition seam connects the certified "
        "S1-B transport to the existing protected desktop conversation path"
    )

    # Presentation identity must still be retained only at the proposal-specific
    # notification edge, after the canonical OFFERED transition succeeds.
    assert "retain_presented_proposal_reference" in notification_source, (
        "RED: broker-dispatched exact proposal identity is not retained by S1-B"
    )

    combined = (bootstrap_source + notification_source).casefold()
    forbidden = (
        "unique_offered",
        "latest_offered",
        "proposal_title_lookup",
        "proposal_summary_lookup",
        "humanresponsebrain",
        "proposalbrain",
        "self_modif",
    )
    assert not any(token in combined for token in forbidden)
