from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.cognitive_memory_recall import (
    CognitiveMemoryRecallItem,
    CognitiveMemoryRecallResult,
)
from core.governed_reasoning.contextual_rule_grounding_compilation import (
    ContextualRuleGroundingCompilationStatus,
    GovernedContextualRuleGroundingCompilation,
    GovernedContextualRuleGroundingCompiler,
)
from core.governed_reasoning.contextual_rule_interpretation import (
    ContextualRuleCandidateStatus,
    GovernedContextualRuleInterpretationProducer,
)
from core.governed_reasoning.contextual_semantic_grounding import (
    ContextualSemanticGroundingStatus,
    GovernedBoundedSemanticRoleRelationGrounder,
    GovernedContextualSemanticGroundingCandidate,
)

_SCHEMA_VERSION = "rc-1.1-governed-recalled-knowledge-structural-projection-v1"


class RecalledKnowledgeStructuralProjectionStatus(StrEnum):
    PROJECTED = "projected"
    UNSUPPORTED = "unsupported"
    AMBIGUOUS = "ambiguous"
    INSUFFICIENT = "insufficient"


@dataclass(frozen=True)
class RecalledKnowledgeStructuralProjectionItem:
    memory_id: int
    memory_content_fingerprint: str
    memory_confidence: float
    recall_score: float
    memory_category: str
    grounding: GovernedContextualSemanticGroundingCandidate
    compilation: GovernedContextualRuleGroundingCompilation
    source_fingerprint: str

    def __post_init__(self) -> None:
        if self.memory_id <= 0:
            raise ValueError("recalled structural projection requires memory id")
        for value in (
            self.memory_content_fingerprint,
            self.memory_category,
            self.source_fingerprint,
        ):
            if not value.strip():
                raise ValueError("recalled structural projection requires provenance")
        if not 0.0 <= self.memory_confidence <= 1.0:
            raise ValueError("memory confidence must be between zero and one")
        if self.recall_score < 0.0:
            raise ValueError("recall score must not be negative")
        if (
            self.grounding.normalized_status
            is not ContextualSemanticGroundingStatus.GROUNDED
        ):
            raise ValueError("projected recalled knowledge requires grounded structure")
        if (
            self.compilation.normalized_status
            is not ContextualRuleGroundingCompilationStatus.COMPILED
        ):
            raise ValueError("projected recalled knowledge requires compiled rule")
        if (
            self.compilation.semantic_grounding_fingerprint
            != self.grounding.source_fingerprint
        ):
            raise ValueError("recalled knowledge compilation lineage mismatch")


@dataclass(frozen=True)
class GovernedRecalledKnowledgeStructuralProjection:
    status: RecalledKnowledgeStructuralProjectionStatus | str
    scope_reference: str
    items: tuple[RecalledKnowledgeStructuralProjectionItem, ...]
    considered_memory_ids: tuple[int, ...]
    rejected_memory_ids: tuple[int, ...]
    ambiguous_memory_ids: tuple[int, ...]
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = _SCHEMA_VERSION
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    session_local: bool = True
    max_recalled_items: int = 5
    persists_results: bool = False
    creates_memory: bool = False
    modifies_memory: bool = False
    creates_learning_candidate: bool = False
    modifies_learning: bool = False
    modifies_world_model: bool = False
    establishes_truth: bool = False
    authorizes_inference: bool = False
    registers_rule: bool = False
    executes_actions: bool = False
    grants_authority: bool = False
    uses_provider: bool = False
    uses_retrieval: bool = False

    def __post_init__(self) -> None:
        status = RecalledKnowledgeStructuralProjectionStatus(self.status)
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("recalled projection must preserve reasoning authority")
        if not self.scope_reference.strip() or not self.source_fingerprint.strip():
            raise ValueError("recalled projection requires scope and provenance")
        if self.max_recalled_items != 5:
            raise ValueError("recalled projection v1 must remain bounded to five items")
        if len(self.considered_memory_ids) > self.max_recalled_items:
            raise ValueError("recalled projection exceeds bounded input size")
        if len(set(self.considered_memory_ids)) != len(self.considered_memory_ids):
            raise ValueError("recalled projection memory ids must be unique")
        if not self.rationale_codes or any(
            not code.strip() for code in self.rationale_codes
        ):
            raise ValueError("recalled projection requires rationale codes")
        exposed_ids = tuple(item.memory_id for item in self.items)
        if any(item_id not in self.considered_memory_ids for item_id in exposed_ids):
            raise ValueError("projected item was not considered")
        if any(
            (
                not self.read_only,
                not self.session_local,
                self.persists_results,
                self.creates_memory,
                self.modifies_memory,
                self.creates_learning_candidate,
                self.modifies_learning,
                self.modifies_world_model,
                self.establishes_truth,
                self.authorizes_inference,
                self.registers_rule,
                self.executes_actions,
                self.grants_authority,
                self.uses_provider,
                self.uses_retrieval,
            )
        ):
            raise ValueError("recalled projection violates governed limits")
        if status is RecalledKnowledgeStructuralProjectionStatus.PROJECTED:
            if not self.items:
                raise ValueError("projected result requires structural items")
        elif self.items:
            raise ValueError("non-projected result cannot expose structural items")

    @property
    def normalized_status(self) -> RecalledKnowledgeStructuralProjectionStatus:
        return RecalledKnowledgeStructuralProjectionStatus(self.status)

    @property
    def groundings(
        self,
    ) -> tuple[GovernedContextualSemanticGroundingCandidate, ...]:
        return tuple(item.grounding for item in self.items)


