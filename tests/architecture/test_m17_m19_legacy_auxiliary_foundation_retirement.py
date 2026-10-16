from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_m17_m19_legacy_auxiliary_foundations_remain_retired() -> None:
    assert not (ROOT / "core" / "event_publisher.py").exists()
    assert not (ROOT / "core" / "memory_pipeline.py").exists()
    assert not (ROOT / "tests" / "test_m17_event_publisher.py").exists()
    assert not (ROOT / "tests" / "test_m19_memory_pipeline.py").exists()

    rules = (ROOT / "architecture_rules.md").read_text(encoding="utf-8")
    assert "M17/M19 Legacy Auxiliary Foundation Retirement Boundary" in rules
    prohibited = (
        "automatic conversation occurrence → Cognitive Memory admission is prohibited"
    )
    assert prohibited in rules

    roadmap = (ROOT / "docs" / "ROADMAP_LAYERS.md").read_text(encoding="utf-8")
    assert "M17 — Internal Event Publisher — HISTORICAL / RETIRED" in roadmap
    assert "M19 — Memory Pipeline — HISTORICAL / RETIRED" in roadmap

    assert (ROOT / "docs" / "milestones" / "M17_internal_event_publisher.md").exists()
    assert (ROOT / "docs" / "milestones" / "M19_memory_pipeline.md").exists()
