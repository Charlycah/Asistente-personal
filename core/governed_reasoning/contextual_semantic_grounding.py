from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.governed_reasoning.contextual_rule_interpretation import (
    ContextualRuleCandidateStatus,
    GovernedContextualRuleCandidate,
)

_SCHEMA_VERSION = "post-m409.1-bounded-semantic-role-relation-grounding-v1"


class ContextualSemanticGroundingStatus(StrEnum):
    GROUNDED = "grounded"
    AMBIGUOUS = "ambiguous"
    INSUFFICIENT = "insufficient"
    UNSUPPORTED = "unsupported"


class ContextualSemanticRole(StrEnum):
    DEPENDENT = "dependent"
    RESOURCE = "resource"
    CAPABILITY = "capability"
    PREREQUISITE = "prerequisite"


class ContextualSemanticRelation(StrEnum):
    DEPENDENCY = "dependency"
    AVAILABILITY = "availability"
    ALTERNATIVE = "alternative"
    CAPABILITY = "capability"
    REQUIRED_FOR = "required_for"


@dataclass(frozen=True)
class ContextualSemanticRoleMention:
    role_id: ContextualSemanticRole | str
    source_text: str
    start_offset: int
    end_offset: int

    def __post_init__(self) -> None:
        ContextualSemanticRole(self.role_id)
        if not self.source_text.strip():
            raise ValueError("semantic role mention must not be blank")
        if self.start_offset < 0 or self.end_offset <= self.start_offset:
            raise ValueError("semantic role mention span is invalid")


@dataclass(frozen=True)
class ContextualSemanticSlot:
    role_id: ContextualSemanticRole | str
    relation: ContextualSemanticRelation | str
    value: str
    source_text: str
    start_offset: int
    end_offset: int

    def __post_init__(self) -> None:
        ContextualSemanticRole(self.role_id)
        ContextualSemanticRelation(self.relation)
        if not self.value.strip() or not self.source_text.strip():
            raise ValueError("semantic slot value and source must not be blank")
        if self.start_offset < 0 or self.end_offset <= self.start_offset:
            raise ValueError("semantic slot span is invalid")


@dataclass(frozen=True)
class GovernedContextualSemanticGroundingCandidate:
    status: ContextualSemanticGroundingStatus | str
    source_reference: str
    scope_reference: str
    source_candidate_fingerprint: str
    family_id: str
    role_mentions: tuple[ContextualSemanticRoleMention, ...]
    semantic_slots: tuple[ContextualSemanticSlot, ...]
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
        status = ContextualSemanticGroundingStatus(self.status)
        if self.canonical_authority != "governed_reasoning":
            raise ValueError(
                "semantic grounding must preserve governed reasoning authority"
            )
        if not self.source_reference.strip() or not self.scope_reference.strip():
            raise ValueError("semantic grounding requires provenance and scope")
        if not self.source_candidate_fingerprint.strip():
            raise ValueError("semantic grounding requires candidate fingerprint")
        if not self.family_id.strip() or not self.source_fingerprint.strip():
            raise ValueError("semantic grounding requires family and fingerprint")
        if not self.rationale_codes or any(
            not code.strip() for code in self.rationale_codes
        ):
            raise ValueError("semantic grounding requires rationale codes")
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
            raise ValueError("semantic grounding violates governed limits")
        if status is ContextualSemanticGroundingStatus.GROUNDED:
            roles = tuple(
                ContextualSemanticRole(item.role_id) for item in self.role_mentions
            )
            if self.family_id == GovernedBoundedSemanticRoleRelationGrounder.FAMILY_ID:
                if len(self.role_mentions) != 3 or len(self.semantic_slots) != 4:
                    raise ValueError(
                        "grounded dependency-loss family requires 3 roles and 4 slots"
                    )
                if roles != (
                    ContextualSemanticRole.DEPENDENT,
                    ContextualSemanticRole.RESOURCE,
                    ContextualSemanticRole.CAPABILITY,
                ):
                    raise ValueError("grounded dependency-loss roles are not canonical")
            elif (
                self.family_id
                == GovernedBoundedSemanticRoleRelationGrounder.VELAR_FAMILY_ID
            ):
                if len(self.role_mentions) != 2 or len(self.semantic_slots) != 3:
                    raise ValueError(
                        "grounded relational prerequisite family requires "
                        "2 roles and 3 slots"
                    )
                if roles != (
                    ContextualSemanticRole.PREREQUISITE,
                    ContextualSemanticRole.DEPENDENT,
                ):
                    raise ValueError(
                        "grounded relational prerequisite roles are not canonical"
                    )
            else:
                raise ValueError("grounded semantic family is not certified")
        elif self.role_mentions or self.semantic_slots:
            raise ValueError(
                "non-grounded semantic result cannot expose partial grounding"
            )

    @property
    def normalized_status(self) -> ContextualSemanticGroundingStatus:
        return ContextualSemanticGroundingStatus(self.status)


