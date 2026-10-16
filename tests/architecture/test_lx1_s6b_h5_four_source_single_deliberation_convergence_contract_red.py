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


def _argument_names(node: ast.FunctionDef) -> set[str]:
    return {argument.arg for argument in node.args.args + node.args.kwonlyargs}


def _controller_submit_calls(node: ast.FunctionDef) -> list[ast.Call]:
    calls = []
    for candidate in ast.walk(node):
        if not isinstance(candidate, ast.Call):
            continue
        function = candidate.func
        if (
            not isinstance(function, ast.Attribute)
            or function.attr != "submit_with_visual_companion"
        ):
            continue
        owner = function.value
        if not isinstance(owner, ast.Attribute) or owner.attr != "controller":
            continue
        calls.append(candidate)
    return calls


def test_s6b_ordinary_submit_accepts_all_four_source_channels() -> None:
    submit = _nested_function("submit")
    names = _argument_names(submit)

    required = {
        "explicit_document_ids",
        "explicit_sources",
        "explicit_evidence_references",
        "integrated_visual_context",
    }
    assert required <= names, (
        "RED: ordinary Desktop submit cannot receive all four certified source "
        f"channels together; missing={sorted(required - names)}"
    )


def test_s6b_worker_forwards_all_four_channels_in_one_controller_submit() -> None:
    submit = _nested_function("submit")
    calls = _controller_submit_calls(submit)

    assert len(calls) == 1, (
        "RED: one ordinary explicit-evidence turn must reach exactly one "
        "DesktopConversationController.submit_with_visual_companion call"
    )
    keywords = {keyword.arg for keyword in calls[0].keywords}
    required = {
        "explicit_document_ids",
        "explicit_sources",
        "explicit_evidence_references",
        "integrated_visual_context",
    }
    assert required <= keywords, (
        "RED: the single Desktop controller call does not carry all four "
        f"source channels; missing={sorted(required - keywords)}"
    )


def test_s6b_controller_contract_preserves_single_adapter_submission() -> None:
    source = textwrap.dedent(
        inspect.getsource(
            desktop_ui.DesktopConversationController.submit_with_visual_companion
        )
    )
    tree = ast.parse(source)
    function = tree.body[0]
    names = _argument_names(function)

    required = {
        "explicit_document_ids",
        "explicit_sources",
        "explicit_evidence_references",
        "integrated_visual_context",
    }
    assert required <= names

    adapter_calls = []
    for candidate in ast.walk(function):
        if not isinstance(candidate, ast.Call):
            continue
        target = candidate.func
        if (
            isinstance(target, ast.Name)
            and target.id == "submit_visual"
        ):
            adapter_calls.append(candidate)

    composite_calls = [
        call
        for call in adapter_calls
        if {
            "explicit_document_ids",
            "explicit_sources",
            "explicit_evidence_references",
            "integrated_visual_context",
        }
        <= {keyword.arg for keyword in call.keywords}
    ]
    assert len(composite_calls) == 1, (
        "RED: four-source evidence must converge through one existing adapter "
        "submission, not source-specific deliberations"
    )


def test_s6b_desktop_creates_no_parallel_multisource_cognitive_authority() -> None:
    source = inspect.getsource(desktop_ui.ROBYDesktopApp)
    forbidden = (
        "FourSourceManager(",
        "MultisourceBrain(",
        "MultimodalBrain(",
        "VisualReasoningBrain(",
        "CompositeDeliberationManager(",
        "SourceSpecificReasoner(",
    )
    assert all(item not in source for item in forbidden)
