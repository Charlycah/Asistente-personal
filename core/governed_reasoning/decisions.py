from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
from typing import Protocol, runtime_checkable

from core.governed_reasoning.bounded_non_rule_derivation import (
    BoundedNonRuleDerivationStatus,
    GovernedBoundedNonRuleDerivation,
)
from core.governed_reasoning.conflicts import (
    ConflictAnalysis,
    ResolutionStatus,
)
from core.governed_reasoning.context import (
    ContextAssemblyStatus,
    ReasoningContextBundle,
)
from core.governed_reasoning.inference import InferenceRun, InferenceStatus


class DecisionStatus(str, Enum):
    """Lifecycle state of an immutable reasoning decision record."""

    COMPLETED = "completed"
    INCONCLUSIVE = "inconclusive"
    BLOCKED = "blocked"
    CONFLICT_UNRESOLVED = "conflict_unresolved"
    REVIEW_REQUIRED = "review_required"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


class DecisionOutcome(str, Enum):
    """Public outcome category, distinct from lifecycle state."""

    CONCLUSION = "conclusion"
    ABSTENTION = "abstention"
    BLOCKED = "blocked"
    HUMAN_REVIEW = "human_review"


class ReviewStatus(str, Enum):
    """Human review state attached to a decision record."""

    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(frozen=True)
class DecisionEvidenceLink:
    evidence_id: str
    fingerprint: str

    def __post_init__(self) -> None:
        if not self.evidence_id.strip():
            raise ValueError("decision evidence id must not be empty")
        if len(self.fingerprint) != 64:
            raise ValueError("decision evidence fingerprint must be SHA-256")


@dataclass(frozen=True)
class DecisionClaimLink:
    claim_id: str
    revision: int

    def __post_init__(self) -> None:
        if not self.claim_id.strip():
            raise ValueError("decision claim id must not be empty")
        if self.revision < 1:
            raise ValueError("decision claim revision must be positive")


@dataclass(frozen=True)
class DecisionRuleLink:
    rule_id: str
    version: str

    def __post_init__(self) -> None:
        if not self.rule_id.strip():
            raise ValueError("decision rule id must not be empty")
        if not self.version.strip():
            raise ValueError("decision rule version must not be empty")


@dataclass(frozen=True)
class ReviewEvent:
    reviewer: str
    status: ReviewStatus | str
    comment: str
    reviewed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        ReviewStatus(self.status)
        if not self.reviewer.strip() or not self.comment.strip():
            raise ValueError("review event requires reviewer and comment")
        if self.reviewed_at.tzinfo is None:
            raise ValueError("review timestamp must be timezone-aware")
        if self.normalized_status in {
            ReviewStatus.NOT_REQUIRED,
            ReviewStatus.PENDING,
        }:
            raise ValueError("review events require a final review status")

    @property
    def normalized_status(self) -> ReviewStatus:
        return ReviewStatus(self.status)


