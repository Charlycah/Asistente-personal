from __future__ import annotations

from scripts.diagnostics.l3_adversarial_flexible_composition_evidence import (
    Status,
    _source_boundary_assertions,
    controls,
)


def test_l3_harness_defines_six_adversarial_controls() -> None:
    assert tuple(item.control_id for item in controls()) == (
        "A1",
        "A2",
        "A3",
        "A4",
        "A5",
        "A6",
    )


def test_l3_harness_contains_required_adversarial_pairs() -> None:
    claims = " ".join(item.title.casefold() for item in controls())
    assert "different vocabulary" in claims
    assert "different relational structure" in claims
    assert "distractor" in claims
    assert "changed conditions" in claims


def test_l3_harness_does_not_promote_runtime_orchestration_to_pass() -> None:
    statuses = {item.control_id: item.expected_status for item in controls()}
    assert statuses["A5"] is Status.PARTIAL
    assert statuses["A6"] is Status.PARTIAL


def test_l3_harness_recognizes_governed_non_selection() -> None:
    statuses = {item.control_id: item.expected_status for item in controls()}
    assert statuses["A3"] is Status.PASS_BY_DESIGN
    assert statuses["A4"] is Status.PASS_BY_DESIGN


def test_l3_source_boundaries_are_explicit() -> None:
    boundaries = _source_boundary_assertions(
        __import__("pathlib").Path(__file__).resolve().parents[2]
    )
    assert all(boundaries.values())
