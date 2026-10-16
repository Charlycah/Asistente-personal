from datetime import datetime, timezone

import pytest

from app.current_affairs_router import CurrentAffairsItem, CurrentAffairsRouter
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    ResponseConfidence,
    ResponseConfidenceRecord,
    ResponseDecision,
    ResponseOrigin,
    ResponseOriginMetadata,
    ResponseVerification,
)


def request(text: str) -> GovernedConversationPipelineRequest:
    return GovernedConversationPipelineRequest(
        owner="Carlos",
        session_id="confidence-session",
        text=text,
    )


def test_general_knowledge_has_complete_internal_confidence_record():
    metadata = ResponseOriginMetadata.general_knowledge()
    record = metadata.confidence_record

    assert record.origin is ResponseOrigin.GENERAL_KNOWLEDGE
    assert record.confidence is ResponseConfidence.MEDIUM
    assert record.evidence_count == 0
    assert record.conflicting_sources is False
    assert record.verification is ResponseVerification.UNAVAILABLE
    assert record.decision is ResponseDecision.ANSWERED
    assert record.reason_code == "general_knowledge_response_completed"


def test_verified_response_requires_evidence():
    with pytest.raises(ValueError, match="at least one evidence"):
        ResponseConfidenceRecord(
            origin=ResponseOrigin.WEB_RECENT,
            confidence=ResponseConfidence.HIGH,
            freshness="recent",
            evidence_count=0,
            conflicting_sources=False,
            verification=ResponseVerification.VERIFIED,
            decision=ResponseDecision.ANSWERED,
            reason_code="invalid_verified_response",
        )


def test_conflicting_sources_cannot_retain_high_confidence():
    with pytest.raises(ValueError, match="cannot retain high confidence"):
        ResponseConfidenceRecord(
            origin=ResponseOrigin.WEB_RECENT,
            confidence=ResponseConfidence.HIGH,
            freshness="recent_but_conflicting",
            evidence_count=2,
            conflicting_sources=True,
            verification=ResponseVerification.PARTIAL,
            decision=ResponseDecision.ANSWERED,
            reason_code="invalid_conflict_confidence",
        )


def test_current_affairs_records_accepted_evidence_count():
    class TwoSources:
        def search(self, query, *, limit=5):
            return (
                CurrentAffairsItem(
                    "NASA prepara una nueva misión científica",
                    "NASA",
                    "https://example.test/nasa",
                    datetime(2026, 7, 19, 9, tzinfo=timezone.utc),
                ),
                CurrentAffairsItem(
                    "La misión científica de NASA completa su revisión",
                    "Agencia",
                    "https://example.test/agency",
                    datetime(2026, 7, 19, 10, tzinfo=timezone.utc),
                ),
            )

    result = CurrentAffairsRouter(TwoSources()).intercept(
        request("últimas noticias de la NASA"),
        now=datetime(2026, 7, 19, 12, tzinfo=timezone.utc),
    )

    assert result is not None
    record = result.origin.confidence_record
    assert record.evidence_count == 2
    assert record.verification is ResponseVerification.VERIFIED
    assert record.decision is ResponseDecision.ANSWERED
    assert record.reason_code == "current_affairs_web_retrieval_completed"


def test_current_affairs_abstention_records_exact_reason():
    class Offline:
        def search(self, query, *, limit=5):
            raise OSError("offline")

    result = CurrentAffairsRouter(Offline()).intercept(
        request("últimas noticias de OpenAI"),
        now=datetime(2026, 7, 19, 12, tzinfo=timezone.utc),
    )

    assert result is not None
    record = result.origin.confidence_record
    assert record.confidence is ResponseConfidence.WITHHELD
    assert record.decision is ResponseDecision.ABSTAINED
    assert record.verification is ResponseVerification.UNAVAILABLE
    assert record.reason_code == "current_affairs_web_retrieval_failed"
