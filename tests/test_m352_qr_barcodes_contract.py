from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_m352_is_documented_without_displacing_historical_changelog_header():
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    document = (ROOT / "docs" / "M352_QR_BARCODES.md").read_text(
        encoding="utf-8"
    )
    assert changelog.startswith("# M347.15 — Estabilización de la serie")
    assert "# ROBY XI.2 M352 — QR y códigos de barras gobernados" in changelog
    assert "OfficialVisionCore" in document
    assert "No abre enlaces" in document


def test_m352_keeps_one_official_core_and_no_automatic_execution_api():
    source = (ROOT / "app" / "vision_core.py").read_text(encoding="utf-8")
    models = (
        ROOT / "core" / "visual_code_detection" / "models.py"
    ).read_text(encoding="utf-8")
    assert source.count("class OfficialVisionCore") == 1
    assert "VisualCodeDecoder" in models
    result_source = source[source.index("class VisualCodeDetectionResult") :]
    result_source = result_source[: result_source.index("class FaceDetectionResult")]
    assert "image_bytes" not in result_source
    assert "open_url" not in source
    assert "execute_command" not in source
