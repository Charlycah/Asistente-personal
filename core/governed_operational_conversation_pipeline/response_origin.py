from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ResponseOrigin(str, Enum):
    """Explicit origin of the information used to build a response."""

    LOCAL = "local"
    WEB_RECENT = "web_recent"
    GENERAL_KNOWLEDGE = "general_knowledge"
    INFERENCE = "inference"


class ResponseConfidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    WITHHELD = "withheld"


class ResponseVerification(str, Enum):
    VERIFIED = "verified"
    PARTIAL = "partial"
    UNAVAILABLE = "unavailable"


class ResponseDecision(str, Enum):
    ANSWERED = "answered"
    ABSTAINED = "abstained"


@dataclass(frozen=True)
class ResponseConfidenceRecord:
    """Auditable decision record produced before a response is emitted."""

    origin: ResponseOrigin | str
    confidence: ResponseConfidence | str
    freshness: str
    evidence_count: int
    conflicting_sources: bool
    verification: ResponseVerification | str
    decision: ResponseDecision | str
    reason_code: str

    def __post_init__(self) -> None:
        origin = ResponseOrigin(self.origin)
        confidence = ResponseConfidence(self.confidence)
        verification = ResponseVerification(self.verification)
        decision = ResponseDecision(self.decision)
        freshness = self.freshness.strip()
        reason_code = self.reason_code.strip()
        if not freshness or not reason_code:
            raise ValueError(
                "confidence record freshness and reason code must not be blank"
            )
        if self.evidence_count < 0:
            raise ValueError("confidence record evidence count must not be negative")
        if decision is ResponseDecision.ABSTAINED:
            if confidence is not ResponseConfidence.WITHHELD:
                raise ValueError("abstained decisions must use withheld confidence")
            if verification is not ResponseVerification.UNAVAILABLE:
                raise ValueError("abstained decisions cannot be verified")
        elif confidence is ResponseConfidence.WITHHELD:
            raise ValueError("answered decisions cannot use withheld confidence")
        if verification is ResponseVerification.VERIFIED and self.evidence_count < 1:
            raise ValueError("verified responses require at least one evidence item")
        if self.conflicting_sources:
            if self.evidence_count < 2:
                raise ValueError("source conflicts require at least two evidence items")
            if confidence is ResponseConfidence.HIGH:
                raise ValueError("conflicting sources cannot retain high confidence")
        object.__setattr__(self, "origin", origin)
        object.__setattr__(self, "confidence", confidence)
        object.__setattr__(self, "freshness", freshness)
        object.__setattr__(self, "verification", verification)
        object.__setattr__(self, "decision", decision)
        object.__setattr__(self, "reason_code", reason_code)


