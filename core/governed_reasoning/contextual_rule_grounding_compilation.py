from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.governed_reasoning.contextual_claim_normalization import (
    ContextualClaimNormalizationStatus,
    GovernedContextualClaimCandidate,
    GovernedContextualClaimNormalizer,
)
from core.governed_reasoning.contextual_predicate_vocabulary import (
    ContextualPredicateAlias,
    TemporaryContextualPredicateEntrySpec,
    TemporaryContextualPredicateVocabulary,
    TemporaryContextualPredicateVocabularyFactory,
)
from core.governed_reasoning.contextual_rule_instantiation import (
    ContextualRuleConclusionTemplate,
    ContextualRuleConditionTemplate,
    ContextualRuleInstantiationSpec,
)
from core.governed_reasoning.contextual_rule_interpretation import (
    ContextualRuleCandidateStatus,
    GovernedContextualRuleCandidate,
)
from core.governed_reasoning.contextual_semantic_grounding import (
    ContextualSemanticGroundingStatus,
    ContextualSemanticRelation,
    ContextualSemanticRole,
    ContextualSemanticSlot,
    GovernedContextualSemanticGroundingCandidate,
)

_SCHEMA_VERSION = "post-m409.1-contextual-rule-grounding-compilation-v1"
_FAMILY_ID = "exclusive_dependency_capability_loss_v1"
_VELAR_FAMILY_ID = "relational_prerequisite_capability_block_v1"


class ContextualRuleGroundingCompilationStatus(StrEnum):
    COMPILED = "compiled"
    AMBIGUOUS = "ambiguous"
    INSUFFICIENT = "insufficient"
    UNSUPPORTED = "unsupported"
    SCOPE_MISMATCH = "scope_mismatch"
    PROVENANCE_MISMATCH = "provenance_mismatch"


@dataclass(frozen=True)
class GovernedContextualRuleGroundingCompilation:
    status: ContextualRuleGroundingCompilationStatus | str
    source_rule_candidate_fingerprint: str
    semantic_grounding_fingerprint: str
    source_reference: str
    scope_reference: str
    vocabulary: TemporaryContextualPredicateVocabulary | None
    normalized_conditions: tuple[GovernedContextualClaimCandidate, ...]
    normalized_conclusion: GovernedContextualClaimCandidate | None
    instantiation_spec: ContextualRuleInstantiationSpec | None
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
        status = ContextualRuleGroundingCompilationStatus(self.status)
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("grounding compilation must preserve reasoning authority")
        if not self.source_reference.strip() or not self.scope_reference.strip():
            raise ValueError("grounding compilation requires provenance and scope")
        if not self.source_rule_candidate_fingerprint.strip():
            raise ValueError("grounding compilation requires rule fingerprint")
        if not self.semantic_grounding_fingerprint.strip():
            raise ValueError("grounding compilation requires semantic fingerprint")
        if not self.source_fingerprint.strip():
            raise ValueError("grounding compilation requires fingerprint")
        if not self.rationale_codes or any(
            not code.strip() for code in self.rationale_codes
        ):
            raise ValueError("grounding compilation requires rationale codes")
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
            raise ValueError("grounding compilation violates governed limits")
        if status is ContextualRuleGroundingCompilationStatus.COMPILED:
            if self.vocabulary is None or self.instantiation_spec is None:
                raise ValueError("compiled grounding requires vocabulary and spec")
            if not self.normalized_conditions or self.normalized_conclusion is None:
                raise ValueError("compiled grounding requires normalized claims")
        elif any(
            (
                self.vocabulary is not None,
                bool(self.normalized_conditions),
                self.normalized_conclusion is not None,
                self.instantiation_spec is not None,
            )
        ):
            raise ValueError("non-compiled grounding cannot expose partial compilation")

    @property
    def normalized_status(self) -> ContextualRuleGroundingCompilationStatus:
        return ContextualRuleGroundingCompilationStatus(self.status)


