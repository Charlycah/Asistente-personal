from __future__ import annotations

import importlib
import os
from collections.abc import Callable

from core.local_runtime_bootstrap import (
    LocalRuntimeBootstrap,
    LocalRuntimeBootstrapConfig,
)
from core.runtime_composition_root import RuntimeCompositionRoot

from .personal_profile_factory import select_runtime_identity_from_environment


class LocalRuntimeFactoryError(RuntimeError):
    pass


def build_local_runtime_from_environment() -> LocalRuntimeBootstrap:
    factory = _load_root_factory(os.getenv("ROBY_RUNTIME_ROOT_FACTORY", ""))
    identity = select_runtime_identity_from_environment()
    owner = identity.profile.owner
    session_id = identity.session.session_id
    state_path = identity.state_path
    root = factory()
    if not isinstance(root, RuntimeCompositionRoot):
        raise LocalRuntimeFactoryError(
            "ROBY runtime root factory must return RuntimeCompositionRoot"
        )
    return LocalRuntimeBootstrap(
        root=root,
        config=LocalRuntimeBootstrapConfig(
            owner=owner,
            session_id=session_id,
            state_path=state_path,
        ),
    )


def _load_root_factory(path: str) -> Callable[[], RuntimeCompositionRoot]:
    normalized = path.strip()
    if not normalized or ":" not in normalized:
        raise LocalRuntimeFactoryError(
            "Set ROBY_RUNTIME_ROOT_FACTORY to 'module:function'"
        )
    module_name, function_name = normalized.split(":", 1)
    try:
        module = importlib.import_module(module_name)
        factory = getattr(module, function_name)
    except (ImportError, AttributeError) as exc:
        raise LocalRuntimeFactoryError(
            f"Cannot load ROBY runtime root factory: {normalized}"
        ) from exc
    if not callable(factory):
        raise LocalRuntimeFactoryError("ROBY runtime root factory must be callable")
    return factory
