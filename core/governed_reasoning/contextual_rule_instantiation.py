from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

_SCHEMA_VERSION = "post-m409.1-object-aware-relational-role-binding-v1"


class ContextualRuleInstantiationStatus(StrEnum):
    INSTANTIATED = "instantiated"
    INSUFFICIENT_BINDINGS = "insufficient_bindings"
    AMBIGUOUS_BINDINGS = "ambiguous_bindings"
    UNSUPPORTED = "unsupported"


@dataclass(frozen=True)
class ContextualRuleRoleBinding:
    role_id: str
    entity_reference: str
    source_reference: str
    source_text: str

    def __post_init__(self) -> None:
        if not self.role_id.strip() or not self.entity_reference.strip():
            raise ValueError("contextual role binding requires role and entity")
        if not self.source_reference.strip() or not self.source_text.strip():
            raise ValueError("contextual role binding requires explicit provenance")


@dataclass(frozen=True)
class ContextualRuleConditionTemplate:
    role_id: str
    predicate_id: str
    object_value: str | None = None
    object_role_id: str | None = None

    def __post_init__(self) -> None:
        if not self.role_id.strip():
            raise ValueError("contextual condition template requires role")
        _validate_predicate(self.predicate_id)
        _validate_template_object(self.object_value, self.object_role_id)


@dataclass(frozen=True)
class ContextualRuleConclusionTemplate:
    role_id: str
    predicate_id: str
    object_value: str | None = None
    object_role_id: str | None = None

    def __post_init__(self) -> None:
        if not self.role_id.strip():
            raise ValueError("contextual conclusion template requires role")
        _validate_predicate(self.predicate_id)
        _validate_template_object(self.object_value, self.object_role_id)


@dataclass(frozen=True)
class ContextualRuleInstantiationSpec:
    rule_candidate_id: str
    scope_reference: str
    vocabulary_id: str
    source_reference: str
    roles: tuple[str, ...]
    conditions: tuple[ContextualRuleConditionTemplate, ...]
    conclusion: ContextualRuleConclusionTemplate

    def __post_init__(self) -> None:
        if not self.rule_candidate_id.strip() or not self.source_reference.strip():
            raise ValueError("contextual rule spec requires identity and provenance")
        if not self.scope_reference.strip():
            raise ValueError("contextual rule spec requires scope")
        if not self.vocabulary_id.startswith("ctx-vocabulary-"):
            raise ValueError("contextual rule spec vocabulary is invalid")
        if not 1 <= len(self.roles) <= 4:
            raise ValueError("contextual rule spec supports one to four roles")
        normalized_roles = tuple(role.strip() for role in self.roles)
        if any(not role for role in normalized_roles):
            raise ValueError("contextual rule roles must not be blank")
        if len(set(normalized_roles)) != len(normalized_roles):
            raise ValueError("contextual rule roles must be unique")
        if not self.conditions:
            raise ValueError("contextual rule spec requires conditions")
        templates = (*self.conditions, self.conclusion)
        referenced_roles = {item.role_id for item in templates}
        referenced_roles.update(
            item.object_role_id
            for item in templates
            if item.object_role_id is not None
        )
        if not referenced_roles.issubset(set(normalized_roles)):
            raise ValueError("contextual rule template references undeclared role")


@dataclass(frozen=True)
class ConcreteContextualRuleCondition:
    subject: str
    predicate_id: str
    object_value: str


@dataclass(frozen=True)
class ConcreteContextualRuleConclusion:
    subject: str
    predicate_id: str
    object_value: str


