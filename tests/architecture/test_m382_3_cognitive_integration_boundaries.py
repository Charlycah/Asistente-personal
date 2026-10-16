from __future__ import annotations

import ast
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _source(relative_path: str) -> str:
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def _tree(relative_path: str) -> ast.Module:
    return ast.parse(_source(relative_path), filename=relative_path)


def _class_method(
    relative_path: str,
    class_name: str,
    method_name: str,
) -> ast.FunctionDef:
    for node in _tree(relative_path).body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for member in node.body:
                if isinstance(member, ast.FunctionDef) and member.name == method_name:
                    return member
    raise AssertionError(f"missing {class_name}.{method_name} in {relative_path}")


def _qualified_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = _qualified_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    return ""


def _calls(node: ast.AST) -> tuple[str, ...]:
    return tuple(
        _qualified_name(item.func)
        for item in ast.walk(node)
        if isinstance(item, ast.Call)
    )


def _first_call_line(node: ast.AST, qualified_name: str) -> int:
    lines = [
        item.lineno
        for item in ast.walk(node)
        if isinstance(item, ast.Call) and _qualified_name(item.func) == qualified_name
    ]
    if not lines:
        raise AssertionError(f"missing call to {qualified_name}")
    return min(lines)


def test_desktop_uses_the_official_conversation_gateway_path() -> None:
    bootstrap = _source("app/desktop_bootstrap.py")
    adapter = _class_method(
        "app/runtime_ui_adapter.py",
        "LocalConversationUIAdapter",
        "_submit",
    )

    assert "runtime = official_runtime.conversation" in bootstrap
    assert "LocalConversationUIAdapter(runtime)" in bootstrap
    assert "self._brain.process" in _calls(adapter)


def test_official_gateway_is_the_single_runtime_delegation_boundary() -> None:
    submit = _class_method(
        "app/official_conversation_gateway.py",
        "OfficialConversationGateway",
        "submit",
    )
    calls = _calls(submit)

    assert "self._runtime.converse" in calls
    assert "self._runtime.process" not in calls
    assert "self._runtime.execute" not in calls


def test_turn_runs_pipeline_before_recording_personal_memory() -> None:
    converse = _class_method(
        "core/end_to_end_local_conversation/runtime.py",
        "EndToEndLocalConversation",
        "converse",
    )

    pipeline_line = _first_call_line(
        converse,
        "composition.conversation_pipeline.process",
    )
    memory_line = _first_call_line(converse, "memory_runtime.record")

    assert pipeline_line < memory_line


def test_prompt_context_is_applied_before_personal_memory() -> None:
    prepare = _class_method(
        "core/runtime_composition_root/preparation.py",
        "GovernedRuntimePreparation",
        "prepare",
    )

    context_line = _first_call_line(prepare, "context_runtime.enrich")
    memory_line = _first_call_line(prepare, "memory_runtime.enrich")

    assert context_line < memory_line


def test_pipeline_keeps_interception_before_provider_execution() -> None:
    process = _class_method(
        "core/governed_operational_conversation_pipeline/pipeline.py",
        "GovernedOperationalConversationPipeline",
        "process",
    )

    interception_line = _first_call_line(
        process,
        "self.operational_interceptor.intercept",
    )
    provider_line = _first_call_line(process, "self.provider_executor.execute")

    assert interception_line < provider_line


def test_runtime_composition_keeps_one_operational_interceptor() -> None:
    factory = _source("app/runtime_root_factory.py")
    root = _source("core/runtime_composition_root/root.py")

    assert "operational_interceptor=capability_registry" in factory
    assert "operational_interceptor=dependencies.operational_interceptor" in root


def test_governed_autonomy_cannot_execute_directly() -> None:
    autonomy = _source("core/governed_autonomy.py")

    assert "can_execute: bool = False" in autonomy
    assert "if self.can_execute:" in autonomy
    assert "governed autonomy decisions must not execute directly" in autonomy


def test_canonical_reflection_facade_does_not_schedule_reflection() -> None:
    reflection = _source("app/canonical_reflection_facade.py")

    assert "The facade does not schedule reflection or mutate state" in reflection
    assert "reflection observers cannot be operational" in reflection


def test_architecture_controls_never_access_credentials() -> None:
    source = Path(__file__).read_text(encoding="utf-8").casefold()
    forbidden_fragments = (
        ".roby/" + "credentials.json",
        "google_" + "client_secret",
        "activate_" + "credentials",
    )

    assert all(fragment not in source for fragment in forbidden_fragments)
