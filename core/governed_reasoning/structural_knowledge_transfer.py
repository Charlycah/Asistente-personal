from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.governed_reasoning.contextual_semantic_grounding import (
    ContextualSemanticGroundingStatus,
    ContextualSemanticRelation,
    ContextualSemanticRole,
    GovernedContextualSemanticGroundingCandidate,
)
from core.governed_reasoning.target_problem_structural_projection import (
    GovernedTargetProblemStructuralProjection,
    TargetProblemStructuralProjectionStatus,
)

_SCHEMA_VERSION = "rc-1-governed-structural-knowledge-transfer-candidate-v1"


class StructuralKnowledgeTransferStatus(StrEnum):
    NO_TRANSFER = "no_transfer"
    TRANSFER_CANDIDATE = "transfer_candidate"
    AMBIGUOUS = "ambiguous"


@dataclass(frozen=True)
class StructuralRoleCorrespondence:
    role_id: ContextualSemanticRole | str
    source_text: str
    target_text: str

    def __post_init__(self) -> None:
        ContextualSemanticRole(self.role_id)
        if not self.source_text.strip() or not self.target_text.strip():
            raise ValueError("structural role correspondence requires concrete texts")

    @property
    def normalized_role(self) -> ContextualSemanticRole:
        return ContextualSemanticRole(self.role_id)


@dataclass(frozen=True)
class GovernedStructuralKnowledgeTransferCandidate:
    status: StructuralKnowledgeTransferStatus | str
    scope_reference: str
    target_source_fingerprint: str
    matched_source_fingerprints: tuple[str, ...]
    family_id: str | None
    correspondences: tuple[StructuralRoleCorrespondence, ...]
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = _SCHEMA_VERSION
    canonical_authority: str = "governed_reasoning"
    read_only: bool = True
    session_local: bool = True
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
        status = StructuralKnowledgeTransferStatus(self.status)
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("structural transfer must preserve reasoning authority")
        if not self.scope_reference.strip():
            raise ValueError("structural transfer requires scope")
        if (
            not self.target_source_fingerprint.strip()
            or not self.source_fingerprint.strip()
        ):
            raise ValueError("structural transfer requires provenance")
        if not self.rationale_codes or any(
            not item.strip() for item in self.rationale_codes
        ):
            raise ValueError("structural transfer requires rationale codes")
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
            raise ValueError("structural transfer violates governed limits")
        if status is StructuralKnowledgeTransferStatus.TRANSFER_CANDIDATE:
            if len(self.matched_source_fingerprints) != 1:
                raise ValueError("transfer candidate requires one matched source")
            if not self.family_id or not self.correspondences:
                raise ValueError("transfer candidate requires family and mapping")
        elif status is StructuralKnowledgeTransferStatus.AMBIGUOUS:
            if len(self.matched_source_fingerprints) < 2:
                raise ValueError("ambiguous transfer requires multiple matches")
            if self.correspondences:
                raise ValueError("ambiguous transfer cannot expose one mapping")
        else:
            if self.matched_source_fingerprints or self.correspondences:
                raise ValueError("no-transfer result cannot expose a match")

    @property
    def normalized_status(self) -> StructuralKnowledgeTransferStatus:
        return StructuralKnowledgeTransferStatus(self.status)


