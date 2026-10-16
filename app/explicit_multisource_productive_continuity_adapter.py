from __future__ import annotations

from dataclasses import dataclass

from core.governed_reasoning.orchestrator import GovernedReasoningResult


@dataclass(frozen=True)
class ExplicitMultisourceProductiveContinuityV1:
    """Bounded identity projection for an already-produced reasoning result."""

    owner: str
    session_id: str
    turn_id: str
    result: GovernedReasoningResult


class ExplicitMultisourceProductiveContinuityAdapterV1:
    """Project exact multisource result continuity without reasoning or storage."""

    def project(
        self,
        *,
        owner: str,
        session_id: str,
        turn_id: str,
        result: GovernedReasoningResult,
    ) -> ExplicitMultisourceProductiveContinuityV1:
        if not owner.strip():
            raise ValueError("owner must be non-empty")
        if not session_id.strip():
            raise ValueError("session_id must be non-empty")
        if not turn_id.strip():
            raise ValueError("turn_id must be non-empty")
        return ExplicitMultisourceProductiveContinuityV1(
            owner=owner,
            session_id=session_id,
            turn_id=turn_id,
            result=result,
        )
