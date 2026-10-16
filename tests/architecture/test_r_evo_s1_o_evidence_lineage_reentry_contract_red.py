from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path

from core.runtime_composition_root.models import RuntimeCompositionDependencies

ROOT = Path(__file__).resolve().parents[2]
REENTRY_MODULE = "app.explicit_multisource_evidence_lineage_reentry_adapter"

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


def test_evo_p1_evidence_reentry_keeps_protected_surfaces_identical():
    for relative_path, expected_hash in PROTECTED_SURFACES.items():
        actual_hash = hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest()
        assert actual_hash == expected_hash, relative_path


def test_evo_p1_f4_j_continuity_and_reachability_remain_available():
    fields = RuntimeCompositionDependencies.__dataclass_fields__
    assert "explicit_multisource_productive_continuity_adapter" in fields
    assert "explicit_multisource_productive_consumer_reachability_adapter" in fields


def test_evo_p1_existing_revision_authority_remains_the_target():
    revision = ROOT / "app/governed_explanatory_model_revision.py"
    runtime = ROOT / "app/governed_reasoning_runtime.py"
    revision_source = revision.read_text(encoding="utf-8")
    runtime_source = runtime.read_text(encoding="utf-8")
    assert "GovernedEvidenceDrivenExplanatoryModelRevisionV1" in revision_source
    assert "bind_productive_explanatory_model_revision" in runtime_source


def test_evo_p1_bounded_evidence_lineage_reentry_surface_exists():
    assert importlib.util.find_spec(REENTRY_MODULE) is not None, (
        "RED: F4/J reasoning lineage and governed revision artifacts have no "
        "bounded reentry seam to the existing revision consumer"
    )


def test_evo_p1_composition_exposes_evidence_lineage_reentry():
    fields = RuntimeCompositionDependencies.__dataclass_fields__
    assert "explicit_multisource_evidence_lineage_reentry_adapter" in fields, (
        "RED: Composition Root does not expose bounded evidence-lineage reentry"
    )


def test_evo_p1_reentry_transports_existing_artifacts_without_new_authority():
    module_path = ROOT / "app/explicit_multisource_evidence_lineage_reentry_adapter.py"
    assert module_path.exists(), (
        "RED: no bounded seam carries F4/J lineage plus governed reentry and "
        "reassessment artifacts toward existing explanatory-model revision"
    )
    source = module_path.read_text(encoding="utf-8")
    for token in (
        "continuity",
        "source_turn_id",
        "reentry",
        "revised_report",
        "consumer",
    ):
        assert token in source, f"RED: evidence-lineage reentry lacks {token}"
    assert ".reason(" not in source
    assert "evaluate_productive_episode" not in source
    assert "GovernedExplicitHypothesisSource(" not in source
    assert "GovernedAuthorizedIntellectualGoal(" not in source
    assert "visual_context_contribution" not in source
