from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_m22_standalone_cache_contract_is_retired_without_global_replacement() -> None:
    assert not (ROOT / "core/cache.py").exists()
    assert not (ROOT / "tests/test_m22_cache.py").exists()

    roadmap = (ROOT / "docs/ROADMAP_LAYERS.md").read_text(encoding="utf-8")
    assert "M22 — Cache — HISTORICAL / RETIRED" in roadmap

    rules = (ROOT / "architecture_rules.md").read_text(encoding="utf-8")
    assert "M22 Standalone Cache Contract Retirement Boundary" in rules
    assert "must not be restored as a global cache authority" in rules
