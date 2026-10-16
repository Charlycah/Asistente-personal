from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from core.local_identity_profile import LocalIdentityProfileStore
from core.personal_identity_and_session_profiles.models import (
    IdentityScope,
    PersonalIdentityProfile,
)
from core.personal_identity_and_session_profiles.store import IdentityProfileStore


class ActiveIdentityStatus(str, Enum):
    RESOLVED = "resolved"
    SHARED = "shared"
    UNKNOWN = "unknown"
    CONFLICT = "conflict"


class ActiveIdentitySource(str, Enum):
    EXPLICIT_PROFILE = "explicit_profile"
    DECLARED_NAME = "declared_name"
    SESSION_PROFILE = "session_profile"
    NONE = "none"


@dataclass(frozen=True)
class ActiveIdentityRequest:
    """Non-biometric evidence available for one controlled resolution."""

    declared_name: str | None = None
    profile_id: str | None = None
    session_profile_id: str | None = None


@dataclass(frozen=True)
class ActiveIdentityResolution:
    status: ActiveIdentityStatus
    source: ActiveIdentitySource
    profile_id: str | None = None
    display_name: str | None = None
    subject: str | None = None
    participants: tuple[str, ...] = ()
    confidence: float = 0.0
    reason: str = ""

    @property
    def is_personal(self) -> bool:
        return self.status is ActiveIdentityStatus.RESOLVED

    @property
    def may_use_private_preferences(self) -> bool:
        return self.is_personal and self.subject is not None


class ActiveIdentityResolver:
    """Resolve active identity from explicit, non-biometric evidence only."""

    def __init__(
        self,
        *,
        local_profile_store: LocalIdentityProfileStore,
        identity_profile_store: IdentityProfileStore,
    ) -> None:
        self.local_profile_store = local_profile_store
        self.identity_profile_store = identity_profile_store

    def resolve(self, request: ActiveIdentityRequest) -> ActiveIdentityResolution:
        profiles = self.identity_profile_store.list_profiles()
        evidence = self._evidence(request)
        if not evidence:
            return ActiveIdentityResolution(
                status=ActiveIdentityStatus.UNKNOWN,
                source=ActiveIdentitySource.NONE,
                reason="no explicit identity evidence was provided",
            )

        resolved = [
            self._resolve_value(value, source, profiles)
            for source, value in evidence
        ]
        known = [item for item in resolved if item is not None]
        if not known:
            source = evidence[0][0]
            return ActiveIdentityResolution(
                status=ActiveIdentityStatus.UNKNOWN,
                source=source,
                reason="identity evidence does not match a known profile",
            )

        identifiers = {item.profile_id.casefold() for item in known}
        if len(identifiers) > 1:
            return ActiveIdentityResolution(
                status=ActiveIdentityStatus.CONFLICT,
                source=evidence[0][0],
                reason="identity evidence points to different profiles",
            )

        profile = known[0]
        source = next(
            source
            for source, value in evidence
            if self._resolve_value(value, source, profiles) is not None
        )
        return self._resolution(profile, source)

    def _resolve_value(
        self,
        value: str,
        source: ActiveIdentitySource,
        profiles: tuple[PersonalIdentityProfile, ...],
    ) -> PersonalIdentityProfile | None:
        normalized = value.strip().casefold()
        if not normalized:
            return None
        if source is ActiveIdentitySource.DECLARED_NAME:
            local_match = self._from_local_names(normalized, profiles)
            if local_match is not None:
                return local_match
        matches = []
        for profile in profiles:
            aliases = {
                profile.profile_id.casefold(),
                profile.display_name.casefold(),
                profile.owner.casefold(),
            }
            if normalized in aliases:
                matches.append(profile)
        return matches[0] if len(matches) == 1 else None

    def _from_local_names(
        self,
        normalized: str,
        profiles: tuple[PersonalIdentityProfile, ...],
    ) -> PersonalIdentityProfile | None:
        local = self.local_profile_store.load()
        if local is None:
            return None
        for name in local.recognized_names:
            if name.casefold() != normalized:
                continue
            private = [
                profile
                for profile in profiles
                if profile.scope is IdentityScope.PRIVATE
                and profile.owner.casefold() == normalized
            ]
            return private[0] if len(private) == 1 else None
        return None

    @staticmethod
    def _evidence(
        request: ActiveIdentityRequest,
    ) -> tuple[tuple[ActiveIdentitySource, str], ...]:
        values = (
            (ActiveIdentitySource.EXPLICIT_PROFILE, request.profile_id),
            (ActiveIdentitySource.SESSION_PROFILE, request.session_profile_id),
            (ActiveIdentitySource.DECLARED_NAME, request.declared_name),
        )
        return tuple(
            (source, value.strip())
            for source, value in values
            if value is not None and value.strip()
        )

    @staticmethod
    def _resolution(
        profile: PersonalIdentityProfile,
        source: ActiveIdentitySource,
    ) -> ActiveIdentityResolution:
        shared = profile.scope is IdentityScope.SHARED
        return ActiveIdentityResolution(
            status=(
                ActiveIdentityStatus.SHARED
                if shared
                else ActiveIdentityStatus.RESOLVED
            ),
            source=source,
            profile_id=profile.profile_id,
            display_name=profile.display_name,
            subject=profile.owner,
            participants=tuple(profile.participants),
            confidence=1.0,
            reason="identity resolved from explicit non-biometric evidence",
        )
