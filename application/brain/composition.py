from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from core.household_goals import HouseholdGoalRepository
from core.household_projects import HouseholdProjectRepository
from core.local_identity_profile import LocalIdentityProfileStore
from core.memory import MemoryStore
from core.personal_identity_and_session_profiles.store import JsonIdentityProfileStore
from core.relationship_memory import RelationshipMemoryManager

from .active_identity import ActiveIdentityResolver
from .conversation_context import ConversationContextPreparer
from .conversation_context_diagnostic import ConversationContextDiagnostic
from .goal_project_adapter import GoalProjectBrainAdapter
from .identity_profile_adapter import IdentityProfileBrainAdapter
from .official_memory_adapter import OfficialMemoryBrainAdapter
from .relationship_preference_adapter import RelationshipPreferenceBrainAdapter
from .safe_personal_context import SafePersonalContextService
from .service import BrainRepository, BrainService
from .structural_audit import BrainStructuralAudit


@dataclass(frozen=True)
class OfficialMemoryBrainComposition:
    """Controlled, read-only composition for the official memory gateway."""

    service: BrainService
    gateway: MemoryStore
    adapter: OfficialMemoryBrainAdapter


def build_official_memory_brain_composition(
    *,
    brain_repository: BrainRepository,
    memory_gateway: MemoryStore,
    owner: str,
) -> OfficialMemoryBrainComposition:
    """Build the BRAIN view without wiring it into ROBY's visible runtime."""

    normalized_owner = owner.strip()
    if not normalized_owner:
        raise ValueError("brain composition owner must not be blank")

    gateway = memory_gateway
    adapter = OfficialMemoryBrainAdapter(
        gateway=gateway,
        owner=normalized_owner,
    )
    service = BrainService(brain_repository, readers=(adapter,))
    return OfficialMemoryBrainComposition(
        service=service,
        gateway=gateway,
        adapter=adapter,
    )


@dataclass(frozen=True)
class HistoricalMemoryBrainComposition:
    """Controlled read-only composition for official memory, goals and projects."""

    service: BrainService
    official_adapter: OfficialMemoryBrainAdapter
    goal_project_adapter: GoalProjectBrainAdapter


def build_historical_memory_brain_composition(
    *,
    brain_repository: BrainRepository,
    memory_gateway: MemoryStore,
    goal_repository: HouseholdGoalRepository,
    project_repository: HouseholdProjectRepository,
    owner: str,
) -> HistoricalMemoryBrainComposition:
    normalized_owner = owner.strip()
    if not normalized_owner:
        raise ValueError("brain composition owner must not be blank")

    gateway = memory_gateway
    official_adapter = OfficialMemoryBrainAdapter(
        gateway=gateway,
        owner=normalized_owner,
    )
    goal_adapter = GoalProjectBrainAdapter(
        goal_repository=goal_repository,
        project_repository=project_repository,
        owner=normalized_owner,
    )
    service = BrainService(
        brain_repository,
        readers=(official_adapter, goal_adapter),
    )
    return HistoricalMemoryBrainComposition(
        service=service,
        official_adapter=official_adapter,
        goal_project_adapter=goal_adapter,
    )


@dataclass(frozen=True)
class RelationalMemoryBrainComposition:
    """Controlled composition including relational memory and preferences."""

    service: BrainService
    official_adapter: OfficialMemoryBrainAdapter
    goal_project_adapter: GoalProjectBrainAdapter
    relationship_preference_adapter: RelationshipPreferenceBrainAdapter


