from pathlib import Path


def test_m354_contract_declares_governed_scene_understanding():
    root = Path(__file__).resolve().parents[1]
    source = (root / "app" / "vision_core.py").read_text(encoding="utf-8")
    models = (root / "core" / "scene_understanding" / "fusion.py").read_text(
        encoding="utf-8"
    )
    docs = (root / "docs" / "M354_SCENE_UNDERSTANDING.md").read_text(
        encoding="utf-8"
    )

    assert "def understand_scene(" in source
    assert "class SceneUnderstandingResult" in source
    assert "class SceneAnalyzer(Protocol)" in models
    assert "class DeterministicSceneAnalyzer" in models
    assert "one authorized frame" in docs
    assert "does not infer activities" in docs
