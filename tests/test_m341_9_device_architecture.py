from __future__ import annotations

from app.desktop_ui import DesktopConversationController
from app.device_architecture import (
    DeviceArchitectureService,
    DeviceCapability,
    DeviceCommand,
    DeviceCommandResult,
    DeviceDescriptor,
    DeviceRegistry,
    DeviceStatus,
    SimulatedDeviceAdapter,
)


class StubAdapter:
    def submit_text(self, text: str, session_id: str | None = None):
        raise AssertionError("No debe llegar al adaptador general.")


def make_adapter(
    *,
    device_id: str = "sensor-1",
    status: DeviceStatus = DeviceStatus.AVAILABLE,
    writable: bool = False,
) -> SimulatedDeviceAdapter:
    return SimulatedDeviceAdapter(
        DeviceDescriptor(
            device_id=device_id,
            name="Sensor simulado",
            category="sensor",
            status=status,
            capabilities=(
                DeviceCapability(
                    "temperatura",
                    readable=True,
                    writable=writable,
                ),
            ),
        )
    )


def test_registers_and_lists_device() -> None:
    registry = DeviceRegistry()
    descriptor = registry.register(make_adapter())
    assert descriptor.device_id == "sensor-1"
    assert registry.list_devices() == (descriptor,)


def test_rejects_duplicate_identifier() -> None:
    registry = DeviceRegistry()
    registry.register(make_adapter())
    try:
        registry.register(make_adapter())
    except ValueError as exc:
        assert "Ya existe" in str(exc)
    else:
        raise AssertionError("Debía rechazar el identificador duplicado.")


def test_unregisters_device() -> None:
    registry = DeviceRegistry()
    registry.register(make_adapter())
    assert registry.unregister("sensor-1") is True
    assert registry.unregister("sensor-1") is False


def test_filters_by_status_and_capability() -> None:
    registry = DeviceRegistry()
    registry.register(make_adapter(device_id="available"))
    registry.register(
        make_adapter(
            device_id="disabled",
            status=DeviceStatus.DISABLED,
        )
    )
    assert len(
        registry.list_devices(status=DeviceStatus.AVAILABLE)
    ) == 1
    assert len(
        registry.list_devices(capability="temperatura")
    ) == 2


def test_executes_supported_read_command() -> None:
    registry = DeviceRegistry()
    adapter = make_adapter()
    registry.register(adapter)
    result = registry.execute(
        DeviceCommand("sensor-1", "temperatura", "leer")
    )
    assert result.accepted is True
    assert len(adapter.commands) == 1


def test_blocks_write_on_read_only_capability() -> None:
    registry = DeviceRegistry()
    registry.register(make_adapter())
    result = registry.execute(
        DeviceCommand("sensor-1", "temperatura", "configurar")
    )
    assert result.accepted is False
    assert "solo lectura" in result.message


def test_blocks_unavailable_device() -> None:
    registry = DeviceRegistry()
    registry.register(
        make_adapter(status=DeviceStatus.UNAVAILABLE)
    )
    result = registry.execute(
        DeviceCommand("sensor-1", "temperatura", "leer")
    )
    assert result.accepted is False
    assert "no disponible" in result.message


def test_custom_simulated_response() -> None:
    descriptor = make_adapter().describe()
    adapter = SimulatedDeviceAdapter(
        descriptor,
        {
            ("temperatura", "leer"): DeviceCommandResult(
                True,
                "Lectura simulada.",
                {"value": "22.5", "unit": "C"},
            )
        },
    )
    registry = DeviceRegistry()
    registry.register(adapter)
    result = registry.execute(
        DeviceCommand("sensor-1", "temperatura", "leer")
    )
    assert result.data["value"] == "22.5"


def test_service_reports_empty_registry() -> None:
    response = DeviceArchitectureService().prepare(
        "arquitectura de dispositivos"
    )
    assert response.handled is True
    assert "no hay dispositivos registrados" in response.response


def test_desktop_routes_device_architecture_command() -> None:
    controller = DesktopConversationController(StubAdapter())
    messages = controller.submit("dispositivos disponibles")
    assert len(messages) == 2
    assert "arquitectura para dispositivos" in messages[1].text
