from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256

from core.governed_reasoning.claims import (
    Claim,
    ClaimRegistryManager,
    ClaimStatus,
)
from core.governed_reasoning.derived_assessment_contract import (
    ReasoningContextDerivedAssessment,
)
from core.governed_reasoning.evidence import (
    EvidenceReference,
    EvidenceRegistry,
    EvidenceSourceType,
    EvidenceStatus,
)
from core.scope_guard import (
    ScopeDomain,
    ScopeGuardDecision,
    ScopeGuardManager,
    ScopeGuardStatus,
)


class ContextAssemblyStatus(str, Enum):
    """Resultado gobernado del ensamblado de contexto."""

    READY = "ready"
    INSUFFICIENT = "insufficient"
    REVIEW_REQUIRED = "review_required"
    BLOCKED = "blocked"


class ContextItemType(str, Enum):
    """Tipos auditables de elementos evaluados para un contexto."""

    CLAIM = "claim"
    EVIDENCE = "evidence"


class ContextDecisionOutcome(str, Enum):
    """Resultado de selección para un elemento candidato."""

    INCLUDED = "included"
    EXCLUDED = "excluded"


@dataclass(frozen=True)
class ReasoningQuery:
    """Consulta normalizada que delimita propietario, dominios y tiempo."""

    text: str
    owner: str = "shared"
    domains: tuple[ScopeDomain | str, ...] = (ScopeDomain.PERSONAL_OPERATIONS,)
    topics: tuple[str, ...] = ()
    claim_ids: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    as_of: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    query_id: str = ""

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise ValueError("reasoning query text must not be empty")
        if not self.owner.strip():
            raise ValueError("reasoning query owner must not be empty")
        if self.as_of.tzinfo is None:
            raise ValueError("reasoning query timestamp must be timezone-aware")
        if not self.domains:
            raise ValueError("reasoning query requires at least one domain")
        for domain in self.domains:
            ScopeDomain(domain)
        for values, label in (
            (self.topics, "topics"),
            (self.claim_ids, "claim ids"),
            (self.evidence_ids, "evidence ids"),
        ):
            if any(not value.strip() for value in values):
                raise ValueError(f"reasoning query {label} must not contain blanks")
            if len(values) != len(set(values)):
                raise ValueError(f"reasoning query {label} must be unique")
        expected_id = sha256(self._identity_payload().encode("utf-8")).hexdigest()
        if self.query_id and self.query_id != expected_id:
            raise ValueError("reasoning query id is inconsistent")
        object.__setattr__(self, "query_id", expected_id)

    @property
    def normalized_domains(self) -> tuple[ScopeDomain, ...]:
        return tuple(ScopeDomain(domain) for domain in self.domains)

    @property
    def search_terms(self) -> tuple[str, ...]:
        terms = _tokens(self.text)
        for topic in self.topics:
            terms.update(_tokens(topic))
        return tuple(sorted(terms))

    def _identity_payload(self) -> str:
        return "|".join(
            (
                _normalize_text(self.text),
                self.owner.casefold(),
                ",".join(sorted(ScopeDomain(item).value for item in self.domains)),
                ",".join(sorted(_normalize_text(item) for item in self.topics)),
                ",".join(sorted(self.claim_ids)),
                ",".join(sorted(self.evidence_ids)),
                self.as_of.isoformat(),
            )
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.query_id,
            "text": self.text,
            "owner": self.owner,
            "domains": [domain.value for domain in self.normalized_domains],
            "topics": list(self.topics),
            "claim_ids": list(self.claim_ids),
            "evidence_ids": list(self.evidence_ids),
            "as_of": self.as_of.isoformat(),
        }


