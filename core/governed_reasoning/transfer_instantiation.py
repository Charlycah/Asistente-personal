from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.governed_reasoning.contextual_rule_instantiation import (
    ContextualRuleInstantiationStatus,
    ContextualRuleRoleBinding,
    GovernedContextualRuleInstantiationCandidate,
    GovernedContextualRuleInstantiator,
)
from core.governed_reasoning.contextual_semantic_grounding import (
    ContextualSemanticRole,
)
from core.governed_reasoning.recalled_knowledge_structural_projection import (
    RecalledKnowledgeStructuralProjectionItem,
)
from core.governed_reasoning.structural_knowledge_transfer import (
    GovernedStructuralKnowledgeTransferCandidate,
    StructuralKnowledgeTransferStatus,
)
from core.governed_reasoning.target_problem_structural_projection import (
    GovernedTargetProblemStructuralProjection,
    TargetProblemStructuralProjectionStatus,
)

_SCHEMA_VERSION = "rc-1.3-governed-transfer-instantiation-package-v1"


class TransferInstantiationStatus(StrEnum):
    TRANSFER_INSTANTIATED = "transfer_instantiated"
    NO_TRANSFER = "no_transfer"
    AMBIGUOUS = "ambiguous"
    PROVENANCE_MISMATCH = "provenance_mismatch"
    SCOPE_MISMATCH = "scope_mismatch"
    UNSUPPORTED = "unsupported"


@dataclass(frozen=True)
class GovernedTransferInstantiationPackage:
    status: TransferInstantiationStatus | str
    scope_reference: str
    source_memory_id: int
    source_memory_content_fingerprint: str
    source_grounding_fingerprint: str
    source_compilation_fingerprint: str
    transfer_candidate_fingerprint: str
    target_projection_fingerprint: str
    bindings: tuple[ContextualRuleRoleBinding, ...]
    instantiated_candidate: GovernedContextualRuleInstantiationCandidate | None
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
        status = TransferInstantiationStatus(self.status)
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("transfer instantiation must preserve reasoning authority")
        if not self.scope_reference.strip() or self.source_memory_id <= 0:
            raise ValueError("transfer instantiation requires scope and source memory")
        fingerprints = (
            self.source_memory_content_fingerprint,
            self.source_grounding_fingerprint,
            self.source_compilation_fingerprint,
            self.transfer_candidate_fingerprint,
            self.target_projection_fingerprint,
            self.source_fingerprint,
        )
        if any(not item.strip() for item in fingerprints):
            raise ValueError("transfer instantiation requires complete provenance")
        if not self.rationale_codes or any(
            not item.strip() for item in self.rationale_codes
        ):
            raise ValueError("transfer instantiation requires rationale codes")
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
            raise ValueError("transfer instantiation violates governed limits")
        if status is TransferInstantiationStatus.TRANSFER_INSTANTIATED:
            if not self.bindings or self.instantiated_candidate is None:
                raise ValueError(
                    "instantiated transfer requires bindings and candidate"
                )
            if (
                self.instantiated_candidate.status
                is not ContextualRuleInstantiationStatus.INSTANTIATED
            ):
                raise ValueError(
                    "transfer package requires instantiated rule candidate"
                )
        elif self.bindings or self.instantiated_candidate is not None:
            raise ValueError("failed transfer cannot expose executable instantiation")

    @property
    def normalized_status(self) -> TransferInstantiationStatus:
        return TransferInstantiationStatus(self.status)


