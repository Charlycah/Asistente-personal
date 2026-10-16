from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from core.cognitive_intent import CognitiveIntent, CognitiveIntentResult
from core.cognitive_memory import (
    LearningAction,
    LearningCandidate,
    LearningCategory,
)
from core.cognitive_memory_recall import (
    CognitiveMemoryRecall,
    CognitiveMemoryRecallItem,
    CognitiveMemoryRecallRequest,
    CognitiveMemoryRecallResult,
)
from core.cognitive_memory_store import (
    CognitiveMemoryRecord,
    CognitiveMemoryStore,
    CognitiveMemoryStoreConfig,
)
from core.governed_reasoning import (
    ContextualSemanticGroundingStatus,
    ContextualSemanticRelation,
    ContextualSemanticRole,
    ContextualSemanticRoleMention,
    ContextualSemanticSlot,
    GovernedContextualSemanticGroundingCandidate,
    GovernedRecalledKnowledgeStructuralProjector,
    GovernedStructuralKnowledgeTransferMatcher,
    RecalledKnowledgeStructuralProjectionStatus,
    StructuralKnowledgeTransferStatus,
)

SCOPE = "rc-1-1-recalled-knowledge"
NERAL_MEMORY = (
    "Usá esta regla: si un sistema depende exclusivamente de un recurso para una "
    "capacidad y ese recurso está indisponible y no existe alternativa, entonces "
    "el sistema pierde esa capacidad."
)
VELAR_AMBIGUOUS_MEMORY = (
    "Regla adicional artificial: Principio Velar: si una capacidad X es requisito "
    "indispensable para una capacidad Y, la pérdida de X impide Z mientras siga "
    "faltando X."
)


def _record(
    memory_id: int,
    content: str,
    *,
    confidence: float = 0.9,
) -> CognitiveMemoryRecord:
    return CognitiveMemoryRecord(
        id=memory_id,
        content=content,
        category=LearningCategory.STABLE_KNOWLEDGE,
        confidence=confidence,
        reason="test recalled knowledge",
        tags=("deep_reasoning",),
        metadata={"source": "test"},
        created_at="2026-08-19T10:00:00+00:00",
    )


def _item(memory_id: int, content: str, score: float = 0.8):
    return CognitiveMemoryRecallItem(
        memory=_record(memory_id, content),
        score=score,
        matched_signals=("deep_reasoning",),
    )


def _recall(*items: CognitiveMemoryRecallItem):
    return CognitiveMemoryRecallResult(
        should_use_memory=True,
        items=items,
        reason="relevant_memory_found",
    )


def _target_dependency() -> GovernedContextualSemanticGroundingCandidate:
    dependent = "misión orbital"
    resource = "ventana de lanzamiento"
    capability = "ejecutar maniobra"
    roles = (
        ContextualSemanticRoleMention(
            ContextualSemanticRole.DEPENDENT,
            dependent,
            0,
            len(dependent),
        ),
        ContextualSemanticRoleMention(
            ContextualSemanticRole.RESOURCE,
            resource,
            20,
            20 + len(resource),
        ),
        ContextualSemanticRoleMention(
            ContextualSemanticRole.CAPABILITY,
            capability,
            50,
            50 + len(capability),
        ),
    )
    slots = (
        ContextualSemanticSlot(
            ContextualSemanticRole.DEPENDENT,
            ContextualSemanticRelation.DEPENDENCY,
            "exclusive",
            "exclusive dependency",
            80,
            100,
        ),
        ContextualSemanticSlot(
            ContextualSemanticRole.RESOURCE,
            ContextualSemanticRelation.AVAILABILITY,
            "unavailable",
            "resource unavailable",
            101,
            121,
        ),
        ContextualSemanticSlot(
            ContextualSemanticRole.DEPENDENT,
            ContextualSemanticRelation.ALTERNATIVE,
            "absent",
            "no alternative",
            122,
            136,
        ),
        ContextualSemanticSlot(
            ContextualSemanticRole.DEPENDENT,
            ContextualSemanticRelation.CAPABILITY,
            "unavailable",
            "capability unavailable",
            137,
            159,
        ),
    )
    return GovernedContextualSemanticGroundingCandidate(
        status=ContextualSemanticGroundingStatus.GROUNDED,
        source_reference="conversation:target-domain",
        scope_reference=SCOPE,
        source_candidate_fingerprint="candidate:target-domain",
        family_id="exclusive_dependency_capability_loss_v1",
        role_mentions=roles,
        semantic_slots=slots,
        rationale_codes=("test:target_grounded",),
        source_fingerprint="target-structural-fingerprint",
    )