@dataclass(frozen=True)
class ContextSelectionPolicy:
    """Política determinista para limitar y filtrar el contexto."""

    max_claims: int = 20
    max_evidence: int = 30
    minimum_relevance: int = 1
    include_shared_owner: bool = True
    include_derived_summaries: bool = False
    allowed_claim_statuses: tuple[ClaimStatus | str, ...] = (
        ClaimStatus.PROPOSED,
        ClaimStatus.SUPPORTED,
        ClaimStatus.CORROBORATED,
        ClaimStatus.DISPUTED,
        ClaimStatus.REVIEW_REQUIRED,
    )
    allowed_evidence_statuses: tuple[EvidenceStatus | str, ...] = (
        EvidenceStatus.ACTIVE,
        EvidenceStatus.REVIEW_REQUIRED,
        EvidenceStatus.COMPLETED,
    )

    def __post_init__(self) -> None:
        if self.max_claims <= 0 or self.max_evidence <= 0:
            raise ValueError("context selection limits must be positive")
        if self.minimum_relevance < 0:
            raise ValueError("minimum context relevance must not be negative")
        if not self.allowed_claim_statuses or not self.allowed_evidence_statuses:
            raise ValueError("context selection status policies must not be empty")
        for status in self.allowed_claim_statuses:
            ClaimStatus(status)
        for status in self.allowed_evidence_statuses:
            EvidenceStatus(status)

    @property
    def normalized_claim_statuses(self) -> tuple[ClaimStatus, ...]:
        return tuple(ClaimStatus(status) for status in self.allowed_claim_statuses)

    @property
    def normalized_evidence_statuses(self) -> tuple[EvidenceStatus, ...]:
        return tuple(
            EvidenceStatus(status) for status in self.allowed_evidence_statuses
        )


@dataclass(frozen=True)
class ContextSelectionDecision:
    """Razón auditable de inclusión o exclusión de un candidato."""

    item_type: ContextItemType | str
    item_id: str
    outcome: ContextDecisionOutcome | str
    reason: str
    relevance: int = 0

    def __post_init__(self) -> None:
        ContextItemType(self.item_type)
        ContextDecisionOutcome(self.outcome)
        if not self.item_id.strip() or not self.reason.strip():
            raise ValueError("context selection decision fields must not be empty")
        if self.relevance < 0:
            raise ValueError("context relevance must not be negative")

    @property
    def normalized_item_type(self) -> ContextItemType:
        return ContextItemType(self.item_type)

    @property
    def normalized_outcome(self) -> ContextDecisionOutcome:
        return ContextDecisionOutcome(self.outcome)

    def to_dict(self) -> dict[str, object]:
        return {
            "item_type": self.normalized_item_type.value,
            "item_id": self.item_id,
            "outcome": self.normalized_outcome.value,
            "reason": self.reason,
            "relevance": self.relevance,
        }


