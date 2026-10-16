from __future__ import annotations

from datetime import datetime, timezone

from core.context_transfer import ContextTransferStatus
from core.device_capabilities import CapabilityMatchStatus
from core.device_continuity import DeviceTrustLevel

from .models import (
    DeviceArbitrationAction,
    DeviceArbitrationCandidate,
    DeviceArbitrationDecision,
    DeviceArbitrationPolicy,
    DeviceArbitrationRepository,
    DeviceArbitrationRequest,
    DeviceArbitrationStatus,
    InMemoryDeviceArbitrationRepository,
)


class ActiveDeviceArbitrator:
    """Selects an eligible active device without activating or transporting it."""

    def __init__(
        self,
        *,
        repository: DeviceArbitrationRepository | None = None,
        policy: DeviceArbitrationPolicy | None = None,
    ) -> None:
        self.repository = repository or InMemoryDeviceArbitrationRepository()
        self.policy = policy or DeviceArbitrationPolicy()

    def arbitrate(
        self,
        request: DeviceArbitrationRequest,
        *,
        now: datetime | None = None,
    ) -> DeviceArbitrationDecision:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("arbitration evaluation timestamp must be aware")
        self._validate(request)
        status, action, selected, scores, rationale = self._evaluate(request, timestamp)
        result = DeviceArbitrationDecision(
            request=request,
            status=status,
            action=action,
            selected_device_id=selected,
            previous_device_id=request.session.active_device_id,
            candidate_scores=scores,
            eligible_for_activation=status is DeviceArbitrationStatus.READY,
            rationale=rationale,
            created_at=timestamp,
        )
        self.repository.add(result)
        return result

    def _validate(self, request: DeviceArbitrationRequest) -> None:
        if request.owner.casefold() != request.session.owner.casefold():
            raise ValueError("arbitration owner does not own the session")
        for candidate in request.candidates:
            if candidate.endpoint.device.owner.casefold() != request.owner.casefold():
                raise ValueError("candidate device owner is inconsistent")

    def _evaluate(self, request: DeviceArbitrationRequest, now: datetime):
        if not request.candidates:
            return (
                DeviceArbitrationStatus.NOT_APPLICABLE,
                DeviceArbitrationAction.NONE,
                None,
                (),
                ("no_device_candidates",),
            )
        scored: list[tuple[DeviceArbitrationCandidate, float, str | None]] = []
        for candidate in request.candidates:
            score, issue = self._score(candidate, request.session.active_device_id, now)
            scored.append((candidate, score, issue))
        scores = tuple(
            sorted(
                (
                    (item.endpoint.device.device_id, round(score, 6))
                    for item, score, _ in scored
                ),
                key=lambda value: value[0],
            )
        )
        eligible = [item for item in scored if item[2] is None]
        if not eligible:
            review = any(
                issue and issue.startswith("review:") for _, _, issue in scored
            )
            return (
                DeviceArbitrationStatus.REVIEW_REQUIRED
                if review
                else DeviceArbitrationStatus.BLOCKED,
                DeviceArbitrationAction.CONFIRM
                if review
                else DeviceArbitrationAction.STAY,
                request.session.active_device_id if review else None,
                scores,
                ("no_eligible_device",),
            )
        eligible.sort(key=lambda value: (-value[1], value[0].endpoint.device.device_id))
        best, best_score, _ = eligible[0]
        current = next(
            (
                item
                for item in eligible
                if item[0].endpoint.device.device_id == request.session.active_device_id
            ),
            None,
        )
        if (
            current is not None
            and best.endpoint.device.device_id != request.session.active_device_id
        ):
            margin = best_score - current[1]
            if margin < self.policy.minimum_switch_margin:
                best, best_score, _ = current
        selected = best.endpoint.device.device_id
        action = (
            DeviceArbitrationAction.STAY
            if selected == request.session.active_device_id
            else DeviceArbitrationAction.SWITCH
        )
        return (
            DeviceArbitrationStatus.READY,
            action,
            selected,
            scores,
            ("active_device_selected", f"score:{best_score:.6f}"),
        )

    def _score(
        self,
        candidate: DeviceArbitrationCandidate,
        active_device_id: str,
        now: datetime,
    ) -> tuple[float, str | None]:
        endpoint = candidate.endpoint
        device = endpoint.device
        if not endpoint.available:
            return -10.0, "blocked:unavailable"
        if not endpoint.authenticated:
            return -10.0, "blocked:unauthenticated"
        age = (now - endpoint.observed_at).total_seconds()
        if age < 0 or age > self.policy.max_observation_age_seconds:
            return -5.0, "review:stale_observation"
        if device.trust_level is DeviceTrustLevel.UNTRUSTED:
            if not self.policy.allow_untrusted_devices:
                return -10.0, "blocked:untrusted"
        match = candidate.capability_match.status
        if match is CapabilityMatchStatus.UNSATISFIED:
            return -10.0, "blocked:capabilities"
        if match is CapabilityMatchStatus.REVIEW_REQUIRED:
            return -5.0, "review:capabilities"
        score = candidate.user_preference
        if match is CapabilityMatchStatus.SATISFIED:
            score += 1.0
        if device.trust_level is DeviceTrustLevel.TRUSTED:
            score += 0.5
        elif device.trust_level is DeviceTrustLevel.RECOGNIZED:
            score += 0.2
        if self.policy.prefer_current_device and device.device_id == active_device_id:
            score += 0.25
        if (
            device.device_id != active_device_id
            and self.policy.require_ready_transfer_for_switch
        ):
            manifest = candidate.transfer_manifest
            if manifest is None:
                return -10.0, "blocked:missing_transfer_manifest"
            if manifest.status is ContextTransferStatus.REVIEW_REQUIRED:
                return -5.0, "review:transfer_manifest"
            if manifest.status is not ContextTransferStatus.READY:
                return -10.0, "blocked:transfer_manifest"
            score += 0.25
        return score, None
