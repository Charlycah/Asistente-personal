from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from app.official_runtime_composition import OfficialROBYRuntime

ROOT = Path(__file__).resolve().parents[2]


class _WiringSpy:
    def __init__(self) -> None:
        self.calls = []

    def execute_certified_write_request(self, request, authorization):
        self.calls.append((request, authorization))
        return "delegated-result"


def _runtime_with(wiring):
    runtime = object.__new__(OfficialROBYRuntime)
    runtime.composition = SimpleNamespace(
        productive_governed_learning_wiring=wiring,
    )
    return runtime


def test_reentry_delegates_exact_pair_to_existing_wiring_reference_once() -> None:
    wiring = _WiringSpy()
    runtime = _runtime_with(wiring)
    request = object()
    authorization = object()

    result = runtime.execute_authorized_governed_memory_write(
        request,
        authorization,
    )

    assert result == "delegated-result"
    assert runtime.productive_governed_learning_wiring is wiring
    assert wiring.calls == [(request, authorization)]


def test_reentry_fails_closed_when_existing_wiring_reference_is_unavailable() -> None:
    runtime = _runtime_with(None)

    try:
        runtime.execute_authorized_governed_memory_write(object(), object())
    except RuntimeError as exc:
        assert str(exc) == "productive governed learning wiring is unavailable"
    else:
        raise AssertionError("missing wiring must fail closed")


def test_official_composition_binds_gateway_owned_instance_without_new_wiring() -> None:
    source = (ROOT / "app/official_runtime_composition.py").read_text(encoding="utf-8")

    assert '"_productive_governed_learning_wiring"' in source
    assert "productive_governed_learning_wiring = getattr(" in source
    assert (
        "productive_governed_learning_wiring=productive_governed_learning_wiring"
    ) in source
    assert "ProductiveGovernedLearningWiring(" not in source


def test_protected_official_conversation_gateway_remains_byte_identical() -> None:
    gateway_source = Path("app/official_conversation_gateway.py").read_text(
        encoding="utf-8"
    )
    assert "class OfficialConversationGateway" in gateway_source
    assert "def submit(" in gateway_source