class GovernedTransferInstantiator:
    """Instantiate one certified structural transfer without admitting it."""

    def __init__(self) -> None:
        self._instantiator = GovernedContextualRuleInstantiator()

    def instantiate(
        self,
        *,
        source: RecalledKnowledgeStructuralProjectionItem,
        transfer: GovernedStructuralKnowledgeTransferCandidate,
        target: GovernedTargetProblemStructuralProjection,
        scope_reference: str,
    ) -> GovernedTransferInstantiationPackage:
        if not scope_reference.strip():
            raise ValueError("transfer instantiation requires scope")

        mismatch = self._scope_mismatch(
            source=source,
            transfer=transfer,
            target=target,
            scope_reference=scope_reference,
        )
        if mismatch:
            return self._result(
                status=TransferInstantiationStatus.SCOPE_MISMATCH,
                source=source,
                transfer=transfer,
                target=target,
                scope_reference=scope_reference,
                rationale_codes=("transfer_instantiation:scope_mismatch",),
            )

        if transfer.normalized_status is StructuralKnowledgeTransferStatus.AMBIGUOUS:
            return self._result(
                status=TransferInstantiationStatus.AMBIGUOUS,
                source=source,
                transfer=transfer,
                target=target,
                scope_reference=scope_reference,
                rationale_codes=(
                    "transfer_instantiation:structural_transfer_ambiguous",
                    "transfer_instantiation:no_executable_candidate_exposed",
                ),
            )
        if (
            transfer.normalized_status
            is not StructuralKnowledgeTransferStatus.TRANSFER_CANDIDATE
        ):
            return self._result(
                status=TransferInstantiationStatus.NO_TRANSFER,
                source=source,
                transfer=transfer,
                target=target,
                scope_reference=scope_reference,
                rationale_codes=("transfer_instantiation:no_transfer_candidate",),
            )
        if (
            target.normalized_status
            is not TargetProblemStructuralProjectionStatus.PROJECTED
        ):
            return self._result(
                status=TransferInstantiationStatus.UNSUPPORTED,
                source=source,
                transfer=transfer,
                target=target,
                scope_reference=scope_reference,
                rationale_codes=("transfer_instantiation:target_not_projected",),
            )

        if not self._lineage_matches(source=source, transfer=transfer, target=target):
            return self._result(
                status=TransferInstantiationStatus.PROVENANCE_MISMATCH,
                source=source,
                transfer=transfer,
                target=target,
                scope_reference=scope_reference,
                rationale_codes=(
                    "transfer_instantiation:lineage_mismatch",
                    "transfer_instantiation:no_executable_candidate_exposed",
                ),
            )

        spec = source.compilation.instantiation_spec
        if spec is None:
            return self._result(
                status=TransferInstantiationStatus.UNSUPPORTED,
                source=source,
                transfer=transfer,
                target=target,
                scope_reference=scope_reference,
                rationale_codes=("transfer_instantiation:source_spec_missing",),
            )

        bindings = tuple(
            ContextualRuleRoleBinding(
                role_id=item.normalized_role.value,
                entity_reference=item.entity_reference,
                source_reference=target.source_reference,
                source_text=item.source_text,
            )
            for item in target.role_bindings
        )
        instantiated = self._instantiator.instantiate(
            spec=spec,
            bindings=bindings,
            scope_reference=scope_reference,
        )
        if instantiated.status is not ContextualRuleInstantiationStatus.INSTANTIATED:
            return self._result(
                status=TransferInstantiationStatus.UNSUPPORTED,
                source=source,
                transfer=transfer,
                target=target,
                scope_reference=scope_reference,
                rationale_codes=(
                    "transfer_instantiation:canonical_instantiator_rejected",
                    *instantiated.rationale_codes,
                ),
            )

        return self._result(
            status=TransferInstantiationStatus.TRANSFER_INSTANTIATED,
            source=source,
            transfer=transfer,
            target=target,
            scope_reference=scope_reference,
            bindings=bindings,
            instantiated_candidate=instantiated,
            rationale_codes=(
                "transfer_instantiation:source_compilation_reused",
                "transfer_instantiation:target_bindings_reused",
                "transfer_instantiation:canonical_instantiator_reused",
                "transfer_instantiation:not_admitted",
            ),
        )

    @staticmethod
    def _scope_mismatch(
        *,
        source: RecalledKnowledgeStructuralProjectionItem,
        transfer: GovernedStructuralKnowledgeTransferCandidate,
        target: GovernedTargetProblemStructuralProjection,
        scope_reference: str,
    ) -> bool:
        return any(
            item != scope_reference
            for item in (
                source.grounding.scope_reference,
                source.compilation.scope_reference,
                transfer.scope_reference,
                target.scope_reference,
            )
        )

    @staticmethod
    def _lineage_matches(
        *,
        source: RecalledKnowledgeStructuralProjectionItem,
        transfer: GovernedStructuralKnowledgeTransferCandidate,
        target: GovernedTargetProblemStructuralProjection,
    ) -> bool:
        if transfer.target_source_fingerprint != target.source_fingerprint:
            return False
        if transfer.matched_source_fingerprints != (
            source.grounding.source_fingerprint,
        ):
            return False
        if source.compilation.semantic_grounding_fingerprint != (
            source.grounding.source_fingerprint
        ):
            return False
        if source.compilation.instantiation_spec is None:
            return False
        if (
            source.compilation.instantiation_spec.scope_reference
            != target.scope_reference
        ):
            return False
        source_roles = {
            ContextualSemanticRole(item.role_id): item
            for item in source.grounding.role_mentions
        }
        target_roles = {item.normalized_role: item for item in target.role_bindings}
        if set(source_roles) != set(target_roles):
            return False
        expected = tuple(
            (
                item.normalized_role,
                source_roles[item.normalized_role].source_text,
                target_roles[item.normalized_role].entity_reference,
            )
            for item in transfer.correspondences
        )
        actual = tuple(
            (item.normalized_role, item.source_text, item.target_text)
            for item in transfer.correspondences
        )
        return expected == actual

    @staticmethod
    def _result(
        *,
        status: TransferInstantiationStatus,
        source: RecalledKnowledgeStructuralProjectionItem,
        transfer: GovernedStructuralKnowledgeTransferCandidate,
        target: GovernedTargetProblemStructuralProjection,
        scope_reference: str,
        rationale_codes: tuple[str, ...],
        bindings: tuple[ContextualRuleRoleBinding, ...] = (),
        instantiated_candidate: (
            GovernedContextualRuleInstantiationCandidate | None
        ) = None,
    ) -> GovernedTransferInstantiationPackage:
        payload = repr(
            (
                _SCHEMA_VERSION,
                status.value,
                scope_reference,
                source.memory_id,
                source.memory_content_fingerprint,
                source.grounding.source_fingerprint,
                source.compilation.source_fingerprint,
                transfer.source_fingerprint,
                target.source_fingerprint,
                bindings,
                (
                    instantiated_candidate.source_fingerprint
                    if instantiated_candidate is not None
                    else None
                ),
                rationale_codes,
            )
        )
        return GovernedTransferInstantiationPackage(
            status=status,
            scope_reference=scope_reference,
            source_memory_id=source.memory_id,
            source_memory_content_fingerprint=source.memory_content_fingerprint,
            source_grounding_fingerprint=source.grounding.source_fingerprint,
            source_compilation_fingerprint=source.compilation.source_fingerprint,
            transfer_candidate_fingerprint=transfer.source_fingerprint,
            target_projection_fingerprint=target.source_fingerprint,
            bindings=bindings,
            instantiated_candidate=instantiated_candidate,
            rationale_codes=rationale_codes,
            source_fingerprint=sha256(payload.encode("utf-8")).hexdigest(),
        )