@dataclass(frozen=True)
class ResponseOriginMetadata:
    origin: ResponseOrigin | str
    confidence: ResponseConfidence | str
    freshness: str
    verifiable: bool
    abstained: bool = False
    confidence_record: ResponseConfidenceRecord | None = field(default=None)

    def __post_init__(self) -> None:
        origin = ResponseOrigin(self.origin)
        confidence = ResponseConfidence(self.confidence)
        freshness = self.freshness.strip()
        if not freshness:
            raise ValueError("response origin freshness must not be blank")
        if self.abstained and confidence is not ResponseConfidence.WITHHELD:
            raise ValueError("abstained responses must use withheld confidence")
        record = self.confidence_record or self._default_record(
            origin=origin,
            confidence=confidence,
            freshness=freshness,
            verifiable=self.verifiable,
            abstained=self.abstained,
        )
        if record.origin is not origin or record.confidence is not confidence:
            raise ValueError("response origin and confidence record must agree")
        if record.freshness != freshness:
            raise ValueError("response freshness and confidence record must agree")
        if (record.decision is ResponseDecision.ABSTAINED) != self.abstained:
            raise ValueError("response abstention and confidence record must agree")
        if self.verifiable and record.verification is ResponseVerification.UNAVAILABLE:
            raise ValueError("verifiable responses need available verification")
        if not self.verifiable and record.verification is ResponseVerification.VERIFIED:
            raise ValueError("non-verifiable responses cannot be verified")
        object.__setattr__(self, "origin", origin)
        object.__setattr__(self, "confidence", confidence)
        object.__setattr__(self, "freshness", freshness)
        object.__setattr__(self, "confidence_record", record)

    @staticmethod
    def _default_record(*, origin, confidence, freshness, verifiable, abstained):
        return ResponseConfidenceRecord(
            origin=origin,
            confidence=confidence,
            freshness=freshness,
            evidence_count=1 if verifiable and not abstained else 0,
            conflicting_sources=False,
            verification=(
                ResponseVerification.VERIFIED
                if verifiable and not abstained
                else ResponseVerification.UNAVAILABLE
            ),
            decision=(
                ResponseDecision.ABSTAINED if abstained else ResponseDecision.ANSWERED
            ),
            reason_code=(
                "response_abstained"
                if abstained
                else f"{origin.value}_response_completed"
            ),
        )

    @classmethod
    def local(
        cls, *, reason_code: str = "local_response_completed"
    ) -> ResponseOriginMetadata:
        return cls(
            ResponseOrigin.LOCAL,
            ResponseConfidence.HIGH,
            "live",
            True,
            confidence_record=ResponseConfidenceRecord(
                ResponseOrigin.LOCAL,
                ResponseConfidence.HIGH,
                "live",
                1,
                False,
                ResponseVerification.VERIFIED,
                ResponseDecision.ANSWERED,
                reason_code,
            ),
        )

    @classmethod
    def web_recent(
        cls,
        *,
        evidence_count: int = 1,
        reason_code: str = "web_recent_response_completed",
    ) -> ResponseOriginMetadata:
        return cls(
            ResponseOrigin.WEB_RECENT,
            ResponseConfidence.HIGH,
            "recent",
            True,
            confidence_record=ResponseConfidenceRecord(
                ResponseOrigin.WEB_RECENT,
                ResponseConfidence.HIGH,
                "recent",
                evidence_count,
                False,
                ResponseVerification.VERIFIED,
                ResponseDecision.ANSWERED,
                reason_code,
            ),
        )

    @classmethod
    def web_recent_conflicted(
        cls,
        *,
        evidence_count: int = 2,
        reason_code: str = "web_recent_sources_conflicted",
    ) -> ResponseOriginMetadata:
        return cls(
            ResponseOrigin.WEB_RECENT,
            ResponseConfidence.MEDIUM,
            "recent_but_conflicting",
            True,
            confidence_record=ResponseConfidenceRecord(
                ResponseOrigin.WEB_RECENT,
                ResponseConfidence.MEDIUM,
                "recent_but_conflicting",
                evidence_count,
                True,
                ResponseVerification.PARTIAL,
                ResponseDecision.ANSWERED,
                reason_code,
            ),
        )

    @classmethod
    def general_knowledge(cls) -> ResponseOriginMetadata:
        return cls(
            ResponseOrigin.GENERAL_KNOWLEDGE,
            ResponseConfidence.MEDIUM,
            "not_guaranteed_current",
            False,
            confidence_record=ResponseConfidenceRecord(
                ResponseOrigin.GENERAL_KNOWLEDGE,
                ResponseConfidence.MEDIUM,
                "not_guaranteed_current",
                0,
                False,
                ResponseVerification.UNAVAILABLE,
                ResponseDecision.ANSWERED,
                "general_knowledge_response_completed",
            ),
        )

    @classmethod
    def inference(cls) -> ResponseOriginMetadata:
        return cls(
            ResponseOrigin.INFERENCE,
            ResponseConfidence.LOW,
            "not_applicable",
            False,
            confidence_record=ResponseConfidenceRecord(
                ResponseOrigin.INFERENCE,
                ResponseConfidence.LOW,
                "not_applicable",
                0,
                False,
                ResponseVerification.UNAVAILABLE,
                ResponseDecision.ANSWERED,
                "inference_response_completed",
            ),
        )

    @classmethod
    def abstained_web(
        cls, *, reason_code: str = "web_response_withheld"
    ) -> ResponseOriginMetadata:
        return cls(
            ResponseOrigin.WEB_RECENT,
            ResponseConfidence.WITHHELD,
            "unavailable",
            False,
            abstained=True,
            confidence_record=ResponseConfidenceRecord(
                ResponseOrigin.WEB_RECENT,
                ResponseConfidence.WITHHELD,
                "unavailable",
                0,
                False,
                ResponseVerification.UNAVAILABLE,
                ResponseDecision.ABSTAINED,
                reason_code,
            ),
        )
