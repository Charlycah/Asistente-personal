from __future__ import annotations

from app.cognitive_memory_foundation import CognitiveMemoryFoundation
from app.episodic_memory_foundation import EpisodicMemoryFoundation
from app.long_term_memory_foundation import LongTermMemoryFoundation
from core.memory_consolidation_foundation import (
    ConsolidationAssessment,
    ConsolidationCandidate,
    ConsolidationDisposition,
    ConsolidationReason,
    ConsolidationTarget,
    MemoryConsolidationFoundationSnapshot,
)


class MemoryConsolidationFoundation:
    """Pure governed assessment between existing memory authorities."""

    SCHEMA_VERSION = "m366.6"

    def __init__(
        self,
        *,
        cognitive_memory: CognitiveMemoryFoundation | None = None,
        episodic_memory: EpisodicMemoryFoundation | None = None,
        long_term_memory: LongTermMemoryFoundation | None = None,
    ) -> None:
        self._cognitive_memory = cognitive_memory or CognitiveMemoryFoundation()
        self._episodic_memory = episodic_memory or EpisodicMemoryFoundation()
        self._long_term_memory = long_term_memory or LongTermMemoryFoundation()
        self._validate()

    @property
    def snapshot(self) -> MemoryConsolidationFoundationSnapshot:
        episodic_domain = self._cognitive_memory.snapshot.domain_for("episodic")
        long_term_domain = self._cognitive_memory.snapshot.domain_for("long_term")
        return MemoryConsolidationFoundationSnapshot(
            schema_version=self.SCHEMA_VERSION,
            canonical_authority=long_term_domain.authority_key,
            source_authority=episodic_domain.authority_key,
            writer_authority="app.memory_consolidation:OfficialMemoryGateway",
            supported_targets=tuple(ConsolidationTarget),
            assessment_only=True,
            automatic_writes_enabled=False,
            automatic_truth_promotion_enabled=False,
            conflict_review_required=True,
            sensitive_memory_confirmation_required=True,
            runtime_behavior_changed=False,
        )

    def assess(self, candidate: ConsolidationCandidate) -> ConsolidationAssessment:
        reasons: list[ConsolidationReason] = []

        if candidate.conflicts_with_memory:
            reasons.append(ConsolidationReason.CONFLICT_REQUIRES_REVIEW)
            return self._assessment(
                candidate,
                ConsolidationDisposition.REQUEST_CONFIRMATION,
                reasons,
                requires_confirmation=True,
            )

        if candidate.personal_or_sensitive:
            reasons.append(ConsolidationReason.PERSONAL_OR_SENSITIVE)
            if candidate.explicit_user_intent:
                reasons.append(ConsolidationReason.EXPLICIT_USER_INTENT)
            return self._assessment(
                candidate,
                ConsolidationDisposition.REQUEST_CONFIRMATION,
                reasons,
                requires_confirmation=True,
            )

        if candidate.explicit_user_intent:
            reasons.append(ConsolidationReason.EXPLICIT_USER_INTENT)
            return self._assessment(
                candidate,
                self._proposal_for(candidate.proposed_target),
                reasons,
                requires_confirmation=True,
            )

        if candidate.procedural_structure:
            reasons.append(ConsolidationReason.PROCEDURAL_STRUCTURE)
            if candidate.repetitions >= 2 and candidate.confidence >= 0.7:
                reasons.append(ConsolidationReason.REPEATED_EVIDENCE)
                return self._assessment(
                    candidate,
                    ConsolidationDisposition.PROPOSE_PROCEDURAL,
                    reasons,
                    requires_confirmation=True,
                )

        if candidate.repetitions >= 3 and candidate.relevance >= 7:
            reasons.extend(
                (
                    ConsolidationReason.REPEATED_EVIDENCE,
                    ConsolidationReason.HIGH_RELEVANCE,
                )
            )
            return self._assessment(
                candidate,
                self._proposal_for(candidate.proposed_target),
                reasons,
                requires_confirmation=True,
            )

        if candidate.relevance <= 2 and candidate.confidence < 0.5:
            reasons.append(ConsolidationReason.LOW_RELEVANCE)
            return self._assessment(
                candidate,
                ConsolidationDisposition.ARCHIVE_CANDIDATE,
                reasons,
                requires_confirmation=False,
            )

        reasons.append(ConsolidationReason.INSUFFICIENT_EVIDENCE)
        return self._assessment(
            candidate,
            ConsolidationDisposition.KEEP_EPISODIC,
            reasons,
            requires_confirmation=False,
        )

    @staticmethod
    def _proposal_for(target: ConsolidationTarget) -> ConsolidationDisposition:
        mapping = {
            ConsolidationTarget.EPISODIC: ConsolidationDisposition.KEEP_EPISODIC,
            ConsolidationTarget.SEMANTIC: ConsolidationDisposition.PROPOSE_SEMANTIC,
            ConsolidationTarget.PROCEDURAL: (
                ConsolidationDisposition.PROPOSE_PROCEDURAL
            ),
            ConsolidationTarget.LONG_TERM: ConsolidationDisposition.PROPOSE_LONG_TERM,
        }
        return mapping[target]

    @staticmethod
    def _assessment(
        candidate: ConsolidationCandidate,
        disposition: ConsolidationDisposition,
        reasons: list[ConsolidationReason],
        *,
        requires_confirmation: bool,
    ) -> ConsolidationAssessment:
        return ConsolidationAssessment(
            candidate_id=candidate.candidate_id,
            disposition=disposition,
            proposed_target=candidate.proposed_target,
            reasons=tuple(dict.fromkeys(reasons)),
            requires_human_confirmation=requires_confirmation,
        )

    def _validate(self) -> None:
        episodic_snapshot = self._episodic_memory.snapshot
        long_term_snapshot = self._long_term_memory.snapshot
        if episodic_snapshot.canonical_authority != "episodic_memory":
            raise ValueError("consolidation must source canonical episodic memory")
        if long_term_snapshot.canonical_authority != "memory_gateway":
            raise ValueError("consolidation must remain under memory_gateway")
        if not long_term_snapshot.consolidation_requires_governance:
            raise ValueError("long-term memory must require governed consolidation")
