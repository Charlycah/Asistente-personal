"""Contracts for the governed floating viewer desktop binding."""

from __future__ import annotations

import ast
from pathlib import Path


_UI_PATH = Path("app/desktop_ui.py")


def _run_method() -> ast.FunctionDef:
    tree = ast.parse(_UI_PATH.read_text(encoding="utf-8-sig"))

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            if node.name != "ROBYDesktopApp":
                continue
            for method in node.body:
                if isinstance(method, ast.FunctionDef):
                    if method.name == "run":
                        return method

    raise AssertionError("ROBYDesktopApp.run not found")


def _calls(method: ast.FunctionDef) -> list[ast.Call]:
    return [
        node
        for node in ast.walk(method)
        if isinstance(node, ast.Call)
    ]


def _call_name(call: ast.Call) -> str | None:
    function = call.func
    if isinstance(function, ast.Name):
        return function.id
    if isinstance(function, ast.Attribute):
        return function.attr
    return None


def test_run_constructs_existing_floating_viewer() -> None:
    method = _run_method()
    names = {_call_name(call) for call in _calls(method)}

    assert "DesktopGovernedFloatingImageViewer" in names


def test_viewer_receives_existing_tk_root() -> None:
    method = _run_method()
    constructors = [
        call
        for call in _calls(method)
        if _call_name(call) == "DesktopGovernedFloatingImageViewer"
    ]

    assert len(constructors) == 1

    keywords = {
        keyword.arg: keyword.value
        for keyword in constructors[0].keywords
    }

    assert isinstance(keywords.get("root"), ast.Name)
    assert keywords["root"].id == "root"
    assert isinstance(keywords.get("toolkit"), ast.Name)
    assert keywords["toolkit"].id == "tk"


def test_run_connects_existing_presenter_and_viewer() -> None:
    method = _run_method()
    connections = [
        call
        for call in _calls(method)
        if _call_name(call) == "connect_governed_floating_viewer"
    ]

    assert len(connections) >= 1

    keywords = {
        keyword.arg: keyword.value
        for keyword in connections[0].keywords
    }

    presenter = keywords.get("presenter")
    assert isinstance(presenter, ast.Attribute)
    assert isinstance(presenter.value, ast.Name)
    assert presenter.value.id == "self"
    assert presenter.attr == "external_image_presenter"

    assert "viewer" in keywords
    assert "artifacts" in keywords


def test_connection_uses_governed_visual_turn_artifacts() -> None:
    method = _run_method()
    connections = [
        call
        for call in _calls(method)
        if _call_name(call) == "connect_governed_floating_viewer"
    ]

    assert connections

    artifacts = next(
        (
            keyword.value
            for keyword in connections[0].keywords
            if keyword.arg == "artifacts"
        ),
        None,
    )

    assert isinstance(artifacts, ast.Attribute)
    assert isinstance(artifacts.value, ast.Attribute)
    assert isinstance(artifacts.value.value, ast.Name)
    assert artifacts.value.value.id == "visual_turn"
    assert artifacts.value.attr == "visual_companion"
    assert artifacts.attr == "artifacts"


def test_connection_remains_inside_ui_dispatch_callback() -> None:
    method = _run_method()
    dispatches = [
        call
        for call in _calls(method)
        if _call_name(call) == "dispatch_desktop_runtime_visual_render"
    ]

    assert dispatches

    dispatched_source = ast.unparse(dispatches[0])

    assert "connect_governed_floating_viewer" in dispatched_source