def build_relational_memory_brain_composition(
    *,
    brain_repository: BrainRepository,
    memory_gateway: MemoryStore,
    goal_repository: HouseholdGoalRepository,
    project_repository: HouseholdProjectRepository,
    relationship_memory: RelationshipMemoryManager,
    owner: str,
) -> RelationalMemoryBrainComposition:
    normalized_owner = owner.strip()
    if not normalized_owner:
        raise ValueError("brain composition owner must not be blank")

    gateway = memory_gateway
    official_adapter = OfficialMemoryBrainAdapter(
        gateway=gateway,
        owner=normalized_owner,
    )
    goal_project_adapter = GoalProjectBrainAdapter(
        goal_repository=goal_repository,
        project_repository=project_repository,
        owner=normalized_owner,
    )
    relationship_preference_adapter = RelationshipPreferenceBrainAdapter(
        relationship_memory=relationship_memory,
        owner=normalized_owner,
    )
    service = BrainService(
        brain_repository,
        readers=(
            official_adapter,
            goal_project_adapter,
            relationship_preference_adapter,
        ),
    )
    return RelationalMemoryBrainComposition(
        service=service,
        official_adapter=official_adapter,
        goal_project_adapter=goal_project_adapter,
        relationship_preference_adapter=relationship_preference_adapter,
    )


@dataclass(frozen=True)
class IdentityMemoryBrainComposition:
    """Controlled composition including identity and personal profiles."""

    service: BrainService
    official_adapter: OfficialMemoryBrainAdapter
    goal_project_adapter: GoalProjectBrainAdapter
    relationship_preference_adapter: RelationshipPreferenceBrainAdapter
    identity_profile_adapter: IdentityProfileBrainAdapter
    active_identity_resolver: ActiveIdentityResolver
    safe_personal_context: SafePersonalContextService
    conversation_context_preparer: ConversationContextPreparer
    conversation_context_diagnostic: ConversationContextDiagnostic
    structural_audit: BrainStructuralAudit


def build_identity_memory_brain_composition(
    *,
    brain_repository: BrainRepository,
    memory_gateway: MemoryStore,
    goal_repository: HouseholdGoalRepository,
    project_repository: HouseholdProjectRepository,
    storage_root: str | Path,
    relationship_memory: RelationshipMemoryManager,
    owner: str,
) -> IdentityMemoryBrainComposition:
    root = Path(storage_root)
    relational = build_relational_memory_brain_composition(
        brain_repository=brain_repository,
        memory_gateway=memory_gateway,
        goal_repository=goal_repository,
        project_repository=project_repository,
        relationship_memory=relationship_memory,
        owner=owner,
    )
    local_profile_store = LocalIdentityProfileStore(root / "profile.toml")
    identity_profile_store = JsonIdentityProfileStore(
        root / "identity" / "profiles.json"
    )
    identity_adapter = IdentityProfileBrainAdapter(
        local_profile_store=local_profile_store,
        identity_profile_store=identity_profile_store,
    )
    active_identity_resolver = ActiveIdentityResolver(
        local_profile_store=local_profile_store,
        identity_profile_store=identity_profile_store,
    )
    service = BrainService(
        brain_repository,
        readers=(
            relational.official_adapter,
            relational.goal_project_adapter,
            relational.relationship_preference_adapter,
            identity_adapter,
        ),
    )
    safe_personal_context = SafePersonalContextService(
        brain_service=service,
        identity_resolver=active_identity_resolver,
        identity_profile_store=identity_profile_store,
    )
    conversation_context_preparer = ConversationContextPreparer(
        safe_personal_context
    )
    conversation_context_diagnostic = ConversationContextDiagnostic(
        conversation_context_preparer
    )
    structural_audit = BrainStructuralAudit()
    return IdentityMemoryBrainComposition(
        service=service,
        official_adapter=relational.official_adapter,
        goal_project_adapter=relational.goal_project_adapter,
        relationship_preference_adapter=(
            relational.relationship_preference_adapter
        ),
        identity_profile_adapter=identity_adapter,
        active_identity_resolver=active_identity_resolver,
        safe_personal_context=safe_personal_context,
        conversation_context_preparer=conversation_context_preparer,
        conversation_context_diagnostic=conversation_context_diagnostic,
        structural_audit=structural_audit,
    )
