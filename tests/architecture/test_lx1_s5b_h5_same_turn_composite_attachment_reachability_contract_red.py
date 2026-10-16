from __future__ import annotations

import ast
import inspect
import textwrap

from app import desktop_ui


def _run_tree() -> ast.FunctionDef:
    source = textwrap.dedent(inspect.getsource(desktop_ui.ROBYDesktopApp.run))
    tree = ast.parse(source)
    return tree.body[0]


def _nested_function(name: str) -> ast.FunctionDef:
    run = _run_tree()
    for node in run.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"RED: ROBYDesktopApp.run lacks nested {name}()")


def _source(node: ast.AST) -> str:
    return ast.unparse(node)


def test_s5b_attachment_selection_does_not_start_an_ordinary_turn() -> None:
    attach_source = _source(_nested_function("attach_file"))

    assert "submit(" not in attach_source, (
        "RED: attaching a document or image still starts its own ordinary turn"
    )


def test_s5b_attachment_selection_retains_only_existing_canonical_outputs() -> None:
    attach_source = _source(_nested_function("attach_file"))

    assert "record.document_id" in attach_source
    assert "visual_context" in attach_source
    assert "stored.image_id" in attach_source
    assert "analyze_image_for_cognitive_convergence(" in attach_source
    assert "image_bytes=" in attach_source


def test_s5b_next_ordinary_submit_can_carry_document_and_visual_together() -> None:
    submit_source = _source(_nested_function("submit"))

    assert "explicit_document_ids=" in submit_source
    assert "integrated_visual_context=" in submit_source


def test_s5b_run_has_ephemeral_attachment_state_consumed_one_shot() -> None:
    attach = _nested_function("attach_file")
    submit = _nested_function("submit")

    attach_nonlocal = {
        name
        for node in ast.walk(attach)
        if isinstance(node, ast.Nonlocal)
        for name in node.names
    }
    submit_nonlocal = {
        name
        for node in ast.walk(submit)
        if isinstance(node, ast.Nonlocal)
        for name in node.names
    }
    shared_turn_state = (attach_nonlocal & submit_nonlocal) - {"busy"}

    assert len(shared_turn_state) >= 2, (
        "RED: document and visual canonical outputs are not retained in "
        "shared ephemeral Desktop turn state"
    )

    cleared = set()
    for node in ast.walk(submit):
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name) or target.id not in shared_turn_state:
            continue
        value = node.value
        if isinstance(value, ast.Constant) and value.value is None:
            cleared.add(target.id)
        if isinstance(value, ast.Tuple) and not value.elts:
            cleared.add(target.id)

    assert shared_turn_state <= cleared, (
        "RED: staged attachment inputs are not consumed with one-shot "
        "clearing semantics"
    )


def test_s5b_desktop_creates_no_parallel_attachment_or_reasoning_authority() -> None:
    source = inspect.getsource(desktop_ui.ROBYDesktopApp)

    forbidden = (
        "AttachmentManager(",
        "AttachmentRepository(",
        "MultimodalAttachmentManager(",
        "CompositeTurnManager(",
        "PendingEvidenceManager(",
        "FileImageRepository(",
        "SQLiteDocumentRepository(",
        "OfficialVisionCore(",
        "GovernedVisualSemanticComposition(",
        "GovernedVisualCognitiveContextBridge(",
        "CognitiveRuntimeOrchestrator(",
        "OfficialGovernedReasoningRuntimeGateway(",
        "explicit_image_ids",
    )
    assert all(item not in source for item in forbidden)
