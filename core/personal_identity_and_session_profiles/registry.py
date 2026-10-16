from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

from .models import PersonalIdentityProfile, RuntimeSessionProfile, SessionStatus
from .store import IdentityProfileStore, SessionProfileStore


class PersonalIdentityRegistry:
    def __init__(
        self,
        *,
        profile_store: IdentityProfileStore,
        session_store: SessionProfileStore,
        defaults: tuple[PersonalIdentityProfile, ...],
    ) -> None:
        self.profile_store = profile_store
        self.session_store = session_store
        profiles = profile_store.list_profiles()
        if not profiles:
            self._validate_profiles(defaults)
            profile_store.save_profiles(defaults)
            profiles = defaults
        self._validate_profiles(profiles)
        self._profiles = profiles

    @property
    def profiles(self) -> tuple[PersonalIdentityProfile, ...]:
        return self._profiles

    def profile(self, profile_id: str) -> PersonalIdentityProfile:
        normalized = profile_id.strip().casefold()
        for item in self._profiles:
            if item.profile_id.casefold() == normalized:
                return item
        raise KeyError(f"unknown ROBY identity profile: {profile_id}")

    def open_session(
        self,
        *,
        profile_id: str,
        session_id: str,
        now: datetime | None = None,
    ) -> tuple[PersonalIdentityProfile, RuntimeSessionProfile]:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise ValueError("session time must be timezone-aware")
        profile = self.profile(profile_id)
        sessions = list(self.session_store.list_sessions())
        for index, session in enumerate(sessions):
            if session.session_id.casefold() != session_id.strip().casefold():
                continue
            if session.profile_id.casefold() != profile.profile_id.casefold():
                raise ValueError("session is already bound to another identity profile")
            if session.status is SessionStatus.ARCHIVED:
                raise ValueError("archived session cannot be resumed")
            active = replace(session, last_active_at=timestamp)
            sessions[index] = active
            self.session_store.save_sessions(tuple(sessions))
            return profile, active
        created = RuntimeSessionProfile(
            session_id=session_id,
            profile_id=profile.profile_id,
            created_at=timestamp,
            last_active_at=timestamp,
        )
        sessions.append(created)
        self.session_store.save_sessions(tuple(sessions))
        return profile, created

    def archive_session(
        self,
        *,
        profile_id: str,
        session_id: str,
        now: datetime | None = None,
    ) -> RuntimeSessionProfile:
        timestamp = now or datetime.now(timezone.utc)
        sessions = list(self.session_store.list_sessions())
        for index, session in enumerate(sessions):
            if session.session_id == session_id and session.profile_id == profile_id:
                archived = replace(
                    session,
                    status=SessionStatus.ARCHIVED,
                    archived_at=timestamp,
                    last_active_at=timestamp,
                )
                sessions[index] = archived
                self.session_store.save_sessions(tuple(sessions))
                return archived
        raise KeyError("session profile not found")

    @staticmethod
    def _validate_profiles(profiles: tuple[PersonalIdentityProfile, ...]) -> None:
        if not profiles:
            raise ValueError("at least one ROBY identity profile is required")
        identifiers = [item.profile_id.casefold() for item in profiles]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("ROBY identity profile ids must be unique")
