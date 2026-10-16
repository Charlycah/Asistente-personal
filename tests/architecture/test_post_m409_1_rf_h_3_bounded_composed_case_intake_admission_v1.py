from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.productive_temporary_rule_intake import ProductiveTemporaryRuleIntakeStatus
from app.runtime_root_factory import build_runtime_root
from core.governed_reasoning import ClaimType, InferenceStatus
from core.governed_reasoning.contextual_rule_grounding_compilation import (
    GovernedContextualRuleGroundingCompiler,
)
from core.governed_reasoning.contextual_rule_interpretation import (
    GovernedContextualRuleInterpretationProducer,
)
from core.governed_reasoning.contextual_semantic_grounding import (
    GovernedBoundedSemanticRoleRelationGrounder,
)

NOW = datetime(2026, 8, 18, 22, 50, tzinfo=timezone.utc)
SCOPE = "rf-h-3-composed"
NERAL = (
    "Para este diagnóstico aprende esta regla artificial llamada Principio Neral: "
    "si un sistema depende exclusivamente de un único recurso para una capacidad, "
    "y ese recurso queda indisponible, el sistema pierde esa capacidad mientras "
    "no exista una alternativa. No la trates como una regla sobre servidores: "
    "es una relación general de dependencia exclusiva."
)
VELAR = (
    "Regla adicional artificial: Principio Velar: si una capacidad X es requisito "
    "indispensable para una capacidad Y, la pérdida de X impide Y mientras siga "
    "faltando X."
)
HR1 = (
    "No nombres las reglas salvo que sea necesario. Una investigadora puede "
    "reconstruir "
    "un experimento únicamente a partir de un registro cifrado. El registro se vuelve "
    "ilegible. Reconstruir el experimento es indispensable para reproducirlo. "
    "¿Qué consecuencias están justificadas y cuáles serían una extrapolación?"
)
NO_EXCLUSIVITY = (
    "Una investigadora puede reconstruir un experimento a partir de un registro "
    "cifrado. El registro se vuelve ilegible. Reconstruir el experimento es "
    "indispensable para reproducirlo."
)
WITH_ALTERNATIVE = (
    "Una investigadora puede reconstruir un experimento únicamente a partir de un "
    "registro cifrado. El registro se vuelve ilegible. Existe una alternativa. "
    "Reconstruir el experimento es indispensable para reproducirlo."
)


def _root(monkeypatch, tmp_path):
    monkeypatch.setenv("ROBY_PERSONAL_MEMORY_PATH", str(tmp_path / "memory"))
    return build_runtime_root()


def _reasoning(root):
    return root.dependencies.governed_reasoning_runtime


def _teach(reasoning, text: str, minute: int) -> None:
    reasoning.evaluate_text(
        owner="Carlos",
        text=text,
        now=NOW + timedelta(minutes=minute),
        scope_reference=SCOPE,
    )


