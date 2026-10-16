from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_m349_is_documented_without_displacing_historical_changelog_header():
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    document = (ROOT / "docs" / "M349_PERSON_DETECTION.md").read_text(encoding="utf-8")

    assert changelog.startswith("# M347.15 — Estabilización de la serie")
    assert "# ROBY XI.2 M349 — Person Detection gobernado" in changelog
    assert "OfficialVisionCore" in document
    assert "No reconoce rostros ni identidades" in document


def test_m349_keeps_one_official_vision_core_and_no_biometric_api():
    source = (ROOT / "app" / "vision_core.py").read_text(encoding="utf-8")
    models = (ROOT / "core" / "person_detection" / "models.py").read_text(
        encoding="utf-8"
    )

    assert source.count("class OfficialVisionCore") == 1
    assert "PersonDetector" in models
    assert "face_recognition" not in source.lower()
    assert "biometric_identification" not in source.lower()
