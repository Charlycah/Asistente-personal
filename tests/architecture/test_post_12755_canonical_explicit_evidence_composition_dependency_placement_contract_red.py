from __future__ import annotations

import inspect
from hashlib import sha256
from pathlib import Path

from core.runtime_composition_root.models import RuntimeCompositionDependencies

ROOT = Path(__file__).resolve().parents[2]

PROTECTED_HASHES = {
    "core/governed_operational_conversation_pipeline/models.py": (
        "f65c3f87c64c5b8cd8525aa326f31a66550711916d564fc0c90cde3d2730b063"
    ),
    "app/same_episode_explicit_evidence_convergence_adapter.py": (
        "5be01adfe0c0e3a32065bcb15918013d7e20e5cb7e0092072c88df1dea5aef3d"
    ),
    "app/ordinary_turn_multisource_reachability_adapter.py": (
        "b943f0d354fc4b7fa0dbb0d4e055e9e35289ce2a3d87a855038af4bcf73c7e97"
    ),
}


def test_post_12755_composition_dependencies_retain_canonical_document_inbox():
    fields = RuntimeCompositionDependencies.__dataclass_fields__
    assert "document_inbox" in fields, (
        "RED: the existing Composition Root does not retain the canonical "
        "DocumentInboxManager for governed reuse"
    )


def test_post_12755_runtime_factory_reuses_canonical_inbox_for_same_episode_adapter():
    source = (ROOT / "app/runtime_root_factory.py").read_text(encoding="utf-8")
    assert "SameEpisodeExplicitEvidenceConvergenceAdapterV1" in source, (
        "RED: runtime factory does not yet compose the certified same-episode "
        "authority from canonical dependencies"
    )
    assert "document_inbox=document_inbox" in source, (
        "RED: runtime factory must reuse the already-built canonical document inbox"
    )
    assert "reasoning_gateway=governed_reasoning_runtime" in source, (
        "RED: same-episode composition must reuse the canonical reasoning runtime"
    )


def test_post_12755_runtime_factory_composes_certified_ordinary_turn_transport_once():
    source = (ROOT / "app/runtime_root_factory.py").read_text(encoding="utf-8")
    assert "OrdinaryTurnMultisourceReachabilityAdapterV1" in source, (
        "RED: runtime factory does not yet compose the certified ordinary-turn "
        "multisource transport seam"
    )
    assert "same_episode_adapter=" in source, (
        "RED: ordinary-turn transport must reuse the certified same-episode adapter"
    )


def test_post_12755_dependencies_expose_transport_without_invocation():
    fields = RuntimeCompositionDependencies.__dataclass_fields__
    assert "ordinary_turn_multisource_reachability_adapter" in fields, (
        "RED: Composition Root dependencies do not expose the already-certified "
        "transport seam for later bounded consumption"
    )

    from core.runtime_composition_root import GovernedRuntimePreparation

    prepare_source = inspect.getsource(GovernedRuntimePreparation.prepare)
    assert "ordinary_turn_multisource_reachability_adapter" not in prepare_source, (
        "composition placement must not activate explicit-evidence reasoning "
        "automatically during ordinary prepare()"
    )


def test_post_12755_protected_ingress_and_certified_adapters_remain_byte_identical():
    for relative_path, expected_hash in PROTECTED_HASHES.items():
        payload = (ROOT / relative_path).read_bytes()
        assert sha256(payload).hexdigest() == expected_hash, relative_path