class GovernedRecalledKnowledgeStructuralProjector:
    """Project already-recalled memories into certified bounded structures."""

    MAX_RECALLED_ITEMS = 5

    def __init__(self) -> None:
        self._interpreter = GovernedContextualRuleInterpretationProducer()
        self._grounder = GovernedBoundedSemanticRoleRelationGrounder()
        self._compiler = GovernedContextualRuleGroundingCompiler()

    def project(
        self,
        *,
        recall_result: CognitiveMemoryRecallResult,
        scope_reference: str,
    ) -> GovernedRecalledKnowledgeStructuralProjection:
        if not scope_reference.strip():
            raise ValueError("recalled structural projection requires scope")

        recalled = recall_result.items[: self.MAX_RECALLED_ITEMS]
        considered_ids = tuple(item.memory.id for item in recalled)
        if not recall_result.should_use_memory or not recalled:
            return self._result(
                status=RecalledKnowledgeStructuralProjectionStatus.INSUFFICIENT,
                scope_reference=scope_reference,
                considered_memory_ids=considered_ids,
                rationale_codes=(
                    "recalled_projection:no_recalled_knowledge_candidates",
                    "recalled_projection:read_only_non_authoritative",
                ),
            )

        projected: list[RecalledKnowledgeStructuralProjectionItem] = []
        rejected: list[int] = []
        ambiguous: list[int] = []
        for recalled_item in recalled:
            projection = self._project_item(
                recalled_item,
                scope_reference=scope_reference,
            )
            if isinstance(projection, RecalledKnowledgeStructuralProjectionItem):
                projected.append(projection)
            elif projection == "ambiguous":
                ambiguous.append(recalled_item.memory.id)
            else:
                rejected.append(recalled_item.memory.id)

        if projected:
            return self._result(
                status=RecalledKnowledgeStructuralProjectionStatus.PROJECTED,
                scope_reference=scope_reference,
                considered_memory_ids=considered_ids,
                rejected_memory_ids=tuple(rejected),
                ambiguous_memory_ids=tuple(ambiguous),
                items=tuple(projected),
                rationale_codes=(
                    "recalled_projection:certified_structures_projected",
                    "recalled_projection:memory_provenance_preserved",
                    "recalled_projection:read_only_non_authoritative",
                ),
            )
        if ambiguous:
            return self._result(
                status=RecalledKnowledgeStructuralProjectionStatus.AMBIGUOUS,
                scope_reference=scope_reference,
                considered_memory_ids=considered_ids,
                rejected_memory_ids=tuple(rejected),
                ambiguous_memory_ids=tuple(ambiguous),
                rationale_codes=(
                    "recalled_projection:semantic_projection_ambiguous",
                    "recalled_projection:no_partial_structure_exposed",
                ),
            )
        return self._result(
            status=RecalledKnowledgeStructuralProjectionStatus.UNSUPPORTED,
            scope_reference=scope_reference,
            considered_memory_ids=considered_ids,
            rejected_memory_ids=tuple(rejected),
            rationale_codes=(
                "recalled_projection:no_certified_structural_memory",
                "recalled_projection:text_relevance_not_structural_truth",
            ),
        )

    def _project_item(
        self,
        recalled_item: CognitiveMemoryRecallItem,
        *,
        scope_reference: str,
    ) -> RecalledKnowledgeStructuralProjectionItem | str:
        memory = recalled_item.memory
        content_fingerprint = sha256(memory.content.encode("utf-8")).hexdigest()
        source_reference = f"cognitive-memory:{memory.id}:{content_fingerprint[:16]}"
        candidate = self._interpreter.produce(
            memory.content,
            source_reference=source_reference,
            scope_reference=scope_reference,
        )
        if candidate.normalized_status is ContextualRuleCandidateStatus.AMBIGUOUS:
            return "ambiguous"
        if candidate.normalized_status is not ContextualRuleCandidateStatus.CANDIDATE:
            return "unsupported"

        grounding = self._grounder.ground(
            candidate,
            scope_reference=scope_reference,
        )
        if grounding.normalized_status is ContextualSemanticGroundingStatus.AMBIGUOUS:
            return "ambiguous"
        if (
            grounding.normalized_status
            is not ContextualSemanticGroundingStatus.GROUNDED
        ):
            return "unsupported"

        compilation = self._compiler.compile(
            rule_candidate=candidate,
            semantic_grounding=grounding,
            scope_reference=scope_reference,
        )
        if (
            compilation.normalized_status
            is ContextualRuleGroundingCompilationStatus.AMBIGUOUS
        ):
            return "ambiguous"
        if (
            compilation.normalized_status
            is not ContextualRuleGroundingCompilationStatus.COMPILED
        ):
            return "unsupported"

        payload = repr(
            (
                _SCHEMA_VERSION,
                memory.id,
                content_fingerprint,
                memory.confidence,
                recalled_item.score,
                memory.category.value,
                grounding.source_fingerprint,
                compilation.source_fingerprint,
                scope_reference,
            )
        )
        return RecalledKnowledgeStructuralProjectionItem(
            memory_id=memory.id,
            memory_content_fingerprint=content_fingerprint,
            memory_confidence=memory.confidence,
            recall_score=recalled_item.score,
            memory_category=memory.category.value,
            grounding=grounding,
            compilation=compilation,
            source_fingerprint=sha256(payload.encode("utf-8")).hexdigest(),
        )

    @staticmethod
    def _result(
        *,
        status: RecalledKnowledgeStructuralProjectionStatus,
        scope_reference: str,
        considered_memory_ids: tuple[int, ...],
        rationale_codes: tuple[str, ...],
        rejected_memory_ids: tuple[int, ...] = (),
        ambiguous_memory_ids: tuple[int, ...] = (),
        items: tuple[RecalledKnowledgeStructuralProjectionItem, ...] = (),
    ) -> GovernedRecalledKnowledgeStructuralProjection:
        payload = repr(
            (
                _SCHEMA_VERSION,
                status.value,
                scope_reference,
                considered_memory_ids,
                rejected_memory_ids,
                ambiguous_memory_ids,
                tuple(item.source_fingerprint for item in items),
                rationale_codes,
            )
        )
        return GovernedRecalledKnowledgeStructuralProjection(
            status=status,
            scope_reference=scope_reference,
            items=items,
            considered_memory_ids=considered_memory_ids,
            rejected_memory_ids=rejected_memory_ids,
            ambiguous_memory_ids=ambiguous_memory_ids,
            rationale_codes=rationale_codes,
            source_fingerprint=sha256(payload.encode("utf-8")).hexdigest(),
        )
