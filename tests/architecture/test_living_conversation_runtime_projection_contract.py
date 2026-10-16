from pathlib import Path

from core.living_conversation_runtime_integration import (
    LivingConversationRuntimeProjection,
)

ROOT = Path(__file__).resolve().parents[2]


def test_official_living_conversation_runtime_uses_typed_neutral_projection() -> None:
    runtime_source = (ROOT / "app" / "conversation_runtime.py").read_text(
        encoding="utf-8"
    )
    seam_source = (
        ROOT / "core" / "living_conversation_runtime_integration.py"
    ).read_text(encoding="utf-8")

    assert "SimpleNamespace" not in runtime_source
    assert "LivingConversationRuntimeProjection(" in runtime_source
    assert "-> LivingConversationRuntimeProjection | None" in seam_source
    assert LivingConversationRuntimeProjection.__dataclass_params__.frozen is True
