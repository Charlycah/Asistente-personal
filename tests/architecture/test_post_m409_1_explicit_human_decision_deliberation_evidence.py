from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest

from core.explicit_human_decision_deliberation import (
    ExplicitDecisionDeliberationStatus,
    ExplicitHumanDecisionDeliberationEvidenceProducer,
)

PRODUCER = ExplicitHumanDecisionDeliberationEvidenceProducer()


@pytest.mark.parametrize(
    ("text", "expected"),
    (
        ("¿A o B?", ("A", "B")),
        ("¿Conviene A o B?", ("A", "B")),
        ("¿Qué me conviene: A o B?", ("A", "B")),
        ("QUE ME CONVIENE: A O B?", ("A", "B")),
        ("Entre A y B, ¿cuál conviene?", ("A", "B")),
        ("Entre A y B, cual conviene?", ("A", "B")),
        ("Tengo dos opciones: A o B.", ("A", "B")),
        ("Tengo tres opciones: A, B o C.", ("A", "B", "C")),
        ("Tengo 4 opciones: A, B, C o D.", ("A", "B", "C", "D")),
        (
            "Tengo cinco opciones: A, B, C, D o E.",
            ("A", "B", "C", "D", "E"),
        ),
        ("¿Comprar o no comprar?", ("Comprar", "no comprar")),
    ),
)
def test_v1_extracts_only_approved_explicit_forms(text, expected):
    evidence = PRODUCER.analyze(text)

    assert evidence.status is ExplicitDecisionDeliberationStatus.EXPLICIT
    assert tuple(item.raw_text for item in evidence.alternatives) == expected
    assert tuple(item.normalized_text for item in evidence.alternatives) == expected


@pytest.mark.parametrize(
    "text",
    (
        "",
        "   ",
        "A o B.",
        "Puede ser A o B.",
        "Creo que fue lunes o martes.",
        "Dame opciones.",
        "¿Qué hago?",
        "Pensaba en A. Aunque quizá B.",
        "A parece mejor, pero B también.",
    ),
)
def test_v1_abstains_from_non_deliberative_or_implicit_forms(text):
    evidence = PRODUCER.analyze(text)

    assert evidence.status is ExplicitDecisionDeliberationStatus.NOT_DELIBERATION
    assert evidence.alternatives == ()


def test_v1_abstains_when_simple_binary_split_crosses_sentence_boundaries():
    text = (
        "Una estación recibe datos de temperatura del sensor T. "
        "T dejó de responder. "
        "No sabemos si existen otros sensores o fuentes. "
        "¿Qué podés concluir?"
    )

    evidence = PRODUCER.analyze(text)

    assert evidence.status is ExplicitDecisionDeliberationStatus.NOT_DELIBERATION
    assert evidence.alternatives == ()


@pytest.mark.parametrize(
    "text",
    (
        "¿Qué me conviene?",
        "¿Qué opciones tengo?",
        "¿Cuáles son mis opciones?",
        "¿A o qué otra cosa?",
        "¿A o A?",
        "¿A o B o C?",
        "¿A, después de X, o B?",
        "Tengo tres opciones: A o B.",
        "Tengo dos opciones: A, B o C.",
    ),
)
def test_v1_reports_insufficient_options_without_exposing_partial_choices(text):
    evidence = PRODUCER.analyze(text)

    assert evidence.status is ExplicitDecisionDeliberationStatus.INSUFFICIENT_OPTIONS
    assert evidence.alternatives == ()


@pytest.mark.parametrize(
    "text",
    (
        "¿A o el otro?",
        "¿A o la otra?",
        "¿esto o aquello?",
        "¿ese o esa?",
    ),
)
def test_v1_reports_ambiguous_references_without_context_resolution(text):
    evidence = PRODUCER.analyze(text)

    assert evidence.status is ExplicitDecisionDeliberationStatus.AMBIGUOUS
    assert evidence.alternatives == ()
    assert evidence.resolves_context is False


