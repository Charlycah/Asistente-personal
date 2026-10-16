from __future__ import annotations

from pathlib import Path

from domain.cognitive_agenda import CognitiveAgendaItem as NeutralAgendaItem
from domain.priority_reasoning import PriorityReasoning as NeutralPriorityReasoning
from domain.response import ResponseStatus as NeutralResponseStatus
from domain.vision.camera_frame import CameraFrame as NeutralCameraFrame

ROOT = Path(__file__).resolve().parents[2]


def _text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def test_core_no_longer_depends_on_app_for_m395_1_boundaries() -> None:
    assert "from app.priority_reasoning" not in _text(
        "core/intelligent_personal_organization.py"
    )


def test_infrastructure_no_longer_depends_on_app_agenda_models() -> None:
    assert "from app.cognitive_agenda_manager" not in _text(
        "infrastructure/repositories/sqlite_cognitive_agenda_repository.py"
    )


def test_core_vision_no_longer_depends_on_camera_infrastructure_contract() -> None:
    paths = (
        "core/face_detection/models.py",
        "core/object_detection/models.py",
        "core/person_detection/models.py",
        "core/text_extraction/models.py",
        "core/visual_code_detection/models.py",
    )
    forbidden = "from infrastructure.camera.camera_client import CameraFrame"
    for path in paths:
        assert forbidden not in _text(path)


def test_camera_frame_compatibility_surface_is_identity_preserving() -> None:
    from infrastructure.camera.camera_client import CameraFrame as CompatCameraFrame

    assert CompatCameraFrame is NeutralCameraFrame


def test_agenda_compatibility_surface_is_identity_preserving() -> None:
    from app.cognitive_agenda_manager import CognitiveAgendaItem as CompatAgendaItem

    assert CompatAgendaItem is NeutralAgendaItem


def test_priority_reasoning_compatibility_surfaces_are_identity_preserving() -> None:
    from app.priority_reasoning import PriorityReasoning as AppPriorityReasoning
    from core.priority_reasoning import PriorityReasoning as CorePriorityReasoning

    assert AppPriorityReasoning is NeutralPriorityReasoning
    assert CorePriorityReasoning is NeutralPriorityReasoning


def test_m6_response_models_are_now_a_compatibility_shim() -> None:
    from m6.response.models import ResponseStatus as LegacyResponseStatus

    assert LegacyResponseStatus is NeutralResponseStatus
    assert "from domain.response import" in _text("m6/response/models.py")


def test_modern_runtime_no_longer_imports_m6_response_models() -> None:
    modern_paths = (
        "app/desktop_operational_adapter.py",
        "app/runtime_ui_adapter.py",
        "app/ui_adapter.py",
    )
    for path in modern_paths:
        assert "from m6.response.models import" not in _text(path)
