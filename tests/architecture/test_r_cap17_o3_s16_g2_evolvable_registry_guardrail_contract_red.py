"""G2 RED: reconcile S1 historical identity with evolvable root masters.

No product change, no rewrite of historical evidence, no silent hash refresh.
"""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
S1 = ROOT / "tests/architecture/test_r_doc_master_consolidation_s1_contract_red.py"
ROOT_1 = ROOT / (
    "tests/architecture/"
    "test_r_doc_root_1_governed_historical_root_archival_contract_red.py"
)
REGISTRY = "ROBY_XI_2_MASTER_CAPABILITY_REGISTRY.md"
HISTORICAL_SHA256 = (
    "973b41c614b401915d0429bb3206f742fbfc1057779fd8fc57786130b6eeb320"
)


def _assignment(tree: ast.Module, name: str) -> ast.AST:
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == name
            for target in node.targets
        ):
            return node.value
    raise AssertionError(f"Missing governed contract assignment: {name}")


def test_g2_original_s1_hash_is_preserved_as_historical_evidence() -> None:
    tree = ast.parse(S1.read_text(encoding="utf-8"))
    values = ast.literal_eval(_assignment(tree, "EVOLVABLE_UNCHANGED"))
    assert values[REGISTRY] == HISTORICAL_SHA256


def test_g2_root_1_explicitly_declares_registry_evolvable() -> None:
    tree = ast.parse(ROOT_1.read_text(encoding="utf-8"))
    declaration = _assignment(tree, "EVOLVABLE_ROOT_AUTHORITIES")
    assert isinstance(declaration, ast.Call)
    assert isinstance(declaration.func, ast.Name)
    assert declaration.func.id == "frozenset"
    evolvable = ast.literal_eval(declaration.args[0])
    protected = ast.literal_eval(_assignment(tree, "BYTE_PROTECTED_ROOT"))
    assert REGISTRY in evolvable
    assert REGISTRY not in protected
    assert (ROOT / REGISTRY).is_file()


def test_g2_s1_current_registry_guardrail_does_not_freeze_historical_hash() -> None:
    """Intentional RED until GREEN separates S1 evidence from live authority.

    The S1 original digest must remain recorded, but no live-root SHA assertion
    may require that historical digest for a governed evolvable master.
    """
    tree = ast.parse(S1.read_text(encoding="utf-8"))
    guardrail = next(
        node for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "test_s1_preserves_unchanged_evolvable_masters"
    )
    assert not any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "_sha256"
        for node in ast.walk(guardrail)
    ), (
        "G2 RED: S1 live-root guardrail still compares a governed evolvable "
        "registry against the frozen S1 digest"
    )
