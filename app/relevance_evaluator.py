from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from types import MappingProxyType
from typing import Mapping

from .personal_interest_center import (
    InterestPriority,
    InterestTopic,
    PersonalInterestCenter,
    PersonalInterestProfile,
)


class RelevanceRecipient(StrEnum):
    NOBODY = "nobody"
    CARLOS = "carlos"
    CRISTINA = "cristina"
    BOTH = "both"


@dataclass(frozen=True)
class RelevanceCandidate:
    title: str
    topics: frozenset[InterestTopic]
    location: str | None = None
    is_free: bool = False
    time_sensitive: bool = False
    importance: int = 0
    source_confidence: int | None = None
    verification: str | None = None
    information_kind: str | None = None
    published_at: datetime | None = None
    event_at: datetime | None = None
    region: str | None = None

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("relevance candidate title cannot be empty")
        if not 0 <= self.importance <= 20:
            raise ValueError("importance must be between 0 and 20")
        if self.source_confidence is not None and not (
            0 <= self.source_confidence <= 100
        ):
            raise ValueError("source confidence must be between 0 and 100")


@dataclass(frozen=True)
class RelevanceScoreBreakdown:
    interest_match: int
    priority_bonus: int
    locality_bonus: int
    free_access_bonus: int
    urgency_bonus: int
    importance_bonus: int
    source_quality_adjustment: int
    verification_adjustment: int
    freshness_adjustment: int
    kind_adjustment: int
    total: int


@dataclass(frozen=True)
class RelevanceDecision:
    recipient: RelevanceRecipient
    scores: Mapping[str, int]
    should_share: bool
    should_interrupt: bool
    reasons: tuple[str, ...]
    breakdowns: Mapping[str, RelevanceScoreBreakdown]


@dataclass(frozen=True)
class RelevanceEvaluatorSnapshot:
    schema_version: str
    authority: str
    share_threshold: int
    interrupt_threshold: int


