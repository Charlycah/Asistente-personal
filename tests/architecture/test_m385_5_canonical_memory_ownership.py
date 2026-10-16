from __future__ import annotations

from hashlib import sha256

import pytest

from app.memory_consolidation import OfficialMemoryGateway
from core.memory_runtime_integration import (
    MemoryRuntimeConfig,
    MemoryRuntimeIntegration,
)


def _runtime(tmp_path, **overrides):
    return MemoryRuntimeIntegration(
        MemoryRuntimeConfig(
            root_path=tmp_path / "memory",
            canonical_joint_owner=True,
            **overrides,
        )
    )


def _legacy_filename(owner: str) -> str:
    digest = sha256(owner.casefold().encode("utf-8")).hexdigest()[:16]
    return f"owner-{digest}.sqlite3"


def test_m385_5_coowner_aliases_converge_on_one_store(tmp_path):
    runtime = _runtime(tmp_path)
    runtime.store_explicit(owner="Carlos", text="recuerdo conjunto")

    assert runtime.count(owner="Cristina") == 1
    assert runtime.count(owner="Carlos y Cristina") == 1
    assert (tmp_path / "memory" / "coowners.sqlite3").exists()
    assert not tuple((tmp_path / "memory").glob("owner-*.sqlite3"))


def test_m385_5_free_owner_cannot_create_a_store(tmp_path):
    runtime = _runtime(tmp_path)

    with pytest.raises(ValueError, match="not a recognized ROBY coowner"):
        runtime.store_explicit(owner="Persona inventada", text="no guardar")

    assert not (tmp_path / "memory").exists()


def test_m385_5_one_recognized_legacy_store_is_copied_not_moved(tmp_path):
    root = tmp_path / "memory"
    legacy = MemoryRuntimeIntegration(MemoryRuntimeConfig(root_path=root))
    legacy.store_explicit(owner="Carlos", text="recuerdo histórico")
    legacy_path = root / _legacy_filename("Carlos")

    runtime = _runtime(tmp_path)
    assert runtime.count(owner="Cristina") == 1
    assert legacy_path.exists()
    assert (root / "coowners.sqlite3").exists()


def test_m385_5_ambiguous_legacy_stores_stop_without_merging(tmp_path):
    root = tmp_path / "memory"
    legacy = MemoryRuntimeIntegration(MemoryRuntimeConfig(root_path=root))
    legacy.store_explicit(owner="Carlos", text="recuerdo de Carlos")
    legacy.store_explicit(owner="Cristina", text="recuerdo de Cristina")

    runtime = _runtime(tmp_path)
    with pytest.raises(RuntimeError, match="require human review"):
        runtime.count(owner="Carlos y Cristina")

    assert (root / _legacy_filename("Carlos")).exists()
    assert (root / _legacy_filename("Cristina")).exists()
    assert not (root / "coowners.sqlite3").exists()


def test_m385_5_gateway_has_bounded_subject_vocabulary(tmp_path):
    runtime = _runtime(tmp_path)
    gateway = OfficialMemoryGateway(runtime, owner="Carlos y Cristina")

    assert gateway._memory_subject("Carlos") == "Carlos"
    assert gateway._memory_subject("cristina") == "Cristina"
    assert gateway._memory_subject("Familia") is None