@dataclass(frozen=True)
class DecisionRecord:
    query_id: str
    query_text: str
    context_id: str
    scope_status: str
    status: DecisionStatus | str
    outcome: DecisionOutcome | str
    conclusion: str
    confidence_score: float
    confidence_rationale: str
    evidence_links: tuple[DecisionEvidenceLink, ...] = ()
    claim_links: tuple[DecisionClaimLink, ...] = ()
    rule_links: tuple[DecisionRuleLink, ...] = ()
    conflict_ids: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()
    review_status: ReviewStatus | str = ReviewStatus.NOT_REQUIRED
    review_events: tuple[ReviewEvent, ...] = ()
    supersedes: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    decision_id: str = ""

    def __post_init__(self) -> None:
        DecisionStatus(self.status)
        DecisionOutcome(self.outcome)
        ReviewStatus(self.review_status)
        for value, label in (
            (self.query_id, "query id"),
            (self.query_text, "query text"),
            (self.context_id, "context id"),
            (self.scope_status, "scope status"),
            (self.conclusion, "conclusion"),
            (self.confidence_rationale, "confidence rationale"),
        ):
            if not value.strip():
                raise ValueError(f"decision {label} must not be empty")
        if not 0.0 <= self.confidence_score <= 1.0:
            raise ValueError("decision confidence must be between zero and one")
        if self.created_at.tzinfo is None:
            raise ValueError("decision timestamp must be timezone-aware")
        if self.supersedes is not None and not self.supersedes.strip():
            raise ValueError("superseded decision id must not be blank")
        self._validate_unique_links()
        self._validate_governance()
        object.__setattr__(
            self,
            "evidence_links",
            tuple(sorted(self.evidence_links, key=lambda item: item.evidence_id)),
        )
        object.__setattr__(
            self,
            "claim_links",
            tuple(
                sorted(
                    self.claim_links, key=lambda item: (item.claim_id, item.revision)
                )
            ),
        )
        object.__setattr__(
            self,
            "rule_links",
            tuple(
                sorted(self.rule_links, key=lambda item: (item.rule_id, item.version))
            ),
        )
        object.__setattr__(self, "conflict_ids", tuple(sorted(self.conflict_ids)))
        object.__setattr__(self, "limitations", tuple(sorted(self.limitations)))
        object.__setattr__(self, "assumptions", tuple(sorted(self.assumptions)))
        expected = sha256(self._identity_payload().encode("utf-8")).hexdigest()
        if self.decision_id and self.decision_id != expected:
            raise ValueError("decision id is inconsistent")
        object.__setattr__(self, "decision_id", expected)

    @property
    def normalized_status(self) -> DecisionStatus:
        return DecisionStatus(self.status)

    @property
    def normalized_outcome(self) -> DecisionOutcome:
        return DecisionOutcome(self.outcome)

    @property
    def normalized_review_status(self) -> ReviewStatus:
        return ReviewStatus(self.review_status)

    @property
    def requires_human_review(self) -> bool:
        return self.normalized_review_status is ReviewStatus.PENDING

    def _validate_unique_links(self) -> None:
        for values, label in (
            ([item.evidence_id for item in self.evidence_links], "evidence"),
            ([item.claim_id for item in self.claim_links], "claim"),
            ([f"{item.rule_id}:{item.version}" for item in self.rule_links], "rule"),
            (list(self.conflict_ids), "conflict"),
        ):
            if len(values) != len(set(values)):
                raise ValueError(f"decision {label} links must be unique")

    def _validate_governance(self) -> None:
        status = self.normalized_status
        outcome = self.normalized_outcome
        review = self.normalized_review_status
        if status is DecisionStatus.BLOCKED and outcome is not DecisionOutcome.BLOCKED:
            raise ValueError("blocked decisions require blocked outcome")
        if status is DecisionStatus.REVIEW_REQUIRED:
            if outcome is not DecisionOutcome.HUMAN_REVIEW:
                raise ValueError(
                    "review-required decisions require human-review outcome"
                )
            if review is not ReviewStatus.PENDING:
                raise ValueError("review-required decisions require pending review")
        if (
            review is ReviewStatus.PENDING
            and status is not DecisionStatus.REVIEW_REQUIRED
        ):
            raise ValueError("pending review requires review-required decision status")
        if self.review_events:
            latest = self.review_events[-1].normalized_status
            if review is not latest:
                raise ValueError("review status must match latest review event")

    def _identity_payload(self) -> str:
        return "|".join(
            (
                self.query_id,
                self.context_id,
                self.scope_status,
                self.normalized_status.value,
                self.normalized_outcome.value,
                self.conclusion,
                f"{self.confidence_score:.6f}",
                self.confidence_rationale,
                ",".join(
                    f"{item.evidence_id}:{item.fingerprint}"
                    for item in self.evidence_links
                ),
                ",".join(
                    f"{item.claim_id}:{item.revision}" for item in self.claim_links
                ),
                ",".join(f"{item.rule_id}:{item.version}" for item in self.rule_links),
                ",".join(self.conflict_ids),
                ",".join(self.limitations),
                ",".join(self.assumptions),
                self.normalized_review_status.value,
                ",".join(
                    f"{item.reviewer}:{item.normalized_status.value}:"
                    f"{item.comment}:{item.reviewed_at.isoformat()}"
                    for item in self.review_events
                ),
                self.supersedes or "",
                self.created_at.isoformat(),
            )
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.decision_id,
            "query_id": self.query_id,
            "query_text": self.query_text,
            "context_id": self.context_id,
            "scope_status": self.scope_status,
            "status": self.normalized_status.value,
            "outcome": self.normalized_outcome.value,
            "conclusion": self.conclusion,
            "confidence": {
                "score": self.confidence_score,
                "rationale": self.confidence_rationale,
            },
            "evidence": [item.evidence_id for item in self.evidence_links],
            "claims": [
                {"id": item.claim_id, "revision": item.revision}
                for item in self.claim_links
            ],
            "rules": [
                {"id": item.rule_id, "version": item.version}
                for item in self.rule_links
            ],
            "conflicts": list(self.conflict_ids),
            "limitations": list(self.limitations),
            "assumptions": list(self.assumptions),
            "review_status": self.normalized_review_status.value,
            "supersedes": self.supersedes,
            "created_at": self.created_at.isoformat(),
        }


