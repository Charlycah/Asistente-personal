from __future__ import annotations

from core.external_resource_registry import ExternalResourceRegistryAuthority

from .official_runtime_composition import OfficialROBYRuntime


class RuntimeWebPanelSource:
    """Minimal projection of official runtime facts; no lifecycle ownership."""

    def __init__(self, runtime: OfficialROBYRuntime) -> None:
        self._runtime = runtime

    def read(self) -> dict[str, object]:
        operational = self._runtime.snapshot()
        readiness = self._runtime.readiness()
        return {
            "system_status": operational.status.value,
            "runtime_ready": readiness.ready,
            "diagnostic_status": operational.health.value,
            "observed_at": operational.generated_at.isoformat(),
        }



class ExternalResourcesWebPanelSource:
    """Minimized M394 projection without endpoints, metadata or credentials."""

    def __init__(self, registry: ExternalResourceRegistryAuthority) -> None:
        self._registry = registry

    def read(self) -> dict[str, object]:
        snapshot = self._registry.snapshot()
        resources = tuple(
            {
                "resource_id": item.resource_id,
                "kind": item.kind.value,
                "authorization_status": item.authorization_state.value,
                "availability_status": item.state.value,
                "connectivity_status": item.connectivity_state.value,
                "capabilities": tuple(item.capabilities),
            }
            for item in snapshot.resources
        )
        return {
            "authority_id": snapshot.authority_id,
            "resource_count": len(resources),
            "resources": resources,
        }
