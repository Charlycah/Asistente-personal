from __future__ import annotations

from scripts.diagnostics.whole_system_cognitive_limits_evidence_harness import (
    Status,
    families,
)


def test_harness_defines_exactly_f1_to_f10() -> None:
    specs = families()
    assert tuple(spec.family_id for spec in specs) == tuple(
        f"F{i}" for i in range(1, 11)
    )


def test_harness_covers_d1_to_d15() -> None:
    covered = {dimension for spec in families() for dimension in spec.dimensions}
    assert covered == {f"D{i}" for i in range(1, 16)}


def test_harness_keeps_improvisation_uncertified_by_construction() -> None:
    f9 = next(spec for spec in families() if spec.family_id == "F9")
    assert "insufficient for PASS" in f9.interpretation


def test_status_vocabulary_matches_contract() -> None:
    assert {item.value for item in Status} == {
        "PASS",
        "PASS_BY_DESIGN",
        "PARTIAL",
        "FAIL",
        "NOT_PRESENT",
        "OUT_OF_SCOPE_BY_DESIGN",
    }
