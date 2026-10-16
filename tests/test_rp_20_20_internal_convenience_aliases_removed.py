from __future__ import annotations

from app.official_runtime_composition import OfficialROBYRuntime


def test_operational_snapshot_alias_is_removed() -> None:
    assert not hasattr(OfficialROBYRuntime, "operational_snapshot")


def test_health_readiness_alias_is_removed() -> None:
    assert not hasattr(OfficialROBYRuntime, "health_readiness")


def test_canonical_runtime_operations_remain_available() -> None:
    assert callable(OfficialROBYRuntime.snapshot)
    assert callable(OfficialROBYRuntime.readiness)
