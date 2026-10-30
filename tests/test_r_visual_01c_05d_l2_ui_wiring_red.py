from __future__ import annotations

import ast
from pathlib import Path


UI_PATH = Path("app/desktop_ui.py")
COORDINATOR_PATH = Path(
    "app/desktop_governed_image_preview_coordinator.py"
)


def _tree(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8-sig"))


def _imports(tree: ast.Module) -> set[str]:
    return {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    }


def _calls(tree: ast.AST, name: str) -> list[ast.Call]:
    return [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == name
    ]


def _run_method(tree: ast.Module) -> ast.FunctionDef:
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.FunctionDef)
            and node.name == "run"
        ):
            return node
    raise AssertionError("Desktop run method missing")


def _named_function(
    parent: ast.AST,
    name: str,
) -> ast.FunctionDef:
    for node in ast.walk(parent):
        if (
            isinstance(node, ast.FunctionDef)
            and node.name == name
        ):
            return node
    raise AssertionError(f"Function missing: {name}")


def _method_calls(
    node: ast.AST,
    method: str,
) -> list[ast.Call]:
    return [
        item
        for item in ast.walk(node)
        if isinstance(item, ast.Call)
        and isinstance(item.func, ast.Attribute)
        and item.func.attr == method
    ]


def test_ui_imports_governed_async_components():
    imports = _imports(_tree(UI_PATH))

    assert "GovernedImagePreviewCoordinator" in imports
    assert "fetch_desktop_governed_preview" in imports
    assert "ThreadPoolExecutor" in imports


def test_ui_constructs_coordinator_inside_run():
    run = _run_method(_tree(UI_PATH))

    assert _calls(
        run,
        "GovernedImagePreviewCoordinator",
    )


def test_visual_dispatch_uses_async_coordinator():
    run = _run_method(_tree(UI_PATH))
    worker = _named_function(run, "worker")

    bridge = next(
        node for node in ast.walk(run)
        if isinstance(node, ast.ClassDef)
        and node.name == "PreviewBridge"
    )
    bridge_open = _named_function(bridge, "open")
    assert any(
        isinstance(call.func.value, ast.Name)
        and call.func.value.id == "preview_coordinator"
        for call in _method_calls(bridge_open, "present")
    )
    assert not _calls(
        worker,
        "present_desktop_runtime_visuals",
    )


def test_application_close_releases_preview_executor():
    run = _run_method(_tree(UI_PATH))
    close = _named_function(run, "close")

    assert any(
        isinstance(call.func.value, ast.Name)
        and call.func.value.id == "preview_coordinator"
        for call in _method_calls(close, "shutdown")
    )


def test_coordinator_passes_transport_limits_by_keyword():
    tree = _tree(COORDINATOR_PATH)
    coordinator = next(
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef)
        and node.name == "GovernedImagePreviewCoordinator"
    )
    submit_method = _named_function(coordinator, "_submit")
    submits = _method_calls(submit_method, "submit")

    assert submits
    assert any(
        len(call.args) >= 4
        and isinstance(call.args[2], ast.Attribute)
        and call.args[2].attr == "_timeout"
        and isinstance(call.args[3], ast.Attribute)
        and call.args[3].attr == "_max_bytes"
        for call in submits
    )
