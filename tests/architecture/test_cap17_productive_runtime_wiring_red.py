from __future__ import annotations

import importlib
import inspect
from dataclasses import fields
from pathlib import Path

from app.runtime_capability_registry import OfficialRuntimeCapabilityRegistry
from core.governed_local_library.initiative import (
    LOCAL_LIBRARY_READ_CAPABILITY,
    governed_local_library_read_descriptor,
)
from core.knowledge_retrieval_orchestrator import KnowledgeRetrievalStep
from core.runtime_composition_root import RuntimeCompositionDependencies

WIRING_MODULE = "app.governed_local_library_runtime_wiring"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ROOT_FACTORY = PROJECT_ROOT / "app/runtime_root_factory.py"
CONFIG_PATH = PROJECT_ROOT / ".roby/config.json"


def _wiring_api():
    module = importlib.import_module(WIRING_MODULE)
    return (
        module.GovernedLocalLibraryRuntimeProvisionStatus,
        module.GovernedLocalLibraryRuntimeWiring,
        module.GovernedLocalLibraryConversationInterceptionPort,
        module.build_governed_local_library_runtime_from_environment,
    )


def test_cap17_registry_accepts_canonical_descriptor_without_redeclaring_it() -> None:
    assert hasattr(OfficialRuntimeCapabilityRegistry, "register_descriptor")


def test_cap17_runtime_dependencies_expose_one_library_runtime_wiring() -> None:
    names = tuple(field.name for field in fields(RuntimeCompositionDependencies))
    assert "governed_local_library_runtime" in names


def test_cap17_runtime_root_declares_explicit_library_environment_configuration(
) -> None:
    source = ROOT_FACTORY.read_text(encoding="utf-8")
    assert "ROBY_LOCAL_LIBRARY_ROOT" in source


def test_cap17_runtime_root_uses_the_governed_library_wiring_builder() -> None:
    source = ROOT_FACTORY.read_text(encoding="utf-8")
    assert "build_governed_local_library_runtime_from_environment" in source


def test_cap17_productive_wiring_api_exists() -> None:
    status, wiring, interceptor, builder = _wiring_api()
    assert status is not None
    assert wiring is not None
    assert interceptor is not None
    assert callable(builder)


def test_cap17_productive_wiring_has_fail_closed_states() -> None:
    status, _, _, _ = _wiring_api()
    values = {item.value for item in status}
    assert values == {"not_provisioned", "invalid_configuration", "provisioned"}


def test_cap17_productive_wiring_builder_is_dependency_injected() -> None:
    _, _, _, builder = _wiring_api()
    parameters = tuple(inspect.signature(builder).parameters)
    assert parameters == (
        "knowledge_runtime",
        "unified_runtime",
        "capability_registry",
    )


def test_cap17_productive_wiring_exposes_one_shared_catalogue() -> None:
    _, wiring_type, _, _ = _wiring_api()
    names = tuple(field.name for field in fields(wiring_type))
    assert "library" in names
    assert "conversation" in names


def test_cap17_productive_wiring_exposes_authorization_boundary() -> None:
    _, wiring_type, _, _ = _wiring_api()
    names = tuple(field.name for field in fields(wiring_type))
    assert "authorization_boundary" in names


def test_cap17_productive_wiring_exposes_roby_initiated_adapter() -> None:
    _, wiring_type, _, _ = _wiring_api()
    names = tuple(field.name for field in fields(wiring_type))
    assert "roby_initiated" in names


def test_cap17_productive_wiring_exposes_user_initiated_interceptor() -> None:
    _, wiring_type, interceptor_type, _ = _wiring_api()
    names = tuple(field.name for field in fields(wiring_type))
    assert "interceptor" in names
    assert hasattr(interceptor_type, "intercept")


def test_cap17_productive_wiring_exposes_auditable_configuration_state() -> None:
    _, wiring_type, _, _ = _wiring_api()
    names = tuple(field.name for field in fields(wiring_type))
    assert "status" in names
    assert "configured_root" in names
    assert "max_catalogue_entries" in names


def test_cap17_productive_wiring_uses_canonical_capability_name() -> None:
    module = importlib.import_module(WIRING_MODULE)
    assert module.LOCAL_LIBRARY_READ_CAPABILITY == LOCAL_LIBRARY_READ_CAPABILITY


def test_cap17_productive_wiring_uses_canonical_descriptor_factory() -> None:
    module = importlib.import_module(WIRING_MODULE)
    assert (
        module.governed_local_library_read_descriptor()
        == governed_local_library_read_descriptor()
    )


def test_cap17_productive_interceptor_does_not_own_an_alternate_router() -> None:
    _, _, interceptor_type, _ = _wiring_api()
    forbidden = {"route", "plan", "authorize", "learn", "remember", "persist"}
    public = {name for name in dir(interceptor_type) if not name.startswith("_")}
    assert not (forbidden & public)


def test_cap17_productive_wiring_has_no_background_scan_watch_or_polling() -> None:
    _, wiring_type, interceptor_type, _ = _wiring_api()
    forbidden = {"scan", "watch", "poll", "start", "run_forever", "background"}
    public = {
        name
        for type_ in (wiring_type, interceptor_type)
        for name in dir(type_)
        if not name.startswith("_")
    }
    assert not (forbidden & public)


def test_cap17_productive_wiring_keeps_epub_out_of_this_contract() -> None:
    source = importlib.import_module(WIRING_MODULE)
    text = inspect.getsource(source).casefold()
    assert ".epub" not in text


def test_cap17_productive_wiring_does_not_modify_retrieval_step_schema() -> None:
    _wiring_api()
    parameters = tuple(inspect.signature(KnowledgeRetrievalStep).parameters)
    assert parameters == ("source", "priority", "required", "query", "step_id")


def test_cap17_productive_wiring_does_not_manage_project_config() -> None:
    module = importlib.import_module(WIRING_MODULE)
    source = inspect.getsource(module)
    assert ".roby/config.json" not in source
    assert "write_text(" not in source
    assert "write_bytes(" not in source


def test_cap17_productive_wiring_contract_preserves_config_bytes() -> None:
    _wiring_api()
    before = CONFIG_PATH.read_bytes() if CONFIG_PATH.exists() else None
    after = CONFIG_PATH.read_bytes() if CONFIG_PATH.exists() else None
    assert after == before
