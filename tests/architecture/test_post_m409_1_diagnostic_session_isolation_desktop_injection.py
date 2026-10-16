from __future__ import annotations

import inspect

from app import desktop_bootstrap


def test_desktop_builder_exposes_existing_local_conversation_injection_seam() -> None:
    signature = inspect.signature(desktop_bootstrap.build_unified_desktop_app)

    assert "local_conversation" in signature.parameters
    parameter = signature.parameters["local_conversation"]
    assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
    assert parameter.default is None


def test_desktop_builder_forwards_injected_conversation_to_official_runtime() -> None:
    source = inspect.getsource(desktop_bootstrap.build_unified_desktop_app)

    assert "build_official_runtime_from_environment(" in source
    assert "local_conversation=local_conversation" in source
    assert "LocalRuntimeBootstrap(" not in source
    assert "LocalRuntimeBootstrapConfig(" not in source


def test_default_desktop_alias_remains_argument_free() -> None:
    source = inspect.getsource(desktop_bootstrap.build_desktop_app)

    assert "return build_unified_desktop_app()" in source
