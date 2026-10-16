from __future__ import annotations

from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
M17_MILESTONE_SHA256 = (
    "8d54822edc950bf35b5b1b078595284a5b9167d3fa25759a99f44766bf81d189"
)


def test_m17_era_generic_trace_contract_residue_remains_retired() -> None:
    retired = (
        "core/tracing.py",
        "tests/fakes/fake_trace_recorder.py",
    )
    for relative_path in retired:
        assert not (ROOT / relative_path).exists()

    preserved = (
        "core/operational_trace_model/__init__.py",
        "core/operational_trace_model/recorder.py",
        "core/end_to_end_local_conversation/runtime.py",
        "tests/test_m181_operational_trace_model.py",
    )
    for relative_path in preserved:
        assert (ROOT / relative_path).exists()

    rules = (ROOT / "architecture_rules.md").read_text(encoding="utf-8")
    boundary = "M17-Era Generic Trace Contract Residue Retirement Boundary"
    assert boundary in rules
    assert "current operational trace model remains independently owned" in rules

    # Historical M17 evidence remains immutable and M17 stays historical.
    milestone = ROOT / "docs" / "milestones" / "M17_internal_event_publisher.md"
    assert milestone.exists()
    assert sha256(milestone.read_bytes()).hexdigest() == M17_MILESTONE_SHA256

    roadmap = (ROOT / "docs" / "ROADMAP_LAYERS.md").read_text(encoding="utf-8")
    assert "M17 — Internal Event Publisher — HISTORICAL / RETIRED" in roadmap