class GovernedContextualRuleGroundingCompiler:
    """Compile certified bounded grounding through existing contextual contracts."""

    def __init__(self) -> None:
        self._vocabulary_factory = TemporaryContextualPredicateVocabularyFactory()
        self._normalizer = GovernedContextualClaimNormalizer()

    def compile(
        self,
        *,
        rule_candidate: GovernedContextualRuleCandidate,
        semantic_grounding: GovernedContextualSemanticGroundingCandidate,
        scope_reference: str,
    ) -> GovernedContextualRuleGroundingCompilation:
        if not scope_reference.strip():
            raise ValueError("grounding compilation requires scope")
        mismatch = self._validate_lineage(
            rule_candidate=rule_candidate,
            semantic_grounding=semantic_grounding,
            scope_reference=scope_reference,
        )
        if mismatch is not None:
            return self._result(
                rule_candidate,
                semantic_grounding,
                mismatch[0],
                mismatch[1],
            )
        if (
            rule_candidate.normalized_status
            is not ContextualRuleCandidateStatus.CANDIDATE
        ):
            return self._result(
                rule_candidate,
                semantic_grounding,
                ContextualRuleGroundingCompilationStatus.UNSUPPORTED,
                ("grounding_compilation:rule_candidate_not_compilable",),
            )
        if (
            semantic_grounding.normalized_status
            is not ContextualSemanticGroundingStatus.GROUNDED
        ):
            return self._result(
                rule_candidate,
                semantic_grounding,
                self._status_for_grounding(semantic_grounding),
                ("grounding_compilation:semantic_grounding_not_grounded",),
            )
        if semantic_grounding.family_id not in (_FAMILY_ID, _VELAR_FAMILY_ID):
            return self._result(
                rule_candidate,
                semantic_grounding,
                ContextualRuleGroundingCompilationStatus.UNSUPPORTED,
                ("grounding_compilation:semantic_family_not_supported",),
            )

        slots = self._canonical_slots(
            semantic_grounding.semantic_slots,
            family_id=semantic_grounding.family_id,
        )
        if slots is None:
            return self._result(
                rule_candidate,
                semantic_grounding,
                ContextualRuleGroundingCompilationStatus.UNSUPPORTED,
                ("grounding_compilation:semantic_slots_not_canonical",),
            )
        vocabulary = self._build_vocabulary(
            semantic_grounding=semantic_grounding,
            slots=slots,
        )
        normalized = tuple(
            self._normalize_slot(
                slot,
                vocabulary=vocabulary,
                source_reference=semantic_grounding.source_reference,
                scope_reference=scope_reference,
            )
            for slot in slots
        )
        failed = tuple(
            claim for claim in normalized
            if claim.status is not ContextualClaimNormalizationStatus.CANDIDATE
        )
        if failed:
            status = (
                ContextualRuleGroundingCompilationStatus.AMBIGUOUS
                if any(
                    claim.status is ContextualClaimNormalizationStatus.AMBIGUOUS
                    for claim in failed
                )
                else ContextualRuleGroundingCompilationStatus.UNSUPPORTED
            )
            return self._result(
                rule_candidate,
                semantic_grounding,
                status,
                ("grounding_compilation:claim_normalization_failed",),
            )

        if semantic_grounding.family_id == _VELAR_FAMILY_ID:
            conditions = normalized[:2]
            conclusion = normalized[2]
            spec = ContextualRuleInstantiationSpec(
                rule_candidate_id=f"rule:{rule_candidate.source_fingerprint[:16]}",
                scope_reference=scope_reference,
                vocabulary_id=vocabulary.vocabulary_id,
                source_reference=rule_candidate.source_reference,
                roles=(
                    ContextualSemanticRole.PREREQUISITE.value,
                    ContextualSemanticRole.DEPENDENT.value,
                ),
                conditions=(
                    ContextualRuleConditionTemplate(
                        role_id=conditions[0].subject or "",
                        predicate_id=conditions[0].predicate_id or "",
                        object_role_id=ContextualSemanticRole.DEPENDENT.value,
                    ),
                    ContextualRuleConditionTemplate(
                        role_id=conditions[1].subject or "",
                        predicate_id=conditions[1].predicate_id or "",
                        object_value=conditions[1].object_value or "",
                    ),
                ),
                conclusion=ContextualRuleConclusionTemplate(
                    role_id=conclusion.subject or "",
                    predicate_id=conclusion.predicate_id or "",
                    object_value=conclusion.object_value or "",
                ),
            )
        else:
            conditions = normalized[:3]
            conclusion = normalized[3]
            historical_neral = (
                "grammar:bounded_postcondition_v1"
                in rule_candidate.rationale_codes
            )
            availability_entry = vocabulary.entry_by_label("availability")
            if historical_neral and availability_entry is None:
                return self._result(
                    rule_candidate,
                    semantic_grounding,
                    ContextualRuleGroundingCompilationStatus.UNSUPPORTED,
                    ("grounding_compilation:availability_predicate_missing",),
                )
            spec = ContextualRuleInstantiationSpec(
                rule_candidate_id=f"rule:{rule_candidate.source_fingerprint[:16]}",
                scope_reference=scope_reference,
                vocabulary_id=vocabulary.vocabulary_id,
                source_reference=rule_candidate.source_reference,
                roles=(
                    ContextualSemanticRole.DEPENDENT.value,
                    ContextualSemanticRole.RESOURCE.value,
                    ContextualSemanticRole.CAPABILITY.value,
                ),
                conditions=tuple(
                    ContextualRuleConditionTemplate(
                        role_id=claim.subject or "",
                        predicate_id=claim.predicate_id or "",
                        object_value=claim.object_value or "",
                    )
                    for claim in conditions
                ),
                conclusion=ContextualRuleConclusionTemplate(
                    role_id=(
                        ContextualSemanticRole.CAPABILITY.value
                        if historical_neral
                        else (conclusion.subject or "")
                    ),
                    predicate_id=(
                        availability_entry.predicate_id
                        if historical_neral and availability_entry is not None
                        else (conclusion.predicate_id or "")
                    ),
                    object_value=conclusion.object_value or "",
                ),
            )
        return self._result(
            rule_candidate,
            semantic_grounding,
            ContextualRuleGroundingCompilationStatus.COMPILED,
            (
                "grounding_compilation:bounded_family_compiled",
                "grounding_compilation:vocabulary_reused",
                "grounding_compilation:normalization_reused",
                "grounding_compilation:abstract_spec_only",
            ),
            vocabulary=vocabulary,
            conditions=conditions,
            conclusion=conclusion,
            spec=spec,
        )

    @staticmethod
    def _validate_lineage(
        *,
        rule_candidate: GovernedContextualRuleCandidate,
        semantic_grounding: GovernedContextualSemanticGroundingCandidate,
        scope_reference: str,
    ) -> tuple[
        ContextualRuleGroundingCompilationStatus, tuple[str, ...]
    ] | None:
        if (
            rule_candidate.scope_reference != scope_reference
            or semantic_grounding.scope_reference != scope_reference
        ):
            return (
                ContextualRuleGroundingCompilationStatus.SCOPE_MISMATCH,
                ("grounding_compilation:scope_mismatch",),
            )
        if (
            semantic_grounding.source_candidate_fingerprint
            != rule_candidate.source_fingerprint
            or semantic_grounding.source_reference != rule_candidate.source_reference
        ):
            return (
                ContextualRuleGroundingCompilationStatus.PROVENANCE_MISMATCH,
                ("grounding_compilation:provenance_mismatch",),
            )
        return None

    @staticmethod
    def _status_for_grounding(
        semantic_grounding: GovernedContextualSemanticGroundingCandidate,
    ) -> ContextualRuleGroundingCompilationStatus:
        status = semantic_grounding.normalized_status
        if status is ContextualSemanticGroundingStatus.AMBIGUOUS:
            return ContextualRuleGroundingCompilationStatus.AMBIGUOUS
        if status is ContextualSemanticGroundingStatus.INSUFFICIENT:
            return ContextualRuleGroundingCompilationStatus.INSUFFICIENT
        return ContextualRuleGroundingCompilationStatus.UNSUPPORTED

    @staticmethod
    def _canonical_slots(
        slots: tuple[ContextualSemanticSlot, ...],
        *,
        family_id: str,
    ) -> tuple[ContextualSemanticSlot, ...] | None:
        if family_id == _VELAR_FAMILY_ID:
            expected = (
                (
                    ContextualSemanticRole.PREREQUISITE,
                    ContextualSemanticRelation.REQUIRED_FOR,
                    ContextualSemanticRole.DEPENDENT.value,
                ),
                (
                    ContextualSemanticRole.PREREQUISITE,
                    ContextualSemanticRelation.AVAILABILITY,
                    "unavailable",
                ),
                (
                    ContextualSemanticRole.DEPENDENT,
                    ContextualSemanticRelation.CAPABILITY,
                    "unavailable",
                ),
            )
        else:
            expected = (
                (
                    ContextualSemanticRole.DEPENDENT,
                    ContextualSemanticRelation.DEPENDENCY,
                    "exclusive",
                ),
                (
                    ContextualSemanticRole.RESOURCE,
                    ContextualSemanticRelation.AVAILABILITY,
                    "unavailable",
                ),
                (
                    ContextualSemanticRole.DEPENDENT,
                    ContextualSemanticRelation.ALTERNATIVE,
                    "absent",
                ),
                (
                    ContextualSemanticRole.DEPENDENT,
                    ContextualSemanticRelation.CAPABILITY,
                    "unavailable",
                ),
            )
        actual = tuple(
            (
                ContextualSemanticRole(slot.role_id),
                ContextualSemanticRelation(slot.relation),
                slot.value,
            )
            for slot in slots
        )
        return slots if actual == expected else None

    def _build_vocabulary(
        self,
        *,
        semantic_grounding: GovernedContextualSemanticGroundingCandidate,
        slots: tuple[ContextualSemanticSlot, ...],
    ) -> TemporaryContextualPredicateVocabulary:
        specs = tuple(self._entry_spec(slot, semantic_grounding) for slot in slots)
        return self._vocabulary_factory.build(
            scope_reference=semantic_grounding.scope_reference,
            source_reference=semantic_grounding.source_reference,
            entries=specs,
        )

    @staticmethod
    def _entry_spec(
        slot: ContextualSemanticSlot,
        semantic_grounding: GovernedContextualSemanticGroundingCandidate,
    ) -> TemporaryContextualPredicateEntrySpec:
        relation = ContextualSemanticRelation(slot.relation)
        value = (
            "false"
            if relation is ContextualSemanticRelation.ALTERNATIVE
            else slot.value
        )
        return TemporaryContextualPredicateEntrySpec(
            label=relation.value,
            allowed_values=(value,),
            aliases=(ContextualPredicateAlias(slot.source_text, value),),
            source_reference=semantic_grounding.source_reference,
        )

    def _normalize_slot(
        self,
        slot: ContextualSemanticSlot,
        *,
        vocabulary: TemporaryContextualPredicateVocabulary,
        source_reference: str,
        scope_reference: str,
    ) -> GovernedContextualClaimCandidate:
        return self._normalizer.normalize(
            source_text=slot.source_text,
            subject=ContextualSemanticRole(slot.role_id).value,
            predicate_phrase=slot.source_text,
            vocabulary=vocabulary,
            source_reference=source_reference,
            scope_reference=scope_reference,
        )

    @staticmethod
    def _result(
        rule_candidate: GovernedContextualRuleCandidate,
        semantic_grounding: GovernedContextualSemanticGroundingCandidate,
        status: ContextualRuleGroundingCompilationStatus,
        rationale_codes: tuple[str, ...],
        *,
        vocabulary: TemporaryContextualPredicateVocabulary | None = None,
        conditions: tuple[GovernedContextualClaimCandidate, ...] = (),
        conclusion: GovernedContextualClaimCandidate | None = None,
        spec: ContextualRuleInstantiationSpec | None = None,
    ) -> GovernedContextualRuleGroundingCompilation:
        payload = (
            _SCHEMA_VERSION,
            status.value,
            rule_candidate.source_fingerprint,
            semantic_grounding.source_fingerprint,
            rule_candidate.source_reference,
            rule_candidate.scope_reference,
            vocabulary.source_fingerprint if vocabulary else None,
            tuple(claim.source_fingerprint for claim in conditions),
            conclusion.source_fingerprint if conclusion else None,
            spec,
            rationale_codes,
        )
        fingerprint = sha256(repr(payload).encode("utf-8")).hexdigest()
        return GovernedContextualRuleGroundingCompilation(
            status=status,
            source_rule_candidate_fingerprint=rule_candidate.source_fingerprint,
            semantic_grounding_fingerprint=semantic_grounding.source_fingerprint,
            source_reference=rule_candidate.source_reference,
            scope_reference=rule_candidate.scope_reference,
            vocabulary=vocabulary,
            normalized_conditions=conditions,
            normalized_conclusion=conclusion,
            instantiation_spec=spec,
            rationale_codes=rationale_codes,
            source_fingerprint=fingerprint,
        )
