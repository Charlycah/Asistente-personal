from __future__ import annotations

from hashlib import sha256

from core.learning_foundation import (
    LearningAuthority,
    LearningCandidate,
    LearningCandidateDisposition,
    LearningDomain,
    LearningFoundationSnapshot,
    LearningObservation,
    LearningRole,
)

LEARNING_AUTHORITIES: tuple[LearningAuthority, ...] = (
    LearningAuthority(
        domain=LearningDomain.OBSERVATIONS,
        role=LearningRole.OBSERVE,
        authority_key="learning_foundation",
        implementation_path="core.learning:LearningSignal",
        purpose="Reutilizar observaciones explícitas sin aprender automáticamente.",
        parent_authority="experiential_learning",
        runtime_connected=False,
        persistent=False,
    ),
    LearningAuthority(
        domain=LearningDomain.EXPERIENCES,
        role=LearningRole.DESCRIBE,
        authority_key="learning_foundation",
        implementation_path="core.learning:LearnedExperience",
        purpose="Describir experiencias existentes sin promoverlas a conocimiento.",
        parent_authority="experiential_learning",
        runtime_connected=False,
        persistent=False,
    ),
    LearningAuthority(
        domain=LearningDomain.EVIDENCE,
        role=LearningRole.SUPPORT,
        authority_key="learning_foundation",
        implementation_path=(
            "core.controlled_autonomy.operational_learning:OperationalLearning"
        ),
        purpose="Conservar trazabilidad de evidencia explícita y revisable.",
        parent_authority="operational_learning",
        runtime_connected=False,
        persistent=False,
    ),
    LearningAuthority(
        domain=LearningDomain.POLICY,
        role=LearningRole.GOVERN,
        authority_key="learning_foundation",
        implementation_path="core.cognitive_memory:CognitiveLearningPolicy",
        purpose="Mantener toda admisión futura bajo política cognitiva gobernada.",
        parent_authority="cognitive_learning_policy",
        runtime_connected=False,
        persistent=False,
    ),
)


class LearningFoundation:
    """Canonical read-only boundary for future governed learning."""

    SCHEMA_VERSION = "m369.1"
    CANONICAL_AUTHORITY = "learning_foundation"
    PARENT_MEMORY_AUTHORITY = "cognitive_memory"

    def __init__(self) -> None:
        self._validate()

    @property
    def snapshot(self) -> LearningFoundationSnapshot:
        return LearningFoundationSnapshot(
            schema_version=self.SCHEMA_VERSION,
            canonical_authority=self.CANONICAL_AUTHORITY,
            parent_memory_authority=self.PARENT_MEMORY_AUTHORITY,
            authorities=LEARNING_AUTHORITIES,
            supported_domains=tuple(LearningDomain),
            read_only=True,
            automatic_learning=False,
            automatic_preference_learning=False,
            automatic_habit_detection=False,
            automatic_pattern_recognition=False,
            adaptive_reasoning_enabled=False,
            persistence_added=False,
            runtime_behavior_changed=False,
        )

    def structure_candidate(
        self,
        *,
        subject: str,
        proposed_value: str,
        observations: tuple[LearningObservation, ...],
        confidence: float,
    ) -> LearningCandidate:
        if not observations:
            raise ValueError("learning candidate requires explicit observations")
        observation_ids = tuple(item.observation_id for item in observations)
        if len(observation_ids) != len(set(observation_ids)):
            raise ValueError("learning observations must be unique")
        payload = "|".join(
            (
                subject.strip(),
                proposed_value.strip(),
                *observation_ids,
                f"{confidence:.6f}",
            )
        )
        candidate_id = f"learning-{sha256(payload.encode('utf-8')).hexdigest()[:16]}"
        return LearningCandidate(
            candidate_id=candidate_id,
            subject=subject.strip(),
            proposed_value=proposed_value.strip(),
            observation_ids=observation_ids,
            confidence=confidence,
            disposition=LearningCandidateDisposition.REVIEW_REQUIRED,
            accepted_as_knowledge=False,
            persistence_authorized=False,
        )

    @staticmethod
    def _validate() -> None:
        domains = tuple(item.domain for item in LEARNING_AUTHORITIES)
        if len(domains) != len(set(domains)):
            raise ValueError("learning domains must be unique")
        if set(domains) != set(LearningDomain):
            raise ValueError("learning foundation must declare every domain")
        if {item.authority_key for item in LEARNING_AUTHORITIES} != {
            "learning_foundation"
        }:
            raise ValueError("learning foundation must preserve one authority")
