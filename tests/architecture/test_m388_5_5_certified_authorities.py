from __future__ import annotations

import ast
from pathlib import Path

from app.cognitive_authority_map import CognitiveAuthorityMap
from app.cognitive_operational_inventory import CognitiveAuthority

ROOT = Path(__file__).resolve().parents[2]


def test_m388_5_5_every_authority_has_one_canonical_primary() -> None:
    snapshot = CognitiveAuthorityMap().snapshot
    assert len(snapshot.assignments) == len(CognitiveAuthority)
    authorities = {item.authority for item in snapshot.assignments}
    assert len(authorities) == len(CognitiveAuthority)
    assert all(item.primary.strip() for item in snapshot.assignments)


def test_m388_5_5_primary_components_are_unique_per_authority() -> None:
    assignments = CognitiveAuthorityMap().snapshot.assignments
    assert len({item.primary for item in assignments}) == len(assignments)


def test_m388_5_5_shadow_components_do_not_become_primary() -> None:
    snapshot = CognitiveAuthorityMap().snapshot
    shadows = {key for item in snapshot.assignments for key in item.shadow}
    primaries = {item.primary for item in snapshot.assignments}
    assert shadows.isdisjoint(primaries)


def test_m388_5_5_canonical_core_constructor_remains_only_on_line_52() -> None:
    path = ROOT / "app" / "official_conversation_gateway.py"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    lines = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "CanonicalCognitiveCore"
    ]
    assert lines == [52]


def test_m388_5_5_gateway_has_no_second_cognitive_core_constructor() -> None:
    path = ROOT / "app" / "official_conversation_gateway.py"
    text = path.read_text(encoding="utf-8")
    assert text.count("CanonicalCognitiveCore(") == 1