def test_recalled_rule_memory_projects_to_certified_semantic_structure() -> None:
    result = GovernedRecalledKnowledgeStructuralProjector().project(
        recall_result=_recall(_item(1, NERAL_MEMORY)),
        scope_reference=SCOPE,
    )

    assert (
        result.normalized_status
        is RecalledKnowledgeStructuralProjectionStatus.PROJECTED
    )
    assert len(result.items) == 1
    projected = result.items[0]
    assert projected.memory_id == 1
    assert projected.memory_category == LearningCategory.STABLE_KNOWLEDGE.value
    assert (
        projected.grounding.normalized_status
        is ContextualSemanticGroundingStatus.GROUNDED
    )
    assert projected.grounding.family_id == "exclusive_dependency_capability_loss_v1"
    assert projected.grounding.source_reference.startswith("cognitive-memory:1:")


def test_projection_and_rc1_match_form_read_only_cross_domain_chain() -> None:
    projection = GovernedRecalledKnowledgeStructuralProjector().project(
        recall_result=_recall(_item(1, NERAL_MEMORY)),
        scope_reference=SCOPE,
    )

    transfer = GovernedStructuralKnowledgeTransferMatcher().match(
        target=_target_dependency(),
        known=projection.groundings,
        scope_reference=SCOPE,
    )

    assert (
        transfer.normalized_status
        is StructuralKnowledgeTransferStatus.TRANSFER_CANDIDATE
    )
    assert len(transfer.correspondences) == 3
    assert transfer.correspondences[0].target_text == "misión orbital"
    assert transfer.correspondences[1].target_text == "ventana de lanzamiento"


def test_relevant_but_non_structural_memory_is_unsupported() -> None:
    result = GovernedRecalledKnowledgeStructuralProjector().project(
        recall_result=_recall(
            _item(2, "Prefiero respuestas breves cuando trabajamos en ROBY.")
        ),
        scope_reference=SCOPE,
    )

    assert (
        result.normalized_status
        is RecalledKnowledgeStructuralProjectionStatus.UNSUPPORTED
    )
    assert result.items == ()
    assert result.rejected_memory_ids == (2,)


def test_ambiguous_memory_exposes_no_partial_grounding() -> None:
    result = GovernedRecalledKnowledgeStructuralProjector().project(
        recall_result=_recall(_item(3, VELAR_AMBIGUOUS_MEMORY)),
        scope_reference=SCOPE,
    )

    assert (
        result.normalized_status
        is RecalledKnowledgeStructuralProjectionStatus.AMBIGUOUS
    )
    assert result.items == ()
    assert result.ambiguous_memory_ids == (3,)


def test_no_recall_signal_is_insufficient() -> None:
    recall = CognitiveMemoryRecallResult(
        should_use_memory=False,
        items=(),
        reason="no_relevant_memory",
    )

    result = GovernedRecalledKnowledgeStructuralProjector().project(
        recall_result=recall,
        scope_reference=SCOPE,
    )

    assert (
        result.normalized_status
        is RecalledKnowledgeStructuralProjectionStatus.INSUFFICIENT
    )
    assert result.groundings == ()


