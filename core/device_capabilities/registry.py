from __future__ import annotations

from datetime import datetime, timezone

from .models import (
    CapabilityMatchStatus,
    DeviceCapabilityAccess,
    DeviceCapabilityMatch,
    DeviceCapabilityRegistryPolicy,
    DeviceCapabilityRegistryRepository,
    DeviceCapabilityRequirement,
    DeviceCapabilityState,
    InMemoryDeviceCapabilityRegistryRepository,
    RegisteredDeviceCapability,
)


class DeviceCapabilityRegistry:
    """Registers and evaluates device capabilities without executing them."""

    def __init__(
        self,
        *,
        repository: DeviceCapabilityRegistryRepository | None = None,
        policy: DeviceCapabilityRegistryPolicy | None = None,
    ) -> None:
        self.repository = repository or InMemoryDeviceCapabilityRegistryRepository()
        self.policy = policy or DeviceCapabilityRegistryPolicy()

    def register(self, item: RegisteredDeviceCapability) -> None:
        if item.descriptor.name not in item.device.capabilities:
            raise ValueError(
                "registered capability must be declared by device identity"
            )
        self.repository.add(item)

    def evaluate(
        self,
        device_id: str,
        requirements: tuple[DeviceCapabilityRequirement, ...],
        *,
        now: datetime | None = None,
    ) -> DeviceCapabilityMatch:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("capability evaluation timestamp must be aware")
        if not device_id.strip():
            raise ValueError("device id must not be blank")
        names = tuple(item.name for item in requirements)
        if len(names) != len(set(names)):
            raise ValueError("capability requirements must be unique")
        items = self.repository.list_for_device(device_id)
        if not items:
            raise ValueError("device has no registered capabilities")
        device = items[0].device
        if any(item.device != device for item in items):
            raise ValueError(
                "device capability registry contains inconsistent identity"
            )
        if not requirements:
            return DeviceCapabilityMatch(
                device,
                (),
                (),
                (),
                (),
                CapabilityMatchStatus.NOT_APPLICABLE,
                ("no_capability_requirements",),
                timestamp,
            )
        matched: list[str] = []
        missing: list[str] = []
        review: list[str] = []
        for requirement in requirements:
            candidates = [
                item for item in items if item.descriptor.name == requirement.name
            ]
            if not candidates:
                missing.append(requirement.name)
                continue
            item = max(candidates, key=lambda value: value.observed_at)
            outcome = self._assess(item, requirement, timestamp)
            if outcome == "matched":
                matched.append(item.registration_id)
            elif outcome == "review":
                review.append(requirement.name)
            else:
                missing.append(requirement.name)
        if missing:
            status = CapabilityMatchStatus.UNSATISFIED
            rationale = ("required_device_capabilities_are_unsatisfied", *missing)
        elif review:
            status = CapabilityMatchStatus.REVIEW_REQUIRED
            rationale = ("device_capabilities_require_review", *review)
        else:
            status = CapabilityMatchStatus.SATISFIED
            rationale = ("device_capabilities_satisfy_requirements",)
        return DeviceCapabilityMatch(
            device,
            requirements,
            tuple(matched),
            tuple(missing),
            tuple(review),
            status,
            rationale,
            timestamp,
        )

    def _assess(
        self,
        item: RegisteredDeviceCapability,
        requirement: DeviceCapabilityRequirement,
        now: datetime,
    ) -> str:
        age = (now - item.observed_at).total_seconds()
        if age < 0 or age > self.policy.max_observation_age_seconds:
            return "review"
        if item.confidence < self.policy.minimum_confidence:
            return "review"
        if item.state is DeviceCapabilityState.UNAVAILABLE:
            return "missing"
        if item.state is DeviceCapabilityState.UNKNOWN:
            return "review"
        if (
            item.state is DeviceCapabilityState.DEGRADED
            and not requirement.allow_degraded
        ):
            return "review"
        if requirement.require_access:
            if item.access is DeviceCapabilityAccess.DENIED:
                return "missing"
            if (
                item.access is DeviceCapabilityAccess.CONSENT_REQUIRED
                and not self.policy.allow_consent_required
            ):
                return "review"
        if requirement.minimum_version and not self._version_at_least(
            item.descriptor.version, requirement.minimum_version
        ):
            return "missing"
        if any(
            feature not in item.descriptor.features
            for feature in requirement.required_features
        ):
            return "missing"
        return "matched"

    @staticmethod
    def _version_at_least(actual: str, required: str) -> bool:
        def parts(value: str) -> tuple[int | str, ...]:
            return tuple(
                int(part) if part.isdigit() else part for part in value.split(".")
            )

        try:
            return parts(actual) >= parts(required)
        except TypeError:
            return actual >= required
