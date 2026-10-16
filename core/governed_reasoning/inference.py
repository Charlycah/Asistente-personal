from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.governed_reasoning.claims import (
    Claim,
    ClaimConfidence,
    ClaimEvidenceLink,
    ClaimOrigin,
    ClaimStatus,
    ClaimType,
    EvidenceLinkRole,
)
from core.governed_reasoning.context import (
    ContextAssemblyStatus,
    ReasoningContextBundle,
)
from core.scope_guard import ScopeDomain


class InferenceOperator(str, Enum):
    EQUALS = "equals"
    IN = "in"
    BEFORE_AS_OF = "before_as_of"
    AFTER_AS_OF = "after_as_of"


class InferenceStatus(str, Enum):
    APPLIED = "applied"
    NOT_APPLICABLE = "not_applicable"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"
    REJECTED = "rejected"


@dataclass(frozen=True)
class ClaimCondition:
    predicate: str
    operator: InferenceOperator | str = InferenceOperator.EQUALS
    values: tuple[str, ...] = ()
    subject: str | None = None

    def __post_init__(self) -> None:
        InferenceOperator(self.operator)
        if not self.predicate.strip():
            raise ValueError("inference condition predicate must not be empty")
        if (
            self.normalized_operator
            in {
                InferenceOperator.EQUALS,
                InferenceOperator.IN,
            }
            and not self.values
        ):
            raise ValueError("value-based inference conditions require values")
        if any(not value.strip() for value in self.values):
            raise ValueError("inference condition values must not contain blanks")
        if self.subject is not None and not self.subject.strip():
            raise ValueError("inference condition subject must not be blank")

    @property
    def normalized_operator(self) -> InferenceOperator:
        return InferenceOperator(self.operator)


@dataclass(frozen=True)
class InferenceRule:
    rule_id: str
    version: str
    description: str
    conditions: tuple[ClaimCondition, ...]
    conclusion_subject: str
    conclusion_predicate: str
    conclusion_object: str
    allowed_domains: tuple[ScopeDomain | str, ...] = (ScopeDomain.PERSONAL_OPERATIONS,)
    base_confidence: float = 0.6
    requires_review: bool = False
    enabled: bool = True
    source_fingerprint: str | None = None
    scope_reference: str | None = None
    valid_from: datetime | None = None
    valid_until: datetime | None = None
    temporary: bool = False

    def __post_init__(self) -> None:
        for value, label in (
            (self.rule_id, "id"),
            (self.version, "version"),
            (self.description, "description"),
            (self.conclusion_subject, "conclusion subject"),
            (self.conclusion_predicate, "conclusion predicate"),
            (self.conclusion_object, "conclusion object"),
        ):
            if not value.strip():
                raise ValueError(f"inference rule {label} must not be empty")
        if not self.conditions:
            raise ValueError("inference rule requires at least one condition")
        if not self.allowed_domains:
            raise ValueError("inference rule requires at least one allowed domain")
        for domain in self.allowed_domains:
            ScopeDomain(domain)
        if not 0.0 <= self.base_confidence <= 1.0:
            raise ValueError("inference rule confidence must be between zero and one")
        if self.source_fingerprint is not None and len(self.source_fingerprint) != 64:
            raise ValueError("inference rule source fingerprint must be SHA-256")
        if self.scope_reference is not None and not self.scope_reference.strip():
            raise ValueError("inference rule scope reference must not be blank")
        for timestamp in (self.valid_from, self.valid_until):
            if timestamp is not None and timestamp.tzinfo is None:
                raise ValueError(
                    "inference rule validity timestamps must be timezone-aware"
                )
        if (
            self.valid_from is not None
            and self.valid_until is not None
            and self.valid_until <= self.valid_from
        ):
            raise ValueError("inference rule validity window must be increasing")
        if self.temporary:
            if self.source_fingerprint is None:
                raise ValueError("temporary inference rule requires source fingerprint")
            if self.scope_reference is None:
                raise ValueError("temporary inference rule requires scope reference")
            if self.valid_from is None or self.valid_until is None:
                raise ValueError("temporary inference rule requires bounded validity")

    @property
    def normalized_domains(self) -> tuple[ScopeDomain, ...]:
        return tuple(ScopeDomain(item) for item in self.allowed_domains)

    @property
    def reference(self) -> str:
        return f"{self.rule_id}@{self.version}"

    @property
    def fingerprint(self) -> str:
        payload = "|".join(
            (
                self.reference,
                self.description,
                ";".join(
                    f"{item.subject or ''}:{item.predicate}:"
                    f"{item.normalized_operator.value}:{','.join(item.values)}"
                    for item in self.conditions
                ),
                self.conclusion_subject,
                self.conclusion_predicate,
                self.conclusion_object,
                ",".join(
                    sorted(ScopeDomain(item).value for item in self.allowed_domains)
                ),
                str(self.base_confidence),
                str(self.requires_review),
                str(self.enabled),
                self.source_fingerprint or "",
                self.scope_reference or "",
                self.valid_from.isoformat() if self.valid_from else "",
                self.valid_until.isoformat() if self.valid_until else "",
                str(self.temporary),
            )
        )
        return sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class InferencePolicy:
    max_results: int = 20
    allow_review_required_context: bool = True
    include_proposed_claims: bool = True

    def __post_init__(self) -> None:
        if self.max_results <= 0:
            raise ValueError("inference result limit must be positive")


