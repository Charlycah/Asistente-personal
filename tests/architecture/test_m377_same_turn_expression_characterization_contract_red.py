"""M377 characterization RED: no production changes.

Characterize missing same-response tone correlation without prescribing a carrier.
"""

from __future__ import annotations

import ast
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DESKTOP = ROOT / "app" / "desktop_ui.py"


def _desktop_class() -> ast.ClassDef:
    module = ast.parse(DESKTOP.read_text(encoding="utf-8"))
    return next(
        node
        for node in module.body
        if isinstance(node, ast.ClassDef)
        and node.name == "DesktopConversationController"
    )


def _tone_method() -> ast.FunctionDef:
    return next(
        node
        for node in _desktop_class().body
        if isinstance(node, ast.FunctionDef)
        and node.name == "_adaptive_delivery_tone"
    )


def test_red_tone_resolution_requires_response_scoped_evidence() -> None:
    """RED: a lateral no-argument lookup cannot establish same-turn identity."""
    method = _tone_method()
    arguments = [arg.arg for arg in method.args.args]
    assert any(
        name in arguments
        for name in ("response", "turn", "turn_id", "response_id")
    ), "M377 RED: tone resolver has no response/turn correlation input"


def test_red_voice_calls_supply_same_turn_correlation_to_tone_resolution() -> None:
    """RED: tone resolution must receive a response/turn join."""
    cls = _desktop_class()
    calls = [
        node
        for method in cls.body
        if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef))
        for node in ast.walk(method)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "_adaptive_delivery_tone"
    ]
    assert calls, "M377 RED: no adaptive tone resolution call sites found"
    assert all(call.args or call.keywords for call in calls), (
        "M377 RED: one or more voice paths read a lateral tone "
        "without response correlation"
    )


def test_guard_adapter_hash_unchanged() -> None:
    path = ROOT / "app" / "runtime_ui_adapter.py"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == (
        "2afb8629a78800c64932e289a905a098bb1a32bd5952ec152b204e42924a08e1"
    )


def test_guard_desktop_does_not_instantiate_parallel_personality() -> None:
    source = DESKTOP.read_text(encoding="utf-8")
    assert "AdaptivePersonalityAuthority" not in source
    assert "AdaptivePersonalityProfile(" not in source
