from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256

from core.governed_reasoning.claims import Claim, ClaimStatus, ClaimType
from core.governed_reasoning.inference import InferenceRun


class ConflictType(str, Enum):
    VALUE_MISMATCH = "value_mismatch"
    STATUS_MISMATCH = "status_mismatch"
    EVIDENCE_CONTRADICTION = "evidence_contradiction"
    VALIDITY_OVERLAP = "validity_overlap"


class ConflictSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ResolutionStatus(str, Enum):
    RESOLVED = "resolved"
    UNRESOLVED = "unresolved"
    REVIEW_REQUIRED = "review_required"
    NO_CONFLICT = "no_conflict"


@dataclass(frozen=True)
class Conflict:
    conflict_type: ConflictType | str
    claim_ids: tuple[str, ...]
    subject: str
    predicate: str
    severity: ConflictSeverity | str
    rationale: str
    conflict_id: str = ""

    def __post_init__(self) -> None:
        ConflictType(self.conflict_type)
        ConflictSeverity(self.severity)
        if len(self.claim_ids) < 2:
            raise ValueError("conflicts require at least two claims")
        if len(self.claim_ids) != len(set(self.claim_ids)):
            raise ValueError("conflict claims must be unique")
        if not self.subject.strip() or not self.predicate.strip():
            raise ValueError("conflict subject and predicate must not be empty")
        if not self.rationale.strip():
            raise ValueError("conflict rationale must not be empty")
        ordered = tuple(sorted(self.claim_ids))
        object.__setattr__(self, "claim_ids", ordered)
        expected = sha256(
            "|".join(
                (
                    ConflictType(self.conflict_type).value,
                    self.subject.casefold(),
                    self.predicate.casefold(),
                    ",".join(ordered),
                )
            ).encode("utf-8")
        ).hexdigest()
        if self.conflict_id and self.conflict_id != expected:
            raise ValueError("conflict id is inconsistent")
        object.__setattr__(self, "conflict_id", expected)


@dataclass(frozen=True)
class UncertaintyFactor:
    name: str
    weight: float
    rationale: str

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.rationale.strip():
            raise ValueError("uncertainty factors require name and rationale")
        if not -1.0 <= self.weight <= 1.0:
            raise ValueError("uncertainty factor weight must be between -1 and 1")


@dataclass(frozen=True)
class ConfidenceAssessment:
    score: float
    factors: tuple[UncertaintyFactor, ...]
    rationale: str

    def __post_init__(self) -> None:
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("confidence score must be between zero and one")
        if not self.rationale.strip():
            raise ValueError("confidence rationale must not be empty")


@dataclass(frozen=True)
class ResolutionDecision:
    conflict_id: str
    status: ResolutionStatus | str
    selected_claim_id: str | None
    rationale: str

    def __post_init__(self) -> None:
        ResolutionStatus(self.status)
        if not self.conflict_id.strip() or not self.rationale.strip():
            raise ValueError("resolution decision requires identity and rationale")
        if self.normalized_status is ResolutionStatus.RESOLVED:
            if self.selected_claim_id is None:
                raise ValueError("resolved conflicts require a selected claim")
        elif self.selected_claim_id is not None:
            raise ValueError("unresolved conflicts cannot select a claim")

    @property
    def normalized_status(self) -> ResolutionStatus:
        return ResolutionStatus(self.status)


@dataclass(frozen=True)
class ConflictResolutionPolicy:
    prefer_corroborated: bool = True
    prefer_supported: bool = True
    prefer_non_rule_claims: bool = True
    require_review_for_high: bool = True
    unresolved_confidence_cap: float = 0.49
    conservative_epistemic_adjudication: bool = False

    def __post_init__(self) -> None:
        if not 0.0 <= self.unresolved_confidence_cap <= 1.0:
            raise ValueError("confidence cap must be between zero and one")


@dataclass(frozen=True)
class ConflictAnalysis:
    conflicts: tuple[Conflict, ...]
    decisions: tuple[ResolutionDecision, ...]
    confidence: ConfidenceAssessment
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    analysis_id: str = ""

    def __post_init__(self) -> None:
        if self.created_at.tzinfo is None:
            raise ValueError("analysis timestamp must be timezone-aware")
        ordered_conflicts = tuple(
            sorted(self.conflicts, key=lambda item: item.conflict_id)
        )
        ordered_decisions = tuple(
            sorted(self.decisions, key=lambda item: item.conflict_id)
        )
        object.__setattr__(self, "conflicts", ordered_conflicts)
        object.__setattr__(self, "decisions", ordered_decisions)
        payload = "|".join(
            (
                ",".join(item.conflict_id for item in ordered_conflicts),
                ",".join(
                    f"{item.conflict_id}:{item.normalized_status.value}:"
                    f"{item.selected_claim_id or ''}"
                    for item in ordered_decisions
                ),
                f"{self.confidence.score:.6f}",
            )
        )
        expected = sha256(payload.encode("utf-8")).hexdigest()
        if self.analysis_id and self.analysis_id != expected:
            raise ValueError("analysis id is inconsistent")
        object.__setattr__(self, "analysis_id", expected)

    @property
    def requires_review(self) -> bool:
        return any(
            decision.normalized_status is ResolutionStatus.REVIEW_REQUIRED
            for decision in self.decisions
        )


