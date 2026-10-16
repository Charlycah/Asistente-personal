from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

from core.governed_reasoning import (
    ContextualCaseGroundingStatus,
    ContextualRuleInstantiationStatus,
    GovernedBoundedSemanticRoleRelationGrounder,
    GovernedContextualCaseRoleGrounder,
    GovernedContextualRuleGroundingCompiler,
    GovernedContextualRuleInstantiator,
)
from core.governed_reasoning.contextual_rule_interpretation import (
    GovernedContextualRuleInterpretationProducer,
)

SCOPE = "session:case-grounding-v1"
RULE_SOURCE = "conversation:case-grounding-v1/turn-1"
CASE_SOURCE = "conversation:case-grounding-v1/turn-2"
RULE_TEXT = (
    "Usá esta regla: si un sistema depende exclusivamente de un recurso para una "
    "capacidad y ese recurso está indisponible y no existe alternativa, entonces "
    "el sistema pierde esa capacidad."
)
CASE_TEXT = (
    "La estación depende exclusivamente del sensor T para recibir temperatura. "
    "El sensor T dejó de responder y no existe alternativa."
)


def test_supported_case_produces_complete_provenance_bound_bindings() -> None:
    result = _ground_case(CASE_TEXT)

    assert result.normalized_status is ContextualCaseGroundingStatus.GROUNDED
    assert tuple(item.role_id for item in result.bindings) == (
        "dependent",
        "resource",
        "capability",
    )
    assert tuple(item.entity_reference for item in result.bindings) == (
        "La estación",
        "sensor T",
        "temperatura",
    )
    assert all(item.source_reference == CASE_SOURCE for item in result.bindings)


def test_role_mentions_preserve_exact_case_spans() -> None:
    result = _ground_case(CASE_TEXT)

    for mention in result.role_mentions:
        span_text = CASE_TEXT[mention.start_offset : mention.end_offset]
        assert span_text == mention.source_text


def test_domain_neutral_case_uses_same_bounded_family() -> None:
    text = (
        "La aplicación depende exclusivamente del servicio Q para procesar pagos. "
        "El servicio Q está indisponible y no hay alternativa."
    )
    result = _ground_case(text)

    assert result.normalized_status is ContextualCaseGroundingStatus.GROUNDED
    assert tuple(item.entity_reference for item in result.bindings) == (
        "La aplicación",
        "servicio Q",
        "pagos",
    )


def test_complete_bindings_allow_3a4_concrete_instantiation() -> None:
    spec = _spec()
    grounding = _ground_case(CASE_TEXT, spec=spec)
    result = GovernedContextualRuleInstantiator().instantiate(
        spec=spec,
        bindings=grounding.bindings,
        scope_reference=SCOPE,
    )

    assert result.status is ContextualRuleInstantiationStatus.INSTANTIATED
    assert result.concrete_conclusion is not None
    assert result.concrete_conclusion.subject == "La estación"
    assert tuple(item.subject for item in result.concrete_conditions) == (
        "La estación",
        "sensor T",
        "La estación",
    )


def test_missing_alternative_evidence_is_insufficient_without_partial_bindings(
) -> None:
    text = (
        "La estación depende exclusivamente del sensor T para recibir temperatura. "
        "El sensor T dejó de responder."
    )
    result = _ground_case(text)

    assert result.normalized_status is ContextualCaseGroundingStatus.INSUFFICIENT
    assert result.rationale_codes == ("case_grounding:alternative_unknown",)
    _assert_no_partial(result)


def test_missing_resource_availability_is_insufficient() -> None:
    text = (
        "La estación depende exclusivamente del sensor T para recibir temperatura. "
        "No existe alternativa."
    )
    result = _ground_case(text)

    assert result.normalized_status is ContextualCaseGroundingStatus.INSUFFICIENT
    assert result.rationale_codes == (
        "case_grounding:resource_availability_unknown",
    )
    _assert_no_partial(result)


def test_multiple_resources_are_ambiguous_without_partial_bindings() -> None:
    text = (
        "La estación depende exclusivamente de sensor T y sensor U para recibir "
        "temperatura. El sensor T dejó de responder y no existe alternativa."
    )
    result = _ground_case(text)

    assert result.normalized_status is ContextualCaseGroundingStatus.AMBIGUOUS
    assert result.rationale_codes == ("case_grounding:multiple_resources",)
    _assert_no_partial(result)


