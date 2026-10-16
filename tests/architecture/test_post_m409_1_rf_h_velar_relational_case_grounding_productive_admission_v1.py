from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.productive_temporary_rule_intake import (
    ProductiveTemporaryRuleIntakeStatus,
)
from app.runtime_root_factory import build_runtime_root
from core.governed_reasoning.contextual_case_grounding import (
    ContextualCaseGroundingStatus,
    GovernedContextualCaseRoleGrounder,
)
from core.governed_reasoning.contextual_rule_grounding_compilation import (
    GovernedContextualRuleGroundingCompiler,
)
from core.governed_reasoning.contextual_rule_interpretation import (
    GovernedContextualRuleInterpretationProducer,
)
from core.governed_reasoning.contextual_semantic_grounding import (
    GovernedBoundedSemanticRoleRelationGrounder,
)

NOW = datetime(2026, 8, 18, 15, 20, tzinfo=timezone.utc)
SESSION = "rf-h-velar-case-v1"
OTHER = "rf-h-velar-case-v1-other"
RULE_TEXT = (
    "Regla temporal: si capacidad alfa es requisito indispensable para capacidad beta "
    "y la capacidad requisito queda indisponible, entonces la capacidad dependiente "
    "queda impedida."
)
CASE_TEXT = (
    "Reconstruir el experimento es requisito indispensable para reproducir el "
    "experimento. Reconstruir el experimento queda indisponible."
)
UNKNOWN_AVAILABILITY = (
    "Reconstruir el experimento es requisito indispensable para reproducir el "
    "experimento."
)
AVAILABLE_PREREQUISITE = (
    "Reconstruir el experimento es requisito indispensable para reproducir el "
    "experimento. Reconstruir el experimento funciona."
)
AMBIGUOUS_CASE = (
    "Reconstruir el experimento es requisito indispensable para reproducir el "
    "experimento. Validar el experimento es requisito indispensable para publicarlo. "
    "Reconstruir el experimento queda indisponible."
)


def _root(monkeypatch, tmp_path):
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_PATH", str(tmp_path / "memory"))
    return build_runtime_root()


def _reasoning(root):
    return root.dependencies.governed_reasoning_runtime


def _spec():
    source = "conversation:rf-h/velar-case-v1"
    candidate = GovernedContextualRuleInterpretationProducer().produce(
        RULE_TEXT,
        source_reference=source,
        scope_reference=SESSION,
    )
    grounding = GovernedBoundedSemanticRoleRelationGrounder().ground(
        candidate,
        scope_reference=SESSION,
    )
    compilation = GovernedContextualRuleGroundingCompiler().compile(
        rule_candidate=candidate,
        semantic_grounding=grounding,
        scope_reference=SESSION,
    )
    assert compilation.instantiation_spec is not None
    return compilation.instantiation_spec


def test_velar_case_grounder_reuses_existing_authority_and_binds_two_roles() -> None:
    result = GovernedContextualCaseRoleGrounder().ground(
        case_text=CASE_TEXT,
        spec=_spec(),
        scope_reference=SESSION,
        source_reference="case:velar:1",
    )

    assert result.normalized_status is ContextualCaseGroundingStatus.GROUNDED
    assert result.family_id == "relational_prerequisite_capability_block_v1"
    assert tuple(item.role_id for item in result.bindings) == (
        "prerequisite",
        "dependent",
    )
    assert result.bindings[0].entity_reference == "Reconstruir el experimento"
    assert result.bindings[1].entity_reference == "reproducir el experimento"


def test_relational_case_projection_resolves_object_role_to_bound_entity(
    monkeypatch, tmp_path
) -> None:
    root = _root(monkeypatch, tmp_path)
    reasoning = _reasoning(root)

    reasoning.evaluate_text(
        owner="Carlos",
        text=RULE_TEXT,
        now=NOW,
        scope_reference=SESSION,
    )
    reasoning.evaluate_text(
        owner="Carlos",
        text=CASE_TEXT,
        now=NOW + timedelta(minutes=1),
        scope_reference=SESSION,
    )

    result = reasoning.productive_temporary_rule_intake.last_result
    assert result is not None
    assert result.projection is not None
    relation = result.projection.claims[0]
    assert relation.subject == "Reconstruir el experimento"
    assert relation.object_value == "reproducir el experimento"


def test_velar_teaching_then_concrete_case_reaches_rule_admitted(
    monkeypatch, tmp_path
) -> None:
    root = _root(monkeypatch, tmp_path)
    reasoning = _reasoning(root)
    registry = reasoning.orchestrator.inference_engine.registry

    reasoning.evaluate_text(
        owner="Carlos",
        text=RULE_TEXT,
        now=NOW,
        scope_reference=SESSION,
    )
    stored = reasoning.productive_temporary_rule_intake.last_result
    assert stored is not None
    assert stored.status is ProductiveTemporaryRuleIntakeStatus.SPEC_STORED
    assert stored.pending_specs == 1

    reasoning.evaluate_text(
        owner="Carlos",
        text=CASE_TEXT,
        now=NOW + timedelta(minutes=1),
        scope_reference=SESSION,
    )
    result = reasoning.productive_temporary_rule_intake.last_result

    assert result is not None
    assert result.status is ProductiveTemporaryRuleIntakeStatus.RULE_ADMITTED
    assert result.projection is not None
    assert result.admission is not None
    assert result.pending_specs == 0
    assert len(registry.list()) == 1
    assert registry.get(
        result.admission.rule.rule_id,
        result.admission.rule.version,
    ) is result.admission.rule


