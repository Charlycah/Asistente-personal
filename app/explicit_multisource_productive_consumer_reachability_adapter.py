from __future__ import annotations

from typing import Protocol

from core.governed_reasoning.orchestrator import GovernedReasoningResult

from .explicit_multisource_productive_continuity_adapter import (
    ExplicitMultisourceProductiveContinuityV1,
)


class ExplicitMultisourceProductiveConsumerV1(Protocol):
    """Existing productive consumer surface for exact multisource lineage."""

    def consume(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
        result: GovernedReasoningResult,
    ) -> object: ...


class ExplicitMultisourceProductiveConsumerReachabilityAdapterV1:
    """Deliver F4 continuity to a supplied consumer without new authority."""

    def deliver(
        self,
        *,
        continuity: ExplicitMultisourceProductiveContinuityV1,
        consumer: ExplicitMultisourceProductiveConsumerV1,
    ) -> object:
        return consumer.consume(
            owner=continuity.owner,
            session_id=continuity.session_id,
            turn_id=continuity.turn_id,
            result=continuity.result,
        )
