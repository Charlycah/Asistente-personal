from __future__ import annotations

import sys
from types import SimpleNamespace

import pytest

from core.capability_registry import (
    CapabilityRegistryManager,
    default_semantic_capabilities,
)
from core.permission_consent import PermissionConsentManager, PermissionGrant
from core.tool_gateway import ToolGatewayManager, ToolGatewayStatus, ToolRequest
from infrastructure.camera.camera_adapter import (
    CameraAdapter,
    CameraAdapterPolicy,
    build_camera_adapter_from_config,
)
from infrastructure.camera.camera_client import (
    CameraFrame,
    CameraProviderError,
    OpenCVCameraClient,
)
from infrastructure.config.config_schema import (
    AppConfig,
    AssistantConfig,
    LLMConfig,
    MemoryConfig,
    RemindersConfig,
    SecretsConfig,
    VoiceConfig,
    WeatherConfig,
)


class FakeCameraProvider:
    def __init__(self) -> None:
        self.captured_indices: list[int] = []

    def capture(self, camera_index: int) -> CameraFrame:
        self.captured_indices.append(camera_index)
        return CameraFrame(
            camera_index=camera_index,
            mime_type="image/jpeg",
            image_bytes=b"fake-jpeg-bytes",
            width=640,
            height=480,
        )


def build_gateway(*, grant_device: bool = False) -> ToolGatewayManager:
    registry = CapabilityRegistryManager()
    registry.register_many(default_semantic_capabilities())
    permissions = PermissionConsentManager()
    if grant_device:
        permissions.grant(PermissionGrant("camera.capture", "device"))
    return ToolGatewayManager(
        capability_registry=registry,
        permission_consent=permissions,
    )


def base_config(*, camera_index: int = 2) -> AppConfig:
    return AppConfig(
        assistant=AssistantConfig("ROBY", "es", "America/Argentina/Buenos_Aires"),
        weather=WeatherConfig("Buenos Aires", "openweather", "openweather"),
        memory=MemoryConfig(True, "roby.db"),
        reminders=RemindersConfig(True, 60),
        llm=LLMConfig("none", "none"),
        voice=VoiceConfig(False, "none", "none"),
        secrets=SecretsConfig(
            openweather_api_key=None,
            weatherapi_key=None,
            google_client_secret_file=None,
            google_token_file=None,
            gmail_address=None,
            gmail_app_password=None,
            gemini_api_key=None,
            openrouter_api_key=None,
            mistral_api_key=None,
            openai_api_key=None,
            camera_index=camera_index,
        ),
        debug=False,
    )


def test_camera_adapter_registers_device_handler_after_consent():
    gateway = build_gateway(grant_device=True)
    adapter = CameraAdapter(FakeCameraProvider())

    adapter.register_with_gateway(gateway)
    result = gateway.execute(ToolRequest("camera.capture"))

    assert result.normalized_status is ToolGatewayStatus.ROUTED
    assert result.output["kind"] == "camera_frame"
    assert result.output["frame"]["width"] == 640
    assert result.output["requires_consent"] is True


def test_camera_adapter_requires_explicit_device_consent():
    gateway = build_gateway(grant_device=False)
    adapter = CameraAdapter(FakeCameraProvider())
    adapter.register_with_gateway(gateway)

    result = adapter.execute_capture(gateway)

    assert result.normalized_status is ToolGatewayStatus.BLOCKED
    assert result.error == "consent_required:device"
    assert gateway.permission_consent is not None
    assert gateway.permission_consent.last_decision is not None
    assert gateway.permission_consent.last_decision.required_confirmation is True


def test_camera_adapter_uses_default_camera_index():
    provider = FakeCameraProvider()
    gateway = build_gateway(grant_device=True)
    adapter = CameraAdapter(
        provider,
        CameraAdapterPolicy(default_camera_index=3),
    )
    adapter.register_with_gateway(gateway)

    result = adapter.execute_capture(gateway)

    assert result.succeeded is True
    assert provider.captured_indices == [3]
    assert result.output["frame"]["camera_index"] == 3


def test_camera_adapter_accepts_explicit_camera_index():
    provider = FakeCameraProvider()
    gateway = build_gateway(grant_device=True)
    adapter = CameraAdapter(provider)
    adapter.register_with_gateway(gateway)

    result = adapter.execute_capture(gateway, camera_index=1)

    assert result.succeeded is True
    assert provider.captured_indices == [1]


def test_camera_adapter_rejects_invalid_camera_index():
    adapter = CameraAdapter(FakeCameraProvider())

    with pytest.raises(ValueError, match="integer"):
        adapter.capture({"camera_index": "main"})
    with pytest.raises(ValueError, match="negative"):
        adapter.capture({"camera_index": -1})


def test_camera_adapter_can_disable_capture_by_policy():
    adapter = CameraAdapter(
        FakeCameraProvider(),
        CameraAdapterPolicy(allow_capture=False),
    )

    with pytest.raises(ValueError, match="disabled"):
        adapter.capture({})


def test_camera_frame_does_not_expose_bytes_by_default():
    adapter = CameraAdapter(FakeCameraProvider())

    output = adapter.capture({})

    assert "image_bytes" not in output["frame"]
    assert output["frame"]["size_bytes"] == len(b"fake-jpeg-bytes")


def test_camera_frame_can_expose_bytes_when_policy_allows_it():
    adapter = CameraAdapter(
        FakeCameraProvider(),
        CameraAdapterPolicy(include_image_bytes_in_output=True),
    )

    output = adapter.capture({})

    assert output["frame"]["image_bytes"] == b"fake-jpeg-bytes"


def test_semantic_registry_discovers_camera_by_natural_language():
    gateway = build_gateway(grant_device=True)
    adapter = CameraAdapter(FakeCameraProvider())
    adapter.register_with_gateway(gateway)

    snapshot = gateway.observe_turn("ROBY, mirá esto y decime qué ves")

    assert "camera.capture" in snapshot.requested_capabilities


def test_opencv_client_uses_injected_backend_and_encodes_frame(monkeypatch):
    class FakeEncoded:
        def tobytes(self) -> bytes:
            return b"encoded-frame"

    class FakeFrame:
        shape = (720, 1280, 3)

    class FakeCapture:
        def __init__(self) -> None:
            self.released = False

        def isOpened(self) -> bool:
            return True

        def read(self):
            return True, FakeFrame()

        def release(self) -> None:
            self.released = True

    fake_capture = FakeCapture()
    fake_cv2 = SimpleNamespace(
        VideoCapture=lambda index: fake_capture,
        imencode=lambda ext, frame: (True, FakeEncoded()),
    )
    monkeypatch.setitem(sys.modules, "cv2", fake_cv2)

    frame = OpenCVCameraClient().capture(0)

    assert frame.width == 1280
    assert frame.height == 720
    assert frame.image_bytes == b"encoded-frame"
    assert fake_capture.released is True


def test_opencv_client_reports_unavailable_device(monkeypatch):
    class FakeCapture:
        def isOpened(self) -> bool:
            return False

        def release(self) -> None:
            pass

    fake_cv2 = SimpleNamespace(
        VideoCapture=lambda index: FakeCapture(),
        imencode=lambda ext, frame: (True, b""),
    )
    monkeypatch.setitem(sys.modules, "cv2", fake_cv2)

    with pytest.raises(CameraProviderError, match="not available"):
        OpenCVCameraClient().capture(0)


def test_build_camera_adapter_from_config_uses_camera_index():
    adapter = build_camera_adapter_from_config(base_config(camera_index=4))

    assert adapter.policy.default_camera_index == 4
