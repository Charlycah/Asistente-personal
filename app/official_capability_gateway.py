from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from core.cognitive_maturity import ResponseActionEvidenceAdapter
from core.governed_operational_conversation_pipeline import (
    GovernedConversationPipelineRequest,
    GovernedOperationalInterception,
)
from core.governed_read_only_evidence import (
    GovernedReadOnlyEvidenceObservation,
    GovernedReadOnlyEvidenceRequest,
)


@dataclass(frozen=True)
class OfficialCapabilityGatewaySnapshot:
    executions: int
    last_capability: str | None
    last_origin: str | None
    last_rationale: str | None


class OfficialCapabilityGateway:
    """Single execution boundary for official runtime capabilities."""

    def __init__(self) -> None:
        self._executions = 0
        self._last_capability: str | None = None
        self._last_origin: str | None = None
        self._last_rationale: str | None = None

    @property
    def snapshot(self) -> OfficialCapabilityGatewaySnapshot:
        return OfficialCapabilityGatewaySnapshot(
            executions=self._executions,
            last_capability=self._last_capability,
            last_origin=self._last_origin,
            last_rationale=self._last_rationale,
        )

    def execute(
        self,
        registration,
        request: GovernedConversationPipelineRequest,
        *,
        now: datetime,
        origin: str,
    ) -> GovernedOperationalInterception | None:
        """Execute one registered capability through the canonical boundary."""
        self._executions += 1
        self._last_capability = registration.descriptor.name
        self._last_origin = origin
        result = registration.interceptor.intercept(request, now=now)
        self._last_rationale = None if result is None else result.rationale
        scope = registration.descriptor.normalized_permission_scope.value
        ResponseActionEvidenceAdapter().observe_official_capability(
            external_scope=scope != "none",
            completed=result is not None,
        )
        return result
    def execute_read_only_evidence(
        self,
        registration,
        request: GovernedReadOnlyEvidenceRequest,
        *,
        now: datetime,
    ) -> GovernedReadOnlyEvidenceObservation:
        """Execute one evidence read through the canonical capability boundary."""
        reader = getattr(registration, "evidence_reader", None)
        if reader is None:
            raise LookupError("registered capability has no evidence reader")
        self._executions += 1
        self._last_capability = registration.descriptor.name
        self._last_origin = "governed_level2_read_only_evidence"
        result = reader.read_evidence(request, now=now)
        if not isinstance(result, GovernedReadOnlyEvidenceObservation):
            raise TypeError("evidence reader returned an invalid observation")
        self._last_rationale = (
            result.rationale_codes[0] if result.rationale_codes else None
        )
        return result