@dataclass(frozen=True)
class ReasoningContextBundle:
    """Contexto mínimo, ordenado y verificable para milestones posteriores."""

    query: ReasoningQuery
    status: ContextAssemblyStatus | str
    scope_decision: ScopeGuardDecision
    claims: tuple[Claim, ...]
    evidence: tuple[EvidenceReference, ...]
    decisions: tuple[ContextSelectionDecision, ...]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    context_id: str = ""
    derived_assessments: tuple[ReasoningContextDerivedAssessment, ...] = ()

    def __post_init__(self) -> None:
        ContextAssemblyStatus(self.status)
        if self.created_at.tzinfo is None:
            raise ValueError("reasoning context timestamp must be timezone-aware")
        claim_ids = [claim.claim_id for claim in self.claims]
        evidence_ids = [item.evidence_id for item in self.evidence]
        assessment_ids = [item.assessment_id for item in self.derived_assessments]
        if len(claim_ids) != len(set(claim_ids)):
            raise ValueError("reasoning context must not repeat claims")
        if len(evidence_ids) != len(set(evidence_ids)):
            raise ValueError("reasoning context must not repeat evidence")
        if len(assessment_ids) != len(set(assessment_ids)):
            raise ValueError("reasoning context must not repeat derived assessments")
        ordered_claims = tuple(sorted(self.claims, key=_claim_context_sort_key))
        ordered_evidence = tuple(sorted(self.evidence, key=_evidence_context_sort_key))
        ordered_decisions = tuple(sorted(self.decisions, key=_decision_sort_key))
        ordered_assessments = tuple(
            sorted(self.derived_assessments, key=lambda item: item.assessment_id)
        )
        object.__setattr__(self, "claims", ordered_claims)
        object.__setattr__(self, "evidence", ordered_evidence)
        object.__setattr__(self, "decisions", ordered_decisions)
        object.__setattr__(self, "derived_assessments", ordered_assessments)
        expected_id = sha256(self._fingerprint_payload().encode("utf-8")).hexdigest()
        if self.context_id and self.context_id != expected_id:
            raise ValueError("reasoning context id is inconsistent")
        object.__setattr__(self, "context_id", expected_id)

    @property
    def normalized_status(self) -> ContextAssemblyStatus:
        return ContextAssemblyStatus(self.status)

    @property
    def requires_human_review(self) -> bool:
        return self.normalized_status is ContextAssemblyStatus.REVIEW_REQUIRED

    def _fingerprint_payload(self) -> str:
        return "|".join(
            (
                self.query.query_id,
                self.normalized_status.value,
                self.scope_decision.normalized_status.value,
                ",".join(f"{claim.claim_id}:{claim.revision}" for claim in self.claims),
                ",".join(item.evidence_id for item in self.evidence),
                ",".join(
                    f"{item.normalized_item_type.value}:{item.item_id}:"
                    f"{item.normalized_outcome.value}:{item.reason}:{item.relevance}"
                    for item in self.decisions
                ),
                *(
                    (
                        ",".join(
                            item.assessment_id for item in self.derived_assessments
                        ),
                    )
                    if self.derived_assessments
                    else ()
                ),
            )
        )

    def to_dict(self) -> dict[str, object]:
        payload = {
            "id": self.context_id,
            "status": self.normalized_status.value,
            "query": self.query.to_dict(),
            "scope_decision": self.scope_decision.to_dict(),
            "claims": [claim.to_dict() for claim in self.claims],
            "evidence": [item.to_dict() for item in self.evidence],
            "decisions": [item.to_dict() for item in self.decisions],
            "requires_human_review": self.requires_human_review,
            "created_at": self.created_at.isoformat(),
        }
        if self.derived_assessments:
            payload["derived_assessments"] = [
                item.to_dict() for item in self.derived_assessments
            ]
        return payload


