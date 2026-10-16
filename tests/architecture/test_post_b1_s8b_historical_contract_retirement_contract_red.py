from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RETIREMENT = ROOT / "docs" / "ROBY_XI_2_POST_B1_S8B_HISTORICAL_CONTRACT_RETIREMENT.md"


def _retirement_text() -> str:
    assert RETIREMENT.exists()
    return RETIREMENT.read_text(encoding="utf-8")


def test_retirement_classifies_all_twelve_stale_guards():
    text = _retirement_text()

    assert "CONFIG_GUARDS: 7" in text
    assert "DESKTOP_GUARDS: 2" in text
    assert "REGISTRY_GUARDS: 3" in text
    assert "TOTAL_STALE_GUARDS: 12" in text


def test_retirement_preserves_historical_hashes_without_reanchoring():
    text = _retirement_text()

    assert "PRESERVE_HISTORICAL_HASH_EVIDENCE" in text
    assert "NO_SILENT_REANCHOR" in text
    assert "RETIRE_ACTIVE_BYTE_IDENTITY_ASSERTION" in text
    assert "DO_NOT_REPLACE_OLD_HASH_WITH_CURRENT_HASH" in text


def test_retirement_preserves_current_desktop_semantics():
    text = _retirement_text()

    assert "DO_NOT_REVERT_PRODUCT" in text
    assert "PRESERVE_CURRENT_DESKTOP_SEMANTICS" in text
    assert "REFORMULATE_DESKTOP_GUARD" in text


def test_retirement_replaces_absolute_registry_positions_with_invariants():
    text = _retirement_text()

    assert "DO_NOT_REORDER_REGISTRY" in text
    assert "NO_NEW_ABSOLUTE_POSITION_GUARD" in text
    assert "PRESERVE_REGISTRY_UNIQUENESS" in text
    assert "PRESERVE_REQUIRED_CAPABILITY_MEMBERSHIP" in text
    assert "PRESERVE_ONLY_REQUIRED_RELATIVE_PRECEDENCE" in text


def test_retirement_authorizes_only_test_and_documentary_green():
    text = _retirement_text()

    assert "PRODUCT_CHANGE: NONE" in text
    assert "AUTHORIZED_GREEN: TESTS_AND_DOCUMENTATION_ONLY" in text
    assert "B2: STOP" in text
    assert "B3: STOP" in text
    assert "B4: STOP" in text
