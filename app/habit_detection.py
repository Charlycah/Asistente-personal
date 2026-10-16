from __future__ import annotations

from hashlib import sha256

from core.habit_detection import (
    HabitCandidate,
    HabitDetectionSnapshot,
    HabitDisposition,
    HabitOccurrence,
)


class HabitDetection:
    """Governed read-only evaluator for repeated temporal behavior."""

    SCHEMA_VERSION = "m369.3"
    CANONICAL_AUTHORITY = "habit_detection"
    PARENT_AUTHORITY = "preference_learning"
    MINIMUM_OCCURRENCE_COUNT = 3
    MINIMUM_DISTINCT_DAYS = 3
    MINIMUM_SPAN_DAYS = 2

    @property
    def snapshot(self) -> HabitDetectionSnapshot:
        return HabitDetectionSnapshot(
            schema_version=self.SCHEMA_VERSION,
            canonical_authority=self.CANONICAL_AUTHORITY,
            parent_authority=self.PARENT_AUTHORITY,
            minimum_occurrence_count=self.MINIMUM_OCCURRENCE_COUNT,
            minimum_distinct_days=self.MINIMUM_DISTINCT_DAYS,
            minimum_span_days=self.MINIMUM_SPAN_DAYS,
            read_only=True,
            automatic_habit_acceptance=False,
            pattern_recognition_enabled=False,
            adaptive_reasoning_enabled=False,
            persistence_added=False,
            runtime_behavior_changed=False,
        )

    def evaluate(
        self,
        *,
        occurrences: tuple[HabitOccurrence, ...],
    ) -> HabitCandidate:
        if not occurrences:
            raise ValueError("habit detection requires explicit occurrences")
        occurrence_ids = tuple(item.occurrence_id for item in occurrences)
        if len(occurrence_ids) != len(set(occurrence_ids)):
            raise ValueError("habit occurrences must be unique")

        subjects = {item.subject.strip() for item in occurrences}
        behaviors = {item.behavior.strip() for item in occurrences}
        if len(subjects) != 1 or len(behaviors) != 1:
            raise ValueError("habit occurrences must support one subject and behavior")

        ordered = tuple(sorted(occurrences, key=lambda item: item.observed_on))
        distinct_days = {item.observed_on for item in ordered}
        first_observed_on = ordered[0].observed_on
        last_observed_on = ordered[-1].observed_on
        span_days = (last_observed_on - first_observed_on).days
        confidence = round(
            sum(item.confidence for item in ordered) / len(ordered), 6
        )
        sufficient_history = (
            len(ordered) >= self.MINIMUM_OCCURRENCE_COUNT
            and len(distinct_days) >= self.MINIMUM_DISTINCT_DAYS
            and span_days >= self.MINIMUM_SPAN_DAYS
        )
        disposition = (
            HabitDisposition.REVIEW_REQUIRED
            if sufficient_history
            else HabitDisposition.INSUFFICIENT_HISTORY
        )
        subject = next(iter(subjects))
        behavior = next(iter(behaviors))
        payload = "|".join(
            (
                subject,
                behavior,
                *(item.occurrence_id for item in ordered),
                first_observed_on.isoformat(),
                last_observed_on.isoformat(),
                f"{confidence:.6f}",
            )
        )
        habit_id = f"habit-{sha256(payload.encode('utf-8')).hexdigest()[:16]}"
        return HabitCandidate(
            habit_id=habit_id,
            subject=subject,
            behavior=behavior,
            occurrence_ids=tuple(item.occurrence_id for item in ordered),
            occurrence_count=len(ordered),
            distinct_day_count=len(distinct_days),
            first_observed_on=first_observed_on,
            last_observed_on=last_observed_on,
            span_days=span_days,
            confidence=confidence,
            disposition=disposition,
            accepted_as_habit=False,
            persistence_authorized=False,
        )