def test_projection_is_bounded_to_first_five_recalled_items() -> None:
    recall = _recall(
        *tuple(_item(index, NERAL_MEMORY) for index in range(1, 7))
    )

    result = GovernedRecalledKnowledgeStructuralProjector().project(
        recall_result=recall,
        scope_reference=SCOPE,
    )

    assert result.considered_memory_ids == (1, 2, 3, 4, 5)
    assert tuple(item.memory_id for item in result.items) == (1, 2, 3, 4, 5)
    assert result.max_recalled_items == 5


def test_projector_does_not_mutate_recalled_memory_metadata() -> None:
    memory = _record(7, NERAL_MEMORY)
    item = CognitiveMemoryRecallItem(
        memory=memory,
        score=0.8,
        matched_signals=("deep_reasoning",),
    )
    before = dict(memory.metadata)

    GovernedRecalledKnowledgeStructuralProjector().project(
        recall_result=_recall(item),
        scope_reference=SCOPE,
    )

    assert memory.metadata == before
    assert memory.access_count == 0
    assert memory.last_accessed_at is None


def test_projected_result_has_no_memory_learning_or_inference_authority() -> None:
    result = GovernedRecalledKnowledgeStructuralProjector().project(
        recall_result=_recall(_item(8, NERAL_MEMORY)),
        scope_reference=SCOPE,
    )

    assert result.canonical_authority == "governed_reasoning"
    assert result.read_only is True
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


def test_projection_is_deterministic_and_immutable() -> None:
    projector = GovernedRecalledKnowledgeStructuralProjector()
    recall = _recall(_item(9, NERAL_MEMORY))

    first = projector.project(recall_result=recall, scope_reference=SCOPE)
    second = projector.project(recall_result=recall, scope_reference=SCOPE)

    assert first == second
    with pytest.raises(FrozenInstanceError):
        first.scope_reference = "changed"  # type: ignore[misc]


def test_actual_cognitive_recall_can_feed_projection_without_shared_query_words(
    tmp_path,
) -> None:
    store = CognitiveMemoryStore(
        CognitiveMemoryStoreConfig(db_path=tmp_path / "cognitive.db")
    )
    candidate = LearningCandidate(
        content=NERAL_MEMORY,
        category=LearningCategory.STABLE_KNOWLEDGE,
        action=LearningAction.STORE,
        confidence=0.9,
        reason="stable structural knowledge",
        tags=("deep_reasoning",),
        metadata={"source": "rc-1.1-test"},
    )
    store.store_candidate(candidate)
    recall = CognitiveMemoryRecall(store).recall(
        request=CognitiveMemoryRecallRequest(
            text="Analizá una misión orbital y su ventana de lanzamiento.",
            intent_result=CognitiveIntentResult(
                intent=CognitiveIntent.DEEP_REASONING,
                confidence=0.95,
                normalized_text=(
                    "analizá una misión orbital y su ventana de lanzamiento"
                ),
            ),
            limit=5,
            minimum_score=0.3,
        )
    )

    assert recall.should_use_memory is True
    assert recall.items
    projection = GovernedRecalledKnowledgeStructuralProjector().project(
        recall_result=recall,
        scope_reference=SCOPE,
    )
    assert (
        projection.normalized_status
        is RecalledKnowledgeStructuralProjectionStatus.PROJECTED
    )


def test_mixed_recall_projects_supported_items_and_records_rejections() -> None:
    result = GovernedRecalledKnowledgeStructuralProjector().project(
        recall_result=_recall(
            _item(10, "Una nota doméstica sin estructura de regla."),
            _item(11, NERAL_MEMORY),
        ),
        scope_reference=SCOPE,
    )

    assert (
        result.normalized_status
        is RecalledKnowledgeStructuralProjectionStatus.PROJECTED
    )
    assert tuple(item.memory_id for item in result.items) == (11,)
    assert result.rejected_memory_ids == (10,)
