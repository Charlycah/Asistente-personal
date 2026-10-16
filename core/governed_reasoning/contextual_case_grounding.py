from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256

from core.governed_reasoning.contextual_rule_instantiation import (
    ContextualRuleInstantiationSpec,
    ContextualRuleRoleBinding,
)

_SCHEMA_VERSION = "post-m409.1-contextual-case-role-binding-v1"
_FAMILY_ID = "exclusive_dependency_capability_loss_v1"
_VELAR_FAMILY_ID = "relational_prerequisite_capability_block_v1"


class ContextualCaseGroundingStatus(StrEnum):
    GROUNDED = "grounded"
    AMBIGUOUS = "ambiguous"
    INSUFFICIENT = "insufficient"
    UNSUPPORTED = "unsupported"
    SCOPE_MISMATCH = "scope_mismatch"


@dataclass(frozen=True)
class ContextualCaseRoleMention:
    role_id: str
    source_text: str
    start_offset: int
    end_offset: int

    def __post_init__(self) -> None:
        if not self.role_id.strip() or not self.source_text.strip():
            raise ValueError("case role mention requires role and source text")
        if self.start_offset < 0 or self.end_offset <= self.start_offset:
            raise ValueError("case role mention span is invalid")


@dataclass(frozen=True)
class GovernedContextualCaseGrounding:
    status: ContextualCaseGroundingStatus | str
    source_reference: str
    scope_reference: str
    source_rule_candidate_id: str
    family_id: str
    role_mentions: tuple[ContextualCaseRoleMention, ...]
    bindings: tuple[ContextualRuleRoleBinding, ...]
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
        status = ContextualCaseGroundingStatus(self.status)
        if self.canonical_authority != "governed_reasoning":
            raise ValueError(
                "case grounding must preserve governed reasoning authority"
            )
        if not self.source_reference.strip() or not self.scope_reference.strip():
            raise ValueError("case grounding requires provenance and scope")
        if not self.source_rule_candidate_id.strip() or not self.family_id.strip():
            raise ValueError("case grounding requires rule identity and family")
        if not self.rationale_codes or any(
            not item.strip() for item in self.rationale_codes
        ):
            raise ValueError("case grounding requires rationale codes")
        if not self.source_fingerprint.strip():
            raise ValueError("case grounding requires source fingerprint")
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
            raise ValueError("case grounding violates governed limits")
        if status is ContextualCaseGroundingStatus.GROUNDED:
            roles = tuple(item.role_id for item in self.role_mentions)
            if self.family_id == _FAMILY_ID:
                if len(self.role_mentions) != 3 or len(self.bindings) != 3:
                    raise ValueError(
                        "grounded dependency case requires three complete role bindings"
                    )
                if roles != ("dependent", "resource", "capability"):
                    raise ValueError("grounded dependency case roles are not canonical")
            elif self.family_id == _VELAR_FAMILY_ID:
                if len(self.role_mentions) != 2 or len(self.bindings) != 2:
                    raise ValueError(
                        "grounded relational case requires two complete role bindings"
                    )
                if roles != ("prerequisite", "dependent"):
                    raise ValueError("grounded relational case roles are not canonical")
            else:
                raise ValueError("grounded case family is not certified")
            if tuple(item.role_id for item in self.bindings) != roles:
                raise ValueError("case bindings must preserve canonical role order")
        elif self.role_mentions or self.bindings:
            raise ValueError("non-grounded case cannot expose partial bindings")

    @property
    def normalized_status(self) -> ContextualCaseGroundingStatus:
        return ContextualCaseGroundingStatus(self.status)


