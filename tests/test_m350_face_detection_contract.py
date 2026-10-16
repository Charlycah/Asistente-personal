from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_m350_is_documented_without_displacing_historical_changelog_header():
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    document = (ROOT / "docs" / "M350_FACE_DETECTION.md").read_text(encoding="utf-8")

    assert changelog.startswith("# M347.15 — Estabilización de la serie")
    assert "# ROBY XI.2 M350 — Face Detection gobernado" in changelog
    assert "OfficialVisionCore" in document
    assert "no identifica" in document.lower()


def test_m350_exposes_location_only_and_no_attribute_inference():
    source = (ROOT / "app" / "vision_core.py").read_text(encoding="utf-8")
    models = (ROOT / "core" / "face_detection" / "models.py").read_text(
        encoding="utf-8"
    )

    assert source.count("class OfficialVisionCore") == 1
    assert "FaceDetector" in models
    forbidden = ("age_estimation", "gender_inference", "emotion_inference")
    assert all(term not in source.lower() for term in forbidden)
