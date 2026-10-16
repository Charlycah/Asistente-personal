from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from app.runtime_ui_adapter import LocalConversationUIAdapter

ROOT = Path(__file__).resolve().parents[2]
HARNESS = ROOT / "scripts" / "diagnostics" / "roby_conversational_e2e_harness.py"


def _load_harness():
    spec = importlib.util.spec_from_file_location("roby_e2e_harness", HARNESS)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class RuntimeStub:
    pass


class Wrapper:
    def __init__(self, adapter) -> None:
        self.adapter = adapter


@dataclass(frozen=True)
class Message:
    sender: str
    text: str

    def render(self) -> str:
        return f"{self.sender}: {self.text}"


def test_harness_is_external_to_main_and_desktop_runtime() -> None:
    main_source = (ROOT / "main.py").read_text(encoding="utf-8")
    desktop_source = (ROOT / "app" / "desktop_ui.py").read_text(encoding="utf-8")

    assert "roby_conversational_e2e_harness" not in main_source
    assert "roby_conversational_e2e_harness" not in desktop_source
    assert "--observe" not in main_source


def test_harness_reuses_existing_internal_observer() -> None:
    source = HARNESS.read_text(encoding="utf-8")

    assert "DevelopmentConsoleObserver" in source
    assert "DevelopmentConsoleRenderer" in source
    assert "build_unified_desktop_app" in source
    assert "app.controller.submit" in source


def test_local_adapter_discovery_preserves_existing_adapter_chain() -> None:
    harness = _load_harness()
    local = LocalConversationUIAdapter(RuntimeStub())
    wrapped = Wrapper(Wrapper(local))

    assert harness._find_local_adapter(wrapped) is local


def test_local_adapter_discovery_fails_closed() -> None:
    harness = _load_harness()

    try:
        harness._find_local_adapter(Wrapper(object()))
    except RuntimeError as exc:
        assert "LocalConversationUIAdapter not found" in str(exc)
    else:
        raise AssertionError("missing local adapter must fail closed")


def test_cases_are_bounded_and_match_guide_v2_d_through_l() -> None:
    harness = _load_harness()

    assert tuple(item.case_id for item in harness.CASES) == (
        "D",
        "E",
        "F",
        "G",
        "H",
        "I",
        "J",
        "K",
        "L",
    )
    assert tuple(len(item.prompts) for item in harness.CASES) == (
        3,
        3,
        2,
        2,
        3,
        2,
        2,
        2,
        4,
    )
    assert "Corrección" in harness.CASES[0].prompts[1]
    assert "ayer" in harness.CASES[1].prompts[-1].casefold()
    assert "Elena" in harness.CASES[2].prompts[-1]
    assert "afirmar" in harness.CASES[3].prompts[-1]
    assert "más apoyo" in harness.CASES[4].prompts[-1]


def test_message_rendering_uses_existing_desktop_render_contract() -> None:
    harness = _load_harness()

    assert harness._render_messages((Message("Vos", "hola"),)) == ("Vos: hola",)


def test_harness_does_not_register_capability_or_modify_runtime_authority() -> None:
    source = HARNESS.read_text(encoding="utf-8")
    forbidden = (
        "register_capability",
        "set_planner",
        "set_coordinator",
        "CapabilityRegistration",
        "OfficialCapabilityRegistration",
        "main.py --observe",
    )

    assert all(item not in source for item in forbidden)


def test_harness_uses_precomposition_isolated_sessions(
) -> None:
    harness = _load_harness()
    source = HARNESS.read_text(encoding="utf-8")

    sessions = tuple(
        harness._diagnostic_session_id("r01", item.case_id)
        for item in harness.CASES
    )
    assert len(set(sessions)) == len(harness.CASES)
    assert sessions[0] == "diagnostic-guide-v2-r01-d"
    assert "build_unified_desktop_app(local_conversation=local_conversation)" in source
    assert "app.controller.submit(prompt)" in source
    assert "app.controller.submit(prompt, session_id=" not in source


def test_diagnostic_state_is_separate_from_productive_runtime_state() -> None:
    harness = _load_harness()

    session_id = harness._diagnostic_session_id("r01", "D")
    state_path = harness._diagnostic_state_path(session_id)

    assert state_path.as_posix().startswith(".roby/diagnostics/runtime_state/")
    assert state_path.name == "diagnostic-guide-v2-r01-d.json"


def test_harness_direct_execution_resolves_project_root_without_pythonpath() -> None:
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)

    completed = subprocess.run(
        [sys.executable, str(HARNESS), "--help"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    expected = "Run controlled ROBY conversational Guide v2 diagnostics."
    assert expected in completed.stdout
    assert "ModuleNotFoundError" not in completed.stderr