@dataclass(frozen=True)
class InferenceResult:
    rule_id: str
    rule_version: str
    status: InferenceStatus | str
    rationale: str
    input_claim_ids: tuple[str, ...] = ()
    output_claim: Claim | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        InferenceStatus(self.status)
        if not self.rule_id.strip() or not self.rule_version.strip():
            raise ValueError("inference result rule identity must not be empty")
        if not self.rationale.strip():
            raise ValueError("inference result rationale must not be empty")
        if self.created_at.tzinfo is None:
            raise ValueError("inference result timestamp must be timezone-aware")
        if len(self.input_claim_ids) != len(set(self.input_claim_ids)):
            raise ValueError("inference result must not repeat input claims")
        if (
            self.normalized_status is InferenceStatus.APPLIED
            and self.output_claim is None
        ):
            raise ValueError("applied inference requires an output claim")
        if self.output_claim is not None:
            if self.output_claim.normalized_type is not ClaimType.RULE_RESULT:
                raise ValueError("inference outputs must be rule-result claims")
            expected = f"{self.rule_id}@{self.rule_version}"
            if self.output_claim.rule_reference != expected:
                raise ValueError("inference output rule reference is inconsistent")

    @property
    def normalized_status(self) -> InferenceStatus:
        return InferenceStatus(self.status)