class GovernedContextualCaseRoleGrounder:
    """Ground concrete roles for one bounded dependency-loss family only."""

    FAMILY_ID = _FAMILY_ID
    VELAR_FAMILY_ID = _VELAR_FAMILY_ID
    _VELAR_RELATION_RE = re.compile(
        r"(?is)(?P<prerequisite>[^.;,]+?)\s+es\s+"
        r"(?:requisito\s+)?indispensable\s+para\s+"
        r"(?P<dependent>[^.;,]+?)(?=[.;]|$)"
    )
    _DEPENDENCY_RE = re.compile(
        r"(?is)(?P<dependent>[^.;,]+?)\s+depende\s+exclusivamente\s+"
        r"(?:del|de\s+la|de\s+los|de\s+las|de)\s+"
        r"(?P<resource>[^.;,]+?)\s+para\s+"
        r"(?:(?:recibir|obtener|mantener|realizar|procesar|proveer)\s+)?"
        r"(?P<capability>[^.;,]+?)(?=[.;]|$)"
    )
    _HISTORICAL_CAPABILITY_DEPENDENCY_RE = re.compile(
        r"(?is)(?P<dependent>[^.;,]+?)\s+puede\s+"
        r"(?P<capability>[^.;,]+?)\s+"
        r"(?:únicamente|unicamente|exclusivamente)\s+"
        r"a\s+partir\s+de\s+"
        r"(?P<resource>[^.;,]+?)(?=[.;]|$)"
    )
    _NOVEL_DEPENDENCY_RE = re.compile(
        r"(?is)(?P<dependent>[^.;,]+?)\s+"
        r"(?<!no\s)(?:"
        r"requiere\s+(?:el|la)\s+(?:único|única)|"
        r"se\s+sostiene\s+(?:únicamente|unicamente)\s+con|"
        r"necesita\s+como\s+(?:único|única)\s+medio|"
        r"necesita\s+exclusivamente|"
        r"requiere\s+como\s+(?:único|única)\s+recurso"
        r")\s+(?P<resource>[^.;,]+?)\s+para\s+"
        r"(?P<capability>[^.;,]+?)(?=[.;]|$)"
    )
    _NOVEL_REVERSED_DEPENDENCY_RE = re.compile(
        r"(?is)para\s+poder\s+(?P<capability>[^.;,]+?),\s*"
        r"(?P<dependent>[^.;,]+?)\s+"
        r"(?<!no\s)(?:solo|sólo|únicamente|unicamente)\s+puede\s+"
        r"(?:obtener|recibir|mantener|realizar|procesar|proveer)\s+"
        r"(?:los?\s+datos\s+)?(?:del|de\s+la|de\s+los|de\s+las|de)\s+"
        r"(?P<resource>[^.;,]+?)(?=[.;]|$)"
    )
    _NO_ALTERNATIVE_RE = re.compile(
        r"(?is)(?:"
        r"\bno\s+(?:existe|hay)\s+(?:ninguna\s+)?"
        r"(?:alternativa|otra\s+fuente|reemplazo|sustituto)\b|"
        r"\btampoco\s+hay\s+(?:ninguna\s+)?(?:alternativa|otra\s+fuente)\b|"
        r"\bno\s+dispone\s+de\s+"
        r"(?:equipo\s+de\s+)?(?:respaldo|sustituto|reemplazo)\b|"
        r"\bno\s+cuenta\s+con\s+(?:respaldo|sustituto|reemplazo)\b|"
        r"\bcarece\s+de\s+(?:ruta\s+)?(?:alternativa|respaldo|sustituto)\b"
        r")"
    )
    _POSITIVE_ALTERNATIVE_RE = re.compile(
        r"(?is)(?<!no\s)(?<!tampoco\s)\b(?:existe|hay)\s+(?:una\s+)?"
        r"(?:alternativa|otra\s+fuente)\b"
    )
    _MULTI_RESOURCE_RE = re.compile(r"(?i)\b(?:y|o)\b")

    def ground(
        self,
        *,
        case_text: str,
        spec: ContextualRuleInstantiationSpec,
        scope_reference: str,
        source_reference: str,
    ) -> GovernedContextualCaseGrounding:
        if not case_text.strip():
            raise ValueError("case grounding requires case text")
        if not scope_reference.strip() or not source_reference.strip():
            raise ValueError("case grounding requires scope and provenance")
        if scope_reference != spec.scope_reference:
            return self._result(
                case_text=case_text,
                spec=spec,
                scope_reference=scope_reference,
                source_reference=source_reference,
                status=ContextualCaseGroundingStatus.SCOPE_MISMATCH,
                rationale_codes=("case_grounding:scope_mismatch",),
            )
        family_id = self._spec_family(spec)
        if family_id is None:
            return self._result(
                case_text=case_text,
                spec=spec,
                scope_reference=scope_reference,
                source_reference=source_reference,
                status=ContextualCaseGroundingStatus.UNSUPPORTED,
                rationale_codes=("case_grounding:unsupported_rule_family",),
            )
        if family_id == self.VELAR_FAMILY_ID:
            return self._ground_velar(
                case_text=case_text,
                spec=spec,
                scope_reference=scope_reference,
                source_reference=source_reference,
            )

        active_text = self._mask_quoted_spans(case_text)
        matches = tuple(self._DEPENDENCY_RE.finditer(active_text))
        novel_matches = (
            *self._NOVEL_DEPENDENCY_RE.finditer(active_text),
            *self._NOVEL_REVERSED_DEPENDENCY_RE.finditer(active_text),
        )
        historical_matches = tuple(
            self._HISTORICAL_CAPABILITY_DEPENDENCY_RE.finditer(active_text)
        )
        if matches and (novel_matches or historical_matches):
            return self._result(
                case_text=case_text,
                spec=spec,
                scope_reference=scope_reference,
                source_reference=source_reference,
                status=ContextualCaseGroundingStatus.AMBIGUOUS,
                rationale_codes=("case_grounding:mixed_dependency_forms",),
            )
        if novel_matches and historical_matches:
            return self._result(
                case_text=case_text,
                spec=spec,
                scope_reference=scope_reference,
                source_reference=source_reference,
                status=ContextualCaseGroundingStatus.AMBIGUOUS,
                rationale_codes=("case_grounding:mixed_dependency_forms",),
            )
        novel_dependency = False
        if not matches and novel_matches:
            matches = tuple(novel_matches)
            novel_dependency = True
        if matches and historical_matches:
            return self._result(
                case_text=case_text,
                spec=spec,
                scope_reference=scope_reference,
                source_reference=source_reference,
                status=ContextualCaseGroundingStatus.AMBIGUOUS,
                rationale_codes=("case_grounding:mixed_dependency_forms",),
            )
        historical_dependency = False
        if not matches and historical_matches:
            matches = historical_matches
            historical_dependency = True
        if not matches:
            return self._result(
                case_text=case_text,
                spec=spec,
                scope_reference=scope_reference,
                source_reference=source_reference,
                status=ContextualCaseGroundingStatus.INSUFFICIENT,
                rationale_codes=("case_grounding:explicit_roles_missing",),
            )
        if len(matches) != 1:
            return self._result(
                case_text=case_text,
                spec=spec,
                scope_reference=scope_reference,
                source_reference=source_reference,
                status=ContextualCaseGroundingStatus.AMBIGUOUS,
                rationale_codes=("case_grounding:multiple_dependency_candidates",),
            )

        match = matches[0]
        if self._dependency_is_negated(match):
            return self._result(
                case_text=case_text,
                spec=spec,
                scope_reference=scope_reference,
                source_reference=source_reference,
                status=ContextualCaseGroundingStatus.UNSUPPORTED,
                rationale_codes=("case_grounding:dependency_negated",),
            )
        resource = self._clean(match.group("resource"))
        if self._MULTI_RESOURCE_RE.search(resource):
            return self._result(
                case_text=case_text,
                spec=spec,
                scope_reference=scope_reference,
                source_reference=source_reference,
                status=ContextualCaseGroundingStatus.AMBIGUOUS,
                rationale_codes=("case_grounding:multiple_resources",),
            )
        if self._POSITIVE_ALTERNATIVE_RE.search(active_text):
            return self._result(
                case_text=case_text,
                spec=spec,
                scope_reference=scope_reference,
                source_reference=source_reference,
                status=ContextualCaseGroundingStatus.UNSUPPORTED,
                rationale_codes=("case_grounding:alternative_present",),
            )
        if (
            not historical_dependency
            and self._NO_ALTERNATIVE_RE.search(active_text) is None
        ):
            return self._result(
                case_text=case_text,
                spec=spec,
                scope_reference=scope_reference,
                source_reference=source_reference,
                status=ContextualCaseGroundingStatus.INSUFFICIENT,
                rationale_codes=("case_grounding:alternative_unknown",),
            )
        availability = self._resource_availability(active_text, resource)
        if availability == "available":
            return self._result(
                case_text=case_text,
                spec=spec,
                scope_reference=scope_reference,
                source_reference=source_reference,
                status=ContextualCaseGroundingStatus.UNSUPPORTED,
                rationale_codes=("case_grounding:resource_not_unavailable",),
            )
        if availability != "unavailable":
            return self._result(
                case_text=case_text,
                spec=spec,
                scope_reference=scope_reference,
                source_reference=source_reference,
                status=ContextualCaseGroundingStatus.INSUFFICIENT,
                rationale_codes=("case_grounding:resource_availability_unknown",),
            )

        mentions = self._mentions(match)
        capability_entity = self._clean(match.group("capability"))
        velar_matches = tuple(self._VELAR_RELATION_RE.finditer(case_text))
        if historical_dependency and len(velar_matches) == 1:
            prerequisite = self._clean(velar_matches[0].group("prerequisite"))
            if self._same_capability_phrase(capability_entity, prerequisite):
                capability_entity = prerequisite
        bindings = tuple(
            ContextualRuleRoleBinding(
                role_id=mention.role_id,
                entity_reference=(
                    capability_entity
                    if mention.role_id == "capability"
                    else self._clean(mention.source_text)
                ),
                source_reference=source_reference,
                source_text=mention.source_text,
            )
            for mention in mentions
        )
        return self._result(
            case_text=case_text,
            spec=spec,
            scope_reference=scope_reference,
            source_reference=source_reference,
            status=ContextualCaseGroundingStatus.GROUNDED,
            rationale_codes=(
                (
                    "case_grounding:historical_capability_dependency_explicit"
                    if historical_dependency
                    else (
                        "case_grounding:bounded_semantic_dependency_explicit"
                        if novel_dependency
                        else "case_grounding:exclusive_dependency_explicit"
                    )
                ),
                "case_grounding:resource_unavailable_explicit",
                (
                    "case_grounding:exclusivity_encodes_no_alternative"
                    if historical_dependency
                    else "case_grounding:no_alternative_explicit"
                ),
                "case_grounding:complete_role_bindings",
            ),
            mentions=mentions,
            bindings=bindings,
        )

    @staticmethod
    def _supports_neral_spec(spec: ContextualRuleInstantiationSpec) -> bool:
        return (
            spec.roles == ("dependent", "resource", "capability")
            and tuple(
                (item.role_id, item.object_value, item.object_role_id)
                for item in spec.conditions
            )
            == (
                ("dependent", "exclusive", None),
                ("resource", "unavailable", None),
                ("dependent", "false", None),
            )
            and all(
                item.predicate_id.startswith("ctx-predicate-")
                for item in spec.conditions
            )
            and spec.conclusion.role_id in ("dependent", "capability")
            and spec.conclusion.predicate_id.startswith("ctx-predicate-")
            and spec.conclusion.object_value == "unavailable"
            and spec.conclusion.object_role_id is None
        )

    @staticmethod
    def _supports_velar_spec(spec: ContextualRuleInstantiationSpec) -> bool:
        return (
            spec.roles == ("prerequisite", "dependent")
            and len(spec.conditions) == 2
            and spec.conditions[0].role_id == "prerequisite"
            and spec.conditions[0].object_value is None
            and spec.conditions[0].object_role_id == "dependent"
            and spec.conditions[1].role_id == "prerequisite"
            and spec.conditions[1].object_value == "unavailable"
            and spec.conditions[1].object_role_id is None
            and all(
                item.predicate_id.startswith("ctx-predicate-")
                for item in spec.conditions
            )
            and spec.conclusion.role_id == "dependent"
            and spec.conclusion.predicate_id.startswith("ctx-predicate-")
            and spec.conclusion.object_value == "unavailable"
            and spec.conclusion.object_role_id is None
        )

    @classmethod
    def _spec_family(cls, spec: ContextualRuleInstantiationSpec) -> str | None:
        if cls._supports_neral_spec(spec):
            return cls.FAMILY_ID
        if cls._supports_velar_spec(spec):
            return cls.VELAR_FAMILY_ID
        return None

    def _ground_velar(
        self,
        *,
        case_text: str,
        spec: ContextualRuleInstantiationSpec,
        scope_reference: str,
        source_reference: str,
    ) -> GovernedContextualCaseGrounding:
        matches = tuple(self._VELAR_RELATION_RE.finditer(case_text))
        if not matches:
            return self._result(
                case_text=case_text,
                spec=spec,
                scope_reference=scope_reference,
                source_reference=source_reference,
                status=ContextualCaseGroundingStatus.INSUFFICIENT,
                rationale_codes=("case_grounding:relational_roles_missing",),
            )
        if len(matches) != 1:
            return self._result(
                case_text=case_text,
                spec=spec,
                scope_reference=scope_reference,
                source_reference=source_reference,
                status=ContextualCaseGroundingStatus.AMBIGUOUS,
                rationale_codes=("case_grounding:multiple_relational_candidates",),
            )

        match = matches[0]
        prerequisite = self._clean(match.group("prerequisite"))
        dependent = self._clean(match.group("dependent"))
        resolved_dependent = self._resolve_bounded_enclitic(
            dependent,
            prerequisite,
        )
        if prerequisite.casefold() == resolved_dependent.casefold():
            return self._result(
                case_text=case_text,
                spec=spec,
                scope_reference=scope_reference,
                source_reference=source_reference,
                status=ContextualCaseGroundingStatus.AMBIGUOUS,
                rationale_codes=("case_grounding:relational_roles_not_distinct",),
            )
        availability = self._resource_availability(case_text, prerequisite)
        deferred_availability = False
        if availability == "unknown":
            dependency_matches = tuple(
                self._HISTORICAL_CAPABILITY_DEPENDENCY_RE.finditer(case_text)
            )
            if len(dependency_matches) == 1 and self._same_capability_phrase(
                self._clean(dependency_matches[0].group("capability")),
                prerequisite,
            ):
                deferred_availability = True
        if availability == "available":
            return self._result(
                case_text=case_text,
                spec=spec,
                scope_reference=scope_reference,
                source_reference=source_reference,
                status=ContextualCaseGroundingStatus.UNSUPPORTED,
                rationale_codes=("case_grounding:prerequisite_not_unavailable",),
            )
        if availability != "unavailable" and not deferred_availability:
            return self._result(
                case_text=case_text,
                spec=spec,
                scope_reference=scope_reference,
                source_reference=source_reference,
                status=ContextualCaseGroundingStatus.INSUFFICIENT,
                rationale_codes=("case_grounding:prerequisite_availability_unknown",),
            )

        mentions = tuple(
            ContextualCaseRoleMention(
                role_id=role,
                source_text=match.group(group),
                start_offset=match.start(group),
                end_offset=match.end(group),
            )
            for role, group in (
                ("prerequisite", "prerequisite"),
                ("dependent", "dependent"),
            )
        )
        bindings = tuple(
            ContextualRuleRoleBinding(
                role_id=mention.role_id,
                entity_reference=(
                    resolved_dependent
                    if mention.role_id == "dependent"
                    else self._clean(mention.source_text)
                ),
                source_reference=source_reference,
                source_text=mention.source_text,
            )
            for mention in mentions
        )
        return self._result(
            case_text=case_text,
            spec=spec,
            scope_reference=scope_reference,
            source_reference=source_reference,
            status=ContextualCaseGroundingStatus.GROUNDED,
            rationale_codes=(
                "case_grounding:required_for_explicit",
                (
                    "case_grounding:prerequisite_availability_deferred"
                    if deferred_availability
                    else "case_grounding:prerequisite_unavailable_explicit"
                ),
                "case_grounding:complete_relational_role_bindings",
            ),
            mentions=mentions,
            bindings=bindings,
        )

    @classmethod
    def _resource_availability(cls, text: str, resource: str) -> str:
        article = r"(?:el\s+|la\s+|los\s+|las\s+)?"
        resource_pattern = re.escape(resource).replace(r"\ ", r"\s+")
        unavailable = re.compile(
            rf"(?is)\b{article}{resource_pattern}\s+"
            r"(?:est[aá]\s+indisponible|no\s+est[aá]\s+disponible|"
            r"queda\s+indisponible|se\s+vuelve\s+indisponible|"
            r"est[aá]\s+fuera\s+de\s+servicio|"
            r"dej[oó]\s+de\s+estar\s+operativ[oa]|"
            r"dej[oó]\s+de\s+responder|dej[oó]\s+de\s+funcionar|"
            r"qued[oó]\s+inutilizable|fue\s+suspendid[oa]|"
            r"est[aá]\s+bloquead[oa]|fall[oó]|"
            r"se\s+vuelve\s+ilegible|queda\s+ilegible|"
            r"se\s+corrompe|queda\s+corrompido)\b"
        )
        available = re.compile(
            rf"(?is)\b{article}{resource_pattern}\s+"
            r"(?:est[aá]\s+disponible|funciona|sigue\s+funcionando)\b"
        )
        if unavailable.search(text):
            return "unavailable"
        if available.search(text):
            return "available"
        tokens = cls._clean(resource).split()
        if tokens and tokens[0].casefold() in {"un", "una", "el", "la"}:
            tokens = tokens[1:]
        if tokens:
            head = re.escape(tokens[0])
            informational_unavailable = re.compile(
                rf"(?is)\b{article}{head}\s+"
                r"(?:se\s+vuelve\s+ilegible|queda\s+ilegible|"
                r"se\s+corrompe|queda\s+corrompido)\b"
            )
            if informational_unavailable.search(text):
                return "unavailable"
        return "unknown"

    @staticmethod
    def _dependency_is_negated(match: re.Match[str]) -> bool:
        dependent = " ".join(match.group("dependent").strip().split())
        return re.search(r"(?i)\bno$", dependent) is not None

    @staticmethod
    def _mask_quoted_spans(text: str) -> str:
        chars = list(text)
        quote_pairs = {'"': '"', "“": "”", "«": "»"}
        index = 0
        while index < len(chars):
            opener = chars[index]
            closer = quote_pairs.get(opener)
            if closer is None:
                index += 1
                continue
            end = text.find(closer, index + 1)
            if end < 0:
                index += 1
                continue
            for position in range(index, end + 1):
                if chars[position] not in "\r\n":
                    chars[position] = " "
            index = end + 1
        return "".join(chars)

    @staticmethod
    def _resolve_bounded_enclitic(dependent: str, prerequisite: str) -> str:
        match = re.match(r"(?i)^(?P<verb>[\wáéíóúüñ]+)lo$", dependent)
        parts = prerequisite.split(maxsplit=1)
        if match is None or len(parts) != 2:
            return dependent
        return f"{match.group('verb')} {parts[1]}"

    @staticmethod
    def _same_capability_phrase(left: str, right: str) -> bool:
        def normalize(value: str) -> tuple[str, ...]:
            words = re.findall(r"[\wáéíóúüñ]+", value.casefold())
            return tuple(
                word
                for word in words
                if word not in {"un", "una", "el", "la", "los", "las"}
            )

        return normalize(left) == normalize(right)

    @staticmethod
    def _mentions(match: re.Match[str]) -> tuple[ContextualCaseRoleMention, ...]:
        return tuple(
            ContextualCaseRoleMention(
                role_id=role,
                source_text=match.group(group),
                start_offset=match.start(group),
                end_offset=match.end(group),
            )
            for role, group in (
                ("dependent", "dependent"),
                ("resource", "resource"),
                ("capability", "capability"),
            )
        )

    @staticmethod
    def _clean(value: str) -> str:
        return " ".join(value.strip().split())

    def _result(
        self,
        *,
        case_text: str,
        spec: ContextualRuleInstantiationSpec,
        scope_reference: str,
        source_reference: str,
        status: ContextualCaseGroundingStatus,
        rationale_codes: tuple[str, ...],
        mentions: tuple[ContextualCaseRoleMention, ...] = (),
        bindings: tuple[ContextualRuleRoleBinding, ...] = (),
    ) -> GovernedContextualCaseGrounding:
        payload = (
            _SCHEMA_VERSION,
            status.value,
            spec,
            case_text,
            source_reference,
            scope_reference,
            mentions,
            bindings,
            rationale_codes,
        )
        fingerprint = sha256(repr(payload).encode("utf-8")).hexdigest()
        family_id = self._spec_family(spec) or self.FAMILY_ID
        return GovernedContextualCaseGrounding(
            status=status,
            source_reference=source_reference,
            scope_reference=scope_reference,
            source_rule_candidate_id=spec.rule_candidate_id,
            family_id=family_id,
            role_mentions=mentions,
            bindings=bindings,
            rationale_codes=rationale_codes,
            source_fingerprint=fingerprint,
        )
