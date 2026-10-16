from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256


class ContextualRuleCandidateStatus(StrEnum):
    NOT_RULE = "not_rule"
    CANDIDATE = "candidate"
    AMBIGUOUS = "ambiguous"
    UNSUPPORTED = "unsupported"


@dataclass(frozen=True)
class ContextualRuleClauseCandidate:
    raw_text: str
    normalized_text: str
    negated: bool

    def __post_init__(self) -> None:
        if not self.raw_text.strip() or not self.normalized_text.strip():
            raise ValueError("contextual rule clause must not be blank")


@dataclass(frozen=True)
class GovernedContextualRuleCandidate:
    status: ContextualRuleCandidateStatus | str
    source_text: str
    source_reference: str
    scope_reference: str
    rule_start_offset: int
    rule_end_offset: int
    rule_source_text: str
    conditions: tuple[ContextualRuleClauseCandidate, ...]
    conclusion: ContextualRuleClauseCandidate | None
    rationale_codes: tuple[str, ...]
    source_fingerprint: str
    schema_version: str = "post-m409.1-contextual-rule-candidate-v1"
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
    authorizes_action: bool = False
    executes_actions: bool = False
    grants_authority: bool = False

    def __post_init__(self) -> None:
        status = ContextualRuleCandidateStatus(self.status)
        if not self.source_reference.strip() or not self.scope_reference.strip():
            raise ValueError("contextual rule candidate requires provenance and scope")
        if not self.rationale_codes or any(
            not code.strip() for code in self.rationale_codes
        ):
            raise ValueError("contextual rule candidate requires rationale codes")
        if not self.source_fingerprint.strip():
            raise ValueError("contextual rule candidate requires fingerprint")
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
                self.authorizes_action,
                self.executes_actions,
                self.grants_authority,
            )
        ):
            raise ValueError(
                "contextual rule candidate must remain read-only and non-authoritative"
            )
        if status is ContextualRuleCandidateStatus.CANDIDATE:
            if not self.conditions or self.conclusion is None:
                raise ValueError("candidate status requires conditions and conclusion")
            if not 1 <= len(self.conditions) <= 4:
                raise ValueError("candidate supports between one and four conditions")
            if (
                self.rule_start_offset < 0
                or self.rule_end_offset <= self.rule_start_offset
            ):
                raise ValueError("candidate rule source span is invalid")
            if self.rule_end_offset > len(self.source_text):
                raise ValueError("candidate rule source span exceeds source text")
            if (
                self.source_text[self.rule_start_offset : self.rule_end_offset]
                != self.rule_source_text
            ):
                raise ValueError("candidate rule span must match source text exactly")
        else:
            if self.conditions or self.conclusion is not None:
                raise ValueError("non-candidate status cannot expose parsed clauses")
            if self.rule_start_offset != -1 or self.rule_end_offset != -1:
                raise ValueError("non-candidate status cannot expose source span")
            if self.rule_source_text:
                raise ValueError("non-candidate status cannot expose rule source")

    @property
    def normalized_status(self) -> ContextualRuleCandidateStatus:
        return ContextualRuleCandidateStatus(self.status)


