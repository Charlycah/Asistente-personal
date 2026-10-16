from __future__ import annotations

from core.cognitive_memory import LearningCategory
from core.cognitive_memory_recall import (
    CognitiveMemoryRecallItem,
    CognitiveMemoryRecallResult,
)
from core.cognitive_memory_store import CognitiveMemoryRecord
from core.governed_reasoning import (
    GovernedRecalledKnowledgeStructuralProjector,
    GovernedStructuralKnowledgeTransferMatcher,
    GovernedTargetProblemStructuralProjector,
    RecalledKnowledgeStructuralProjectionStatus,
    StructuralKnowledgeTransferStatus,
    TargetProblemStructuralProjectionStatus,
)

SCOPE = "novel-generalization-boundary"
RULE = (
    "Usá esta regla: si un sistema depende exclusivamente de un recurso para una "
    "capacidad y ese recurso está indisponible y no existe alternativa, entonces "
    "el sistema pierde esa capacidad."
)


def _source():
    memory = CognitiveMemoryRecord(
        id=9101,
        content=RULE,
        category=LearningCategory.STABLE_KNOWLEDGE,
        confidence=0.94,
        reason="novel-generalization-source",
        tags=("deep_reasoning",),
        metadata={"source": "novel-generalization-red"},
        created_at="2026-08-22T12:00:00+00:00",
    )
    recall = CognitiveMemoryRecallResult(
        should_use_memory=True,
        items=(
            CognitiveMemoryRecallItem(
                memory=memory,
                score=0.9,
                matched_signals=("deep_reasoning",),
            ),
        ),
        reason="relevant_memory_found",
    )
    result = GovernedRecalledKnowledgeStructuralProjector().project(
        recall_result=recall, scope_reference=SCOPE
    )
    assert (
        result.normalized_status
        is RecalledKnowledgeStructuralProjectionStatus.PROJECTED
    )
    return result.items[0]


def _project(text: str):
    return GovernedTargetProblemStructuralProjector().project(
        text=text,
        source_reference="conversation:novel-generalization:target",
        scope_reference=SCOPE,
    )


def _transfer(text: str):
    source = _source()
    target = _project(text)
    if (
        target.normalized_status
        is not TargetProblemStructuralProjectionStatus.PROJECTED
    ):
        return target, None
    transfer = GovernedStructuralKnowledgeTransferMatcher().match_target_problem(
        target=target, known=(source.grounding,), scope_reference=SCOPE
    )
    return target, transfer


# New RED contracts: semantically equivalent structural formulations outside
# the currently certified narrow surface forms.


def test_ngb_n1_domain_shift_with_requires_and_no_backup_generalizes():
    text = (
        "El laboratorio requiere el único espectrómetro para analizar las muestras. "
        "El espectrómetro está fuera de servicio y no dispone de equipo de respaldo."
    )
    target, transfer = _transfer(text)
    assert target.normalized_status is TargetProblemStructuralProjectionStatus.PROJECTED
    assert transfer is not None
    assert (
        transfer.normalized_status
        is StructuralKnowledgeTransferStatus.TRANSFER_CANDIDATE
    )


def test_ngb_n2_lexical_shift_with_relies_on_and_no_substitute_generalizes():
    text = (
        "El archivo digital se sostiene únicamente con el servidor primario para "
        "consultar los expedientes. El servidor primario dejó de estar operativo "
        "y no cuenta con sustituto."
    )
    target, transfer = _transfer(text)
    assert target.normalized_status is TargetProblemStructuralProjectionStatus.PROJECTED
    assert transfer is not None
    assert (
        transfer.normalized_status
        is StructuralKnowledgeTransferStatus.TRANSFER_CANDIDATE
    )


def test_ngb_n3_entity_role_substitution_generalizes():
    text = (
        "La expedición necesita como único medio el puente norte para cruzar el río. "
        "El puente norte quedó inutilizable y carece de ruta alternativa."
    )
    target, transfer = _transfer(text)
    assert target.normalized_status is TargetProblemStructuralProjectionStatus.PROJECTED
    assert transfer is not None
    assert (
        transfer.normalized_status
        is StructuralKnowledgeTransferStatus.TRANSFER_CANDIDATE
    )


