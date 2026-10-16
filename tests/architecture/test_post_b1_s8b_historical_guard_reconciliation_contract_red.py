from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RECONCILIATION = (
    ROOT / "docs" / "ROBY_XI_2_POST_B1_S8B_HISTORICAL_GUARD_RECONCILIATION.md"
)

HISTORICAL_CONFIG_SHA256 = (
    "11a1dce801533fbe42bb37596e5273e2c9c99d52b2b26c625b7f54ee845132b5"
)
CURRENT_CONFIG_SHA256 = (
    "0d61f2ec940f87939d32b9bad27150de857cca535cd2f4a405dfdacc0422a451"
)
HISTORICAL_DESKTOP_SHA256 = (
    "475d9fca8ac05946936410a5b98e056ee70b945b9c6398e52842106e98929cec"
)
CURRENT_DESKTOP_SHA256 = (
    "60a70c140370a43843854b99f788df4701e31e26ae522d7088bb8391990476f6"
)


def _reconciliation_text() -> str:
    assert RECONCILIATION.exists()
    return RECONCILIATION.read_text(encoding="utf-8")


def test_reconciliation_preserves_historical_config_guard_as_history():
    text = _reconciliation_text()

    assert HISTORICAL_CONFIG_SHA256 in text
    assert CURRENT_CONFIG_SHA256 in text
    assert "HISTORICAL_BASELINE" in text
    assert "CURRENT_GOVERNED_DEPLOYMENT_STATE" in text


def test_reconciliation_preserves_historical_desktop_guard_as_history():
    text = _reconciliation_text()

    assert HISTORICAL_DESKTOP_SHA256 in text
    assert CURRENT_DESKTOP_SHA256 in text
    assert "S6-C" in text
    assert "DO_NOT_REVERT_PRODUCT" in text


def test_reconciliation_records_registry_order_as_historical_expectation():
    text = _reconciliation_text()

    assert "knowledge.local_library.read" in text
    assert "HISTORICAL_ORDER_EXPECTATION" in text
    assert "DO_NOT_REORDER_REGISTRY" in text


def test_reconciliation_forbids_silent_reanchoring_of_historical_guards():
    text = _reconciliation_text()

    assert "NO_SILENT_REANCHOR" in text
    assert "historical byte guards remain historical evidence" in text
    assert "current governed truth requires its own explicit contract" in text


def test_reconciliation_keeps_product_and_future_probe_blocks_stopped():
    text = _reconciliation_text()

    assert "PRODUCT_CHANGE: NONE" in text
    assert "TEST_REWRITE: NONE" in text
    assert "B2: STOP" in text
    assert "B3: STOP" in text
    assert "B4: STOP" in text
