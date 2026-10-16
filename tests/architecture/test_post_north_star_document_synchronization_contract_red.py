from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CURRENT_TRUTH = ROOT / "ROBY_XI_2_CURRENT_TRUTH.md"
COGNITIVE_MASTER = ROOT / "ROBY_XI_2_COGNITIVE_INVENTORY_RECONCILIATION_MASTER_GUIDE.md"
HORIZON_MAP = (
    ROOT / "docs" / "strategy" / "ROBY_XI_2_INTELLECTUAL_EVOLUTION_HORIZON_MAP.md"
)


def _upper(path: Path) -> str:
    return path.read_text(encoding="utf-8").upper()


def test_red_current_truth_records_post_north_star_current_state() -> None:
    text = _upper(CURRENT_TRUTH)
    required = (
        "POST-NORTH-STAR",
        "H1",
        "H2",
        "H3",
        "H4",
        "H5",
        "H6",
        "NO NEXT PRODUCTIVE RESIDUAL",
    )
    missing = [token for token in required if token not in text]
    assert not missing, (
        "RED: Current Truth lacks the compact POST-NORTH-STAR current-state "
        f"reconciliation; missing={missing}"
    )


def test_red_current_truth_no_longer_points_to_completed_horizon_work() -> None:
    text = _upper(CURRENT_TRUTH)
    assert "NEXT AUTHORIZED STEP" in text
    obsolete = "MASTER PLAN HORIZON RECONCILIATION POST-S5"
    assert obsolete not in text, (
        "RED: Current Truth still points to completed horizon reconciliation"
    )
    assert len(CURRENT_TRUTH.read_text(encoding="utf-8").splitlines()) <= 400


def test_red_horizon_map_has_current_h1_h6_reclassification_layer() -> None:
    text = _upper(HORIZON_MAP)
    required = (
        "POST-NORTH-STAR",
        "H1",
        "H2",
        "H3",
        "H4",
        "H5",
        "H6",
        "SUBSTANTIALLY REALIZED",
        "PARTIAL",
        "FUTURE",
        "NO NEXT PRODUCTIVE RESIDUAL",
    )
    missing = [token for token in required if token not in text]
    assert not missing, (
        "RED: Horizon Map lacks the current POST-NORTH-STAR H1-H6 "
        f"reclassification layer; missing={missing}"
    )


def test_red_horizon_map_preserves_closed_north_star_boundary() -> None:
    text = _upper(HORIZON_MAP)
    assert "N1-N7" in text or "N1–N7" in text
    assert "NO N8" in text or "N8 = NOT CREATED" in text
    assert "HORIZON != SURGICAL CANDIDATE" in text


def test_red_cognitive_master_marks_old_priority_matrix_historical() -> None:
    text = _upper(COGNITIVE_MASTER)
    required = (
        "POST-NORTH-STAR",
        "HISTORICAL",
        "P1",
        "P10",
        "NOT",
        "BACKLOG",
        "NO NEXT PRODUCTIVE RESIDUAL",
    )
    missing = [token for token in required if token not in text]
    assert not missing, (
        "RED: Cognitive Master does not yet prevent the historical P1-P10 "
        f"matrix from being read as current backlog; missing={missing}"
    )


def test_red_preserves_non_promotion_semantics() -> None:
    combined = "\n".join(
        (_upper(CURRENT_TRUTH), _upper(COGNITIVE_MASTER), _upper(HORIZON_MAP))
    )
    required = (
        "PARTIAL != DEMONSTRATED RESIDUAL",
        "FUTURE != NEXT",
        "BOUNDED REALIZATION != TOTAL COMPLETION",
    )
    missing = [token for token in required if token not in combined]
    assert not missing, (
        "RED: master documentation lacks required non-promotion semantics; "
        f"missing={missing}"
    )
