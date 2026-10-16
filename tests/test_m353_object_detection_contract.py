from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_m353_is_documented_without_displacing_historical_changelog_header():
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    document = (ROOT / "docs" / "M353_OBJECT_DETECTION.md").read_text(
        encoding="utf-8"
    )

    assert changelog.startswith("# M347.15 — Estabilización de la serie")
    assert "# ROBY XI.2 M353 — Object Detection gobernado" in changelog
    assert "OfficialVisionCore" in document
    assert "no ejecuta acciones" in document.lower()


def test_m353_keeps_one_vision_core_and_no_visual_memory_or_autonomy():
    source = (ROOT / "app" / "vision_core.py").read_text(encoding="utf-8")

    assert source.count("class OfficialVisionCore") == 1
    assert "def detect_objects" in source
    assert "visual_memory" not in source.lower()
    assert "execute_detected" not in source.lower()
