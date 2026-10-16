from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _source(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def _class_method(source: str, class_name: str, method_name: str) -> ast.FunctionDef:
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for member in node.body:
                if isinstance(member, ast.FunctionDef) and member.name == method_name:
                    return member
    raise AssertionError(f"{class_name}.{method_name} is missing")


def _arguments(method: ast.FunctionDef) -> set[str]:
    return {argument.arg for argument in method.args.args + method.args.kwonlyargs}


def test_red_protected_runtime_ui_adapter_remains_byte_identical() -> None:
    adapter = ROOT / "app/runtime_ui_adapter.py"
    assert hashlib_sha256(adapter) == (
        "2afb8629a78800c64932e289a905a098bb1a32bd5952ec152b204e42924a08e1"
    )


def test_red_root_adds_exterior_same_turn_visual_composition() -> None:
    source = _source("app/desktop_bootstrap.py")
    assert "SameTurnVisualUIAdapterComposition" in source
    assert "same_turn_visual" in source.casefold()


def test_red_exterior_composition_reads_gateway_owned_applied_result() -> None:
    source = _source("app/same_turn_governed_visual_result_exposure.py")
    assert "last_applied_owner_turn_result" in source
    assert "execute_applied_conversational_intelligence" not in source


def test_red_exterior_composition_delegates_owner_turn_once() -> None:
    source = _source("app/same_turn_governed_visual_result_exposure.py")
    tree = ast.parse(source)
    method = _class_method(
        source,
        "SameTurnVisualUIAdapterComposition",
        "submit_text_with_visual_companion",
    )
    segment = ast.get_source_segment(source, method) or ""
    assert segment.count("submit_text(") == 1
    assert "process_with_visual_result(" not in segment
    assert "execute_applied" not in segment
    assert isinstance(tree, ast.Module)


def test_red_controller_visual_companion_preserves_explicit_context() -> None:
    source = _source("app/desktop_ui.py")
    method = _class_method(
        source,
        "DesktopConversationController",
        "submit_with_visual_companion",
    )
    assert {
        "explicit_document_ids",
        "explicit_sources",
        "explicit_evidence_references",
        "integrated_visual_context",
    } <= _arguments(method)
    segment = ast.get_source_segment(source, method) or ""
    for name in (
        "explicit_document_ids",
        "explicit_sources",
        "explicit_evidence_references",
        "integrated_visual_context",
    ):
        assert name in segment


def test_red_tk_worker_reaches_existing_visual_controller_seam() -> None:
    source = _source("app/desktop_ui.py")
    assert "self.controller.submit_with_visual_companion(" in source


def test_red_tk_worker_does_not_add_second_thread_or_mainloop() -> None:
    source = _source("app/desktop_ui.py")
    assert source.count("Thread(target=worker, daemon=True).start()") == 1
    assert source.count("root.mainloop()") == 1


def test_red_visual_completion_reuses_existing_ui_dispatcher() -> None:
    source = _source("app/desktop_ui.py")
    assert "ui_dispatcher = UIThreadDispatcher()" in source
    assert "dispatch_desktop_runtime_visual_render(" in source
    assert "ui_dispatcher" in source


def test_red_root_reuses_existing_external_image_presenter() -> None:
    source = _source("app/desktop_bootstrap.py")
    assert "DesktopExternalImagePresenter" in source
    assert "desktop_external_image_presenter" in source
    assert "ROBYDesktopApp(" in source


def test_red_visual_presentation_reuses_certified_runtime_binding() -> None:
    source = _source("app/desktop_ui.py")
    assert "bind_applied_result_to_desktop" in source
    assert "present_desktop_runtime_visuals" in source
    assert "dispatch_desktop_runtime_visual_render" in source


def test_red_visual_failure_does_not_reexecute_owner_turn() -> None:
    source = _source("app/desktop_ui.py")
    worker_start = source.index("            def worker() -> None:")
    worker_end = source.index(
        "            Thread(target=worker, daemon=True).start()",
        worker_start,
    )
    worker = source[worker_start:worker_end]
    assert worker.count("self.controller.submit_with_visual_companion(") == 1
    assert worker.count("self.controller.submit(") == 0


def test_red_no_new_visual_authority_module_is_created() -> None:
    forbidden = (
        "desktop_visual_manager.py",
        "desktop_visual_agent.py",
        "desktop_visual_planner.py",
        "desktop_visual_executor.py",
    )
    for relative in forbidden:
        assert not (ROOT / "app" / relative).exists()


def test_red_protected_schemas_and_unified_brain_remain_unchanged() -> None:
    brain = ROOT / "app/unified_brain.py"
    assert (
        hashlib_sha256(brain)
        == "05f4c65fbb8a1478f9117b9b1de8c450d15211a257aa4835b8123a6babbc1750"
    )
    turn_source = _source("core/end_to_end_local_conversation/models.py")
    ui_source = _source("app/ui_adapter.py")
    assert "class LocalConversationTurn" in turn_source
    assert "class UIResponse" in ui_source


def test_red_does_not_add_reachability_or_freshness_scope() -> None:
    source = _source("app/desktop_bootstrap.py") + _source("app/desktop_ui.py")
    assert "EXTERNAL_IMAGE_NATURAL_LANGUAGE_REACHABILITY" not in source
    assert "EXTERNAL_IMAGE_FRESHNESS_ORDERING" not in source


def hashlib_sha256(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()
