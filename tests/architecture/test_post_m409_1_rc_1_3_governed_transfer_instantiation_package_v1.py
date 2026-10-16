from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from core.cognitive_memory import LearningCategory
from core.cognitive_memory_recall import (
    CognitiveMemoryRecallItem,
    CognitiveMemoryRecallResult,
)
from core.cognitive_memory_store import CognitiveMemoryRecord
from core.governed_reasoning import (
    ContextualRuleGroundingCompilationStatus,
    ContextualRuleInstantiationStatus,
    GovernedRecalledKnowledgeStructuralProjector,
    GovernedStructuralKnowledgeTransferMatcher,
    GovernedTargetProblemStructuralProjector,
    GovernedTransferInstantiator,
    RecalledKnowledgeStructuralProjectionStatus,
    StructuralKnowledgeTransferStatus,
    TargetProblemStructuralProjectionStatus,
    TransferInstantiationStatus,
)

SCOPE = "rc-1-3-transfer-instantiation"
RULE = (
    "Usá esta regla: si un sistema depende exclusivamente de un recurso para una "
    "capacidad y ese recurso está indisponible y no existe alternativa, entonces "
    "el sistema pierde esa capacidad."
)
TARGET = (
    "La misión orbital depende exclusivamente de la ventana de lanzamiento para "
    "ejecutar una maniobra. La ventana de lanzamiento queda indisponible y no "
    "existe alternativa."
)
OTHER_TARGET = (
    "La estación remota depende exclusivamente del enlace principal para mantener "
    "telemetría. El enlace principal queda indisponible y no existe alternativa."
)


def _memory(memory_id: int = 1) -> CognitiveMemoryRecord:
    return CognitiveMemoryRecord(
        id=memory_id,
        content=RULE,
        category=LearningCategory.STABLE_KNOWLEDGE,
        confidence=0.91,
        reason="stable structural rule",
        tags=("deep_reasoning",),
        metadata={"source": "rc-1.3-test"},
        created_at="2026-08-19T12:00:00+00:00",
    )


def _source(memory_id: int = 1):
    recall = CognitiveMemoryRecallResult(
        should_use_memory=True,
        items=(
            CognitiveMemoryRecallItem(
                memory=_memory(memory_id),
                score=0.83,
                matched_signals=("deep_reasoning",),
            ),
        ),
        reason="relevant_memory_found",
    )
    projection = GovernedRecalledKnowledgeStructuralProjector().project(
        recall_result=recall,
        scope_reference=SCOPE,
    )
    assert (
        projection.normalized_status
        is RecalledKnowledgeStructuralProjectionStatus.PROJECTED
    )
    return projection.items[0]


def _target(text: str = TARGET, scope: str = SCOPE):
    result = GovernedTargetProblemStructuralProjector().project(
        text=text,
        source_reference=f"conversation:{scope}:target",
        scope_reference=scope,
    )
    assert (
        result.normalized_status
        is TargetProblemStructuralProjectionStatus.PROJECTED
    )
    return result


def _transfer(source, target):
    result = GovernedStructuralKnowledgeTransferMatcher().match_target_problem(
        target=target,
        known=(source.grounding,),
        scope_reference=SCOPE,
    )
    assert (
        result.normalized_status
        is StructuralKnowledgeTransferStatus.TRANSFER_CANDIDATE
    )
    return result


def test_rc_1_1_preserves_full_certified_source_compilation() -> None:
    source = _source()

    assert (
        source.compilation.normalized_status
        is ContextualRuleGroundingCompilationStatus.COMPILED
    )
    assert source.compilation.instantiation_spec is not None
    assert (
        source.compilation.semantic_grounding_fingerprint
        == source.grounding.source_fingerprint
    )


def test_transfer_candidate_instantiates_through_existing_instantiator() -> None:
    source = _source()
    target = _target()
    transfer = _transfer(source, target)

    package = GovernedTransferInstantiator().instantiate(
        source=source,
        transfer=transfer,
        target=target,
        scope_reference=SCOPE,
    )

    assert (
        package.normalized_status
        is TransferInstantiationStatus.TRANSFER_INSTANTIATED
    )
    assert package.instantiated_candidate is not None
    assert (
        package.instantiated_candidate.status
        is ContextualRuleInstantiationStatus.INSTANTIATED
    )


def test_target_role_bindings_are_reused_without_reinterpretation() -> None:
    source = _source()
    target = _target()
    package = GovernedTransferInstantiator().instantiate(
        source=source,
        transfer=_transfer(source, target),
        target=target,
        scope_reference=SCOPE,
    )

    assert tuple(
        (item.role_id, item.entity_reference)
        for item in package.bindings
    ) == (
        ("dependent", "La misión orbital"),
        ("resource", "ventana de lanzamiento"),
        ("capability", "ejecutar una maniobra"),
    )
    assert all(
        item.source_reference == target.source_reference
        for item in package.bindings
    )