class GovernedBoundedSemanticRoleRelationGrounder:
    """Ground one bounded exclusive-dependency capability-loss family only."""

    FAMILY_ID = "exclusive_dependency_capability_loss_v1"
    VELAR_FAMILY_ID = "relational_prerequisite_capability_block_v1"

    _VELAR_REQUIRED_FOR_RE = re.compile(
        r"(?is)^(?P<prerequisite>.+?)\s+es\s+requisito\s+indispensable\s+para\s+"
        r"(?P<dependent>.+?)$"
    )
    _VELAR_UNAVAILABLE_RE = re.compile(
        r"(?is)^(?:esa\s+capacidad|la\s+capacidad\s+requisito|el\s+requisito)\s+"
        r"(?:queda|est[aá]|se\s+vuelve)\s+indisponible$"
    )
    _VELAR_BLOCKED_RE = re.compile(
        r"(?is)^(?:la\s+capacidad\s+dependiente|esa\s+otra\s+capacidad|"
        r"la\s+capacidad\s+objetivo)\s+(?:queda\s+)?"
        r"(?:impedida|bloqueada|indisponible)$"
    )
    _VELAR_HISTORICAL_LOSS_RE = re.compile(
        r"(?is)^la\s+p[eé]rdida\s+de\s+(?P<prerequisite_ref>"
        r"[\wáéíóúüñ-]+)$"
    )
    _VELAR_HISTORICAL_BLOCKED_RE = re.compile(
        r"(?is)^impide\s+(?P<dependent_ref>[\wáéíóúüñ-]+)\s+"
        r"mientras\s+siga\s+faltando\s+"
        r"(?P<prerequisite_ref>[\wáéíóúüñ-]+)$"
    )

    _DEPENDENCY_RE = re.compile(
        r"(?is)^(?P<dependent>.+?)\s+depende\s+exclusivamente\s+de\s+"
        r"(?P<resource>.+?)\s+para\s+(?P<capability>.+?)$"
    )
    _RESOURCE_UNAVAILABLE_RE = re.compile(
        r"(?is)^(?:ese\s+recurso|el\s+recurso)\s+"
        r"(?:est[aá]|queda|se\s+vuelve)\s+indisponible$"
    )
    _NO_ALTERNATIVE_RE = re.compile(
        r"(?is)^(?:no\s+existe|no\s+exista|no\s+hay)\s+"
        r"(?:(?:una|ninguna)\s+)?alternativa$"
    )
    _CAPABILITY_LOSS_RE = re.compile(
        r"(?is)^(?:ese\s+sistema|el\s+sistema|el\s+dependiente)\s+"
        r"pierde\s+(?:esa\s+capacidad|la\s+capacidad)$"
    )
    _ROLE_PRONOUN_RE = re.compile(
        r"(?i)\b(?:él|ella|ellos|ellas|esto|eso|aquello)\b"
    )

    def ground(
        self,
        candidate: GovernedContextualRuleCandidate,
        *,
        scope_reference: str,
    ) -> GovernedContextualSemanticGroundingCandidate:
        if not scope_reference.strip():
            raise ValueError("semantic grounding requires scope")
        if candidate.scope_reference != scope_reference:
            raise ValueError("semantic grounding scope mismatch")
        if candidate.normalized_status is not ContextualRuleCandidateStatus.CANDIDATE:
            return self._result(
                candidate,
                ContextualSemanticGroundingStatus.UNSUPPORTED,
                ("candidate:not_groundable_status",),
            )
        if len(candidate.conditions) == 2 and candidate.conclusion is not None:
            velar = self._ground_velar(candidate)
            if velar is not None:
                return velar
        if len(candidate.conditions) != 3 or candidate.conclusion is None:
            return self._result(
                candidate,
                ContextualSemanticGroundingStatus.UNSUPPORTED,
                ("family:requires_three_conditions_one_conclusion",),
            )
        if (
            candidate.conditions[0].negated
            or candidate.conditions[1].negated
            or not candidate.conditions[2].negated
            or candidate.conclusion.negated
        ):
            return self._result(
                candidate,
                ContextualSemanticGroundingStatus.UNSUPPORTED,
                ("family:negation_shape_not_supported",),
            )

        dependency = self._DEPENDENCY_RE.fullmatch(
            candidate.conditions[0].normalized_text
        )
        if dependency is None:
            return self._result(
                candidate,
                ContextualSemanticGroundingStatus.UNSUPPORTED,
                ("family:dependency_clause_not_supported",),
            )
        if self._ROLE_PRONOUN_RE.search(candidate.conditions[0].normalized_text):
            return self._result(
                candidate,
                ContextualSemanticGroundingStatus.AMBIGUOUS,
                ("roles:implicit_reference_in_declaration",),
            )
        if self._RESOURCE_UNAVAILABLE_RE.fullmatch(
            candidate.conditions[1].normalized_text
        ) is None:
            return self._result(
                candidate,
                ContextualSemanticGroundingStatus.UNSUPPORTED,
                ("family:resource_availability_clause_not_supported",),
            )
        if self._NO_ALTERNATIVE_RE.fullmatch(
            candidate.conditions[2].normalized_text
        ) is None:
            return self._result(
                candidate,
                ContextualSemanticGroundingStatus.UNSUPPORTED,
                ("family:alternative_clause_not_supported",),
            )
        if self._CAPABILITY_LOSS_RE.fullmatch(
            candidate.conclusion.normalized_text
        ) is None:
            return self._result(
                candidate,
                ContextualSemanticGroundingStatus.UNSUPPORTED,
                ("family:capability_loss_conclusion_not_supported",),
            )

        roles = self._role_mentions(candidate, dependency)
        if roles is None:
            return self._result(
                candidate,
                ContextualSemanticGroundingStatus.AMBIGUOUS,
                ("roles:source_span_not_unique",),
            )
        slots = self._slots(candidate)
        if slots is None:
            return self._result(
                candidate,
                ContextualSemanticGroundingStatus.AMBIGUOUS,
                ("slots:source_span_not_unique",),
            )
        return self._result(
            candidate,
            ContextualSemanticGroundingStatus.GROUNDED,
            (
                "family:exclusive_dependency_capability_loss_v1",
                "roles:explicit_bounded",
                "slots:explicit_bounded",
                "grounding:read_only_non_authoritative",
            ),
            roles=roles,
            slots=slots,
        )

    def _ground_velar(
        self,
        candidate: GovernedContextualRuleCandidate,
    ) -> GovernedContextualSemanticGroundingCandidate | None:
        if any(condition.negated for condition in candidate.conditions):
            return None
        if candidate.conclusion is None or candidate.conclusion.negated:
            return None
        relation = self._VELAR_REQUIRED_FOR_RE.fullmatch(
            candidate.conditions[0].normalized_text
        )
        if relation is None:
            return None
        prerequisite = relation.group("prerequisite").strip()
        dependent = relation.group("dependent").strip()

        historical_loss = self._VELAR_HISTORICAL_LOSS_RE.fullmatch(
            candidate.conditions[1].normalized_text
        )
        standard_loss = self._VELAR_UNAVAILABLE_RE.fullmatch(
            candidate.conditions[1].normalized_text
        )
        historical_conclusion = self._VELAR_HISTORICAL_BLOCKED_RE.fullmatch(
            candidate.conclusion.normalized_text
        )
        standard_conclusion = self._VELAR_BLOCKED_RE.fullmatch(
            candidate.conclusion.normalized_text
        )

        if standard_loss is None and historical_loss is None:
            return self._result(
                candidate,
                ContextualSemanticGroundingStatus.UNSUPPORTED,
                ("family:relational_prerequisite_availability_not_supported",),
                family_id=self.VELAR_FAMILY_ID,
            )
        if standard_conclusion is None and historical_conclusion is None:
            return self._result(
                candidate,
                ContextualSemanticGroundingStatus.UNSUPPORTED,
                ("family:relational_prerequisite_conclusion_not_supported",),
                family_id=self.VELAR_FAMILY_ID,
            )

        if historical_loss is not None or historical_conclusion is not None:
            if historical_loss is None or historical_conclusion is None:
                return self._result(
                    candidate,
                    ContextualSemanticGroundingStatus.AMBIGUOUS,
                    ("family:historical_velar_shape_mixed",),
                    family_id=self.VELAR_FAMILY_ID,
                )
            prerequisite_ref = historical_loss.group("prerequisite_ref").casefold()
            missing_ref = historical_conclusion.group("prerequisite_ref").casefold()
            dependent_ref = historical_conclusion.group("dependent_ref").casefold()
            prerequisite_token = prerequisite.split()[-1].casefold()
            dependent_token = dependent.split()[-1].casefold()
            if (
                prerequisite_ref != prerequisite_token
                or missing_ref != prerequisite_token
                or dependent_ref != dependent_token
            ):
                return self._result(
                    candidate,
                    ContextualSemanticGroundingStatus.AMBIGUOUS,
                    ("roles:historical_velar_reference_mismatch",),
                    family_id=self.VELAR_FAMILY_ID,
                )
        first = candidate.conditions[0]
        first_start = candidate.source_text.casefold().find(first.raw_text.casefold())
        if first_start < 0:
            return self._result(
                candidate,
                ContextualSemanticGroundingStatus.AMBIGUOUS,
                ("roles:source_span_not_found",),
                family_id=self.VELAR_FAMILY_ID,
            )
        clause = first.raw_text
        pre_local = clause.casefold().find(prerequisite.casefold())
        dep_local = clause.casefold().find(dependent.casefold())
        if (
            pre_local < 0
            or dep_local < 0
            or prerequisite.casefold() == dependent.casefold()
        ):
            return self._result(
                candidate,
                ContextualSemanticGroundingStatus.AMBIGUOUS,
                ("roles:relational_role_binding_ambiguous",),
                family_id=self.VELAR_FAMILY_ID,
            )
        roles = (
            ContextualSemanticRoleMention(
                ContextualSemanticRole.PREREQUISITE,
                prerequisite,
                first_start + pre_local,
                first_start + pre_local + len(prerequisite),
            ),
            ContextualSemanticRoleMention(
                ContextualSemanticRole.DEPENDENT,
                dependent,
                first_start + dep_local,
                first_start + dep_local + len(dependent),
            ),
        )
        slots = self._velar_slots(candidate)
        if slots is None:
            return self._result(
                candidate,
                ContextualSemanticGroundingStatus.AMBIGUOUS,
                ("slots:source_span_not_unique",),
                family_id=self.VELAR_FAMILY_ID,
            )
        return self._result(
            candidate,
            ContextualSemanticGroundingStatus.GROUNDED,
            (
                "family:relational_prerequisite_capability_block_v1",
                "roles:explicit_relational_bounded",
                "slots:explicit_relational_bounded",
                "grounding:read_only_non_authoritative",
            ),
            roles=roles,
            slots=slots,
            family_id=self.VELAR_FAMILY_ID,
        )

    def _velar_slots(
        self,
        candidate: GovernedContextualRuleCandidate,
    ) -> tuple[ContextualSemanticSlot, ...] | None:
        assert candidate.conclusion is not None
        specs = (
            (
                ContextualSemanticRole.PREREQUISITE,
                ContextualSemanticRelation.REQUIRED_FOR,
                ContextualSemanticRole.DEPENDENT.value,
                candidate.conditions[0].raw_text,
            ),
            (
                ContextualSemanticRole.PREREQUISITE,
                ContextualSemanticRelation.AVAILABILITY,
                "unavailable",
                candidate.conditions[1].raw_text,
            ),
            (
                ContextualSemanticRole.DEPENDENT,
                ContextualSemanticRelation.CAPABILITY,
                "unavailable",
                candidate.conclusion.raw_text,
            ),
        )
        slots = []
        for role, relation, value, source_text in specs:
            span = self._unique_span(candidate, source_text)
            if span is None:
                return None
            slots.append(
                ContextualSemanticSlot(
                    role_id=role,
                    relation=relation,
                    value=value,
                    source_text=source_text,
                    start_offset=span[0],
                    end_offset=span[1],
                )
            )
        return tuple(slots)

    def _role_mentions(
        self,
        candidate: GovernedContextualRuleCandidate,
        dependency: re.Match[str],
    ) -> tuple[ContextualSemanticRoleMention, ...] | None:
        role_values = (
            (ContextualSemanticRole.DEPENDENT, dependency.group("dependent")),
            (ContextualSemanticRole.RESOURCE, dependency.group("resource")),
            (ContextualSemanticRole.CAPABILITY, dependency.group("capability")),
        )
        mentions = []
        for role, value in role_values:
            span = self._unique_span(candidate, value)
            if span is None:
                return None
            mentions.append(
                ContextualSemanticRoleMention(
                    role_id=role,
                    source_text=value,
                    start_offset=span[0],
                    end_offset=span[1],
                )
            )
        return tuple(mentions)

    def _slots(
        self,
        candidate: GovernedContextualRuleCandidate,
    ) -> tuple[ContextualSemanticSlot, ...] | None:
        specs = (
            (
                ContextualSemanticRole.DEPENDENT,
                ContextualSemanticRelation.DEPENDENCY,
                "exclusive",
                candidate.conditions[0].normalized_text,
            ),
            (
                ContextualSemanticRole.RESOURCE,
                ContextualSemanticRelation.AVAILABILITY,
                "unavailable",
                candidate.conditions[1].normalized_text,
            ),
            (
                ContextualSemanticRole.DEPENDENT,
                ContextualSemanticRelation.ALTERNATIVE,
                "absent",
                candidate.conditions[2].normalized_text,
            ),
            (
                ContextualSemanticRole.DEPENDENT,
                ContextualSemanticRelation.CAPABILITY,
                "unavailable",
                candidate.conclusion.normalized_text,
            ),
        )
        slots = []
        for role, relation, value, source_text in specs:
            span = self._unique_span(candidate, source_text)
            if span is None:
                return None
            slots.append(
                ContextualSemanticSlot(
                    role_id=role,
                    relation=relation,
                    value=value,
                    source_text=source_text,
                    start_offset=span[0],
                    end_offset=span[1],
                )
            )
        return tuple(slots)

    @staticmethod
    def _unique_span(
        candidate: GovernedContextualRuleCandidate,
        fragment: str,
    ) -> tuple[int, int] | None:
        source = candidate.rule_source_text
        pattern = re.compile(re.escape(fragment), re.IGNORECASE)
        matches = tuple(pattern.finditer(source))
        if len(matches) != 1:
            return None
        match = matches[0]
        return (
            candidate.rule_start_offset + match.start(),
            candidate.rule_start_offset + match.end(),
        )

    def _result(
        self,
        candidate: GovernedContextualRuleCandidate,
        status: ContextualSemanticGroundingStatus,
        rationale_codes: tuple[str, ...],
        *,
        roles: tuple[ContextualSemanticRoleMention, ...] = (),
        slots: tuple[ContextualSemanticSlot, ...] = (),
        family_id: str | None = None,
    ) -> GovernedContextualSemanticGroundingCandidate:
        resolved_family_id = family_id or self.FAMILY_ID
        payload = repr(
            (
                _SCHEMA_VERSION,
                resolved_family_id,
                candidate.source_reference,
                candidate.scope_reference,
                candidate.source_fingerprint,
                status.value,
                tuple(
                    (item.role_id, item.source_text, item.start_offset, item.end_offset)
                    for item in roles
                ),
                tuple(
                    (
                        item.role_id,
                        item.relation,
                        item.value,
                        item.source_text,
                        item.start_offset,
                        item.end_offset,
                    )
                    for item in slots
                ),
                rationale_codes,
            )
        )
        fingerprint = sha256(payload.encode("utf-8")).hexdigest()
        return GovernedContextualSemanticGroundingCandidate(
            status=status,
            source_reference=candidate.source_reference,
            scope_reference=candidate.scope_reference,
            source_candidate_fingerprint=candidate.source_fingerprint,
            family_id=resolved_family_id,
            role_mentions=roles,
            semantic_slots=slots,
            rationale_codes=rationale_codes,
            source_fingerprint=fingerprint,
        )
