from __future__ import annotations

from datetime import datetime, timezone

from core.local_identity_profile import LocalIdentityProfileStore
from core.personal_identity_and_session_profiles.store import IdentityProfileStore
from domain.brain import BrainMemory, BrainMemoryType

from .service import BrainQuery


class IdentityProfileBrainAdapter:
    """Read-only BRAIN view over local and personal identity profiles."""

    def __init__(
        self,
        *,
        local_profile_store: LocalIdentityProfileStore,
        identity_profile_store: IdentityProfileStore,
    ) -> None:
        self.local_profile_store = local_profile_store
        self.identity_profile_store = identity_profile_store

    def recall(
        self,
        query: BrainQuery,
        *,
        now: datetime | None = None,
    ) -> tuple[BrainMemory, ...]:
        del query
        timestamp = now or datetime.now(timezone.utc)
        memories: list[BrainMemory] = []
        local_profile = self.local_profile_store.load()
        if local_profile is not None:
            memories.extend(
                (
                    self._local_person_memory(
                        role="owner",
                        name=local_profile.owner_name,
                        partner=local_profile.partner_name,
                        timestamp=timestamp,
                    ),
                    self._local_person_memory(
                        role="partner",
                        name=local_profile.partner_name,
                        partner=local_profile.owner_name,
                        timestamp=timestamp,
                    ),
                )
            )
        memories.extend(
            self._personal_profile_memory(profile, timestamp)
            for profile in self.identity_profile_store.list_profiles()
        )
        return tuple(memories)

    @staticmethod
    def _local_person_memory(
        *,
        role: str,
        name: str,
        partner: str,
        timestamp: datetime,
    ) -> BrainMemory:
        normalized_name = name.strip()
        normalized_partner = partner.strip()
        return BrainMemory(
            memory_id=f"local-identity:{role}:{normalized_name.casefold()}",
            memory_type=BrainMemoryType.PROFILE,
            subject=normalized_name,
            content=(
                f"{normalized_name} es una persona reconocida del hogar y "
                f"su vínculo registrado es {normalized_partner}."
            ),
            importance=1.0,
            confidence=1.0,
            source="local_identity_profile",
            tags=("identity", "household", role),
            metadata={
                "read_only": True,
                "identity_role": role,
                "partner_name": normalized_partner,
            },
            created_at=timestamp,
            updated_at=timestamp,
        )

    @staticmethod
    def _personal_profile_memory(profile, timestamp: datetime) -> BrainMemory:
        participants = tuple(profile.participants)
        if participants:
            content = (
                f"El perfil {profile.display_name} representa a "
                f"{', '.join(participants)}."
            )
        else:
            content = (
                f"{profile.display_name} tiene un perfil personal "
                f"identificado como {profile.profile_id}."
            )
        return BrainMemory(
            memory_id=f"identity-profile:{profile.profile_id}",
            memory_type=BrainMemoryType.PROFILE,
            subject=profile.owner,
            content=content,
            importance=0.95,
            confidence=1.0,
            source="identity_profile_registry",
            tags=("identity", "profile", profile.scope.value),
            metadata={
                "read_only": True,
                "profile_id": profile.profile_id,
                "display_name": profile.display_name,
                "scope": profile.scope.value,
                "participants": list(participants),
            },
            created_at=timestamp,
            updated_at=timestamp,
        )
