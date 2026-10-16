from __future__ import annotations

from hashlib import sha256

from core.preference_learning import (
    PreferenceCandidate,
    PreferenceDisposition,
    PreferenceEvidence,
    PreferenceLearningSnapshot,
)


class PreferenceLearning:
    """Governed read-only evaluator for explicit preference evidence."""

    SCHEMA_VERSION = "m369.2"
    CANONICAL_AUTHORITY = "preference_learning"
    PARENT_AUTHORITY = "learning_foundation"
    MINIMUM_EVIDENCE_COUNT = 2

    @property
    def snapshot(self) -> PreferenceLearningSnapshot:
        return PreferenceLearningSnapshot(
            schema_version=self.SCHEMA_VERSION,
            canonical_authority=self.CANONICAL_AUTHORITY,
            parent_authority=self.PARENT_AUTHORITY,
            minimum_evidence_count=self.MINIMUM_EVIDENCE_COUNT,
            read_only=True,
            automatic_preference_learning=False,
            habit_detection_enabled=False,
            pattern_recognition_enabled=False,
            adaptive_reasoning_enabled=False,
            persistence_added=False,
            runtime_behavior_changed=False,
        )

    def evaluate(
        self,
        *,
        evidence: tuple[PreferenceEvidence, ...],
    ) -> PreferenceCandidate:
        if not evidence:
            raise ValueError("preference learning requires explicit evidence")
        evidence_ids = tuple(item.candidate_id for item in evidence)
        if len(evidence_ids) != len(set(evidence_ids)):
            raise ValueError("preference evidence must be unique")

        subjects = {item.subject.strip() for item in evidence}
        values = {item.proposed_value.strip() for item in evidence}
        if len(subjects) != 1 or len(values) != 1:
            raise ValueError("preference evidence must support one subject and value")

        observation_ids = tuple(
            dict.fromkeys(
                observation_id
                for item in evidence
                for observation_id in item.observation_ids
            )
        )
        confidence = round(
            sum(item.confidence for item in evidence) / len(evidence), 6
        )
        disposition = (
            PreferenceDisposition.REVIEW_REQUIRED
            if len(evidence) >= self.MINIMUM_EVIDENCE_COUNT
            else PreferenceDisposition.INSUFFICIENT_EVIDENCE
        )
        subject = next(iter(subjects))
        preferred_value = next(iter(values))
        payload = "|".join(
            (subject, preferred_value, *evidence_ids, f"{confidence:.6f}")
        )
        preference_id = (
            f"preference-{sha256(payload.encode('utf-8')).hexdigest()[:16]}"
        )
        return PreferenceCandidate(
            preference_id=preference_id,
            subject=subject,
            preferred_value=preferred_value,
            evidence_ids=evidence_ids,
            observation_ids=observation_ids,
            evidence_count=len(evidence),
            confidence=confidence,
            disposition=disposition,
            accepted_as_preference=False,
            persistence_authorized=False,
        )