@runtime_checkable
class DecisionRecordRepository(Protocol):
    def add(self, record: DecisionRecord) -> None: ...

    def get(self, decision_id: str) -> DecisionRecord | None: ...

    def list_all(self) -> tuple[DecisionRecord, ...]: ...


class InMemoryDecisionRecordRepository:
    def __init__(self) -> None:
        self._records: dict[str, DecisionRecord] = {}

    def add(self, record: DecisionRecord) -> None:
        if record.decision_id in self._records:
            raise ValueError("decision record already exists")
        self._records[record.decision_id] = record

    def get(self, decision_id: str) -> DecisionRecord | None:
        return self._records.get(decision_id)

    def list_all(self) -> tuple[DecisionRecord, ...]:
        return tuple(
            sorted(
                self._records.values(),
                key=lambda item: (item.created_at, item.decision_id),
            )
        )


class DecisionRecordManager:
    def __init__(self, repository: DecisionRecordRepository) -> None:
        self.repository = repository

    def record(
        self,
        context: ReasoningContextBundle,
        conflict_analysis: ConflictAnalysis,
        *,
        conclusion: str,
        inference_run: InferenceRun | None = None,
        non_rule_derivations: tuple[GovernedBoundedNonRuleDerivation, ...] = (),
        limitations: tuple[str, ...] = (),
        assumptions: tuple[str, ...] = (),
        created_at: datetime | None = None,
    ) -> DecisionRecord:
        timestamp = created_at or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("decision timestamp must be timezone-aware")
        status, outcome, review = self._classify(
            context,
            conflict_analysis,
            inference_run,
            non_rule_derivations,
        )
        rule_links = self._rule_links(inference_run)
        claim_links = tuple(
            DecisionClaimLink(claim.claim_id, claim.revision)
            for claim in self._all_claims(
                context, inference_run, non_rule_derivations
            )
        )
        record = DecisionRecord(
            query_id=context.query.query_id,
            query_text=context.query.text,
            context_id=context.context_id,
            scope_status=context.scope_decision.normalized_status.value,
            status=status,
            outcome=outcome,
            conclusion=conclusion,
            confidence_score=conflict_analysis.confidence.score,
            confidence_rationale=conflict_analysis.confidence.rationale,
            evidence_links=tuple(
                DecisionEvidenceLink(item.evidence_id, item.fingerprint)
                for item in context.evidence
            ),
            claim_links=claim_links,
            rule_links=rule_links,
            conflict_ids=tuple(
                item.conflict_id for item in conflict_analysis.conflicts
            ),
            limitations=limitations,
            assumptions=assumptions,
            review_status=review,
            created_at=timestamp,
        )
        self.repository.add(record)
        return record

    def review(
        self,
        decision_id: str,
        *,
        reviewer: str,
        approved: bool,
        comment: str,
        reviewed_at: datetime | None = None,
    ) -> DecisionRecord:
        original = self.repository.get(decision_id)
        if original is None:
            raise KeyError(decision_id)
        if not original.requires_human_review:
            raise ValueError("decision is not pending human review")
        event = ReviewEvent(
            reviewer,
            ReviewStatus.APPROVED if approved else ReviewStatus.REJECTED,
            comment,
            reviewed_at or datetime.now(timezone.utc),
        )
        revised = replace(
            original,
            status=(DecisionStatus.COMPLETED if approved else DecisionStatus.REJECTED),
            outcome=(
                DecisionOutcome.CONCLUSION if approved else DecisionOutcome.ABSTENTION
            ),
            review_status=event.normalized_status,
            review_events=original.review_events + (event,),
            supersedes=original.decision_id,
            created_at=event.reviewed_at,
            decision_id="",
        )
        self.repository.add(revised)
        return revised

    def get(self, decision_id: str) -> DecisionRecord | None:
        return self.repository.get(decision_id)

    def list_all(self) -> tuple[DecisionRecord, ...]:
        return self.repository.list_all()

    @staticmethod
    def _all_claims(
        context: ReasoningContextBundle,
        inference_run: InferenceRun | None,
        non_rule_derivations: tuple[GovernedBoundedNonRuleDerivation, ...] = (),
    ) -> tuple:
        claims = {claim.claim_id: claim for claim in context.claims}
        if inference_run is not None:
            for claim in inference_run.applied_claims:
                claims[claim.claim_id] = claim
        for derivation in non_rule_derivations:
            if (
                derivation.status is BoundedNonRuleDerivationStatus.DERIVED
                and derivation.derived_claim is not None
            ):
                claims[derivation.derived_claim.claim_id] = derivation.derived_claim
        return tuple(sorted(claims.values(), key=lambda item: item.claim_id))

    @staticmethod
    def _rule_links(
        inference_run: InferenceRun | None,
    ) -> tuple[DecisionRuleLink, ...]:
        if inference_run is None:
            return ()
        links: dict[tuple[str, int], DecisionRuleLink] = {}
        for result in inference_run.results:
            rule_id = result.rule_id
            version_text = result.rule_version
            link = DecisionRuleLink(rule_id, version_text)
            links[(link.rule_id, link.version)] = link
        return tuple(
            sorted(links.values(), key=lambda item: (item.rule_id, item.version))
        )

    @staticmethod
    def _classify(
        context: ReasoningContextBundle,
        analysis: ConflictAnalysis,
        inference_run: InferenceRun | None,
        non_rule_derivations: tuple[GovernedBoundedNonRuleDerivation, ...] = (),
    ) -> tuple[DecisionStatus, DecisionOutcome, ReviewStatus]:
        if context.normalized_status is ContextAssemblyStatus.BLOCKED:
            return (
                DecisionStatus.BLOCKED,
                DecisionOutcome.BLOCKED,
                ReviewStatus.NOT_REQUIRED,
            )
        if context.normalized_status is ContextAssemblyStatus.REVIEW_REQUIRED:
            return (
                DecisionStatus.REVIEW_REQUIRED,
                DecisionOutcome.HUMAN_REVIEW,
                ReviewStatus.PENDING,
            )
        if analysis.requires_review:
            return (
                DecisionStatus.REVIEW_REQUIRED,
                DecisionOutcome.HUMAN_REVIEW,
                ReviewStatus.PENDING,
            )
        if any(
            item.normalized_status is ResolutionStatus.UNRESOLVED
            for item in analysis.decisions
        ):
            return (
                DecisionStatus.CONFLICT_UNRESOLVED,
                DecisionOutcome.ABSTENTION,
                ReviewStatus.NOT_REQUIRED,
            )
        if context.normalized_status is ContextAssemblyStatus.INSUFFICIENT:
            return (
                DecisionStatus.INCONCLUSIVE,
                DecisionOutcome.ABSTENTION,
                ReviewStatus.NOT_REQUIRED,
            )
        has_non_rule_derivation = any(
            item.status is BoundedNonRuleDerivationStatus.DERIVED
            and item.derived_claim is not None
            for item in non_rule_derivations
        )
        if (
            inference_run is not None
            and all(
                result.normalized_status is not InferenceStatus.APPLIED
                for result in inference_run.results
            )
            and not has_non_rule_derivation
        ):
            return (
                DecisionStatus.INCONCLUSIVE,
                DecisionOutcome.ABSTENTION,
                ReviewStatus.NOT_REQUIRED,
            )
        return (
            DecisionStatus.COMPLETED,
            DecisionOutcome.CONCLUSION,
            ReviewStatus.NOT_REQUIRED,
        )
