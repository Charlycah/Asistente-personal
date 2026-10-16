from __future__ import annotations

import ast
import inspect
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from core.explicit_deliberation_decision_option_adapter import (
    ExplicitDeliberationDecisionOptionAdapter,
)
from core.explicit_human_decision_deliberation import (
    ExplicitDecisionDeliberationStatus,
    ExplicitHumanDecisionDeliberationEvidenceProducer,
)

PRODUCER = ExplicitHumanDecisionDeliberationEvidenceProducer()
ADAPTER = ExplicitDeliberationDecisionOptionAdapter()


def _adapt(text: str):
    return ADAPTER.adapt(PRODUCER.analyze(text))


@pytest.mark.parametrize(
    ("text", "expected_titles"),
    (
        ("¿A o B?", ("A", "B")),
        ("Tengo tres opciones: A, B o C.", ("A", "B", "C")),
        (
            "Tengo cinco opciones: A, B, C, D o E.",
            ("A", "B", "C", "D", "E"),
        ),
    ),
)
def test_adapter_maps_every_explicit_alternative_one_to_one(text, expected_titles):
    adaptation = _adapt(text)

    assert tuple(option.title for option in adaptation.options) == expected_titles
    assert len(adaptation.options) == len(adaptation.bindings) == len(expected_titles)


def test_adapter_uses_normalized_text_without_rewriting_evidence():
    evidence = PRODUCER.analyze(
        "¿Qué me conviene:   comprar   la mini-PC   o   esperar   ?"
    )
    before = evidence

    adaptation = ADAPTER.adapt(evidence)

    assert adaptation.options[0].title == "comprar la mini-PC"
    assert adaptation.options[1].title == "esperar"
    assert evidence == before
    assert evidence.alternatives[0].raw_text == "comprar   la mini-PC"


def test_adapter_preserves_source_order_without_encoding_preference():
    adaptation = _adapt("¿B o A?")

    assert tuple(option.title for option in adaptation.options) == ("B", "A")
    assert all(option.explicit_preference == 0.0 for option in adaptation.options)


def test_adapter_leaves_all_optional_evidence_links_neutral():
    adaptation = _adapt("¿A o B?")

    for option in adaptation.options:
        assert option.organization_item_id is None
        assert option.scenario_hypothesis_id is None
        assert option.causal_relation_id is None
        assert option.explicit_preference == 0.0


def test_adapter_option_ids_are_deterministic_unique_opaque_sha256_ids():
    first = _adapt("¿A o B?")
    second = _adapt("¿A o B?")

    first_ids = tuple(option.option_id for option in first.options)
    second_ids = tuple(option.option_id for option in second.options)
    assert first_ids == second_ids
    assert len(set(first_ids)) == len(first_ids)
    for option_id in first_ids:
        prefix = "explicit-deliberation-option-"
        assert option_id.startswith(prefix)
        digest = option_id.removeprefix(prefix)
        assert len(digest) == 64
        assert all(character in "0123456789abcdef" for character in digest)


def test_same_title_in_different_deliberations_has_different_identity():
    first = _adapt("¿viajar viernes o viajar sábado?")
    second = _adapt("¿viajar viernes o viajar domingo?")

    assert first.options[0].title == second.options[0].title == "viajar viernes"
    assert first.options[0].option_id != second.options[0].option_id


def test_different_ordinals_in_same_evidence_have_different_identity():
    adaptation = _adapt("¿A o B?")

    assert adaptation.options[0].option_id != adaptation.options[1].option_id


def test_bindings_preserve_exact_external_provenance_one_to_one():
    evidence = PRODUCER.analyze("¿Qué me conviene: viajar viernes o viajar sábado?")
    adaptation = ADAPTER.adapt(evidence)

    assert adaptation.source_fingerprint == evidence.source_fingerprint
    for option, binding, alternative in zip(
        adaptation.options,
        adaptation.bindings,
        evidence.alternatives,
        strict=True,
    ):
        assert binding.option_id == option.option_id
        assert binding.source_fingerprint == evidence.source_fingerprint
        assert binding.alternative_ordinal == alternative.ordinal
        assert binding.source_start_offset == alternative.start_offset
        assert binding.source_end_offset == alternative.end_offset
        assert (
            evidence.source_text[
                binding.source_start_offset : binding.source_end_offset
            ]
            == alternative.raw_text
        )


def test_same_evidence_produces_same_complete_adaptation():
    evidence = PRODUCER.analyze("Tengo tres opciones: auto, tren o avión.")

    assert ADAPTER.adapt(evidence) == ADAPTER.adapt(evidence)


@pytest.mark.parametrize(
    "text",
    (
        "¿Qué hago?",
        "¿A o el otro?",
        "¿A o A?",
    ),
)
def test_adapter_rejects_every_non_explicit_evidence_state(text):
    evidence = PRODUCER.analyze(text)
    assert evidence.status is not ExplicitDecisionDeliberationStatus.EXPLICIT

    with pytest.raises(ValueError):
        ADAPTER.adapt(evidence)


def test_adaptation_and_bindings_are_frozen():
    adaptation = _adapt("¿A o B?")

    with pytest.raises(FrozenInstanceError):
        adaptation.source_fingerprint = "changed"  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        adaptation.bindings[0].alternative_ordinal = 99  # type: ignore[misc]


def test_adapter_declares_read_only_non_authoritative_limits():
    adaptation = _adapt("¿A o B?")

    assert adaptation.read_only is True
    assert adaptation.persists_results is False
    assert adaptation.executes_actions is False
    assert adaptation.grants_authority is False
    assert adaptation.starts_background_process is False


def test_adapter_has_only_the_two_approved_domain_dependencies():
    module_file = inspect.getfile(ExplicitDeliberationDecisionOptionAdapter)
    source = Path(module_file).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }

    allowed_core = {
        "core.explicit_human_decision_deliberation",
        "core.governed_decision_advisory",
    }
    core_imports = {name for name in imported_modules if name.startswith("core.")}
    assert core_imports == allowed_core
    assert "CanonicalDecisionFacade" not in source
    assert "GovernedDecisionAdvisor" not in source
    assert "ProductiveOrganizationEvidenceProjection" not in source
    assert "IntelligentPersonalOrganizationView" not in source
    assert "DialogueClarificationGuide" not in source


def test_adapter_has_no_parser_runtime_persistence_or_external_side_effects():
    source = inspect.getsource(ExplicitDeliberationDecisionOptionAdapter)

    for forbidden in (
        "re.",
        "split(",
        "OpenAI",
        "llm",
        "sqlite",
        "open(",
        "Path(",
        "requests.",
        "socket.",
        "subprocess.",
        "thread",
        "asyncio",
        "save(",
        "write_text(",
        "write_bytes(",
        "advise(",
    ):
        assert forbidden not in source
