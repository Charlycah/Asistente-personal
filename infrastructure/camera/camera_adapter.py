from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from core.tool_gateway import ToolGatewayManager, ToolRequest, ToolResult
from infrastructure.camera.camera_client import CameraProvider, OpenCVCameraClient
from infrastructure.config.config_schema import AppConfig


@dataclass(frozen=True)
class CameraAdapterPolicy:
    """Política de M68 para percepción local con consentimiento explícito."""

    default_camera_index: int = 0
    include_image_bytes_in_output: bool = False
    allow_capture: bool = True

    def __post_init__(self) -> None:
        if self.default_camera_index < 0:
            raise ValueError("camera default index must not be negative")


class CameraAdapter:
    """Adapter M68: captura cámara local sin acoplar hardware al core."""

    CAPTURE_CAPABILITY = "camera.capture"

    def __init__(
        self,
        provider: CameraProvider,
        policy: CameraAdapterPolicy | None = None,
    ) -> None:
        self.provider = provider
        self.policy = policy or CameraAdapterPolicy()

    def register_with_gateway(self, gateway: ToolGatewayManager) -> None:
        """Registra la captura de cámara detrás del Tool Gateway."""

        gateway.register_capability(
            gateway.capabilities[self.CAPTURE_CAPABILITY],
            handler=self.capture,
        )

    def capture(self, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        if not self.policy.allow_capture:
            raise ValueError("camera capture is disabled by policy")
        camera_index = self._camera_index_from(payload)
        frame = self.provider.capture(camera_index)
        output = frame.to_dict(include_bytes=self.policy.include_image_bytes_in_output)
        return {
            "capability": self.CAPTURE_CAPABILITY,
            "kind": "camera_frame",
            "frame": output,
            "requires_consent": True,
            "permission_scope": "device",
            "mutates_external_state": False,
            "natural_summary": (
                "Capturé una imagen de la cámara local autorizada "
                f"(índice {frame.camera_index})."
            ),
        }

    def execute_capture(
        self,
        gateway: ToolGatewayManager,
        *,
        camera_index: int | None = None,
        reason: str = "camera_capture_requested",
    ) -> ToolResult:
        payload: dict[str, object] = {}
        if camera_index is not None:
            payload["camera_index"] = camera_index
        return gateway.execute(
            ToolRequest(
                self.CAPTURE_CAPABILITY,
                payload=payload,
                reason=reason,
            )
        )

    def _camera_index_from(self, payload: Mapping[str, Any]) -> int:
        raw = payload.get("camera_index", self.policy.default_camera_index)
        try:
            camera_index = int(raw)
        except (TypeError, ValueError) as exc:
            raise ValueError("camera index must be an integer") from exc
        if camera_index < 0:
            raise ValueError("camera index must not be negative")
        return camera_index


def build_camera_adapter_from_config(config: AppConfig) -> CameraAdapter:
    """Factory segura: usa configuración centralizada de cámara."""

    policy = CameraAdapterPolicy(default_camera_index=config.secrets.camera_index)
    return CameraAdapter(OpenCVCameraClient(), policy)
