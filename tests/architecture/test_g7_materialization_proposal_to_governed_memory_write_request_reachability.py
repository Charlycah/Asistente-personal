from __future__ import annotations

import inspect
from pathlib import Path
from typing import get_type_hints

import pytest

from app.approved_learning_memory_materialization import (
    GovernedMemoryMaterializationProposal,
)
from app.approved_learning_memory_write_adapter import GovernedMemoryWriteRequest
from app.official_runtime_composition import OfficialROBYRuntime

ROOT = Path(__file__).resolve().parents[2]


class _AdapterSpy:
    def __init__(self, request: GovernedMemoryWriteRequest) -> None:
        self.request = request
        self.proposals: list[GovernedMemoryMaterializationProposal] = []

    def adapt(
        self,
        proposal: GovernedMemoryMaterializationProposal,
    ) -> GovernedMemoryWriteRequest:
        self.proposals.append(proposal)
        return self.request


def test_official_runtime_exposes_bounded_proposal_to_request_seam() -> None:
    signature = inspect.signature(
        OfficialROBYRuntime.prepare_governed_memory_write_request
    )

    assert tuple(signature.parameters) == ("self", "proposal")
    hints = get_type_hints(OfficialROBYRuntime.prepare_governed_memory_write_request)
    assert hints["proposal"] is GovernedMemoryMaterializationProposal
    assert hints["return"] is GovernedMemoryWriteRequest


def test_official_runtime_delegates_to_existing_adapter_only() -> None:
    proposal = object.__new__(GovernedMemoryMaterializationProposal)
    request = object.__new__(GovernedMemoryWriteRequest)
    spy = _AdapterSpy(request)
    runtime = object.__new__(OfficialROBYRuntime)
    runtime.composition = type(
        "_Composition",
        (),
        {"governed_memory_write_adapter": spy},
    )()

    result = runtime.prepare_governed_memory_write_request(proposal)

    assert result is request
    assert spy.proposals == [proposal]


def test_missing_adapter_fails_closed_before_request_creation() -> None:
    proposal = object.__new__(GovernedMemoryMaterializationProposal)
    runtime = object.__new__(OfficialROBYRuntime)
    runtime.composition = type(
        "_Composition",
        (),
        {"governed_memory_write_adapter": None},
    )()

    with pytest.raises(
        RuntimeError,
        match="governed memory write adapter is unavailable",
    ):
        runtime.prepare_governed_memory_write_request(proposal)


def test_new_seam_stops_before_productive_memory_execution() -> None:
    source = inspect.getsource(
        OfficialROBYRuntime.prepare_governed_memory_write_request
    )

    assert ".adapt(" in source
    assert "execute_certified_write_request(" not in source
    assert "remember_governed_learning(" not in source
    assert "OfficialMemoryGateway" not in source
    assert ".submit(" not in source


def test_official_composition_does_not_gain_memory_writer_authority() -> None:
    source = (ROOT / "app/official_runtime_composition.py").read_text(encoding="utf-8")

    assert "from .memory_consolidation import" not in source
    assert "OfficialMemoryGateway(" not in source
    assert "ProductiveGovernedLearningWiring(" not in source