class GovernedContextAssembler:
    """Selecciona contexto M77/M78 después de aplicar Scope Guard."""

    def __init__(
        self,
        *,
        claim_registry: ClaimRegistryManager,
        evidence_registry: EvidenceRegistry,
        scope_guard: ScopeGuardManager | None = None,
        policy: ContextSelectionPolicy | None = None,
    ) -> None:
        self.claim_registry = claim_registry
        self.evidence_registry = evidence_registry
        self.scope_guard = scope_guard or ScopeGuardManager()
        self.policy = policy or ContextSelectionPolicy()

    def assemble(
        self,
        query: ReasoningQuery,
        *,
        now: datetime | None = None,
    ) -> ReasoningContextBundle:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("context assembly timestamp must be timezone-aware")
        snapshot = self.scope_guard.observe_turn(
            query.text,
            proposed_domains=query.normalized_domains,
            now=query.as_of,
        )
        scope_decision = snapshot.decision
        if scope_decision.normalized_status is ScopeGuardStatus.OUT_OF_SCOPE:
            return ReasoningContextBundle(
                query=query,
                status=ContextAssemblyStatus.BLOCKED,
                scope_decision=scope_decision,
                claims=(),
                evidence=(),
                decisions=(),
                created_at=timestamp,
            )

        selected_claims, claim_decisions = self._select_claims(query)
        selected_evidence, evidence_decisions = self._select_evidence(
            query,
            selected_claims,
        )
        decisions = claim_decisions + evidence_decisions
        status = self._status_for(scope_decision, selected_claims, selected_evidence)
        return ReasoningContextBundle(
            query=query,
            status=status,
            scope_decision=scope_decision,
            claims=selected_claims,
            evidence=selected_evidence,
            decisions=decisions,
            created_at=timestamp,
        )

    def _select_claims(
        self,
        query: ReasoningQuery,
    ) -> tuple[tuple[Claim, ...], tuple[ContextSelectionDecision, ...]]:
        scored: list[tuple[int, Claim]] = []
        decisions: list[ContextSelectionDecision] = []
        explicit = set(query.claim_ids)
        for claim in self.claim_registry.list_all():
            reason = self._claim_exclusion_reason(claim, query)
            relevance = self._claim_relevance(claim, query)
            if reason is None and claim.claim_id not in explicit:
                if relevance < self.policy.minimum_relevance:
                    reason = "not relevant to query"
            if reason is not None:
                decisions.append(
                    ContextSelectionDecision(
                        ContextItemType.CLAIM,
                        claim.claim_id,
                        ContextDecisionOutcome.EXCLUDED,
                        reason,
                        relevance,
                    )
                )
                continue
            scored.append((relevance, claim))

        scored.sort(key=lambda item: (-item[0], *_claim_context_sort_key(item[1])))
        selected_pairs = scored[: self.policy.max_claims]
        selected_ids = {claim.claim_id for _, claim in selected_pairs}
        for relevance, claim in scored:
            included = claim.claim_id in selected_ids
            decisions.append(
                ContextSelectionDecision(
                    ContextItemType.CLAIM,
                    claim.claim_id,
                    (
                        ContextDecisionOutcome.INCLUDED
                        if included
                        else ContextDecisionOutcome.EXCLUDED
                    ),
                    "explicit or relevant claim" if included else "claim limit reached",
                    relevance,
                )
            )
        return (
            tuple(claim for _, claim in selected_pairs),
            tuple(decisions),
        )

    def _select_evidence(
        self,
        query: ReasoningQuery,
        claims: tuple[Claim, ...],
    ) -> tuple[
        tuple[EvidenceReference, ...],
        tuple[ContextSelectionDecision, ...],
    ]:
        linked_ids = {
            link.evidence_id for claim in claims for link in claim.evidence_links
        }
        explicit = set(query.evidence_ids)
        scored: list[tuple[int, EvidenceReference]] = []
        decisions: list[ContextSelectionDecision] = []
        available = {
            item.evidence_id: item for item in self.evidence_registry.list_all()
        }

        for missing_id in sorted((linked_ids | explicit) - available.keys()):
            decisions.append(
                ContextSelectionDecision(
                    ContextItemType.EVIDENCE,
                    missing_id,
                    ContextDecisionOutcome.EXCLUDED,
                    "referenced evidence is unavailable",
                )
            )

        for evidence in available.values():
            reason = self._evidence_exclusion_reason(evidence, query)
            relevance = self._evidence_relevance(evidence, query)
            is_linked = evidence.evidence_id in linked_ids
            is_explicit = evidence.evidence_id in explicit
            if reason is None and not (is_linked or is_explicit):
                if relevance < self.policy.minimum_relevance:
                    reason = "not relevant to query"
            if reason is not None:
                decisions.append(
                    ContextSelectionDecision(
                        ContextItemType.EVIDENCE,
                        evidence.evidence_id,
                        ContextDecisionOutcome.EXCLUDED,
                        reason,
                        relevance,
                    )
                )
                continue
            priority = relevance + (100 if is_explicit else 50 if is_linked else 0)
            scored.append((priority, evidence))

        scored.sort(key=lambda item: (-item[0], *_evidence_context_sort_key(item[1])))
        selected_pairs = scored[: self.policy.max_evidence]
        selected_ids = {item.evidence_id for _, item in selected_pairs}
        for priority, evidence in scored:
            included = evidence.evidence_id in selected_ids
            decisions.append(
                ContextSelectionDecision(
                    ContextItemType.EVIDENCE,
                    evidence.evidence_id,
                    (
                        ContextDecisionOutcome.INCLUDED
                        if included
                        else ContextDecisionOutcome.EXCLUDED
                    ),
                    (
                        "explicit, linked or relevant evidence"
                        if included
                        else "evidence limit reached"
                    ),
                    priority,
                )
            )
        return (
            tuple(item for _, item in selected_pairs),
            tuple(decisions),
        )

    def _claim_exclusion_reason(
        self,
        claim: Claim,
        query: ReasoningQuery,
    ) -> str | None:
        if not self._owner_allowed(claim.owner, query.owner):
            return "owner outside query scope"
        if claim.normalized_status not in self.policy.normalized_claim_statuses:
            return f"claim status excluded: {claim.normalized_status.value}"
        if claim.valid_from is not None and claim.valid_from > query.as_of:
            return "claim is not yet valid"
        if claim.valid_until is not None and claim.valid_until < query.as_of:
            return "claim is no longer valid"
        return None

    def _evidence_exclusion_reason(
        self,
        evidence: EvidenceReference,
        query: ReasoningQuery,
    ) -> str | None:
        if not self._owner_allowed(evidence.owner, query.owner):
            return "owner outside query scope"
        if evidence.normalized_status not in self.policy.normalized_evidence_statuses:
            return f"evidence status excluded: {evidence.normalized_status.value}"
        if evidence.valid_from is not None and evidence.valid_from > query.as_of:
            return "evidence is not yet valid"
        if evidence.valid_until is not None and evidence.valid_until < query.as_of:
            return "evidence is no longer valid"
        if (
            evidence.normalized_source_type is EvidenceSourceType.DAILY_BRIEFING
            and not self.policy.include_derived_summaries
        ):
            return "derived briefing summaries are excluded by policy"
        return None

    def _owner_allowed(self, item_owner: str, query_owner: str) -> bool:
        if item_owner == query_owner:
            return True
        return self.policy.include_shared_owner and item_owner == "shared"

    @staticmethod
    def _claim_relevance(claim: Claim, query: ReasoningQuery) -> int:
        haystack = " ".join((claim.subject, claim.predicate, claim.object_value))
        return _relevance(haystack, query.search_terms)

    @staticmethod
    def _evidence_relevance(
        evidence: EvidenceReference,
        query: ReasoningQuery,
    ) -> int:
        metadata = " ".join(f"{key} {value}" for key, value in evidence.metadata)
        return _relevance(f"{evidence.summary} {metadata}", query.search_terms)

    @staticmethod
    def _status_for(
        scope_decision: ScopeGuardDecision,
        claims: tuple[Claim, ...],
        evidence: tuple[EvidenceReference, ...],
    ) -> ContextAssemblyStatus:
        if not claims and not evidence:
            return ContextAssemblyStatus.INSUFFICIENT
        requires_review = (
            scope_decision.normalized_status is ScopeGuardStatus.REVIEW_REQUIRED
            or any(
                claim.normalized_status
                in {ClaimStatus.DISPUTED, ClaimStatus.REVIEW_REQUIRED}
                for claim in claims
            )
            or any(
                item.normalized_status is EvidenceStatus.REVIEW_REQUIRED
                for item in evidence
            )
        )
        if requires_review:
            return ContextAssemblyStatus.REVIEW_REQUIRED
        return ContextAssemblyStatus.READY


def _normalize_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value.casefold())
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def _tokens(value: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9_]+", _normalize_text(value))
        if len(token) > 1
    }


def _relevance(value: str, terms: tuple[str, ...]) -> int:
    haystack = _tokens(value)
    return sum(1 for term in terms if term in haystack)


def _claim_context_sort_key(claim: Claim) -> tuple[str, str, str, str]:
    return (
        claim.owner.casefold(),
        claim.subject.casefold(),
        claim.predicate.casefold(),
        claim.claim_id,
    )


def _evidence_context_sort_key(
    evidence: EvidenceReference,
) -> tuple[str, str, str]:
    return (
        evidence.normalized_source_type.value,
        evidence.source_id,
        evidence.evidence_id,
    )


def _decision_sort_key(
    decision: ContextSelectionDecision,
) -> tuple[str, str, str, str]:
    return (
        decision.normalized_item_type.value,
        decision.item_id,
        decision.normalized_outcome.value,
        decision.reason,
    )
