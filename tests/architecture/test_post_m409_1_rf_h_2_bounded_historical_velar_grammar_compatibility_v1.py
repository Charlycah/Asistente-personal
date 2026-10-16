from __future__ import annotations

from datetime import datetime, timezone

from app.productive_temporary_rule_intake import ProductiveTemporaryRuleIntakeStatus
from app.runtime_root_factory import build_runtime_root
from core.governed_reasoning.contextual_rule_grounding_compilation import (
    ContextualRuleGroundingCompilationStatus,
    GovernedContextualRuleGroundingCompiler,
)
from core.governed_reasoning.contextual_rule_interpretation import (
    ContextualRuleCandidateStatus,
    GovernedContextualRuleInterpretationProducer,
)
from core.governed_reasoning.contextual_semantic_grounding import (
    ContextualSemanticGroundingStatus,
    ContextualSemanticRelation,
    ContextualSemanticRole,
    GovernedBoundedSemanticRoleRelationGrounder,
)

NOW = datetime(2026, 8, 18, 22, 20, tzinfo=timezone.utc)
SCOPE = "rf-h-2-historical-velar"
SOURCE = "conversation:rf-h-2/turn-1"
HISTORICAL = (
    "Regla adicional artificial: Principio Velar: si una capacidad X es requisito "
    "indispensable para una capacidad Y, la pérdida de X impide Y mientras siga "
    "faltando X."
)
BOUNDED = (
    "Regla temporal: si capacidad alfa es requisito indispensable para capacidad beta "
    "y la capacidad requisito queda indisponible, entonces la capacidad dependiente "
    "queda impedida."
)


def _candidate(text: str = HISTORICAL):
    return GovernedContextualRuleInterpretationProducer().produce(
        text,
        source_reference=SOURCE,
        scope_reference=SCOPE,
    )


def _ground(text: str = HISTORICAL):
    return GovernedBoundedSemanticRoleRelationGrounder().ground(
        _candidate(text),
        scope_reference=SCOPE,
    )


def _compile(text: str = HISTORICAL):
    candidate = _candidate(text)
    grounding = GovernedBoundedSemanticRoleRelationGrounder().ground(
        candidate,
        scope_reference=SCOPE,
    )
    return GovernedContextualRuleGroundingCompiler().compile(
        rule_candidate=candidate,
        semantic_grounding=grounding,
        scope_reference=SCOPE,
    )


def test_historical_velar_wording_is_bounded_candidate() -> None:
    candidate = _candidate()

    assert candidate.normalized_status is ContextualRuleCandidateStatus.CANDIDATE
    assert candidate.rationale_codes[1] == "grammar:historical_velar_v1"
    assert len(candidate.conditions) == 2
    assert candidate.conditions[0].normalized_text == (
        "una capacidad X es requisito indispensable para una capacidad Y"
    )
    assert candidate.conditions[1].normalized_text == "la pérdida de X"
    assert candidate.conclusion is not None
    assert candidate.conclusion.normalized_text == "impide Y mientras siga faltando X"


def test_nested_principle_label_is_not_part_of_rule_source_span() -> None:
    candidate = _candidate()

    assert candidate.rule_source_text.startswith("si una capacidad X")
    assert "Principio Velar:" not in candidate.rule_source_text
    assert (
        candidate.source_text[
            candidate.rule_start_offset : candidate.rule_end_offset
        ]
        == candidate.rule_source_text
    )


def test_historical_velar_reuses_existing_semantic_family() -> None:
    grounding = _ground()

    assert grounding.normalized_status is ContextualSemanticGroundingStatus.GROUNDED
    assert grounding.family_id == "relational_prerequisite_capability_block_v1"
    assert tuple(item.role_id for item in grounding.role_mentions) == (
        ContextualSemanticRole.PREREQUISITE,
        ContextualSemanticRole.DEPENDENT,
    )


def test_historical_velar_preserves_relational_object_semantics() -> None:
    slots = _ground().semantic_slots

    assert slots[0].relation is ContextualSemanticRelation.REQUIRED_FOR
    assert slots[0].value == ContextualSemanticRole.DEPENDENT.value
    assert slots[1].relation is ContextualSemanticRelation.AVAILABILITY
    assert slots[1].value == "unavailable"
    assert slots[2].role_id is ContextualSemanticRole.DEPENDENT
    assert slots[2].value == "unavailable"


def test_historical_velar_slots_keep_real_source_text() -> None:
    grounding = _ground()

    assert grounding.semantic_slots[1].source_text == "la pérdida de X"
    assert grounding.semantic_slots[2].source_text == (
        "impide Y mientras siga faltando X"
    )


def test_historical_velar_compiles_to_existing_object_role_contract() -> None:
    compilation = _compile()

    assert (
        compilation.normalized_status
        is ContextualRuleGroundingCompilationStatus.COMPILED
    )
    assert compilation.instantiation_spec is not None
    relational = compilation.instantiation_spec.conditions[0]
    assert relational.role_id == "prerequisite"
    assert relational.object_value is None
    assert relational.object_role_id == "dependent"
    assert compilation.instantiation_spec.roles == ("prerequisite", "dependent")


def test_historical_velar_reaches_productive_spec_stored(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_PATH", str(tmp_path / "memory"))
    reasoning = build_runtime_root().dependencies.governed_reasoning_runtime

    reasoning.evaluate_text(
        owner="Carlos",
        text=HISTORICAL,
        now=NOW,
        scope_reference=SCOPE,
    )

    result = reasoning.productive_temporary_rule_intake.last_result
    assert result is not None
    assert result.status is ProductiveTemporaryRuleIntakeStatus.SPEC_STORED
    assert result.pending_specs == 1
    assert reasoning.orchestrator.inference_engine.registry.list() == ()


def test_historical_reference_mismatch_fails_closed_at_interpretation() -> None:
    text = (
        "Regla adicional artificial: Principio Velar: si una capacidad X es requisito "
        "indispensable para una capacidad Y, la pérdida de X impide Y mientras siga "
        "faltando Z."
    )
    candidate = _candidate(text)

    assert candidate.normalized_status is ContextualRuleCandidateStatus.AMBIGUOUS
    assert candidate.conditions == ()
    assert candidate.conclusion is None


def test_historical_dependent_reference_mismatch_fails_closed_at_grounding() -> None:
    text = (
        "Regla adicional artificial: Principio Velar: si una capacidad X es requisito "
        "indispensable para una capacidad Y, la pérdida de X impide Z mientras siga "
        "faltando X."
    )
    grounding = _ground(text)

    assert grounding.normalized_status is ContextualSemanticGroundingStatus.AMBIGUOUS
    assert grounding.role_mentions == ()
    assert grounding.semantic_slots == ()


def test_existing_bounded_velar_wording_remains_supported() -> None:
    candidate = _candidate(BOUNDED)
    grounding = _ground(BOUNDED)
    compilation = _compile(BOUNDED)

    assert candidate.normalized_status is ContextualRuleCandidateStatus.CANDIDATE
    assert grounding.normalized_status is ContextualSemanticGroundingStatus.GROUNDED
    assert (
        compilation.normalized_status
        is ContextualRuleGroundingCompilationStatus.COMPILED
    )