def test_explicit_alternative_rejects_case_as_incompatible() -> None:
    text = (
        "La estación depende exclusivamente del sensor T para recibir temperatura. "
        "El sensor T dejó de responder y existe una alternativa."
    )
    result = _ground_case(text)

    assert result.normalized_status is ContextualCaseGroundingStatus.UNSUPPORTED
    assert result.rationale_codes == ("case_grounding:alternative_present",)
    _assert_no_partial(result)


def test_explicitly_available_resource_rejects_case() -> None:
    text = (
        "La estación depende exclusivamente del sensor T para recibir temperatura. "
        "El sensor T funciona y no existe alternativa."
    )
    result = _ground_case(text)

    assert result.normalized_status is ContextualCaseGroundingStatus.UNSUPPORTED
    assert result.rationale_codes == ("case_grounding:resource_not_unavailable",)
    _assert_no_partial(result)


def test_scope_mismatch_fails_closed() -> None:
    result = GovernedContextualCaseRoleGrounder().ground(
        case_text=CASE_TEXT,
        spec=_spec(),
        scope_reference="session:other",
        source_reference=CASE_SOURCE,
    )

    assert result.normalized_status is ContextualCaseGroundingStatus.SCOPE_MISMATCH
    _assert_no_partial(result)


def test_unsupported_spec_family_fails_closed() -> None:
    spec = _spec()
    changed = replace(
        spec,
        roles=("dependent", "resource", "capability", "extra"),
    )
    result = _ground_case(CASE_TEXT, spec=changed)

    assert result.normalized_status is ContextualCaseGroundingStatus.UNSUPPORTED
    assert result.rationale_codes == ("case_grounding:unsupported_rule_family",)
    _assert_no_partial(result)


def test_case_grounding_is_deterministic_immutable_and_non_authoritative() -> None:
    first = _ground_case(CASE_TEXT)
    second = _ground_case(CASE_TEXT)

    assert first.source_fingerprint == second.source_fingerprint
    assert first.bindings == second.bindings
    assert first.session_local is True
    for name in (
        "persists_results",
        "creates_memory",
        "modifies_memory",
        "creates_learning_candidate",
        "modifies_learning",
        "modifies_world_model",
        "establishes_truth",
        "authorizes_inference",
        "registers_rule",
        "executes_actions",
        "grants_authority",
        "uses_provider",
        "uses_retrieval",
    ):
        assert getattr(first, name) is False
    with pytest.raises(FrozenInstanceError):
        first.scope_reference = "changed"  # type: ignore[misc]


def test_case_grounding_has_no_runtime_admission_or_registry_wiring() -> None:
    import core.governed_reasoning.contextual_case_grounding as module

    source = module.__file__
    assert source is not None
    text = Path(source).read_text(encoding="utf-8")
    assert "OfficialConversationGateway" not in text
    assert "GovernedTemporaryConcreteRuleAdmissionBoundary" not in text
    assert "InMemoryInferenceRuleRegistry" not in text
    assert "llm" not in text.casefold()


def _spec():
    candidate = GovernedContextualRuleInterpretationProducer().produce(
        RULE_TEXT,
        source_reference=RULE_SOURCE,
        scope_reference=SCOPE,
    )
    grounding = GovernedBoundedSemanticRoleRelationGrounder().ground(
        candidate,
        scope_reference=SCOPE,
    )
    compilation = GovernedContextualRuleGroundingCompiler().compile(
        rule_candidate=candidate,
        semantic_grounding=grounding,
        scope_reference=SCOPE,
    )
    assert compilation.instantiation_spec is not None
    return compilation.instantiation_spec


def _ground_case(text: str, *, spec=None):
    return GovernedContextualCaseRoleGrounder().ground(
        case_text=text,
        spec=spec or _spec(),
        scope_reference=SCOPE,
        source_reference=CASE_SOURCE,
    )


def _assert_no_partial(result) -> None:
    assert result.role_mentions == ()
    assert result.bindings == ()
