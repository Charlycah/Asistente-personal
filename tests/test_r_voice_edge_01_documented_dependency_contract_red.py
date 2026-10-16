from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDES = (
    ROOT / "docs" / "guides" / "ROBY_EDGE_TTS_VOICE.md",
    ROOT / "docs" / "guides" / "HAL_EDGE_TTS_VOICE.md",
)

INSTALL_COMMAND = (
    r'& ".\venv\Scripts\python.exe" -m pip install "edge-tts==7.3.1"'
)


def test_r_voice_edge_01_guides_document_verified_installation() -> None:
    for guide in GUIDES:
        assert guide.is_file(), guide
        text = guide.read_text(encoding="utf-8")
        assert INSTALL_COMMAND in text, guide
        assert "pip install -r requirements-voice.txt" not in text, guide


def test_r_voice_edge_01_historical_dependency_remains_unchanged() -> None:
    historical = (
        ROOT
        / "docs"
        / "history"
        / "root-archive-post-g22"
        / "requirements-voice.txt"
    )
    assert historical.read_text(encoding="utf-8").strip() == (
        "edge-tts==7.2.8"
    )


def test_r_voice_edge_01_no_duplicate_root_requirements() -> None:
    assert not (ROOT / "requirements-voice.txt").exists()