@dataclass(frozen=True)
class GovernedContextualRuleInstantiationCandidate:
    status: ContextualRuleInstantiationStatus
    source_rule_candidate_id: str
    scope_reference: str
    vocabulary_id: str
    bindings: tuple[ContextualRuleRoleBinding, ...]
    concrete_conditions: tuple[ConcreteContextualRuleCondition, ...]
    concrete_conclusion: ConcreteContextualRuleConclusion | None
    source_references: tuple[str, ...]
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
    establishes_truth: bool = False
    establishes_falsity: bool = False
    authorizes_inference: bool = False
    registers_rule: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        if (
            not self.source_rule_candidate_id.strip()
            or not self.scope_reference.strip()
        ):
            raise ValueError("rule instantiation candidate requires identity and scope")
        if not self.vocabulary_id.startswith("ctx-vocabulary-"):
            raise ValueError("rule instantiation candidate vocabulary is invalid")
        if not self.source_fingerprint.strip() or not self.source_references:
            raise ValueError("rule instantiation candidate requires provenance")
        if self.canonical_authority != "governed_reasoning":
            raise ValueError("rule instantiation must preserve reasoning authority")
        if any(
            (
                not self.read_only,
                not self.session_local,
                self.persists_results,
                self.creates_memory,
                self.modifies_memory,
                self.creates_learning_candidate,
                self.modifies_learning,
                self.establishes_truth,
                self.establishes_falsity,
                self.authorizes_inference,
                self.registers_rule,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError("rule instantiation candidate violates governed limits")
        if self.status is ContextualRuleInstantiationStatus.INSTANTIATED:
            if not self.bindings or not self.concrete_conditions:
                raise ValueError("instantiated rule requires bindings and conditions")
            if self.concrete_conclusion is None:
                raise ValueError("instantiated rule requires concrete conclusion")
        elif self.concrete_conditions or self.concrete_conclusion is not None:
            raise ValueError("non-instantiated result cannot expose executable rule")


class GovernedContextualRuleInstantiator:
    """Instantiate a closed contextual rule from explicit, provenance-bound roles."""

    def instantiate(
        self,
        *,
        spec: ContextualRuleInstantiationSpec,
        bindings: tuple[ContextualRuleRoleBinding, ...],
        scope_reference: str,
    ) -> GovernedContextualRuleInstantiationCandidate:
        if scope_reference != spec.scope_reference:
            raise ValueError("contextual rule instantiation scope mismatch")
        by_role: dict[str, list[ContextualRuleRoleBinding]] = {
            role: [] for role in spec.roles
        }
        for binding in bindings:
            if binding.role_id not in by_role:
                return self._result(
                    spec=spec,
                    status=ContextualRuleInstantiationStatus.UNSUPPORTED,
                    bindings=bindings,
                    rationale_codes=("rule_instantiation:undeclared_role",),
                )
            by_role[binding.role_id].append(binding)

        if any(len(items) > 1 for items in by_role.values()):
            return self._result(
                spec=spec,
                status=ContextualRuleInstantiationStatus.AMBIGUOUS_BINDINGS,
                bindings=bindings,
                rationale_codes=("rule_instantiation:multiple_bindings_for_role",),
            )
        if any(not items for items in by_role.values()):
            return self._result(
                spec=spec,
                status=ContextualRuleInstantiationStatus.INSUFFICIENT_BINDINGS,
                bindings=bindings,
                rationale_codes=("rule_instantiation:required_role_unbound",),
            )

        resolved = {role: items[0] for role, items in by_role.items()}
        concrete_conditions = tuple(
            ConcreteContextualRuleCondition(
                subject=resolved[item.role_id].entity_reference,
                predicate_id=item.predicate_id,
                object_value=_resolve_template_object(
                    object_value=item.object_value,
                    object_role_id=item.object_role_id,
                    resolved=resolved,
                ),
            )
            for item in spec.conditions
        )
        conclusion = ConcreteContextualRuleConclusion(
            subject=resolved[spec.conclusion.role_id].entity_reference,
            predicate_id=spec.conclusion.predicate_id,
            object_value=_resolve_template_object(
                object_value=spec.conclusion.object_value,
                object_role_id=spec.conclusion.object_role_id,
                resolved=resolved,
            ),
        )
        return self._result(
            spec=spec,
            status=ContextualRuleInstantiationStatus.INSTANTIATED,
            bindings=bindings,
            concrete_conditions=concrete_conditions,
            concrete_conclusion=conclusion,
            rationale_codes=("rule_instantiation:explicit_bindings_resolved",),
        )

    @staticmethod
    def _result(
        *,
        spec: ContextualRuleInstantiationSpec,
        status: ContextualRuleInstantiationStatus,
        bindings: tuple[ContextualRuleRoleBinding, ...],
        rationale_codes: tuple[str, ...],
        concrete_conditions: tuple[ConcreteContextualRuleCondition, ...] = (),
        concrete_conclusion: ConcreteContextualRuleConclusion | None = None,
    ) -> GovernedContextualRuleInstantiationCandidate:
        source_references = tuple(
            dict.fromkeys(
                (spec.source_reference, *(item.source_reference for item in bindings))
            )
        )
        payload = (
            _SCHEMA_VERSION,
            status.value,
            spec,
            bindings,
            concrete_conditions,
            concrete_conclusion,
            source_references,
            rationale_codes,
        )
        fingerprint = sha256(repr(payload).encode("utf-8")).hexdigest()
        return GovernedContextualRuleInstantiationCandidate(
            status=status,
            source_rule_candidate_id=spec.rule_candidate_id,
            scope_reference=spec.scope_reference,
            vocabulary_id=spec.vocabulary_id,
            bindings=bindings,
            concrete_conditions=concrete_conditions,
            concrete_conclusion=concrete_conclusion,
            source_references=source_references,
            rationale_codes=rationale_codes,
            source_fingerprint=fingerprint,
        )


def _validate_predicate(predicate_id: str) -> None:
    if not predicate_id.startswith("ctx-predicate-"):
        raise ValueError("contextual rule predicate identifier is invalid")


def _validate_template_object(
    object_value: str | None, object_role_id: str | None
) -> None:
    if object_value is not None and not object_value.strip():
        raise ValueError("contextual rule literal object must not be blank")
    if object_role_id is not None and not object_role_id.strip():
        raise ValueError("contextual rule object role must not be blank")
    if (object_value is None) == (object_role_id is None):
        raise ValueError(
            "contextual rule template requires exactly one object source"
        )


def _resolve_template_object(
    *,
    object_value: str | None,
    object_role_id: str | None,
    resolved: dict[str, ContextualRuleRoleBinding],
) -> str:
    if object_role_id is not None:
        return resolved[object_role_id].entity_reference
    if object_value is None:
        raise ValueError("contextual rule template object is unresolved")
    return object_value
