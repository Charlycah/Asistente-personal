from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path

from core.runtime_composition_root.models import RuntimeCompositionDependencies

ROOT = Path(__file__).resolve().parents[2]
REACHABILITY_MODULE = (
    "app.explicit_multisource_productive_consumer_reachability_adapter"
)

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


def test_evo_p1_productive_reachability_keeps_protected_surfaces_identical():
    for relative_path, expected_hash in PROTECTED_SURFACES.items():
        actual_hash = hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()
        assert actual_hash == expected_hash, relative_path


def test_evo_p1_existing_f4_continuity_remains_available():
    fields = RuntimeCompositionDependencies.__dataclass_fields__
    assert "explicit_multisource_productive_continuity_adapter" in fields
    assert importlib.util.find_spec(
        "app.explicit_multisource_productive_continuity_adapter"
    ) is not None


def test_evo_p1_bounded_productive_consumer_reachability_surface_exists():
    assert importlib.util.find_spec(REACHABILITY_MODULE) is not None, (
        "RED: F4 continuity has no bounded external route to an existing "
        "productive epistemic consumer"
    )


def test_evo_p1_composition_exposes_productive_consumer_reachability():
    fields = RuntimeCompositionDependencies.__dataclass_fields__
    assert "explicit_multisource_productive_consumer_reachability_adapter" in fields, (
        "RED: Composition Root does not expose bounded productive consumer "
        "reachability for F4 continuity"
    )


def test_evo_p1_reachability_preserves_lineage_without_reasoning_or_hypothesis():
    module_path = (
        ROOT / "app/explicit_multisource_productive_consumer_reachability_adapter.py"
    )
    assert module_path.exists(), (
        "RED: no external surface can carry F4 owner/session/turn/exact-result "
        "lineage toward an existing productive consumer"
    )
    source = module_path.read_text(encoding="utf-8")
    for token in ("owner", "session_id", "turn_id", "result", "consumer"):
        assert token in source, f"RED: reachability surface lacks {token}"
    assert ".reason(" not in source
    assert "evaluate_productive_episode" not in source
    assert "GovernedExplicitHypothesisSource(" not in source