class ConflictResolutionManager:
    def __init__(self, policy: ConflictResolutionPolicy | None = None) -> None:
        self.policy = policy or ConflictResolutionPolicy()

    def analyze(
        self,
        claims: tuple[Claim, ...],
        *,
        inference_run: InferenceRun | None = None,
        now: datetime | None = None,
    ) -> ConflictAnalysis:
        evaluated_at = now or datetime.now(timezone.utc)
        if evaluated_at.tzinfo is None:
            raise ValueError("analysis timestamp must be timezone-aware")
        combined = list(claims)
        if inference_run is not None:
            combined.extend(inference_run.applied_claims)
        unique = {claim.claim_id: claim for claim in combined}
        ordered = tuple(sorted(unique.values(), key=lambda item: item.claim_id))
        conflicts = self._detect(ordered)
        decisions = tuple(self._resolve(conflict, unique) for conflict in conflicts)
        confidence = self._assess(ordered, conflicts, decisions)
        return ConflictAnalysis(conflicts, decisions, confidence, evaluated_at)

    def _detect(self, claims: tuple[Claim, ...]) -> tuple[Conflict, ...]:
        grouped: dict[tuple[str, str, str], list[Claim]] = {}
        for claim in claims:
            key = (
                claim.owner.casefold(),
                claim.subject.casefold(),
                claim.predicate.casefold(),
            )
            grouped.setdefault(key, []).append(claim)
        conflicts: list[Conflict] = []
        for group in grouped.values():
            active = [
                claim
                for claim in group
                if claim.normalized_status
                not in {ClaimStatus.SUPERSEDED, ClaimStatus.STALE}
            ]
            values = {claim.object_value.casefold() for claim in active}
            if len(active) > 1 and len(values) > 1:
                severity = (
                    ConflictSeverity.HIGH
                    if any(
                        claim.normalized_status is ClaimStatus.CORROBORATED
                        for claim in active
                    )
                    else ConflictSeverity.MEDIUM
                )
                conflicts.append(
                    Conflict(
                        ConflictType.VALUE_MISMATCH,
                        tuple(claim.claim_id for claim in active),
                        active[0].subject,
                        active[0].predicate,
                        severity,
                        "active claims assert incompatible values",
                    )
                )
        return tuple(conflicts)

    def _resolve(
        self,
        conflict: Conflict,
        claims: dict[str, Claim],
    ) -> ResolutionDecision:
        candidates = [claims[claim_id] for claim_id in conflict.claim_ids]
        if (
            self.policy.conservative_epistemic_adjudication
            and ConflictType(conflict.conflict_type) is ConflictType.VALUE_MISMATCH
        ):
            return ResolutionDecision(
                conflict.conflict_id,
                ResolutionStatus.UNRESOLVED,
                None,
                "conservative epistemic policy preserves incompatible claims",
            )
        if self.policy.require_review_for_high and ConflictSeverity(
            conflict.severity
        ) in {ConflictSeverity.HIGH, ConflictSeverity.CRITICAL}:
            return ResolutionDecision(
                conflict.conflict_id,
                ResolutionStatus.REVIEW_REQUIRED,
                None,
                "high-severity conflict requires human review",
            )
        ranked = sorted(candidates, key=self._rank, reverse=True)
        if len(ranked) > 1 and self._rank(ranked[0]) == self._rank(ranked[1]):
            return ResolutionDecision(
                conflict.conflict_id,
                ResolutionStatus.UNRESOLVED,
                None,
                "policy cannot distinguish equally ranked claims",
            )
        return ResolutionDecision(
            conflict.conflict_id,
            ResolutionStatus.RESOLVED,
            ranked[0].claim_id,
            "selected by deterministic claim precedence policy",
        )

    def _rank(self, claim: Claim) -> tuple[int, int, float, float, str]:
        status_rank = {
            ClaimStatus.CORROBORATED: 4 if self.policy.prefer_corroborated else 1,
            ClaimStatus.SUPPORTED: 3 if self.policy.prefer_supported else 1,
            ClaimStatus.PROPOSED: 1,
            ClaimStatus.REVIEW_REQUIRED: 0,
            ClaimStatus.DISPUTED: 0,
            ClaimStatus.REFUTED: -1,
            ClaimStatus.STALE: -2,
            ClaimStatus.SUPERSEDED: -3,
        }[claim.normalized_status]
        origin_rank = (
            0
            if self.policy.prefer_non_rule_claims
            and claim.normalized_type is ClaimType.RULE_RESULT
            else 1
        )
        confidence = claim.confidence.score if claim.confidence else 0.0
        return (
            status_rank,
            origin_rank,
            confidence,
            claim.created_at.timestamp(),
            claim.claim_id,
        )

    def _assess(
        self,
        claims: tuple[Claim, ...],
        conflicts: tuple[Conflict, ...],
        decisions: tuple[ResolutionDecision, ...],
    ) -> ConfidenceAssessment:
        base = min(
            (claim.confidence.score for claim in claims if claim.confidence),
            default=0.5,
        )
        factors: list[UncertaintyFactor] = []
        score = base
        if claims:
            factors.append(
                UncertaintyFactor("input_confidence", 0.0, "bounded by inputs")
            )
        unresolved = sum(
            decision.normalized_status
            in {ResolutionStatus.UNRESOLVED, ResolutionStatus.REVIEW_REQUIRED}
            for decision in decisions
        )
        if conflicts:
            penalty = min(0.5, 0.15 * len(conflicts))
            score -= penalty
            factors.append(
                UncertaintyFactor(
                    "conflicts",
                    -penalty,
                    f"{len(conflicts)} conflict(s) detected",
                )
            )
        if unresolved:
            score = min(score, self.policy.unresolved_confidence_cap)
            factors.append(
                UncertaintyFactor(
                    "unresolved_conflicts",
                    -0.25,
                    f"{unresolved} conflict(s) unresolved or under review",
                )
            )
        if not conflicts and claims:
            score += 0.1
            factors.append(
                UncertaintyFactor("consistency", 0.1, "no conflicts detected")
            )
        score = max(0.0, min(1.0, score))
        return ConfidenceAssessment(
            score,
            tuple(factors),
            "deterministic confidence assessment from inputs and conflicts",
        )
