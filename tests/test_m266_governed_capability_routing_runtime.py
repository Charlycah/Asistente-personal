from datetime import datetime, timezone

from app.runtime_root_factory import build_runtime_root
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)


def _request(text: str):
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="m266",
        text=text,
    )


def _intercept(root, text: str):
    return root.dependencies.official_capability_registry.intercept(
        _request(text), now=datetime.now(timezone.utc)
    )


def test_m266_is_composed_and_registered(monkeypatch, tmp_path):
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_PATH", str(tmp_path / "memory"))
    root = build_runtime_root()
    router = root.dependencies.governed_capability_routing_runtime
    registry = root.dependencies.official_capability_registry

    assert router is registry.routing_runtime
    assert registry.registration_for("capability.governed_routing_runtime") is not None


def test_sensitive_capability_requires_explicit_consent(monkeypatch, tmp_path):
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_PATH", str(tmp_path / "memory"))
    root = build_runtime_root()

    result = _intercept(root, "usar capacidad device.runtime")

    assert result is not None
    assert result.rationale == "governed_capability_route_consent_required"
    assert "autorizar capacidad device.runtime" in result.response_text
    assert root.dependencies.device_runtime.snapshot.last_evaluation_status is None


def test_explicit_grant_allows_safe_selection_without_execution(monkeypatch, tmp_path):
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_PATH", str(tmp_path / "memory"))
    root = build_runtime_root()

    granted = _intercept(root, "autorizar capacidad device.runtime")
    routed = _intercept(root, "usar capacidad device.runtime")

    assert granted is not None
    assert granted.rationale == "governed_capability_grant_completed"
    assert routed is not None
    assert routed.rationale == "governed_capability_route_authorized_no_execution"
    assert root.dependencies.device_runtime.snapshot.last_evaluation_status is None


def test_semantic_discovery_never_executes_capability(monkeypatch, tmp_path):
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_PATH", str(tmp_path / "memory"))
    root = build_runtime_root()

    result = _intercept(root, "buscar capacidad para usar cámara")

    assert result is not None
    assert result.rationale == "governed_capability_discovery_completed"
    assert "device.runtime" in result.response_text
    assert root.dependencies.device_runtime.snapshot.last_evaluation_status is None


def test_revocation_restores_consent_requirement(monkeypatch, tmp_path):
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_PATH", str(tmp_path / "memory"))
    root = build_runtime_root()

    _intercept(root, "autorizar capacidad retrieval.external_runtime")
    revoked = _intercept(root, "revocar capacidad retrieval.external_runtime")
    routed = _intercept(root, "usar capacidad retrieval.external_runtime")

    assert revoked is not None
    assert revoked.rationale == "governed_capability_revoke_completed"
    assert routed is not None
    assert routed.rationale == "governed_capability_route_consent_required"
    assert root.dependencies.external_retrieval_runtime.snapshot.evaluations == 0