def test_admitted_velar_rule_preserves_concrete_relational_condition(
    monkeypatch, tmp_path
) -> None:
    root = _root(monkeypatch, tmp_path)
    reasoning = _reasoning(root)

    reasoning.evaluate_text(
        owner="Carlos",
        text=RULE_TEXT,
        now=NOW,
        scope_reference=SESSION,
    )
    reasoning.evaluate_text(
        owner="Carlos",
        text=CASE_TEXT,
        now=NOW + timedelta(minutes=1),
        scope_reference=SESSION,
    )

    result = reasoning.productive_temporary_rule_intake.last_result
    assert result is not None
    assert result.admission is not None
    conditions = result.admission.rule.conditions
    assert conditions[0].subject == "Reconstruir el experimento"
    assert conditions[0].values == ("reproducir el experimento",)
    assert conditions[1].subject == "Reconstruir el experimento"
    assert conditions[1].values == ("unavailable",)
    assert result.admission.rule.conclusion_subject == "reproducir el experimento"
    assert result.admission.rule.conclusion_object == "unavailable"


def test_unknown_prerequisite_availability_fails_closed() -> None:
    result = GovernedContextualCaseRoleGrounder().ground(
        case_text=UNKNOWN_AVAILABILITY,
        spec=_spec(),
        scope_reference=SESSION,
        source_reference="case:velar:unknown",
    )

    assert result.normalized_status is ContextualCaseGroundingStatus.INSUFFICIENT
    assert result.bindings == ()
    assert result.role_mentions == ()


def test_explicitly_available_prerequisite_is_not_admitted(
    monkeypatch, tmp_path
) -> None:
    root = _root(monkeypatch, tmp_path)
    reasoning = _reasoning(root)

    reasoning.evaluate_text(
        owner="Carlos",
        text=RULE_TEXT,
        now=NOW,
        scope_reference=SESSION,
    )
    reasoning.evaluate_text(
        owner="Carlos",
        text=AVAILABLE_PREREQUISITE,
        now=NOW + timedelta(minutes=1),
        scope_reference=SESSION,
    )

    result = reasoning.productive_temporary_rule_intake.last_result
    assert result is not None
    assert result.status is ProductiveTemporaryRuleIntakeStatus.CASE_UNSUPPORTED
    assert result.admission is None
    assert reasoning.orchestrator.inference_engine.registry.list() == ()


def test_multiple_relational_candidates_are_ambiguous_and_fail_closed() -> None:
    result = GovernedContextualCaseRoleGrounder().ground(
        case_text=AMBIGUOUS_CASE,
        spec=_spec(),
        scope_reference=SESSION,
        source_reference="case:velar:ambiguous",
    )

    assert result.normalized_status is ContextualCaseGroundingStatus.AMBIGUOUS
    assert result.bindings == ()
    assert result.role_mentions == ()


def test_velar_pending_spec_is_session_isolated(monkeypatch, tmp_path) -> None:
    root = _root(monkeypatch, tmp_path)
    reasoning = _reasoning(root)

    reasoning.evaluate_text(
        owner="Carlos",
        text=RULE_TEXT,
        now=NOW,
        scope_reference=SESSION,
    )
    reasoning.evaluate_text(
        owner="Carlos",
        text=CASE_TEXT,
        now=NOW + timedelta(minutes=1),
        scope_reference=OTHER,
    )

    result = reasoning.productive_temporary_rule_intake.last_result
    assert result is not None
    assert result.status is ProductiveTemporaryRuleIntakeStatus.NO_CHANGE
    assert reasoning.productive_temporary_rule_intake.pending_count(SESSION) == 1
    assert reasoning.productive_temporary_rule_intake.pending_count(OTHER) == 0
    assert reasoning.orchestrator.inference_engine.registry.list() == ()


def test_velar_case_grounding_preserves_non_persistent_limits() -> None:
    result = GovernedContextualCaseRoleGrounder().ground(
        case_text=CASE_TEXT,
        spec=_spec(),
        scope_reference=SESSION,
        source_reference="case:velar:limits",
    )

    assert result.canonical_authority == "governed_reasoning"
    assert result.session_local is True
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
        assert getattr(result, name) is False


def test_neral_productive_intake_behavior_remains_covered_by_existing_route(
    monkeypatch, tmp_path
) -> None:
    root = _root(monkeypatch, tmp_path)
    reasoning = _reasoning(root)
    neral = (
        "Usá esta regla: si un sistema depende exclusivamente de un recurso para una "
        "capacidad y ese recurso está indisponible y no existe alternativa, entonces "
        "el sistema pierde esa capacidad."
    )
    case = (
        "La estación depende exclusivamente del sensor T para recibir temperatura. "
        "El sensor T dejó de responder y no existe alternativa."
    )

    reasoning.evaluate_text(
        owner="Carlos",
        text=neral,
        now=NOW,
        scope_reference=SESSION,
    )
    reasoning.evaluate_text(
        owner="Carlos",
        text=case,
        now=NOW + timedelta(minutes=1),
        scope_reference=SESSION,
    )

    result = reasoning.productive_temporary_rule_intake.last_result
    assert result is not None
    assert result.status is ProductiveTemporaryRuleIntakeStatus.RULE_ADMITTED
