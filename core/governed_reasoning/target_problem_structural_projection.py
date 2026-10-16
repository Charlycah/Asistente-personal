from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.governed_reasoning.contextual_case_grounding import (
    ContextualCaseGroundingStatus,
    GovernedContextualCaseRoleGrounder,
)
from core.governed_reasoning.contextual_rule_instantiation import (
    ContextualRuleConclusionTemplate,
    ContextualRuleConditionTemplate,
    ContextualRuleInstantiationSpec,
)
from core.governed_reasoning.contextual_semantic_grounding import (
    ContextualSemanticRelation,
    ContextualSemanticRole,
)

_SCHEMA_VERSION = "rc-1.2-governed-target-problem-structural-projection-v1"
_FAMILY_ID = "exclusive_dependency_capability_loss_v1"


class TargetProblemStructuralProjectionStatus(StrEnum):
    PROJECTED = "projected"
    AMBIGUOUS = "ambiguous"
    INSUFFICIENT = "insufficient"
    UNSUPPORTED = "unsupported"


@dataclass(frozen=True)
class TargetProblemRoleBinding:
    role_id: ContextualSemanticRole | str
    entity_reference: str
    source_text: str

    def __post_init__(self) -> None:
        ContextualSemanticRole(self.role_id)
        if not self.entity_reference.strip() or not self.source_text.strip():
            raise ValueError("target problem role binding requires concrete text")

    @property
    def normalized_role(self) -> ContextualSemanticRole:
        return ContextualSemanticRole(self.role_id)


@dataclass(frozen=True)
class TargetProblemObservedSlot:
    role_id: ContextualSemanticRole | str
    relation: ContextualSemanticRelation | str
    value: str

    def __post_init__(self) -> None:
        ContextualSemanticRole(self.role_id)
        ContextualSemanticRelation(self.relation)
        if not self.value.strip():
            raise ValueError("target problem observed slot requires a value")


@dataclass(frozen=True)
class GovernedTargetProblemStructuralProjection:
    status: TargetProblemStructuralProjectionStatus | str
    source_reference: str
    scope_reference: str
    family_id: str | None
    role_bindings: tuple[TargetProblemRoleBinding, ...]
    observed_slots: tuple[TargetProblemObservedSlot, ...]
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
        status = TargetProblemStructuralProjectionStatus(self.status)
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("target projection must preserve reasoning authority")
        if not self.source_reference.strip() or not self.scope_reference.strip():
            raise ValueError("target projection requires provenance and scope")
        if not self.rationale_codes or not self.source_fingerprint.strip():
            raise ValueError("target projection requires rationale and fingerprint")
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
            raise ValueError("target projection violates governed limits")
        if status is TargetProblemStructuralProjectionStatus.PROJECTED:
            if self.family_id != _FAMILY_ID:
                raise ValueError("target projection family is not certified")
            if tuple(item.normalized_role for item in self.role_bindings) != (
                ContextualSemanticRole.DEPENDENT,
                ContextualSemanticRole.RESOURCE,
                ContextualSemanticRole.CAPABILITY,
            ):
                raise ValueError("target projection roles are not canonical")
            if len(self.observed_slots) != 3:
                raise ValueError("target projection requires three observed premises")
        elif self.family_id is not None or self.role_bindings or self.observed_slots:
            raise ValueError("non-projected target cannot expose partial structure")

    @property
    def normalized_status(self) -> TargetProblemStructuralProjectionStatus:
        return TargetProblemStructuralProjectionStatus(self.status)