class GovernedContextualRuleInterpretationProducer:
    """Extract only bounded explicit session-local IF/AND/THEN rule candidates."""

    _PREFIX_RE = re.compile(
        r"(?is)(?:^|[.!?]\s+)"
        r"(?:"
        r"(?:para\s+(?:este|esta)\s+[^:]{0,80}?\s+)?"
        r"(?:us(?:a|á)|aprend(?:e|é))\s+esta\s+regla"
        r"(?:\s+(?:artificial|temporal))?"
        r"(?:\s+llamada\s+principio\s+[\wáéíóúüñ-]+)?"
        r"|regla\s+(?:temporal|adicional(?:\s+artificial)?)"
        r"|supongamos\s+(?:esta|la\s+siguiente)\s+regla"
        r"|principio\s+[\wáéíóúüñ-]+(?:\s+temporal)?"
        r")\s*:\s*",
    )
    _INLINE_PRINCIPLE_RE = re.compile(
        r"(?is)^principio\s+[\wáéíóúüñ-]+\s*:\s*"
    )
    _RULE_RE = re.compile(
        r"(?is)^si\s+(?P<antecedent>.+?)\s*,?\s+entonces\s+"
        r"(?P<conclusion>.+?)\s*[.!?]?$"
    )
    _VELAR_HISTORICAL_RE = re.compile(
        r"(?is)^si\s+(?P<condition_one>.+?\s+es\s+requisito\s+"
        r"indispensable\s+para\s+.+?)\s*,\s*"
        r"(?P<condition_two>la\s+p[eé]rdida\s+de\s+"
        r"(?P<loss_ref>[\wáéíóúüñ-]+))\s+"
        r"(?P<conclusion>impide\s+(?P<dependent_ref>[\wáéíóúüñ-]+)\s+"
        r"mientras\s+siga\s+faltando\s+"
        r"(?P<missing_ref>[\wáéíóúüñ-]+))\s*[.!?]?$"
    )
    _BOUNDED_POSTCONDITION_RE = re.compile(
        r"(?is)^si\s+(?P<condition_one>.+?)\s*,\s+y\s+"
        r"(?P<condition_two>.+?)\s*,\s+"
        r"(?P<conclusion>.+?)\s+mientras\s+"
        r"(?P<condition_three>no\s+exista\s+(?:(?:una|ninguna)\s+)?alternativa)"
        r"\s*[.!?]"
    )
    _UNSUPPORTED_RE = re.compile(
        r"(?i)(?:\s+o\s+|\bsalvo\b|\bexcepto\b|\ba\s+menos\s+que\b|"
        r"\bsi\s+y\s+solo\s+si\b|\bprobablemente\b|\bnormalmente\b|"
        r"\bgeneralmente\b|\bsiempre\s+que\b)"
    )
    _EXPLICIT_NEGATION_RE = re.compile(r"(?i)(?:^|\s)no(?:\s|$)")

    def produce(
        self,
        text: str,
        *,
        source_reference: str,
        scope_reference: str,
    ) -> GovernedContextualRuleCandidate:
        if not source_reference.strip() or not scope_reference.strip():
            raise ValueError(
                "contextual rule interpretation requires provenance and scope"
            )

        prefix = self._PREFIX_RE.search(text)
        if prefix is None:
            return self._result(
                ContextualRuleCandidateStatus.NOT_RULE,
                text,
                source_reference,
                scope_reference,
                ("explicit_rule_intent:not_found",),
            )

        body_start = prefix.end()
        body = text[body_start:].strip()
        inline_principle = self._INLINE_PRINCIPLE_RE.match(body)
        if inline_principle is not None:
            leading = len(text[body_start:]) - len(text[body_start:].lstrip())
            body_start += leading + inline_principle.end()
            body = text[body_start:].strip()
        if not body:
            return self._result(
                ContextualRuleCandidateStatus.AMBIGUOUS,
                text,
                source_reference,
                scope_reference,
                ("explicit_rule_intent:found", "rule_body:missing"),
            )

        if self._UNSUPPORTED_RE.search(body):
            return self._result(
                ContextualRuleCandidateStatus.UNSUPPORTED,
                text,
                source_reference,
                scope_reference,
                ("explicit_rule_intent:found", "grammar:unsupported_operator"),
            )

        match = self._RULE_RE.fullmatch(body)
        compatibility = None
        historical_velar = None
        if match is None:
            compatibility = self._BOUNDED_POSTCONDITION_RE.match(body)
        if match is None and compatibility is None:
            historical_velar = self._VELAR_HISTORICAL_RE.fullmatch(body)
        if (
            match is None
            and compatibility is None
            and historical_velar is None
        ):
            return self._result(
                ContextualRuleCandidateStatus.UNSUPPORTED,
                text,
                source_reference,
                scope_reference,
                ("explicit_rule_intent:found", "grammar:if_then_required"),
            )

        if compatibility is not None:
            condition_parts = tuple(
                compatibility.group(name).strip()
                for name in (
                    "condition_one",
                    "condition_two",
                    "condition_three",
                )
            )
            conclusion_text = compatibility.group("conclusion").strip()
            matched_rule = compatibility.group(0)
            rule_body_length = len(matched_rule.rstrip())
            grammar_code = "grammar:bounded_postcondition_v1"
        elif historical_velar is not None:
            loss_ref = historical_velar.group("loss_ref").casefold()
            missing_ref = historical_velar.group("missing_ref").casefold()
            if loss_ref != missing_ref:
                return self._result(
                    ContextualRuleCandidateStatus.AMBIGUOUS,
                    text,
                    source_reference,
                    scope_reference,
                    (
                        "explicit_rule_intent:found",
                        "grammar:velar_reference_mismatch",
                    ),
                )
            condition_parts = (
                historical_velar.group("condition_one").strip(),
                historical_velar.group("condition_two").strip(),
            )
            conclusion_text = historical_velar.group("conclusion").strip()
            rule_body_length = len(body)
            grammar_code = "grammar:historical_velar_v1"
        else:
            antecedent = match.group("antecedent").strip()
            conclusion_text = match.group("conclusion").strip()
            condition_parts = tuple(
                part.strip()
                for part in re.split(r"(?i)\s+y\s+", antecedent)
            )
            rule_body_length = len(body)
            grammar_code = "grammar:if_and_then_v1"
        if any(not part for part in condition_parts) or not conclusion_text:
            return self._result(
                ContextualRuleCandidateStatus.AMBIGUOUS,
                text,
                source_reference,
                scope_reference,
                ("explicit_rule_intent:found", "grammar:incomplete"),
            )

        if any(not part for part in condition_parts):
            return self._result(
                ContextualRuleCandidateStatus.AMBIGUOUS,
                text,
                source_reference,
                scope_reference,
                ("explicit_rule_intent:found", "grammar:ambiguous_condition"),
            )
        if len(condition_parts) > 4:
            return self._result(
                ContextualRuleCandidateStatus.UNSUPPORTED,
                text,
                source_reference,
                scope_reference,
                ("explicit_rule_intent:found", "grammar:too_many_conditions"),
            )
        if (
            historical_velar is None
            and re.search(r"(?i)\s+y\s+", conclusion_text)
        ):
            return self._result(
                ContextualRuleCandidateStatus.AMBIGUOUS,
                text,
                source_reference,
                scope_reference,
                ("explicit_rule_intent:found", "grammar:compound_conclusion"),
            )

        conditions = tuple(self._clause(part) for part in condition_parts)
        conclusion = self._clause(conclusion_text)

        leading = len(text[body_start:]) - len(text[body_start:].lstrip())
        rule_start = body_start + leading
        rule_end = rule_start + rule_body_length
        rule_source = text[rule_start:rule_end]
        return self._result(
            ContextualRuleCandidateStatus.CANDIDATE,
            text,
            source_reference,
            scope_reference,
            (
                "explicit_rule_intent:found",
                grammar_code,
                "candidate:untrusted_read_only",
            ),
            rule_start=rule_start,
            rule_end=rule_end,
            rule_source=rule_source,
            conditions=conditions,
            conclusion=conclusion,
        )

    def _clause(self, text: str) -> ContextualRuleClauseCandidate:
        normalized = " ".join(text.strip().split())
        return ContextualRuleClauseCandidate(
            raw_text=text,
            normalized_text=normalized,
            negated=bool(self._EXPLICIT_NEGATION_RE.search(normalized)),
        )

    @staticmethod
    def _fingerprint(
        *,
        source_reference: str,
        scope_reference: str,
        status: ContextualRuleCandidateStatus,
        rule_source: str,
        conditions: tuple[ContextualRuleClauseCandidate, ...],
        conclusion: ContextualRuleClauseCandidate | None,
    ) -> str:
        payload = repr(
            (
                "post-m409.1-contextual-rule-candidate-v1",
                source_reference,
                scope_reference,
                status.value,
                rule_source,
                tuple((item.normalized_text, item.negated) for item in conditions),
                (
                    None
                    if conclusion is None
                    else (conclusion.normalized_text, conclusion.negated)
                ),
            )
        )
        return sha256(payload.encode("utf-8")).hexdigest()

    def _result(
        self,
        status: ContextualRuleCandidateStatus,
        source_text: str,
        source_reference: str,
        scope_reference: str,
        rationale_codes: tuple[str, ...],
        *,
        rule_start: int = -1,
        rule_end: int = -1,
        rule_source: str = "",
        conditions: tuple[ContextualRuleClauseCandidate, ...] = (),
        conclusion: ContextualRuleClauseCandidate | None = None,
    ) -> GovernedContextualRuleCandidate:
        fingerprint = self._fingerprint(
            source_reference=source_reference,
            scope_reference=scope_reference,
            status=status,
            rule_source=rule_source,
            conditions=conditions,
            conclusion=conclusion,
        )
        return GovernedContextualRuleCandidate(
            status=status,
            source_text=source_text,
            source_reference=source_reference,
            scope_reference=scope_reference,
            rule_start_offset=rule_start,
            rule_end_offset=rule_end,
            rule_source_text=rule_source,
            conditions=conditions,
            conclusion=conclusion,
            rationale_codes=rationale_codes,
            source_fingerprint=fingerprint,
        )
