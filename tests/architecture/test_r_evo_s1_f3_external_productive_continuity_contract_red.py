from __future__ import annotations

import hashlib
import importlib.util
from datetime import datetime, timezone
from pathlib import Path

from app.governed_reasoning_runtime import (
    CanonicalProductiveReasoningSource,
    OfficialGovernedReasoningRuntimeGateway,
)
from core.governed_reasoning.context import ReasoningQuery
from core.runtime_composition_root.models import RuntimeCompositionDependencies

ROOT = Path(__file__).resolve().parents[2]
CONTINUITY_MODULE = "app.explicit_multisource_productive_continuity_adapter"

PROTECTED_SURFACES = {
    "app/governed_reasoning_runtime.py": (
        "f8c96d92c08fff1b9219afd68974b79ba319f087b2fb32fbb20d5856aaa91f2f"
    ),
    "app/same_episode_explicit_evidence_convergence_adapter.py": (
        "5be01adfe0c0e3a32065bcb15918013d7e20e5cb7e0092072c88df1dea5aef3d"
    ),
    "app/ordinary_turn_multisource_reachability_adapter.py": (
        "b943f0d354fc4b7fa0dbb0d4e055e9e35289ce2a3d87a855038af4bcf73c7e97"
    ),
}


NOW = datetime(2026, 10, 1, 13, 0, tzinfo=timezone.utc)


class _ExplicitMultisourceAdapter:
    def __init__(self, gateway: OfficialGovernedReasoningRuntimeGateway) -> None:
        self.gateway = gateway
        self.calls = 0

    def admit_and_reason(self, *, text: str, owner: str, now: datetime, **kwargs):
        self.calls += 1
        query = ReasoningQuery(
            text=text,
            owner=owner,
            evidence_ids=("document-evidence", "library-evidence"),
            as_of=now,
        )
        return self.gateway.reason(query, now=now)


def test_evo_p1_explicit_multisource_still_uses_one_reasoning_evaluation():
    gateway = OfficialGovernedReasoningRuntimeGateway()
    adapter = _ExplicitMultisourceAdapter(gateway)
    source = CanonicalProductiveReasoningSource(
        gateway,
        ordinary_turn_multisource_reachability_adapter=adapter,
    )
    result = source(
        owner="Carlos",
        session_id="evo-p1-explicit-multisource",
        text="Contrastá el documento con la evidencia de Biblioteca.",
        now=NOW,
        explicit_document_ids=("document-1",),
        explicit_evidence_references=(object(),),
    )

    assert result is not None
    assert adapter.calls == 1
    assert gateway.snapshot.evaluations == 1


def test_evo_p1_protected_multisource_and_reasoning_surfaces_remain_identical():
    for relative_path, expected_hash in PROTECTED_SURFACES.items():
        actual_hash = hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()
        assert actual_hash == expected_hash, relative_path


def test_evo_p1_external_bounded_productive_continuity_adapter_exists():
    assert importlib.util.find_spec(CONTINUITY_MODULE) is not None, (
        "RED: explicit multisource reasoning lacks an external bounded productive "
        "continuity projection outside the protected reasoning and convergence "
        "surfaces"
    )


def test_evo_p1_composition_dependencies_expose_external_continuity_adapter():
    fields = RuntimeCompositionDependencies.__dataclass_fields__
    assert "explicit_multisource_productive_continuity_adapter" in fields, (
        "RED: Composition Root dependencies do not expose the bounded external "
        "explicit-multisource productive continuity projection"
    )


def test_evo_p1_runtime_factory_wires_external_continuity_adapter():
    source = (ROOT / "app/runtime_root_factory.py").read_text(encoding="utf-8")
    assert "ExplicitMultisourceProductiveContinuityAdapterV1" in source, (
        "RED: runtime factory does not construct the bounded external continuity "
        "adapter"
    )
    assert "explicit_multisource_productive_continuity_adapter=" in source, (
        "RED: runtime factory does not inject the bounded external continuity "
        "adapter into Composition Root dependencies"
    )


def test_evo_p1_external_contract_preserves_identity_and_exact_result_semantics():
    module_path = ROOT / "app/explicit_multisource_productive_continuity_adapter.py"
    assert module_path.exists(), (
        "RED: no external continuity surface exists to preserve owner/session/turn "
        "identity and the exact already-produced GovernedReasoningResult"
    )
    source = module_path.read_text(encoding="utf-8")
    for token in ("owner", "session_id", "turn_id", "result"):
        assert token in source, f"RED: external continuity surface lacks {token}"
    assert ".reason(" not in source
    assert "evaluate_productive_episode" not in source