class GovernedTargetProblemStructuralProjector:
    """Project one bounded target problem without projecting its conclusion."""

    FAMILY_ID = _FAMILY_ID

    def __init__(self) -> None:
        self._case_grounder = GovernedContextualCaseRoleGrounder()

    def project(
        self,
        *,
        text: str,
        source_reference: str,
        scope_reference: str,
    ) -> GovernedTargetProblemStructuralProjection:
        if not text.strip():
            raise ValueError("target problem projection requires text")
        if not source_reference.strip() or not scope_reference.strip():
            raise ValueError("target problem projection requires provenance and scope")

        grounding = self._case_grounder.ground(
            case_text=text,
            spec=self._structural_spec(scope_reference, source_reference),
            scope_reference=scope_reference,
            source_reference=source_reference,
        )
        status = grounding.normalized_status
        if status is ContextualCaseGroundingStatus.AMBIGUOUS:
            return self._result(
                status=TargetProblemStructuralProjectionStatus.AMBIGUOUS,
                text=text,
                source_reference=source_reference,
                scope_reference=scope_reference,
                rationale_codes=(
                    "target_projection:case_structure_ambiguous",
                    "target_projection:no_partial_structure_exposed",
                ),
            )
        if status is ContextualCaseGroundingStatus.UNSUPPORTED:
            return self._result(
                status=TargetProblemStructuralProjectionStatus.UNSUPPORTED,
                text=text,
                source_reference=source_reference,
                scope_reference=scope_reference,
                rationale_codes=(
                    "target_projection:case_structure_unsupported",
                    *grounding.rationale_codes,
                ),
            )
        if status is not ContextualCaseGroundingStatus.GROUNDED:
            return self._result(
                status=TargetProblemStructuralProjectionStatus.INSUFFICIENT,
                text=text,
                source_reference=source_reference,
                scope_reference=scope_reference,
                rationale_codes=(
                    "target_projection:explicit_premises_insufficient",
                    *grounding.rationale_codes,
                ),
            )

        bindings = tuple(
            TargetProblemRoleBinding(
                role_id=item.role_id,
                entity_reference=item.entity_reference,
                source_text=item.source_text,
            )
            for item in grounding.bindings
        )
        slots = (
            TargetProblemObservedSlot(
                ContextualSemanticRole.DEPENDENT,
                ContextualSemanticRelation.DEPENDENCY,
                "exclusive",
            ),
            TargetProblemObservedSlot(
                ContextualSemanticRole.RESOURCE,
                ContextualSemanticRelation.AVAILABILITY,
                "unavailable",
            ),
            TargetProblemObservedSlot(
                ContextualSemanticRole.DEPENDENT,
                ContextualSemanticRelation.ALTERNATIVE,
                "absent",
            ),
        )
        return self._result(
            status=TargetProblemStructuralProjectionStatus.PROJECTED,
            text=text,
            source_reference=source_reference,
            scope_reference=scope_reference,
            family_id=self.FAMILY_ID,
            role_bindings=bindings,
            observed_slots=slots,
            rationale_codes=(
                "target_projection:explicit_antecedent_structure_projected",
                "target_projection:conclusion_not_projected",
                "target_projection:read_only_non_authoritative",
            ),
        )

    @staticmethod
    def _structural_spec(
        scope_reference: str,
        source_reference: str,
    ) -> ContextualRuleInstantiationSpec:
        return ContextualRuleInstantiationSpec(
            rule_candidate_id="rc-1.2:target-problem-shape",
            scope_reference=scope_reference,
            vocabulary_id="ctx-vocabulary-rc12target",
            source_reference=source_reference,
            roles=("dependent", "resource", "capability"),
            conditions=(
                ContextualRuleConditionTemplate(
                    "dependent", "ctx-predicate-dependency", "exclusive"
                ),
                ContextualRuleConditionTemplate(
                    "resource", "ctx-predicate-availability", "unavailable"
                ),
                ContextualRuleConditionTemplate(
                    "dependent", "ctx-predicate-alternative", "false"
                ),
            ),
            conclusion=ContextualRuleConclusionTemplate(
                "capability", "ctx-predicate-availability", "unavailable"
            ),
        )

    @staticmethod
    def _result(
        *,
        status: TargetProblemStructuralProjectionStatus,
        text: str,
        source_reference: str,
        scope_reference: str,
        rationale_codes: tuple[str, ...],
        family_id: str | None = None,
        role_bindings: tuple[TargetProblemRoleBinding, ...] = (),
        observed_slots: tuple[TargetProblemObservedSlot, ...] = (),
    ) -> GovernedTargetProblemStructuralProjection:
        payload = repr(
            (
                _SCHEMA_VERSION,
                status.value,
                text,
                source_reference,
                scope_reference,
                family_id,
                role_bindings,
                observed_slots,
                rationale_codes,
            )
        )
        return GovernedTargetProblemStructuralProjection(
            status=status,
            source_reference=source_reference,
            scope_reference=scope_reference,
            family_id=family_id,
            role_bindings=role_bindings,
            observed_slots=observed_slots,
            rationale_codes=rationale_codes,
            source_fingerprint=sha256(payload.encode("utf-8")).hexdigest(),
        )
