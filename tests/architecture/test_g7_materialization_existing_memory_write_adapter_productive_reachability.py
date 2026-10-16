from __future__ import annotations

import inspect
from pathlib import Path

from app.approved_learning_memory_write_adapter import (
    GovernedMemoryWriteAdapterFoundation,
)
from app.official_runtime_composition import (
    OfficialROBYRuntime,
    OfficialRuntimeComposition,
)

ROOT = Path(__file__).resolve().parents[2]


def test_official_composition_declares_existing_memory_write_adapter() -> None:
    annotations = OfficialRuntimeComposition.__annotations__

    assert "governed_memory_write_adapter" in annotations


def test_official_factory_constructs_existing_memory_write_adapter_once() -> None:
    source = (ROOT / "app/official_runtime_composition.py").read_text(
        encoding="utf-8"
    )

    assert source.count("GovernedMemoryWriteAdapterFoundation()") == 1
    assert "governed_memory_write_adapter=" in source


def test_reachability_stops_before_write_request_execution_or_memory_write() -> None:
    source = (ROOT / "app/official_runtime_composition.py").read_text(
        encoding="utf-8"
    )
    preparation = inspect.getsource(
        OfficialROBYRuntime.prepare_governed_memory_write_request
    )
    authorized_reentry = inspect.getsource(
        OfficialROBYRuntime.execute_authorized_governed_memory_write
    )

    assert "GovernedMemoryWriteAdapterFoundation" in source
    assert "prepare_governed_memory_write_request" in source

    # G7 materialization -> write-request preparation remains inert.
    assert "execute_certified_write_request(" not in preparation
    assert "remember_governed_learning(" not in preparation

    # Productive execution exists only behind the separate exact-authorized reentry.
    assert (
        "execute_certified_write_request(request, authorization)"
        in authorized_reentry
    )
    assert "remember_governed_learning(" not in authorized_reentry


def test_existing_adapter_remains_the_exposed_contract() -> None:
    adapter = GovernedMemoryWriteAdapterFoundation()

    assert adapter.__class__ is GovernedMemoryWriteAdapterFoundation