def test_v1_spans_are_exact_ordered_non_overlapping_and_exclude_delimiters():
    text = "¿Qué me conviene: viajar el viernes o viajar el sábado?"
    evidence = PRODUCER.analyze(text)

    previous_end = -1
    for ordinal, alternative in enumerate(evidence.alternatives):
        assert alternative.ordinal == ordinal
        assert 0 <= alternative.start_offset < alternative.end_offset <= len(text)
        assert alternative.start_offset >= previous_end
        extracted = text[alternative.start_offset : alternative.end_offset]
        assert extracted == alternative.raw_text
        assert "¿" not in alternative.raw_text
        assert "?" not in alternative.raw_text
        previous_end = alternative.end_offset


def test_v1_whitespace_normalization_never_rewrites_raw_source_span():
    text = "¿Qué me conviene:   comprar   la mini-PC   o   esperar   ?"
    evidence = PRODUCER.analyze(text)

    assert evidence.status is ExplicitDecisionDeliberationStatus.EXPLICIT
    assert evidence.alternatives[0].raw_text == "comprar   la mini-PC"
    assert evidence.alternatives[0].normalized_text == "comprar la mini-PC"
    assert evidence.alternatives[1].raw_text == "esperar"
    assert evidence.alternatives[1].normalized_text == "esperar"


def test_v1_does_not_complete_ellipsis_or_propagate_subjects():
    evidence = PRODUCER.analyze("¿Comprar la mini-PC ahora o esperar?")

    assert evidence.status is ExplicitDecisionDeliberationStatus.EXPLICIT
    assert evidence.alternatives[1].raw_text == "esperar"
    assert evidence.alternatives[1].normalized_text == "esperar"


def test_v1_same_input_is_structurally_deterministic():
    text = "Tengo tres opciones: auto, tren o avión."

    first = PRODUCER.analyze(text)
    second = PRODUCER.analyze(text)

    assert first == second
    assert first.source_fingerprint == second.source_fingerprint


def test_v1_order_is_source_order_not_preference():
    evidence = PRODUCER.analyze("¿B o A?")

    assert tuple(item.ordinal for item in evidence.alternatives) == (0, 1)
    assert tuple(item.raw_text for item in evidence.alternatives) == ("B", "A")


def test_v1_evidence_declares_governed_non_authoritative_limits():
    evidence = PRODUCER.analyze("¿A o B?")

    assert evidence.read_only is True
    assert evidence.advisory_only is False
    assert evidence.generates_alternatives is False
    assert evidence.resolves_context is False
    assert evidence.uses_llm is False
    assert evidence.persists_results is False
    assert evidence.executes_actions is False
    assert evidence.grants_authority is False
    assert evidence.starts_background_process is False


def test_v1_module_has_no_prohibited_integration_dependencies():
    module_file = inspect.getfile(ExplicitHumanDecisionDeliberationEvidenceProducer)
    module_path = Path(module_file)
    source = module_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    imported_names = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imports = imported_modules | imported_names

    prohibited = {
        "sqlite3",
        "threading",
        "asyncio",
        "core.governed_decision_advisory",
        "core.intelligent_personal_organization",
        "core.productive_organization_evidence_projection",
        "application.brain.dialogue_ambiguity",
    }
    assert imports.isdisjoint(prohibited)
    assert "OpenAI" not in source
    assert "llm" not in source.casefold() or "uses_llm" in source
    assert "CanonicalDecisionFacade" not in source
    assert "GovernedDecisionOption" not in source


def test_v1_has_no_runtime_or_filesystem_side_effect_api():
    source = inspect.getsource(ExplicitHumanDecisionDeliberationEvidenceProducer)

    for forbidden in (
        "open(",
        "Path(",
        "requests.",
        "socket.",
        "subprocess.",
        "save(",
        "write_text(",
        "write_bytes(",
    ):
        assert forbidden not in source
