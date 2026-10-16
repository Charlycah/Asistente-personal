from __future__ import annotations

import hashlib
import importlib
from pathlib import Path
from types import SimpleNamespace

from core.governed_reasoning.longitudinal_intellectual_identity import (
    LongitudinalIntellectualIdentityStatus,
)

ROOT = Path(__file__).resolve().parents[2]
REASONING_RUNTIME = ROOT / "app/governed_reasoning_runtime.py"
CERTIFIED_REASONING_SHA256 = (
    "f8c96d92c08fff1b9219afd68974b79ba319f087b2fb32fbb20d5856aaa91f2f"
)
ADAPTER_MODULE = "app.longitudinal_intellectual_identity_productive_adapter"


class _BoundedExplanatoryModelGateway:
    def __init__(self, *, candidate_model_id: str | None) -> None:
        self.candidate_model_id = candidate_model_id
        self.calls: list[tuple[str, str, str]] = []

    def productive_explanatory_model_consumption(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
    ) -> SimpleNamespace | None:
        self.calls.append((owner, session_id, turn_id))
        if self.candidate_model_id is None:
            return None
        return SimpleNamespace(
            model=SimpleNamespace(model_id=self.candidate_model_id)
        )


def _adapter_class():
    module = importlib.import_module(ADAPTER_MODULE)
    return module.LongitudinalIntellectualIdentityProductiveAdapterV1


def test_cih_2dh_11b_preserves_certified_reasoning_runtime_byte_identical() -> None:
    assert hashlib.sha256(REASONING_RUNTIME.read_bytes()).hexdigest() == (
        CERTIFIED_REASONING_SHA256
    )


def test_cih_2dh_11b_external_adapter_reuses_only_public_bounded_lookup() -> None:
    gateway = _BoundedExplanatoryModelGateway(candidate_model_id="model-a")
    adapter = _adapter_class()(gateway)

    result = adapter.assess(
        owner="OWNER-A",
        session_id="session-a",
        candidate_turn_id="prior-turn",
        current_artifact_reference="current-artifact",
        identity_evidence_references=("identity-evidence-1",),
        relational_evidence_references=("structural-evidence-1",),
    )

    assert gateway.calls == [("OWNER-A", "session-a", "prior-turn")]
    assert result is not None
    assert result.candidate_artifact_reference == "model-a"
    assert result.current_artifact_reference == "current-artifact"
    assert result.status is LongitudinalIntellectualIdentityStatus.INSUFFICIENT


def test_cih_2dh_11b_missing_candidate_fails_closed_without_search() -> None:
    gateway = _BoundedExplanatoryModelGateway(candidate_model_id=None)
    adapter = _adapter_class()(gateway)

    result = adapter.assess(
        owner="owner-a",
        session_id="session-a",
        candidate_turn_id="missing-turn",
        current_artifact_reference="current-artifact",
        identity_evidence_references=("identity-evidence-1",),
    )

    assert result is None
    assert gateway.calls == [("owner-a", "session-a", "missing-turn")]


def test_cih_2dh_11b_assessment_remains_transient_and_non_revisional() -> None:
    gateway = _BoundedExplanatoryModelGateway(candidate_model_id="model-a")
    adapter = _adapter_class()(gateway)

    result = adapter.assess(
        owner="owner-a",
        session_id="session-a",
        candidate_turn_id="prior-turn",
        current_artifact_reference="current-artifact",
        identity_evidence_references=("identity-evidence-1",),
    )

    assert result is not None
    assert result.transient is True
    assert result.persists is False
    assert result.authorizes_revision is False
    assert result.creates_learning is False
    assert result.modifies_memory is False
    assert not hasattr(adapter, "identity_registry")
    assert not hasattr(adapter, "revision_registry")
