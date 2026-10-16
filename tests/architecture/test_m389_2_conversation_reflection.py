from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from core.cognitive_maturity import (
    CognitiveCycleNodeRecord,
    CognitiveCycleNodeState,
    ConversationReflectionAuthority,
    ConversationReflectionStatus,
    EpistemicLevel,
    create_canonical_cognitive_cycle,
    create_cognitive_turn_dossier,
)

ROOT = Path(__file__).resolve().parents[2]


def _dossier():
    cycle = create_canonical_cognitive_cycle(
        "m389-2-turn",
        records=(
            CognitiveCycleNodeRecord(
                node_id="conversation_ingress",
                state=CognitiveCycleNodeState.PARTICIPATED,
                evidence_codes=("synthetic_input",),
            ),
        ),
    )
    return create_cognitive_turn_dossier(cycle)


def test_m389_2_has_one_read_only_reflection_authority() -> None:
    authority = ConversationReflectionAuthority()
    assert authority.authority_id == "conversation_reflection"


def test_m389_2_report_is_structured_and_private() -> None:
    report = ConversationReflectionAuthority().reflect(_dossier())
    assert report.status is ConversationReflectionStatus.COMPLETE
    assert report.read_only is True
    assert report.grants_authority is False
    assert report.contains_conversation_content is False


def test_m389_2_reflection_creates_no_memory_or_learning() -> None:
    report = ConversationReflectionAuthority().reflect(_dossier())
    assert report.creates_memory is False
    assert report.creates_learning_candidate is False


def test_m389_2_reflection_preserves_epistemic_categories() -> None:
    report = ConversationReflectionAuthority().reflect(_dossier())
    assert report.epistemic_levels == ()
    assert EpistemicLevel.FACT not in report.epistemic_levels


def test_m389_2_same_dossier_produces_same_reflection() -> None:
    authority = ConversationReflectionAuthority()
    dossier = _dossier()
    assert authority.reflect(dossier) == authority.reflect(dossier)


def test_m389_2_report_is_immutable() -> None:
    report = ConversationReflectionAuthority().reflect(_dossier())
    with pytest.raises(FrozenInstanceError):
        report.objective_code = "changed"


def test_m389_2_failure_degrades_without_authority() -> None:
    class BrokenAuthority(ConversationReflectionAuthority):
        def reflect(self, dossier, assessments=()):
            raise RuntimeError("synthetic failure")

    report = BrokenAuthority().reflect_safely(_dossier())
    assert report.status is ConversationReflectionStatus.DEGRADED
    assert report.grants_authority is False
    assert report.risk_codes == ("reflection_engine_failure",)


def test_m389_2_does_not_reference_credentials() -> None:
    path = ROOT / "core" / "cognitive_maturity" / "conversation_reflection.py"
    source = path.read_text(encoding="utf-8")
    assert "credentials.json" not in source
    assert ".roby" not in source


def test_m389_2_constructor_remains_only_on_line_52() -> None:
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
