from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_m351_is_documented_without_displacing_historical_changelog_header():
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    document = (ROOT / "docs" / "M351_OCR_GOVERNED.md").read_text(encoding="utf-8")

    assert changelog.startswith("# M347.15 — Estabilización de la serie")
    assert "# ROBY XI.2 M351 — OCR gobernado" in changelog
    assert "OfficialVisionCore" in document
    assert "No interpreta documentos" in document


def test_m351_keeps_one_official_vision_core_and_no_raw_media_result():
    source = (ROOT / "app" / "vision_core.py").read_text(encoding="utf-8")
    models = (ROOT / "core" / "text_extraction" / "models.py").read_text(
        encoding="utf-8"
    )

    assert source.count("class OfficialVisionCore") == 1
    assert "TextExtractor" in models
    result_source = source[source.index("class TextExtractionResult") :]
    result_source = result_source[: result_source.index("class FaceDetectionResult")]
    assert "image_bytes" not in result_source
    assert "document_understanding" not in result_source.lower()
