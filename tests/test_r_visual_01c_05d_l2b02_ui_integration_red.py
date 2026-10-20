from pathlib import Path
import ast


UI_PATH = Path("app/desktop_ui.py")


def _run_tree():
    tree = ast.parse(UI_PATH.read_text(encoding="utf-8-sig"))
    app = next(
        node for node in tree.body
        if isinstance(node, ast.ClassDef)
        and node.name == "ROBYDesktopApp"
    )
    return next(
        node for node in app.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "run"
    )


def _calls(node):
    return [
        call
        for call in ast.walk(node)
        if isinstance(call, ast.Call)
    ]


def _attribute_calls(node, name):
    return [
        call for call in _calls(node)
        if isinstance(call.func, ast.Attribute)
        and call.func.attr == name
    ]


def test_ui_imports_preview_coordinator_and_adapter():
    tree = ast.parse(UI_PATH.read_text(encoding="utf-8-sig"))
    imports = {
        alias.name
        for node in tree.body
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    }
    assert "GovernedImagePreviewCoordinator" in imports
    assert "fetch_desktop_governed_preview" in imports
    assert "ThreadPoolExecutor" in imports


def test_run_constructs_preview_coordinator():
    run = _run_tree()
    assert any(
        isinstance(call.func, ast.Name)
        and call.func.id == "GovernedImagePreviewCoordinator"
        for call in _calls(run)
    )


def test_worker_uses_async_preview_presentation():
    run = _run_tree()

    worker = next(
        node for node in ast.walk(run)
        if isinstance(node, ast.FunctionDef)
        and node.name == "worker"
    )

    bridge = next(
        node for node in ast.walk(run)
        if isinstance(node, ast.ClassDef)
        and node.name == "PreviewBridge"
    )

    bridge_open = next(
        node for node in bridge.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "open"
    )

    dispatches = [
        call for call in _calls(worker)
        if isinstance(call.func, ast.Name)
        and call.func.id == "dispatch_desktop_runtime_visual_render"
    ]

    assert len(dispatches) == 1

    dispatched = dispatches[0]
    assert len(dispatched.args) == 2

    callback = dispatched.args[1]
    assert isinstance(callback, ast.Lambda)

    connections = [
        call for call in _calls(callback)
        if isinstance(call.func, ast.Name)
        and call.func.id == "connect_governed_floating_viewer"
    ]

    assert len(connections) == 1

    keywords = {
        keyword.arg: keyword.value
        for keyword in connections[0].keywords
    }

    assert ast.unparse(keywords["viewer"]) == "preview_bridge"
    assert ast.unparse(keywords["artifacts"]) == (
        "visual_turn.visual_companion.artifacts"
    )

    presentations = [
        call for call in _attribute_calls(bridge_open, "present")
        if isinstance(call.func.value, ast.Name)
        and call.func.value.id == "preview_coordinator"
    ]

    assert len(presentations) == 1
    assert len(presentations[0].args) == 1
    assert ast.unparse(presentations[0].args[0]) == "artifacts"

    assert not any(
        isinstance(call.func, ast.Name)
        and call.func.id == "present_desktop_runtime_visuals"
        for call in _calls(run)
    )


def test_close_shuts_down_preview_coordinator():
    run = _run_tree()
    close = next(
        node for node in ast.walk(run)
        if isinstance(node, ast.FunctionDef)
        and node.name == "close"
    )
    assert any(
        isinstance(call.func, ast.Attribute)
        and isinstance(call.func.value, ast.Name)
        and call.func.value.id == "preview_coordinator"
        and call.func.attr == "shutdown"
        for call in _calls(close)
    )


def test_manual_viewer_close_invalidates_preview():
    run = _run_tree()
    assert any(
        isinstance(call.func, ast.Attribute)
        and isinstance(call.func.value, ast.Name)
        and call.func.value.id == "preview_coordinator"
        and call.func.attr == "cancel"
        for call in _calls(run)
    )