def test_concrete_conditions_reuse_source_spec_predicates() -> None:
    source = _source()
    target = _target()
    package = GovernedTransferInstantiator().instantiate(
        source=source,
        transfer=_transfer(source, target),
        target=target,
        scope_reference=SCOPE,
    )

    spec = source.compilation.instantiation_spec
    candidate = package.instantiated_candidate
    assert spec is not None
    assert candidate is not None
    assert tuple(
        (item.subject, item.predicate_id, item.object_value)
        for item in candidate.concrete_conditions
    ) == (
        (
            "La misión orbital",
            spec.conditions[0].predicate_id,
            "exclusive",
        ),
        (
            "ventana de lanzamiento",
            spec.conditions[1].predicate_id,
            "unavailable",
        ),
        (
            "La misión orbital",
            spec.conditions[2].predicate_id,
            "false",
        ),
    )


def test_conclusion_is_instantiated_from_source_rule_not_target_observation() -> None:
    source = _source()
    target = _target()
    package = GovernedTransferInstantiator().instantiate(
        source=source,
        transfer=_transfer(source, target),
        target=target,
        scope_reference=SCOPE,
    )

    spec = source.compilation.instantiation_spec
    conclusion = package.instantiated_candidate.concrete_conclusion
    assert spec is not None
    assert conclusion is not None
    assert conclusion.predicate_id == spec.conclusion.predicate_id
    assert conclusion.object_value == spec.conclusion.object_value
    assert conclusion.subject == "La misión orbital"
    assert "transfer_instantiation:not_admitted" in package.rationale_codes


def test_package_preserves_end_to_end_provenance() -> None:
    source = _source()
    target = _target()
    transfer = _transfer(source, target)
    package = GovernedTransferInstantiator().instantiate(
        source=source,
        transfer=transfer,
        target=target,
        scope_reference=SCOPE,
    )

    assert package.source_memory_id == source.memory_id
    assert (
        package.source_memory_content_fingerprint
        == source.memory_content_fingerprint
    )
    assert package.source_grounding_fingerprint == source.grounding.source_fingerprint
    assert (
        package.source_compilation_fingerprint
        == source.compilation.source_fingerprint
    )
    assert package.transfer_candidate_fingerprint == transfer.source_fingerprint
    assert package.target_projection_fingerprint == target.source_fingerprint


def test_target_provenance_mismatch_fails_closed() -> None:
    source = _source()
    first_target = _target()
    transfer = _transfer(source, first_target)
    second_target = _target(OTHER_TARGET)

    package = GovernedTransferInstantiator().instantiate(
        source=source,
        transfer=transfer,
        target=second_target,
        scope_reference=SCOPE,
    )

    assert (
        package.normalized_status
        is TransferInstantiationStatus.PROVENANCE_MISMATCH
    )
    assert package.bindings == ()
    assert package.instantiated_candidate is None


def test_no_transfer_candidate_does_not_instantiate() -> None:
    source = _source()
    target = _target()
    transfer = GovernedStructuralKnowledgeTransferMatcher().match_target_problem(
        target=target,
        known=(),
        scope_reference=SCOPE,
    )

    package = GovernedTransferInstantiator().instantiate(
        source=source,
        transfer=transfer,
        target=target,
        scope_reference=SCOPE,
    )

    assert package.normalized_status is TransferInstantiationStatus.NO_TRANSFER
    assert package.instantiated_candidate is None


def test_ambiguous_structural_transfer_does_not_instantiate() -> None:
    source = _source(1)
    other = _source(2)
    target = _target()
    transfer = GovernedStructuralKnowledgeTransferMatcher().match_target_problem(
        target=target,
        known=(source.grounding, other.grounding),
        scope_reference=SCOPE,
    )
    assert transfer.normalized_status is StructuralKnowledgeTransferStatus.AMBIGUOUS

    package = GovernedTransferInstantiator().instantiate(
        source=source,
        transfer=transfer,
        target=target,
        scope_reference=SCOPE,
    )

    assert package.normalized_status is TransferInstantiationStatus.AMBIGUOUS
    assert package.instantiated_candidate is None


def test_scope_mismatch_fails_before_instantiation() -> None:
    source = _source()
    target = _target()
    transfer = _transfer(source, target)

    package = GovernedTransferInstantiator().instantiate(
        source=source,
        transfer=transfer,
        target=target,
        scope_reference="other-scope",
    )

    assert package.normalized_status is TransferInstantiationStatus.SCOPE_MISMATCH
    assert package.instantiated_candidate is None


def test_transfer_instantiation_is_read_only_and_non_authoritative() -> None:
    source = _source()
    target = _target()
    package = GovernedTransferInstantiator().instantiate(
        source=source,
        transfer=_transfer(source, target),
        target=target,
        scope_reference=SCOPE,
    )

    assert package.canonical_authority == "governed_reasoning"
    assert package.read_only is True
    assert package.session_local is True
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
        assert getattr(package, name) is False


def test_package_is_deterministic_and_immutable() -> None:
    source = _source()
    target = _target()
    transfer = _transfer(source, target)
    instantiator = GovernedTransferInstantiator()

    first = instantiator.instantiate(
        source=source,
        transfer=transfer,
        target=target,
        scope_reference=SCOPE,
    )
    second = instantiator.instantiate(
        source=source,
        transfer=transfer,
        target=target,
        scope_reference=SCOPE,
    )

    assert first == second
    with pytest.raises(FrozenInstanceError):
        first.scope_reference = "changed"  # type: ignore[misc]
