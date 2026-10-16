from __future__ import annotations

from pathlib import Path

from core.cognitive_maturity.hypothesis_gap_curiosity_evidence import (
    HypothesisGapCuriosityEvidenceAdapter,
)

ROOT = Path(__file__).resolve().parents[2]
RETIRED_MODULE = "app.hypothesis_gap_curiosity_productive_consumption"
PRODUCTIVE_ROOTS = (
    "app",
    "application",
    "core",
    "domain",
    "infrastructure",
    "scripts",
)


def test_unreached_hypothesis_gap_curiosity_compositor_is_retired() -> None:
    retired = ROOT / "app/hypothesis_gap_curiosity_productive_consumption.py"
    assert not retired.exists()


def test_current_hypothesis_gap_evidence_adapter_remains() -> None:
    assert HypothesisGapCuriosityEvidenceAdapter.__module__ == (
        "core.cognitive_maturity.hypothesis_gap_curiosity_evidence"
    )


def test_productive_python_does_not_depend_on_retired_compositor() -> None:
    offenders: list[str] = []
    for root_name in PRODUCTIVE_ROOTS:
        for path in (ROOT / root_name).rglob("*.py"):
            if RETIRED_MODULE in path.read_text(encoding="utf-8"):
                offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []


def test_whole_system_f8_uses_current_curiosity_evidence() -> None:
    source = (
        ROOT / "scripts/diagnostics/whole_system_cognitive_limits_evidence_harness.py"
    ).read_text(encoding="utf-8")
    assert (
        "test_post_m409_1_curiosity_relevance_initiative_consumption_v1.py" in source
    )
    assert "test_post_m409_1_productive_conversational_curiosity_wiring_v1.py" in source
    assert (
        "test_post_m409_1_hypothesis_gap_curiosity_productive_consumption_v1.py"
        not in source
    )
