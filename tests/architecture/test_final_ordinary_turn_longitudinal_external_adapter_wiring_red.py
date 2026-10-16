from __future__ import annotations

import hashlib
import importlib.util
import inspect
from pathlib import Path

from core.governed_reasoning.longitudinal_intellectual_reconstruction import (
    GovernedLongitudinalIntellectualReconstructionFoundationV1,
)
from core.runtime_composition_root.models import RuntimeCompositionDependencies
from core.runtime_composition_root.preparation import GovernedRuntimePreparation

ROOT = Path(__file__).resolve().parents[2]
REASONING_RUNTIME = ROOT / "app/governed_reasoning_runtime.py"
CERTIFIED_REASONING_SHA256 = (
    "f8c96d92c08fff1b9219afd68974b79ba319f087b2fb32fbb20d5856aaa91f2f"
)
ADAPTER_MODULE = "app.longitudinal_intellectual_reconstruction_productive_adapter"
ORCHESTRATION_HELPER = (
    "_compose_and_enrich_productive_longitudinal_intellectual_reconstruction"
)


def test_protective_reasoning_runtime_remains_certified_byte_identical() -> None:
    assert hashlib.sha256(REASONING_RUNTIME.read_bytes()).hexdigest() == (
        CERTIFIED_REASONING_SHA256
    )


def test_protective_semantic_admission_remains_in_governed_reasoning() -> None:
    method = getattr(
        GovernedLongitudinalIntellectualReconstructionFoundationV1,
        "admit_recalled_antecedent",
        None,
    )
    assert callable(method)


def test_red_external_bounded_productive_adapter_exists() -> None:
    assert importlib.util.find_spec(ADAPTER_MODULE) is not None, (
        "RED: longitudinal antecedent admission still lacks an external bounded "
        "productive adapter that preserves the protected reasoning runtime"
    )


def test_red_composition_dependencies_expose_external_adapter() -> None:
    fields = RuntimeCompositionDependencies.__dataclass_fields__
    assert "longitudinal_reconstruction_productive_adapter" in fields, (
        "RED: Composition Root dependencies do not yet expose the external bounded "
        "longitudinal reconstruction adapter"
    )


def test_red_prepare_supplies_exact_candidates_to_external_adapter() -> None:
    source = inspect.getsource(GovernedRuntimePreparation.prepare)
    assert "recalled_antecedent_candidates" in source, (
        "RED: ordinary prepare() does not yet supply the exact neutral candidates "
        "preserved by MemoryRuntimeContext"
    )
    assert "longitudinal_reconstruction_productive_adapter" in source, (
        "RED: ordinary prepare() does not yet route admission through the external "
        "bounded longitudinal reconstruction adapter"
    )


def test_red_prepare_invokes_certified_orchestration_after_admission() -> None:
    source = inspect.getsource(GovernedRuntimePreparation.prepare)
    assert ORCHESTRATION_HELPER in source, (
        "RED: ordinary prepare() does not yet invoke the certified longitudinal "
        "reconstruction orchestration helper after bounded admission"
    )
    assert "antecedent_admission is not None" in source, (
        "RED: ordinary prepare() does not yet fail closed when bounded antecedent "
        "admission abstains"
    )


def test_red_runtime_factory_wires_external_adapter_without_gateway_extension() -> None:
    source = (ROOT / "app/runtime_root_factory.py").read_text(encoding="utf-8")
    assert "LongitudinalIntellectualReconstructionProductiveAdapterV1" in source, (
        "RED: runtime factory does not yet construct the external bounded adapter"
    )
    assert "longitudinal_reconstruction_productive_adapter=" in source, (
        "RED: runtime factory does not yet inject the external bounded adapter into "
        "Composition Root dependencies"
    )


def test_protective_prepare_does_not_reparse_memory_planning_metadata() -> None:
    source = inspect.getsource(GovernedRuntimePreparation.prepare)
    forbidden = (
        "governed_memory_planning_evidence",
        "decode_memory_planning_evidence",
        "MEMORY_PLANNING_METADATA_KEY",
    )
    assert not any(token in source for token in forbidden)
