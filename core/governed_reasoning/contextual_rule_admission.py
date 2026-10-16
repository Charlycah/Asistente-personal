from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256

from core.governed_reasoning.contextual_rule_instantiation import (
    ContextualRuleInstantiationStatus,
    GovernedContextualRuleInstantiationCandidate,
)
from core.governed_reasoning.inference import (
    ClaimCondition,
    InferenceRule,
    InMemoryInferenceRuleRegistry,
)
from core.scope_guard import ScopeDomain

_SCHEMA_VERSION = "post-m409.1-temporary-concrete-rule-admission-v1"


@dataclass(frozen=True)
class GovernedTemporaryConcreteRuleAdmission:
    rule: InferenceRule
    source_candidate_fingerprint: str
    scope_reference: str
    admitted_at: datetime
    expires_at: datetime
    allowed_domains: tuple[ScopeDomain, ...]
    schema_version: str = _SCHEMA_VERSION
    canonical_authority: str = "governed_reasoning"
    session_local: bool = True
    persistent: bool = False
    creates_memory: bool = False
    creates_learning_candidate: bool = False
    modifies_learning: bool = False
    grants_authority: bool = False
    executes_actions: bool = False

    def __post_init__(self) -> None:
        if self.canonical_authority != "governed_reasoning":
            raise ValueError(
                "temporary rule admission must preserve reasoning authority"
            )
        if len(self.source_candidate_fingerprint) != 64:
            raise ValueError("temporary rule admission requires SHA-256 provenance")
        if not self.scope_reference.strip():
            raise ValueError("temporary rule admission requires scope")
        if self.admitted_at.tzinfo is None or self.expires_at.tzinfo is None:
            raise ValueError(
                "temporary rule admission timestamps must be timezone-aware"
            )
        if self.expires_at <= self.admitted_at:
            raise ValueError("temporary rule admission must expire after admission")
        if not self.allowed_domains:
            raise ValueError("temporary rule admission requires domains")
        if any(
            (
                not self.session_local,
                self.persistent,
                self.creates_memory,
                self.creates_learning_candidate,
                self.modifies_learning,
                self.grants_authority,
                self.executes_actions,
            )
        ):
            raise ValueError("temporary rule admission violates governed limits")
        if not self.rule.temporary:
            raise ValueError("temporary rule admission requires a temporary rule")
        if self.rule.source_fingerprint != self.source_candidate_fingerprint:
            raise ValueError("temporary rule admission provenance mismatch")
        if self.rule.scope_reference != self.scope_reference:
            raise ValueError("temporary rule admission scope mismatch")
        if (
            self.rule.valid_from != self.admitted_at
            or self.rule.valid_until != self.expires_at
        ):
            raise ValueError("temporary rule admission validity mismatch")
        if tuple(self.rule.normalized_domains) != self.allowed_domains:
            raise ValueError("temporary rule admission domain mismatch")


class GovernedTemporaryConcreteRuleAdmissionBoundary:
    """Admit one instantiated candidate into the existing in-memory registry."""

    def admit(
        self,
        *,
        candidate: GovernedContextualRuleInstantiationCandidate,
        registry: InMemoryInferenceRuleRegistry,
        scope_reference: str,
        allowed_domains: tuple[ScopeDomain | str, ...],
        admitted_at: datetime,
        expires_at: datetime,
    ) -> GovernedTemporaryConcreteRuleAdmission:
        if candidate.status is not ContextualRuleInstantiationStatus.INSTANTIATED:
            raise ValueError("temporary rule admission requires instantiated candidate")
        if candidate.scope_reference != scope_reference:
            raise ValueError("temporary rule admission scope mismatch")
        if not allowed_domains:
            raise ValueError("temporary rule admission requires domains")
        normalized_domains = tuple(ScopeDomain(item) for item in allowed_domains)
        if admitted_at.tzinfo is None or expires_at.tzinfo is None:
            raise ValueError(
                "temporary rule admission timestamps must be timezone-aware"
            )
        if expires_at <= admitted_at:
            raise ValueError("temporary rule admission must expire after admission")
        if candidate.concrete_conclusion is None:
            raise ValueError("temporary rule admission requires concrete conclusion")

        identity_payload = (
            _SCHEMA_VERSION,
            candidate.source_fingerprint,
            scope_reference,
            tuple(item.value for item in normalized_domains),
            admitted_at.isoformat(),
            expires_at.isoformat(),
        )
        admission_fingerprint = sha256(
            repr(identity_payload).encode("utf-8")
        ).hexdigest()
        rule = InferenceRule(
            rule_id=candidate.source_rule_candidate_id,
            version=f"temporary-{admission_fingerprint[:16]}",
            description=(
                "Temporary concrete contextual rule admitted from explicit "
                f"candidate {candidate.source_rule_candidate_id}."
            ),
            conditions=tuple(
                ClaimCondition(
                    predicate=item.predicate_id,
                    values=(item.object_value,),
                    subject=item.subject,
                )
                for item in candidate.concrete_conditions
            ),
            conclusion_subject=candidate.concrete_conclusion.subject,
            conclusion_predicate=candidate.concrete_conclusion.predicate_id,
            conclusion_object=candidate.concrete_conclusion.object_value,
            allowed_domains=normalized_domains,
            requires_review=True,
            source_fingerprint=candidate.source_fingerprint,
            scope_reference=scope_reference,
            valid_from=admitted_at,
            valid_until=expires_at,
            temporary=True,
        )
        registered = registry.register(rule)
        return GovernedTemporaryConcreteRuleAdmission(
            rule=registered,
            source_candidate_fingerprint=candidate.source_fingerprint,
            scope_reference=scope_reference,
            admitted_at=admitted_at,
            expires_at=expires_at,
            allowed_domains=normalized_domains,
        )