def test_ngb_n4_conversational_reformulation_generalizes():
    text = (
        "Para poder emitir el informe, el equipo solo puede obtener los datos del "
        "repositorio central. Ahora el repositorio central no está disponible y "
        "tampoco hay otra fuente."
    )
    target, transfer = _transfer(text)
    assert target.normalized_status is TargetProblemStructuralProjectionStatus.PROJECTED
    assert transfer is not None
    assert (
        transfer.normalized_status
        is StructuralKnowledgeTransferStatus.TRANSFER_CANDIDATE
    )


def test_ngb_n5_planning_context_generalizes_without_keyword_dependency():
    text = (
        "El plan mensual necesita exclusivamente la aprobación presupuestaria para "
        "iniciar las compras. La aprobación presupuestaria fue suspendida y no "
        "existe reemplazo."
    )
    target, transfer = _transfer(text)
    assert target.normalized_status is TargetProblemStructuralProjectionStatus.PROJECTED
    assert transfer is not None
    assert (
        transfer.normalized_status
        is StructuralKnowledgeTransferStatus.TRANSFER_CANDIDATE
    )


def test_ngb_n6_distractor_does_not_hide_valid_novel_structure():
    text = (
        "Aunque hoy se habló del clima y de política, el proceso editorial requiere "
        "como único recurso la firma final para publicar la edición. La firma final "
        "está bloqueada y no hay sustituto."
    )
    target, transfer = _transfer(text)
    assert target.normalized_status is TargetProblemStructuralProjectionStatus.PROJECTED
    assert transfer is not None
    assert (
        transfer.normalized_status
        is StructuralKnowledgeTransferStatus.TRANSFER_CANDIDATE
    )


# Adversarial contracts. These must fail closed, not be made GREEN by broad matching.


def test_ngb_a1_same_domain_wrong_structure_is_not_projected():
    target = _project(
        "La misión orbital usa una ventana de lanzamiento, pero también puede "
        "maniobrar con propulsión autónoma. La ventana no está disponible."
    )
    assert (
        target.normalized_status
        is not TargetProblemStructuralProjectionStatus.PROJECTED
    )


def test_ngb_a3_missing_exclusivity_relation_is_not_projected():
    target = _project(
        "El laboratorio utiliza el espectrómetro para analizar muestras. "
        "El espectrómetro está fuera de servicio y no sabemos si existe alternativa."
    )
    assert (
        target.normalized_status
        is not TargetProblemStructuralProjectionStatus.PROJECTED
    )


def test_ngb_a5_negated_dependency_is_not_projected():
    target = _project(
        "El laboratorio no depende exclusivamente del espectrómetro para analizar "
        "muestras. El espectrómetro está fuera de servicio y no existe alternativa."
    )
    assert (
        target.normalized_status
        is not TargetProblemStructuralProjectionStatus.PROJECTED
    )


def test_ngb_a6_quoted_dependency_is_not_projected_as_current_fact():
    target = _project(
        'El informe antiguo decía: "el laboratorio depende exclusivamente del '
        "espectrómetro para analizar muestras; el espectrómetro está fuera de "
        'servicio y no existe alternativa". Hoy no afirmamos esas condiciones.'
    )
    assert (
        target.normalized_status
        is not TargetProblemStructuralProjectionStatus.PROJECTED
    )


def test_ngb_a7_lexical_distractor_without_structure_is_not_projected():
    target = _project(
        "El sistema tiene recursos, alternativas, capacidad y disponibilidad. "
        "Se evalúan dependencias, pero no se afirma una dependencia exclusiva ni "
        "la indisponibilidad de un recurso concreto."
    )
    assert (
        target.normalized_status
        is not TargetProblemStructuralProjectionStatus.PROJECTED
    )