class RelevanceEvaluator:
    """Canonical pure relevance authority for household information candidates."""

    SCHEMA_VERSION = "m343.3"
    AUTHORITY = "app.official_conversation_gateway:OfficialConversationGateway"
    SHARE_THRESHOLD = 60
    INTERRUPT_THRESHOLD = 80

    _PRIORITY_BONUS = {
        InterestPriority.LOW: -5,
        InterestPriority.MEDIUM: 0,
        InterestPriority.HIGH: 5,
        InterestPriority.VERY_HIGH: 10,
    }
    _VERIFICATION_ADJUSTMENT = {
        "confirmed": 5,
        "reported": 0,
        "unverified": -10,
    }
    _KIND_ADJUSTMENT = {
        "release": 4,
        "event": 3,
        "guidance": 2,
        "discovery": 2,
        "news": 0,
    }

    def __init__(self, interest_center: PersonalInterestCenter) -> None:
        self._interest_center = interest_center

    @property
    def snapshot(self) -> RelevanceEvaluatorSnapshot:
        return RelevanceEvaluatorSnapshot(
            schema_version=self.SCHEMA_VERSION,
            authority=self.AUTHORITY,
            share_threshold=self.SHARE_THRESHOLD,
            interrupt_threshold=self.INTERRUPT_THRESHOLD,
        )

    def evaluate(
        self,
        candidate: RelevanceCandidate,
        *,
        now: datetime | None = None,
    ) -> RelevanceDecision:
        effective_now = self._as_utc(now or datetime.now(timezone.utc))
        breakdowns = {
            profile.person: self._score(candidate, profile, effective_now)
            for profile in self._interest_center.snapshot.profiles
        }
        raw_scores = {
            person: breakdown.total for person, breakdown in breakdowns.items()
        }
        selected = tuple(
            person
            for person, score in raw_scores.items()
            if score >= self.SHARE_THRESHOLD
        )
        recipient = self._recipient_for(selected)
        best_score = max(raw_scores.values(), default=0)
        should_share = recipient is not RelevanceRecipient.NOBODY
        should_interrupt = should_share and best_score >= self.INTERRUPT_THRESHOLD
        return RelevanceDecision(
            recipient=recipient,
            scores=MappingProxyType(raw_scores),
            should_share=should_share,
            should_interrupt=should_interrupt,
            reasons=self._reasons(candidate, selected, breakdowns),
            breakdowns=MappingProxyType(breakdowns),
        )

    def _score(
        self,
        candidate: RelevanceCandidate,
        profile: PersonalInterestProfile,
        now: datetime,
    ) -> RelevanceScoreBreakdown:
        matched_topics = candidate.topics.intersection(profile.topics)
        if not matched_topics:
            return RelevanceScoreBreakdown(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

        interest_match = 55 + min((len(matched_topics) - 1) * 5, 15)
        priority_bonus = max(
            self._PRIORITY_BONUS[profile.priority_for(topic)]
            for topic in matched_topics
        )
        locality_bonus = self._locality_bonus(candidate)
        free_access_bonus = 10 if candidate.is_free else 0
        urgency_bonus = 5 if candidate.time_sensitive else 0
        importance_bonus = candidate.importance
        source_quality_adjustment = self._source_quality_adjustment(candidate)
        verification_adjustment = self._VERIFICATION_ADJUSTMENT.get(
            candidate.verification or "",
            0,
        )
        freshness_adjustment = self._freshness_adjustment(candidate, now)
        kind_adjustment = self._KIND_ADJUSTMENT.get(
            candidate.information_kind or "",
            0,
        )
        total = min(
            100,
            max(
                0,
                interest_match
                + priority_bonus
                + locality_bonus
                + free_access_bonus
                + urgency_bonus
                + importance_bonus
                + source_quality_adjustment
                + verification_adjustment
                + freshness_adjustment
                + kind_adjustment,
            ),
        )
        return RelevanceScoreBreakdown(
            interest_match=interest_match,
            priority_bonus=priority_bonus,
            locality_bonus=locality_bonus,
            free_access_bonus=free_access_bonus,
            urgency_bonus=urgency_bonus,
            importance_bonus=importance_bonus,
            source_quality_adjustment=source_quality_adjustment,
            verification_adjustment=verification_adjustment,
            freshness_adjustment=freshness_adjustment,
            kind_adjustment=kind_adjustment,
            total=total,
        )

    @staticmethod
    def _locality_bonus(candidate: RelevanceCandidate) -> int:
        location = (candidate.location or "").casefold()
        region = (candidate.region or "").casefold()
        if "caba" in location or region == "caba":
            return 10
        if region == "argentina":
            return 5
        return 0

    @staticmethod
    def _source_quality_adjustment(candidate: RelevanceCandidate) -> int:
        confidence = candidate.source_confidence
        if confidence is None:
            return 0
        if confidence >= 95:
            return 5
        if confidence >= 80:
            return 2
        if confidence < 50:
            return -10
        if confidence < 70:
            return -5
        return 0

    @staticmethod
    def _freshness_adjustment(
        candidate: RelevanceCandidate,
        now: datetime,
    ) -> int:
        reference = candidate.event_at or candidate.published_at
        if reference is None:
            return 0
        age_days = (now - RelevanceEvaluator._as_utc(reference)).total_seconds() / 86400
        if candidate.event_at is not None and -30 <= age_days < 0:
            return 5
        if age_days < 0:
            return 0
        if age_days <= 1:
            return 5
        if age_days <= 7:
            return 2
        if age_days > 90:
            return -10
        if age_days > 30:
            return -5
        return 0

    @staticmethod
    def _as_utc(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @staticmethod
    def _recipient_for(people: tuple[str, ...]) -> RelevanceRecipient:
        normalized = {person.casefold() for person in people}
        if normalized == {"carlos", "cristina"}:
            return RelevanceRecipient.BOTH
        if normalized == {"carlos"}:
            return RelevanceRecipient.CARLOS
        if normalized == {"cristina"}:
            return RelevanceRecipient.CRISTINA
        return RelevanceRecipient.NOBODY

    @staticmethod
    def _reasons(
        candidate: RelevanceCandidate,
        selected: tuple[str, ...],
        breakdowns: Mapping[str, RelevanceScoreBreakdown],
    ) -> tuple[str, ...]:
        reasons: list[str] = []
        if selected:
            reasons.append("matches_personal_interests")
        if any(item.priority_bonus > 0 for item in breakdowns.values()):
            reasons.append("high_personal_priority")
        if RelevanceEvaluator._locality_bonus(candidate) == 10:
            reasons.append("local_to_caba")
        elif RelevanceEvaluator._locality_bonus(candidate) == 5:
            reasons.append("regional_to_argentina")
        if candidate.is_free:
            reasons.append("free_activity")
        if candidate.time_sensitive:
            reasons.append("time_sensitive")
        if candidate.importance:
            reasons.append("editorial_importance")
        if candidate.source_confidence is not None:
            reasons.append("governed_source_quality")
        if candidate.verification:
            reasons.append(f"verification_{candidate.verification}")
        if candidate.published_at or candidate.event_at:
            reasons.append("temporal_relevance_evaluated")
        if not reasons:
            reasons.append("no_relevant_match")
        return tuple(reasons)