class GovernedStructuralKnowledgeTransferMatcher:
    """Recognize one bounded structural-transfer candidate without applying it."""

    def match(
        self,
        *,
        target: GovernedContextualSemanticGroundingCandidate,
        known: tuple[GovernedContextualSemanticGroundingCandidate, ...],
        scope_reference: str,
    ) -> GovernedStructuralKnowledgeTransferCandidate:
        if not scope_reference.strip():
            raise ValueError("structural transfer requires scope")
        if target.scope_reference != scope_reference:
            return self._result(
                target=target,
                scope_reference=scope_reference,
                status=StructuralKnowledgeTransferStatus.NO_TRANSFER,
                rationale_codes=("structural_transfer:target_scope_mismatch",),
            )
        if target.normalized_status is not ContextualSemanticGroundingStatus.GROUNDED:
            return self._result(
                target=target,
                scope_reference=scope_reference,
                status=StructuralKnowledgeTransferStatus.NO_TRANSFER,
                rationale_codes=("structural_transfer:target_not_grounded",),
            )

        target_signature = self._signature(target)
        matches = tuple(
            item
            for item in known
            if (
                item.scope_reference == scope_reference
                and item.normalized_status is ContextualSemanticGroundingStatus.GROUNDED
                and item.source_fingerprint != target.source_fingerprint
                and self._signature(item) == target_signature
            )
        )
        if not matches:
            return self._result(
                target=target,
                scope_reference=scope_reference,
                status=StructuralKnowledgeTransferStatus.NO_TRANSFER,
                rationale_codes=(
                    "structural_transfer:no_compatible_structure",
                    "structural_transfer:text_similarity_not_sufficient",
                ),
            )
        if len(matches) > 1:
            return self._result(
                target=target,
                scope_reference=scope_reference,
                status=StructuralKnowledgeTransferStatus.AMBIGUOUS,
                rationale_codes=(
                    "structural_transfer:multiple_compatible_structures",
                    "structural_transfer:review_required_before_use",
                ),
                matched=matches,
            )

        source = matches[0]
        source_roles = {
            ContextualSemanticRole(item.role_id): item for item in source.role_mentions
        }
        target_roles = {
            ContextualSemanticRole(item.role_id): item for item in target.role_mentions
        }
        correspondences = tuple(
            StructuralRoleCorrespondence(
                role_id=role,
                source_text=source_roles[role].source_text,
                target_text=target_roles[role].source_text,
            )
            for role in target_roles
        )
        return self._result(
            target=target,
            scope_reference=scope_reference,
            status=StructuralKnowledgeTransferStatus.TRANSFER_CANDIDATE,
            rationale_codes=(
                "structural_transfer:canonical_signature_match",
                "structural_transfer:role_correspondence_explicit",
                "structural_transfer:candidate_only_non_authoritative",
            ),
            matched=matches,
            correspondences=correspondences,
        )

    def match_target_problem(
        self,
        *,
        target: GovernedTargetProblemStructuralProjection,
        known: tuple[GovernedContextualSemanticGroundingCandidate, ...],
        scope_reference: str,
    ) -> GovernedStructuralKnowledgeTransferCandidate:
        if not scope_reference.strip():
            raise ValueError("structural transfer requires scope")
        if target.scope_reference != scope_reference:
            return self._problem_result(
                target=target,
                scope_reference=scope_reference,
                status=StructuralKnowledgeTransferStatus.NO_TRANSFER,
                rationale_codes=("structural_transfer:target_scope_mismatch",),
            )
        if (
            target.normalized_status
            is not TargetProblemStructuralProjectionStatus.PROJECTED
        ):
            return self._problem_result(
                target=target,
                scope_reference=scope_reference,
                status=StructuralKnowledgeTransferStatus.NO_TRANSFER,
                rationale_codes=("structural_transfer:target_problem_not_projected",),
            )

        target_signature = self._target_problem_signature(target)
        matches = tuple(
            item
            for item in known
            if (
                item.scope_reference == scope_reference
                and item.normalized_status is ContextualSemanticGroundingStatus.GROUNDED
                and self._antecedent_signature(item) == target_signature
            )
        )
        if not matches:
            return self._problem_result(
                target=target,
                scope_reference=scope_reference,
                status=StructuralKnowledgeTransferStatus.NO_TRANSFER,
                rationale_codes=(
                    "structural_transfer:no_compatible_antecedent_structure",
                    "structural_transfer:conclusion_not_required_in_target",
                ),
            )
        if len(matches) > 1:
            return self._problem_result(
                target=target,
                scope_reference=scope_reference,
                status=StructuralKnowledgeTransferStatus.AMBIGUOUS,
                rationale_codes=(
                    "structural_transfer:multiple_compatible_structures",
                    "structural_transfer:review_required_before_use",
                ),
                matched=matches,
            )

        source = matches[0]
        source_roles = {
            ContextualSemanticRole(item.role_id): item for item in source.role_mentions
        }
        target_roles = {item.normalized_role: item for item in target.role_bindings}
        correspondences = tuple(
            StructuralRoleCorrespondence(
                role_id=role,
                source_text=source_roles[role].source_text,
                target_text=target_roles[role].entity_reference,
            )
            for role in target_roles
        )
        return self._problem_result(
            target=target,
            scope_reference=scope_reference,
            status=StructuralKnowledgeTransferStatus.TRANSFER_CANDIDATE,
            rationale_codes=(
                "structural_transfer:antecedent_signature_match",
                "structural_transfer:target_conclusion_not_assumed",
                "structural_transfer:candidate_only_non_authoritative",
            ),
            matched=matches,
            correspondences=correspondences,
        )

    @staticmethod
    def _antecedent_signature(
        candidate: GovernedContextualSemanticGroundingCandidate,
    ) -> tuple[object, ...] | None:
        if candidate.family_id != "exclusive_dependency_capability_loss_v1":
            return None
        role_ids = tuple(
            ContextualSemanticRole(item.role_id).value
            for item in candidate.role_mentions
        )
        slots = tuple(
            (
                ContextualSemanticRole(item.role_id).value,
                ContextualSemanticRelation(item.relation).value,
                item.value.casefold(),
            )
            for item in candidate.semantic_slots[:3]
        )
        return (candidate.family_id, role_ids, slots)

    @staticmethod
    def _target_problem_signature(
        target: GovernedTargetProblemStructuralProjection,
    ) -> tuple[object, ...]:
        role_ids = tuple(item.normalized_role.value for item in target.role_bindings)
        slots = tuple(
            (
                ContextualSemanticRole(item.role_id).value,
                ContextualSemanticRelation(item.relation).value,
                item.value.casefold(),
            )
            for item in target.observed_slots
        )
        return (target.family_id, role_ids, slots)

    @staticmethod
    def _signature(
        candidate: GovernedContextualSemanticGroundingCandidate,
    ) -> tuple[object, ...]:
        role_ids = tuple(
            ContextualSemanticRole(item.role_id).value
            for item in candidate.role_mentions
        )
        role_values = set(role_ids)
        slots = tuple(
            (
                ContextualSemanticRole(item.role_id).value,
                ContextualSemanticRelation(item.relation).value,
                (
                    f"role:{item.value}"
                    if item.value in role_values
                    else f"literal:{item.value.casefold()}"
                ),
            )
            for item in candidate.semantic_slots
        )
        return (candidate.family_id, role_ids, slots)

    def _problem_result(
        self,
        *,
        target: GovernedTargetProblemStructuralProjection,
        scope_reference: str,
        status: StructuralKnowledgeTransferStatus,
        rationale_codes: tuple[str, ...],
        matched: tuple[GovernedContextualSemanticGroundingCandidate, ...] = (),
        correspondences: tuple[StructuralRoleCorrespondence, ...] = (),
    ) -> GovernedStructuralKnowledgeTransferCandidate:
        matched_fingerprints = tuple(item.source_fingerprint for item in matched)
        family_id = target.family_id if matched else None
        payload = repr(
            (
                _SCHEMA_VERSION,
                "target-problem",
                status.value,
                scope_reference,
                target.source_fingerprint,
                matched_fingerprints,
                family_id,
                correspondences,
                rationale_codes,
            )
        )
        return GovernedStructuralKnowledgeTransferCandidate(
            status=status,
            scope_reference=scope_reference,
            target_source_fingerprint=target.source_fingerprint,
            matched_source_fingerprints=matched_fingerprints,
            family_id=family_id,
            correspondences=correspondences,
            rationale_codes=rationale_codes,
            source_fingerprint=sha256(payload.encode("utf-8")).hexdigest(),
        )

    def _result(
        self,
        *,
        target: GovernedContextualSemanticGroundingCandidate,
        scope_reference: str,
        status: StructuralKnowledgeTransferStatus,
        rationale_codes: tuple[str, ...],
        matched: tuple[GovernedContextualSemanticGroundingCandidate, ...] = (),
        correspondences: tuple[StructuralRoleCorrespondence, ...] = (),
    ) -> GovernedStructuralKnowledgeTransferCandidate:
        matched_fingerprints = tuple(item.source_fingerprint for item in matched)
        family_id = target.family_id if matched else None
        payload = repr(
            (
                _SCHEMA_VERSION,
                status.value,
                scope_reference,
                target.source_fingerprint,
                matched_fingerprints,
                family_id,
                tuple(
                    (
                        item.normalized_role.value,
                        item.source_text,
                        item.target_text,
                    )
                    for item in correspondences
                ),
                rationale_codes,
            )
        )
        return GovernedStructuralKnowledgeTransferCandidate(
            status=status,
            scope_reference=scope_reference,
            target_source_fingerprint=target.source_fingerprint,
            matched_source_fingerprints=matched_fingerprints,
            family_id=family_id,
            correspondences=correspondences,
            rationale_codes=rationale_codes,
            source_fingerprint=sha256(payload.encode("utf-8")).hexdigest(),
        )