def _compile(text: str, source: str):
    candidate = GovernedContextualRuleInterpretationProducer().produce(
        text,
        source_reference=source,
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
    return compilation


def test_predicate_identity_is_reused_across_independent_rule_sources() -> None:
    neral = _compile(NERAL, "conversation:rf-h-3/neral")
    velar = _compile(VELAR, "conversation:rf-h-3/velar")

    neral_availability = neral.vocabulary.entry_by_label("availability")
    velar_availability = velar.vocabulary.entry_by_label("availability")

    assert neral_availability is not None
    assert velar_availability is not None
    assert neral_availability.predicate_id == velar_availability.predicate_id
    assert neral.vocabulary.source_reference != velar.vocabulary.source_reference


def test_historical_neral_compiles_capability_bound_availability_conclusion() -> None:
    compilation = _compile(NERAL, "conversation:rf-h-3/neral")
    spec = compilation.instantiation_spec
    availability = compilation.vocabulary.entry_by_label("availability")

    assert spec is not None
    assert availability is not None
    assert spec.conclusion.role_id == "capability"
    assert spec.conclusion.predicate_id == availability.predicate_id
    assert spec.conclusion.object_value == "unavailable"


def test_exact_hr1_admits_both_pending_rules_in_one_observation(
    monkeypatch, tmp_path
) -> None:
    reasoning = _reasoning(_root(monkeypatch, tmp_path))
    _teach(reasoning, NERAL, 0)
    _teach(reasoning, VELAR, 1)

    reasoning.evaluate_text(
        owner="Carlos",
        text=HR1,
        now=NOW + timedelta(minutes=2),
        scope_reference=SCOPE,
    )
    intake = reasoning.productive_temporary_rule_intake.last_result

    assert intake is not None
    assert intake.status is ProductiveTemporaryRuleIntakeStatus.RULE_ADMITTED
    assert intake.pending_specs == 0
    assert len(intake.admissions) == 2
    assert len(intake.projections) == 2
    assert len(reasoning.orchestrator.inference_engine.registry.list()) == 2


def test_velar_projection_excludes_unavailable_claim_that_must_be_derived(
    monkeypatch, tmp_path
) -> None:
    reasoning = _reasoning(_root(monkeypatch, tmp_path))
    _teach(reasoning, NERAL, 0)
    _teach(reasoning, VELAR, 1)
    reasoning.evaluate_text(
        owner="Carlos",
        text=HR1,
        now=NOW + timedelta(minutes=2),
        scope_reference=SCOPE,
    )
    intake = reasoning.productive_temporary_rule_intake.last_result

    assert intake is not None
    velar_projection = next(
        projection
        for projection in intake.projections
        if len(projection.claims) == 1
    )
    assert len(velar_projection.claims) == 1
    relation = velar_projection.claims[0]
    assert relation.subject == "Reconstruir el experimento"
    assert relation.object_value == "reproducir el experimento"
    assert all(
        not (
            claim.subject == "Reconstruir el experimento"
            and claim.object_value == "unavailable"
        )
        for projection in intake.projections
        for claim in projection.claims
    )


def test_exact_hr1_completes_neral_to_velar_bounded_propagation(
    monkeypatch, tmp_path
) -> None:
    reasoning = _reasoning(_root(monkeypatch, tmp_path))
    _teach(reasoning, NERAL, 0)
    _teach(reasoning, VELAR, 1)

    result = reasoning.evaluate_text(
        owner="Carlos",
        text=HR1,
        now=NOW + timedelta(minutes=2),
        scope_reference=SCOPE,
    )

    by_subject = {
        item.output_claim.subject: item
        for item in result.inference_run.results
        if item.output_claim is not None
    }
    neral = by_subject["Reconstruir el experimento"]
    velar = by_subject["reproducir el experimento"]

    assert neral.normalized_status is InferenceStatus.REVIEW_REQUIRED
    assert velar.normalized_status is InferenceStatus.REVIEW_REQUIRED
    assert neral.output_claim is not None
    assert velar.output_claim is not None
    assert neral.output_claim.object_value == "unavailable"
    assert velar.output_claim.object_value == "unavailable"
    assert neral.output_claim.claim_id in velar.input_claim_ids


def test_exact_hr1_transient_claims_do_not_enter_claim_registry(
    monkeypatch, tmp_path
) -> None:
    reasoning = _reasoning(_root(monkeypatch, tmp_path))
    registry = reasoning.orchestrator.context_assembler.claim_registry
    _teach(reasoning, NERAL, 0)
    _teach(reasoning, VELAR, 1)

    result = reasoning.evaluate_text(
        owner="Carlos",
        text=HR1,
        now=NOW + timedelta(minutes=2),
        scope_reference=SCOPE,
    )

    assert registry.list_all() == ()
    assert result.context.claims
    assert all(
        claim.normalized_type is ClaimType.HYPOTHESIS
        for claim in result.context.claims
    )


def test_missing_exclusivity_does_not_admit_composed_rules(
    monkeypatch, tmp_path
) -> None:
    reasoning = _reasoning(_root(monkeypatch, tmp_path))
    _teach(reasoning, NERAL, 0)
    _teach(reasoning, VELAR, 1)

    result = reasoning.evaluate_text(
        owner="Carlos",
        text=NO_EXCLUSIVITY,
        now=NOW + timedelta(minutes=2),
        scope_reference=SCOPE,
    )
    intake = reasoning.productive_temporary_rule_intake.last_result

    assert intake is not None
    assert intake.status is ProductiveTemporaryRuleIntakeStatus.CASE_INSUFFICIENT
    assert intake.admissions == ()
    assert reasoning.orchestrator.inference_engine.registry.list() == ()
    assert result.inference_run.applied_claims == ()


def test_explicit_alternative_prevents_neral_result_and_velar_propagation(
    monkeypatch, tmp_path
) -> None:
    reasoning = _reasoning(_root(monkeypatch, tmp_path))
    _teach(reasoning, NERAL, 0)
    _teach(reasoning, VELAR, 1)

    result = reasoning.evaluate_text(
        owner="Carlos",
        text=WITH_ALTERNATIVE,
        now=NOW + timedelta(minutes=2),
        scope_reference=SCOPE,
    )

    assert all(
        claim.subject != "Reconstruir el experimento"
        for claim in result.inference_run.applied_claims
    )
    assert all(
        claim.subject != "reproducir el experimento"
        for claim in result.inference_run.applied_claims
    )


def test_composed_admission_is_bounded_to_two_rules_per_observation(
    monkeypatch, tmp_path
) -> None:
    reasoning = _reasoning(_root(monkeypatch, tmp_path))
    _teach(reasoning, NERAL, 0)
    second_neral = NERAL.replace("Principio Neral", "Principio NeralDos")
    _teach(reasoning, second_neral, 1)
    _teach(reasoning, VELAR, 2)

    reasoning.evaluate_text(
        owner="Carlos",
        text=HR1,
        now=NOW + timedelta(minutes=3),
        scope_reference=SCOPE,
    )
    intake = reasoning.productive_temporary_rule_intake.last_result

    assert intake is not None
    assert len(intake.admissions) == 2
    assert intake.pending_specs == 1
    assert len(reasoning.orchestrator.inference_engine.registry.list()) == 2


def test_aggregate_result_preserves_legacy_single_admission_view(
    monkeypatch, tmp_path
) -> None:
    reasoning = _reasoning(_root(monkeypatch, tmp_path))
    _teach(reasoning, NERAL, 0)
    _teach(reasoning, VELAR, 1)
    reasoning.evaluate_text(
        owner="Carlos",
        text=HR1,
        now=NOW + timedelta(minutes=2),
        scope_reference=SCOPE,
    )
    intake = reasoning.productive_temporary_rule_intake.last_result

    assert intake is not None
    assert intake.admission == intake.admissions[-1]
    assert intake.projection == intake.projections[-1]


def test_cross_scope_case_cannot_consume_pending_specs(monkeypatch, tmp_path) -> None:
    reasoning = _reasoning(_root(monkeypatch, tmp_path))
    _teach(reasoning, NERAL, 0)
    _teach(reasoning, VELAR, 1)

    reasoning.evaluate_text(
        owner="Carlos",
        text=HR1,
        now=NOW + timedelta(minutes=2),
        scope_reference="rf-h-3-other",
    )
    intake = reasoning.productive_temporary_rule_intake.last_result

    assert intake is not None
    assert intake.status is ProductiveTemporaryRuleIntakeStatus.NO_CHANGE
    assert reasoning.productive_temporary_rule_intake.pending_count(SCOPE) == 2
    assert reasoning.orchestrator.inference_engine.registry.list() == ()
