from __future__ import annotations

from pathlib import Path

from app.development_console import run_doctor
from app.development_setup import SetupOptions, setup_environment
from app.knowledge_runtime import OfficialKnowledgeRuntimeGateway
from app.roby_config import DEFAULT_CONFIG
from app.runtime_root_factory import (
    OFFICIAL_RUNTIME_FACTORY,
    EnvironmentInferenceRequestPort,
    EnvironmentReadinessPort,
    build_runtime_root,
)
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
)
from core.runtime_composition_root import RuntimeCompositionRoot


def test_official_factory_path_is_stable():
    assert OFFICIAL_RUNTIME_FACTORY == "app.runtime_root_factory:build_runtime_root"


def test_factory_returns_official_root(monkeypatch):
    monkeypatch.setenv("ROBY_LOCAL_PROVIDER_MODEL", "llama3")
    root = build_runtime_root()
    assert isinstance(root, RuntimeCompositionRoot)


def test_factory_disables_unconfigured_retrieval(monkeypatch):
    monkeypatch.setenv("ROBY_LOCAL_PROVIDER_MODEL", "llama3")
    root = build_runtime_root()
    assert root.config.retrieval_enabled is False


def test_factory_registers_single_local_provider(monkeypatch):
    monkeypatch.setenv("ROBY_LOCAL_PROVIDER_MODEL", "llama3")
    root = build_runtime_root()
    assert len(root.dependencies.local_providers) == 1
    assert root.dependencies.local_providers[0].name == "local-openai"


def test_inference_port_preserves_identity():
    request = GovernedConversationPipelineRequest(
        owner="Carlos", session_id="desktop-main", text="Hola"
    )
    built = EnvironmentInferenceRequestPort().build(request)
    assert built.prompt == "Hola"
    assert built.metadata == {"owner": "Carlos", "session": "desktop-main"}


def test_official_knowledge_gateway_uses_user_text():
    request = GovernedConversationPipelineRequest(
        owner="Carlos", session_id="desktop-main", text="Explicame ROBY"
    )
    need = OfficialKnowledgeRuntimeGateway().describe(request)
    assert need.query == "Explicame ROBY"
    assert need.internal_confidence == 1.0


def test_setup_uses_official_factory_by_default(tmp_path):
    result = setup_environment(
        SetupOptions(
            project_root=tmp_path,
            runtime_factory=OFFICIAL_RUNTIME_FACTORY,
            provider_model="llama3",
        )
    )
    content = (tmp_path / ".roby/config.json").read_text()
    assert OFFICIAL_RUNTIME_FACTORY in content
    assert "runtime.factory" not in result.pending_fields


def test_setup_can_override_official_factory(tmp_path):
    setup_environment(
        SetupOptions(
            project_root=tmp_path,
            runtime_factory="custom.module:factory",
            provider_model="llama3",
        )
    )
    assert "custom.module:factory" in (tmp_path / ".roby/config.json").read_text()


def test_single_config_contains_official_factory():
    assert DEFAULT_CONFIG["runtime"]["factory"] == OFFICIAL_RUNTIME_FACTORY


def test_doctor_accepts_official_factory(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("ROBY_RUNTIME_ROOT_FACTORY", OFFICIAL_RUNTIME_FACTORY)
    monkeypatch.setenv("ROBY_LOCAL_PROVIDER_MODEL", "llama3")
    checks = {item.name: item for item in run_doctor()}
    assert checks["runtime_factory"].passed


def test_root_composes_without_external_retrievers(monkeypatch):
    monkeypatch.setenv("ROBY_LOCAL_PROVIDER_MODEL", "llama3")
    composition = build_runtime_root().compose()
    assert composition.retrieval_executor is None


def test_factory_does_not_create_workers(monkeypatch):
    monkeypatch.setenv("ROBY_LOCAL_PROVIDER_MODEL", "llama3")
    root = build_runtime_root()
    assert not hasattr(root, "executor")


def test_factory_does_not_mutate_environment(monkeypatch):
    monkeypatch.setenv("ROBY_LOCAL_PROVIDER_MODEL", "llama3")
    before = dict(__import__("os").environ)
    build_runtime_root()
    assert dict(__import__("os").environ) == before


def test_direct_setup_preserves_historical_pending_contract(tmp_path, monkeypatch):
    monkeypatch.setattr("app.development_setup.detect_ollama_models", lambda: ())
    result = setup_environment(SetupOptions(project_root=tmp_path))
    assert result.pending_fields == (
        "runtime.factory",
        "providers.local.model",
    )


def test_documentation_names_official_factory():
    guide = Path("docs/guides/ROBY_INSTALLATION_GUIDE.md").read_text()
    assert OFFICIAL_RUNTIME_FACTORY in guide


def test_main_can_import_official_factory():
    module_name, function_name = OFFICIAL_RUNTIME_FACTORY.split(":", 1)
    module = __import__(module_name, fromlist=[function_name])
    assert callable(getattr(module, function_name))


def test_environment_readiness_exposes_required_lineage():
    request = GovernedConversationPipelineRequest(
        owner="Carlos", session_id="desktop-main", text="Hola"
    )
    result = EnvironmentReadinessPort().resolve(request)
    assert result.status.value == "ready"
    assert result.request.owner == "Carlos"
    assert len(result.readiness_id) == 64
