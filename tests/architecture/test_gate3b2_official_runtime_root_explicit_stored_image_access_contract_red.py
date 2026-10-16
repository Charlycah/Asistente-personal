from __future__ import annotations

import importlib
import inspect
from dataclasses import fields
from pathlib import Path

from core.runtime_composition_root import RuntimeCompositionDependencies

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ROOT_FACTORY = PROJECT_ROOT / "app/runtime_root_factory.py"
CONFIG_PATH = PROJECT_ROOT / ".roby/config.json"
WIRING_MODULE = "app.governed_stored_image_runtime_wiring"
CAPABILITY_NAME = "vision.stored_images.read_analyze"


def _wiring_module():
    return importlib.import_module(WIRING_MODULE)


def test_gate3b2_runtime_root_imports_existing_visual_builder() -> None:
    source = ROOT_FACTORY.read_text(encoding="utf-8")
    assert "build_vision_gateway_from_environment" in source


def test_gate3b2_runtime_root_builds_visual_gateway_exactly_once() -> None:
    source = inspect.getsource(importlib.import_module("app.runtime_root_factory"))
    assert source.count("build_vision_gateway_from_environment()") == 1


def test_gate3b2_runtime_dependencies_expose_visual_runtime_wiring() -> None:
    names = tuple(field.name for field in fields(RuntimeCompositionDependencies))
    assert "governed_visual_collection_runtime" in names


def test_gate3b2_productive_wiring_api_exists() -> None:
    module = _wiring_module()
    assert callable(module.build_governed_stored_image_runtime)
    assert hasattr(module, "GovernedStoredImageConversationInterceptionPort")


def test_gate3b2_wiring_reuses_one_existing_gateway_instance() -> None:
    module = _wiring_module()
    parameters = tuple(
        inspect.signature(module.build_governed_stored_image_runtime).parameters
    )
    assert "vision_gateway" in parameters
    source = inspect.getsource(module.build_governed_stored_image_runtime)
    assert "GovernedVisionGateway(" not in source


def test_gate3b2_registers_one_canonical_stored_image_capability() -> None:
    module = _wiring_module()
    assert module.STORED_IMAGE_ACCESS_CAPABILITY == CAPABILITY_NAME
    source = inspect.getsource(module.build_governed_stored_image_runtime)
    assert source.count("register") == 1


def test_gate3b2_list_is_owner_scoped_metadata_only() -> None:
    module = _wiring_module()
    interceptor = module.GovernedStoredImageConversationInterceptionPort
    source = inspect.getsource(interceptor)
    assert "list_stored_images" in source
    assert "owner=" in source
    assert "image_bytes" not in source
    assert "filesystem" not in source.casefold()
    assert ".root" not in source


def test_gate3b2_listing_does_not_analyze_any_image() -> None:
    module = _wiring_module()
    interceptor = module.GovernedStoredImageConversationInterceptionPort
    list_method = getattr(interceptor, "list_images")
    source = inspect.getsource(list_method)
    assert "analyze_stored_image" not in source


def test_gate3b2_analysis_requires_exact_image_id() -> None:
    module = _wiring_module()
    interceptor = module.GovernedStoredImageConversationInterceptionPort
    analyze = getattr(interceptor, "analyze_image")
    parameters = inspect.signature(analyze).parameters
    assert "image_id" in parameters
    source = inspect.getsource(analyze).casefold()
    assert "filename" not in source
    assert "fuzzy" not in source
    assert "semantic" not in source


def test_gate3b2_analysis_requires_fresh_explicit_consent() -> None:
    module = _wiring_module()
    interceptor = module.GovernedStoredImageConversationInterceptionPort
    analyze = getattr(interceptor, "analyze_image")
    source = inspect.getsource(analyze)
    assert "explicit_user_consent" in source
    assert "StoredImageAnalysisRequest" in source


def test_gate3b2_analysis_delegates_once_to_same_existing_gateway() -> None:
    module = _wiring_module()
    interceptor = module.GovernedStoredImageConversationInterceptionPort
    source = inspect.getsource(interceptor.analyze_image)
    assert source.count("self.vision_gateway.analyze_stored_image") == 1
    assert "GovernedVisionGateway(" not in source


def test_gate3b2_preserves_single_visual_authority() -> None:
    import app.vision_core as vision_core
    import app.vision_gateway as vision_gateway
    import core.governed_image_repository as image_repository

    joined = "\n".join(
        (
            inspect.getsource(vision_core),
            inspect.getsource(vision_gateway),
            inspect.getsource(image_repository),
        )
    )
    assert joined.count("class OfficialVisionCore") == 1
    assert joined.count("class GovernedVisionGateway") == 1
    forbidden = (
        "PinacotecaManager",
        "VisualCollectionManager",
        "PersonalVisionManager",
        "SecondVisionCore",
    )
    assert all(name not in joined for name in forbidden)


def test_gate3b2_contract_preserves_project_config_bytes() -> None:
    before = CONFIG_PATH.read_bytes() if CONFIG_PATH.exists() else None
    module = _wiring_module()
    assert module.STORED_IMAGE_ACCESS_CAPABILITY == CAPABILITY_NAME
    after = CONFIG_PATH.read_bytes() if CONFIG_PATH.exists() else None
    assert after == before
