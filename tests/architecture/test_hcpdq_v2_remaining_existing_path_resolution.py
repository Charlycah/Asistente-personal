from __future__ import annotations

from scripts.hcpdq_v2_remaining_existing_path_resolution import (
    resolve_remaining_paths,
)


def test_resolution_keeps_all_seven_remaining_families_fail_closed():
    report = resolve_remaining_paths()
    assert report["newly_certified_families"] == []
    assert report["remaining_uncertified_families"] == [
        "H1", "H2", "H3", "H4", "H5", "H7", "H8"
    ]


def test_p2_surfaces_are_not_overclaimed_as_complete_family_execution():
    report = resolve_remaining_paths()
    for family in ("H2", "H7", "H8"):
        item = report["family_results"][family]
        assert item["productive_surface_exists"] is True
        assert item["full_family_semantics_exposed"] is False
        assert item["calibration_path_certified"] is False


def test_p1_internal_authorities_do_not_become_benchmark_facades():
    report = resolve_remaining_paths()
    for family in ("H3", "H4", "H5"):
        item = report["family_results"][family]
        assert item["authority_exists"] is True
        assert item["productive_surface_exists"] is False
        assert item["calibration_path_certified"] is False


def test_h1_existing_composition_is_not_misreported_as_deterministic_path():
    report = resolve_remaining_paths()
    h1 = report["family_results"]["H1"]
    assert h1["authority_exists"] is True
    assert h1["full_family_semantics_exposed"] is False
    assert h1["resolution"] == "EXISTING_COMPOSITION_COARSE_NOT_H1_CERTIFIED"


def test_held_out_and_production_remain_no_go():
    report = resolve_remaining_paths()
    assert report["held_out_construction_authorized"] is False
    assert report["production_changes_authorized"] is False
    assert report["new_authority_authorized"] is False
    assert report["already_certified_family"] == "H6"
