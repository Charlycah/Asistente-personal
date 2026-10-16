from __future__ import annotations

import importlib

import pytest

from app.runtime_execution_inventory import (
    EXECUTION_ROOT_INVENTORY,
    OFFICIAL_COMPOSITION_ROOT,
    OFFICIAL_PROCESS_ENTRYPOINT,
    OFFICIAL_RUNTIME_FACTORY,
    ExecutionRootDisposition,
    ExecutionRootRole,
    canonical_execution_chain,
    execution_root_by_key,
)


def _resolve(target: str):
    module_name, attribute_name = target.split(":", 1)
    return getattr(importlib.import_module(module_name), attribute_name)


def test_inventory_keys_and_targets_are_unique() -> None:
    keys = [record.key for record in EXECUTION_ROOT_INVENTORY]
    targets = [record.target for record in EXECUTION_ROOT_INVENTORY]

    assert len(keys) == len(set(keys))
    assert len(targets) == len(set(targets))


@pytest.mark.parametrize("record", EXECUTION_ROOT_INVENTORY)
def test_every_inventory_target_is_importable(record) -> None:
    assert callable(_resolve(record.target))


def test_inventory_declares_one_canonical_process_entrypoint() -> None:
    process_roots = [
        record
        for record in EXECUTION_ROOT_INVENTORY
        if record.role is ExecutionRootRole.CANONICAL_PROCESS_ENTRYPOINT
    ]

    assert [record.target for record in process_roots] == [OFFICIAL_PROCESS_ENTRYPOINT]
    assert process_roots[0].disposition is ExecutionRootDisposition.KEEP_CANONICAL


def test_inventory_declares_one_runtime_factory_and_composition_root() -> None:
    canonical_targets = {
        record.role: record.target
        for record in EXECUTION_ROOT_INVENTORY
        if record.disposition is ExecutionRootDisposition.KEEP_CANONICAL
    }

    assert canonical_targets[ExecutionRootRole.CANONICAL_RUNTIME_FACTORY] == (
        OFFICIAL_RUNTIME_FACTORY
    )
    assert canonical_targets[ExecutionRootRole.CANONICAL_COMPOSITION_ROOT] == (
        OFFICIAL_COMPOSITION_ROOT
    )


def test_canonical_execution_chain_is_explicit_and_stable() -> None:
    assert canonical_execution_chain() == (
        "main:main",
        "app.local_conversation_factory:build_local_conversation_from_environment",
        "app.local_runtime_entrypoint:build_local_runtime_from_environment",
        "app.runtime_root_factory:build_runtime_root",
        "core.runtime_composition_root:RuntimeCompositionRoot",
        "app.official_runtime_composition:OfficialROBYRuntime",
    )


def test_retired_legacy_composition_is_absent_from_inventory() -> None:
    assert all(
        record.key != "legacy_application_composition"
        for record in EXECUTION_ROOT_INVENTORY
    )
    with pytest.raises(KeyError):
        execution_root_by_key("legacy_application_composition")