@dataclass(frozen=True)
class InferenceRun:
    context_id: str
    results: tuple[InferenceResult, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    run_id: str = ""

    def __post_init__(self) -> None:
        if not self.context_id.strip():
            raise ValueError("inference run context id must not be empty")
        if self.created_at.tzinfo is None:
            raise ValueError("inference run timestamp must be timezone-aware")
        ordered = tuple(
            sorted(
                self.results,
                key=lambda item: (item.rule_id, item.rule_version, item.status),
            )
        )
        object.__setattr__(self, "results", ordered)
        payload = "|".join(
            (
                self.context_id,
                ",".join(
                    f"{item.rule_id}@{item.rule_version}:{item.status}:"
                    f"{','.join(item.input_claim_ids)}:"
                    f"{item.output_claim.fingerprint if item.output_claim else ''}"
                    for item in ordered
                ),
            )
        )
        expected = sha256(payload.encode("utf-8")).hexdigest()
        if self.run_id and self.run_id != expected:
            raise ValueError("inference run id is inconsistent")
        object.__setattr__(self, "run_id", expected)

    @property
    def applied_claims(self) -> tuple[Claim, ...]:
        return tuple(
            result.output_claim
            for result in self.results
            if result.output_claim is not None
        )


@runtime_checkable
class InferenceRuleRegistry(Protocol):
    def register(self, rule: InferenceRule) -> InferenceRule: ...

    def get(self, rule_id: str, version: str | None = None) -> InferenceRule | None: ...

    def list(self) -> tuple[InferenceRule, ...]: ...


class InMemoryInferenceRuleRegistry:
    def __init__(self) -> None:
        self._rules: dict[tuple[str, str], InferenceRule] = {}

    def register(self, rule: InferenceRule) -> InferenceRule:
        key = (rule.rule_id, rule.version)
        existing = self._rules.get(key)
        if existing is not None and existing.fingerprint != rule.fingerprint:
            raise ValueError("inference rule version is already registered differently")
        self._rules[key] = rule
        return rule

    def get(self, rule_id: str, version: str | None = None) -> InferenceRule | None:
        if version is not None:
            return self._rules.get((rule_id, version))
        matches = [
            rule for (stored_id, _), rule in self._rules.items() if stored_id == rule_id
        ]
        return sorted(matches, key=lambda item: item.version)[-1] if matches else None

    def list(self) -> tuple[InferenceRule, ...]:
        return tuple(
            sorted(self._rules.values(), key=lambda item: (item.rule_id, item.version))
        )


class GovernedInferenceEngine:
    def __init__(
        self,
        registry: InferenceRuleRegistry | None = None,
        policy: InferencePolicy | None = None,
    ) -> None:
        self.registry = registry or InMemoryInferenceRuleRegistry()
        self.policy = policy or InferencePolicy()

    def infer(
        self,
        context: ReasoningContextBundle,
        *,
        now: datetime | None = None,
        scope_reference: str | None = None,
    ) -> InferenceRun:
        evaluated_at = now or datetime.now(timezone.utc)
        if evaluated_at.tzinfo is None:
            raise ValueError("inference timestamp must be timezone-aware")
        if context.normalized_status is ContextAssemblyStatus.BLOCKED:
            return self._uniform_run(context, InferenceStatus.BLOCKED, evaluated_at)
        if context.normalized_status is ContextAssemblyStatus.INSUFFICIENT:
            return self._uniform_run(
                context,
                InferenceStatus.NOT_APPLICABLE,
                evaluated_at,
            )
        if (
            context.normalized_status is ContextAssemblyStatus.REVIEW_REQUIRED
            and not self.policy.allow_review_required_context
        ):
            return self._uniform_run(
                context,
                InferenceStatus.REVIEW_REQUIRED,
                evaluated_at,
            )

        rules = self.registry.list()[: self.policy.max_results]
        results = [
            self._evaluate(
                rule,
                context,
                evaluated_at,
                scope_reference=scope_reference,
            )
            for rule in rules
        ]

        propagated_claims = self._bounded_propagation_claims(results, context.claims)
        if propagated_claims:
            available_claims = context.claims + propagated_claims
            for index, (rule, result) in enumerate(zip(rules, results, strict=True)):
                if result.normalized_status is not InferenceStatus.NOT_APPLICABLE:
                    continue
                propagated = self._evaluate(
                    rule,
                    context,
                    evaluated_at,
                    scope_reference=scope_reference,
                    available_claims=available_claims,
                )
                if propagated.normalized_status in {
                    InferenceStatus.APPLIED,
                    InferenceStatus.REVIEW_REQUIRED,
                }:
                    results[index] = propagated
        return InferenceRun(context.context_id, tuple(results), evaluated_at)

    def _uniform_run(
        self,
        context: ReasoningContextBundle,
        status: InferenceStatus,
        now: datetime,
    ) -> InferenceRun:
        results = tuple(
            InferenceResult(
                rule.rule_id,
                rule.version,
                status,
                f"context status {context.normalized_status.value} prevents inference",
                created_at=now,
            )
            for rule in self.registry.list()[: self.policy.max_results]
        )
        return InferenceRun(context.context_id, results, now)

    def _evaluate(
        self,
        rule: InferenceRule,
        context: ReasoningContextBundle,
        now: datetime,
        *,
        scope_reference: str | None,
        available_claims: tuple[Claim, ...] | None = None,
    ) -> InferenceResult:
        if not rule.enabled:
            return self._result(rule, InferenceStatus.REJECTED, "rule is disabled", now)
        if rule.valid_from is not None and now < rule.valid_from:
            return self._result(
                rule, InferenceStatus.REJECTED, "rule is not yet valid", now
            )
        if rule.valid_until is not None and now >= rule.valid_until:
            return self._result(rule, InferenceStatus.REJECTED, "rule has expired", now)
        if rule.scope_reference is not None and scope_reference != rule.scope_reference:
            return self._result(
                rule,
                InferenceStatus.REJECTED,
                "rule is outside current temporary scope",
                now,
            )
        query_domains = set(context.query.normalized_domains)
        allowed = {ScopeDomain(item) for item in rule.allowed_domains}
        if not query_domains.intersection(allowed):
            return self._result(
                rule,
                InferenceStatus.REJECTED,
                "rule is outside query domains",
                now,
            )
        matches: list[Claim] = []
        for condition in rule.conditions:
            match = next(
                (
                    claim
                    for claim in (available_claims or context.claims)
                    if self._matches(condition, claim, context.query.as_of)
                    and claim not in matches
                ),
                None,
            )
            if match is None:
                return self._result(
                    rule,
                    InferenceStatus.NOT_APPLICABLE,
                    f"condition not satisfied: {condition.predicate}",
                    now,
                )
            matches.append(match)
        status = (
            InferenceStatus.REVIEW_REQUIRED
            if rule.requires_review
            or context.normalized_status is ContextAssemblyStatus.REVIEW_REQUIRED
            or any(
                claim.normalized_status is ClaimStatus.REVIEW_REQUIRED
                for claim in matches
            )
            else InferenceStatus.APPLIED
        )
        output = self._build_output(rule, tuple(matches), context, now, status)
        return InferenceResult(
            rule.rule_id,
            rule.version,
            status,
            f"all {len(rule.conditions)} rule conditions were satisfied",
            tuple(sorted(claim.claim_id for claim in matches)),
            output,
            now,
        )

    @staticmethod
    def _bounded_propagation_claims(
        results: list[InferenceResult],
        original_claims: tuple[Claim, ...],
    ) -> tuple[Claim, ...]:
        original_semantics = {
            (claim.subject, claim.predicate.casefold(), claim.object_value.casefold())
            for claim in original_claims
        }
        selected: dict[tuple[str, str, str], Claim] = {}
        for result in results:
            if result.normalized_status not in {
                InferenceStatus.APPLIED,
                InferenceStatus.REVIEW_REQUIRED,
            }:
                continue
            claim = result.output_claim
            if claim is None or claim.normalized_type is not ClaimType.RULE_RESULT:
                continue
            key = (
                claim.subject,
                claim.predicate.casefold(),
                claim.object_value.casefold(),
            )
            if key in original_semantics:
                continue
            selected.setdefault(key, claim)
        return tuple(
            selected[key]
            for key in sorted(selected)
        )

    def _build_output(
        self,
        rule: InferenceRule,
        inputs: tuple[Claim, ...],
        context: ReasoningContextBundle,
        now: datetime,
        status: InferenceStatus,
    ) -> Claim:
        links: dict[str, ClaimEvidenceLink] = {}
        for claim in inputs:
            for link in claim.evidence_links:
                links.setdefault(
                    link.evidence_id,
                    ClaimEvidenceLink(
                        evidence_id=link.evidence_id,
                        role=EvidenceLinkRole.CONTEXT,
                        source_type=link.source_type,
                        source_id=link.source_id,
                        evidence_fingerprint=link.evidence_fingerprint,
                    ),
                )
        confidence = min(
            [rule.base_confidence]
            + [
                claim.confidence.score
                for claim in inputs
                if claim.confidence is not None
            ]
        )
        claim_status = (
            ClaimStatus.REVIEW_REQUIRED
            if status is InferenceStatus.REVIEW_REQUIRED
            else ClaimStatus.PROPOSED
        )
        claim_id = sha256(
            f"{context.context_id}|{rule.reference}|"
            f"{','.join(sorted(claim.claim_id for claim in inputs))}".encode("utf-8")
        ).hexdigest()
        return Claim(
            subject=rule.conclusion_subject,
            predicate=rule.conclusion_predicate,
            object_value=rule.conclusion_object,
            claim_type=ClaimType.RULE_RESULT,
            origin=ClaimOrigin.RULE,
            status=claim_status,
            evidence_links=tuple(
                sorted(links.values(), key=lambda item: item.evidence_id)
            ),
            confidence=ClaimConfidence(
                confidence,
                f"bounded by rule {rule.reference} and input claim confidence",
            ),
            owner=context.query.owner,
            rule_reference=rule.reference,
            created_at=now,
            claim_id=claim_id,
        )

    @staticmethod
    def _matches(
        condition: ClaimCondition,
        claim: Claim,
        as_of: datetime,
    ) -> bool:
        if condition.subject is not None and claim.subject != condition.subject:
            return False
        if claim.predicate.casefold() != condition.predicate.casefold():
            return False
        value = claim.object_value.strip()
        operator = condition.normalized_operator
        if operator is InferenceOperator.EQUALS:
            return value.casefold() == condition.values[0].casefold()
        if operator is InferenceOperator.IN:
            return value.casefold() in {item.casefold() for item in condition.values}
        try:
            timestamp = datetime.fromisoformat(value)
        except ValueError:
            return False
        if timestamp.tzinfo is None:
            return False
        if operator is InferenceOperator.BEFORE_AS_OF:
            return timestamp < as_of
        return timestamp > as_of

    @staticmethod
    def _result(
        rule: InferenceRule,
        status: InferenceStatus,
        rationale: str,
        now: datetime,
    ) -> InferenceResult:
        return InferenceResult(
            rule.rule_id,
            rule.version,
            status,
            rationale,
            created_at=now,
        )
