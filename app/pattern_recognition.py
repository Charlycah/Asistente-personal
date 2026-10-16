from __future__ import annotations

from hashlib import sha256

from core.pattern_recognition import (
    PatternCandidate,
    PatternDisposition,
    PatternEvidence,
    PatternRecognitionSnapshot,
)


class PatternRecognition:
    """Governed read-only evaluator for explicit recurring relationships."""

    SCHEMA_VERSION = "m369.4"
    CANONICAL_AUTHORITY = "pattern_recognition"
    PARENT_AUTHORITY = "habit_detection"
    MINIMUM_EVIDENCE_COUNT = 2
    MINIMUM_DISTINCT_HABITS = 2

    @property
    def snapshot(self) -> PatternRecognitionSnapshot:
        return PatternRecognitionSnapshot(
            schema_version=self.SCHEMA_VERSION,
            canonical_authority=self.CANONICAL_AUTHORITY,
            parent_authority=self.PARENT_AUTHORITY,
            minimum_evidence_count=self.MINIMUM_EVIDENCE_COUNT,
            minimum_distinct_habits=self.MINIMUM_DISTINCT_HABITS,
            read_only=True,
            automatic_pattern_acceptance=False,
            adaptive_reasoning_enabled=False,
            persistence_added=False,
            runtime_behavior_changed=False,
        )

    def evaluate(
        self,
        *,
        evidence: tuple[PatternEvidence, ...],
    ) -> PatternCandidate:
        if not evidence:
            raise ValueError("pattern recognition requires explicit evidence")
        evidence_ids = tuple(item.evidence_id for item in evidence)
        if len(evidence_ids) != len(set(evidence_ids)):
            raise ValueError("pattern evidence must be unique")

        subjects = {item.subject.strip() for item in evidence}
        contexts = {item.context.strip() for item in evidence}
        values = {item.observed_value.strip() for item in evidence}
        if len(subjects) != 1 or len(contexts) != 1 or len(values) != 1:
            raise ValueError(
                "pattern evidence must support one subject, context and value"
            )

        ordered = tuple(sorted(evidence, key=lambda item: item.evidence_id))
        habit_ids = tuple(dict.fromkeys(item.habit_id for item in ordered))
        confidence = round(
            sum(item.confidence for item in ordered) / len(ordered), 6
        )
        sufficient_evidence = (
            len(ordered) >= self.MINIMUM_EVIDENCE_COUNT
            and len(habit_ids) >= self.MINIMUM_DISTINCT_HABITS
        )
        disposition = (
            PatternDisposition.REVIEW_REQUIRED
            if sufficient_evidence
            else PatternDisposition.INSUFFICIENT_EVIDENCE
        )
        subject = next(iter(subjects))
        context = next(iter(contexts))
        observed_value = next(iter(values))
        payload = "|".join(
            (
                subject,
                context,
                observed_value,
                *(item.evidence_id for item in ordered),
                *habit_ids,
                f"{confidence:.6f}",
            )
        )
        pattern_id = f"pattern-{sha256(payload.encode('utf-8')).hexdigest()[:16]}"
        return PatternCandidate(
            pattern_id=pattern_id,
            subject=subject,
            context=context,
            observed_value=observed_value,
            evidence_ids=tuple(item.evidence_id for item in ordered),
            habit_ids=habit_ids,
            evidence_count=len(ordered),
            confidence=confidence,
            disposition=disposition,
            accepted_as_pattern=False,
            persistence_authorized=False,
        )
