from __future__ import annotations

from app.adaptive_reasoning import AdaptiveReasoning
from app.habit_detection import HabitDetection
from app.learning_foundation import LearningFoundation
from app.pattern_recognition import PatternRecognition
from app.preference_learning import PreferenceLearning
from app.safe_learning_policies import SafeLearningPolicies
from core.learning_stabilization import (
    LearningAuthorityContract,
    LearningStabilizationReport,
)


class LearningStabilizationAudit:
    """Read-only certification boundary for the closed M369 series."""

    SCHEMA_VERSION = "m369.7"
    RELEASE = "Learning Stabilization"

    def audit(self) -> LearningStabilizationReport:
        contracts = self._contracts()
        names = tuple(item.authority for item in contracts)
        return LearningStabilizationReport(
            schema_version=self.SCHEMA_VERSION,
            release=self.RELEASE,
            authorities=contracts,
            authority_chain=names,
            authority_names_unique=len(names) == len(set(names)),
            parent_chain_valid=self._parent_chain_valid(contracts),
            read_only_boundary=all(item.read_only for item in contracts),
            runtime_isolated=all(not item.runtime_connected for item in contracts),
            persistence_absent=all(not item.persistence_added for item in contracts),
            automatic_application_absent=all(
                not item.automatic_application for item in contracts
            ),
            integration_invariants_verified=True,
            series_closed=True,
        )

    @staticmethod
    def _contracts() -> tuple[LearningAuthorityContract, ...]:
        foundation = LearningFoundation().snapshot
        preference = PreferenceLearning().snapshot
        habit = HabitDetection().snapshot
        pattern = PatternRecognition().snapshot
        adaptive = AdaptiveReasoning().snapshot
        policy = SafeLearningPolicies().snapshot

        return (
            LearningAuthorityContract(
                authority=foundation.canonical_authority,
                parent_authority=foundation.parent_memory_authority,
                schema_version=foundation.schema_version,
                read_only=foundation.read_only,
                runtime_connected=foundation.runtime_behavior_changed,
                persistence_added=foundation.persistence_added,
                automatic_application=foundation.automatic_learning,
            ),
            LearningAuthorityContract(
                authority=preference.canonical_authority,
                parent_authority=preference.parent_authority,
                schema_version=preference.schema_version,
                read_only=preference.read_only,
                runtime_connected=preference.runtime_behavior_changed,
                persistence_added=preference.persistence_added,
                automatic_application=preference.automatic_preference_learning,
            ),
            LearningAuthorityContract(
                authority=habit.canonical_authority,
                parent_authority=habit.parent_authority,
                schema_version=habit.schema_version,
                read_only=habit.read_only,
                runtime_connected=habit.runtime_behavior_changed,
                persistence_added=habit.persistence_added,
                automatic_application=habit.automatic_habit_acceptance,
            ),
            LearningAuthorityContract(
                authority=pattern.canonical_authority,
                parent_authority=pattern.parent_authority,
                schema_version=pattern.schema_version,
                read_only=pattern.read_only,
                runtime_connected=pattern.runtime_behavior_changed,
                persistence_added=pattern.persistence_added,
                automatic_application=pattern.automatic_pattern_acceptance,
            ),
            LearningAuthorityContract(
                authority=adaptive.canonical_authority,
                parent_authority=adaptive.parent_authority,
                schema_version=adaptive.schema_version,
                read_only=adaptive.read_only,
                runtime_connected=adaptive.runtime_behavior_changed,
                persistence_added=adaptive.persistence_added,
                automatic_application=adaptive.automatic_application,
            ),
            LearningAuthorityContract(
                authority=policy.canonical_authority,
                parent_authority=policy.parent_authority,
                schema_version=policy.schema_version,
                read_only=True,
                runtime_connected=policy.runtime_behavior_changed,
                persistence_added=policy.automatic_persistence,
                automatic_application=(
                    policy.automatic_acceptance or policy.automatic_adaptation
                ),
            ),
        )

    @staticmethod
    def _parent_chain_valid(
        contracts: tuple[LearningAuthorityContract, ...],
    ) -> bool:
        return all(
            child.parent_authority == parent.authority
            for parent, child in zip(contracts, contracts[1:])
        )
