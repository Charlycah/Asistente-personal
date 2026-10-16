from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.governed_reasoning.epistemic_sufficiency import EpistemicSufficiencyStatus
from core.governed_reasoning.longitudinal_reasoning_assessment import (
    GovernedReasoningAssessmentObservation,
)
from core.governed_reasoning.reasoning_quality_assessment import (
    GovernedReasoningQualityStatus,
)


class GovernedEpistemicObservationRetentionV1:
    """Persist admitted minimum observations under governed_reasoning authority."""

    CANONICAL_AUTHORITY = "governed_reasoning"
    _FILENAME = "observations.json"

    def __init__(self, *, storage_path: Path | str) -> None:
        self._storage_path = Path(storage_path)
        self._storage_path.mkdir(parents=True, exist_ok=True)
        self._data_path = self._storage_path / self._FILENAME

    def retain(self, observation: GovernedReasoningAssessmentObservation) -> None:
        """Retain one already-admitted observation, idempotently."""
        if type(observation) is not GovernedReasoningAssessmentObservation:
            raise TypeError("retention accepts only admitted governed observations")
        self._validate_observation(observation)

        records = self._read_records()
        key = self._identity(observation)
        records[key] = self._serialize(observation)
        self._write_records(records)

    def retrieve(
        self, *, source_reference: str
    ) -> tuple[GovernedReasoningAssessmentObservation, ...]:
        """Retrieve observations for one exact existing source lineage."""
        if not isinstance(source_reference, str) or not source_reference.strip():
            raise ValueError("retrieval requires an exact source reference")

        observations = tuple(
            self._deserialize(record)
            for record in self._read_records().values()
            if record.get("source_reference") == source_reference
        )
        return tuple(
            sorted(
                observations,
                key=lambda item: (
                    item.quality_assessment_id,
                    item.sufficiency_assessment_id,
                ),
            )
        )

    @classmethod
    def _validate_observation(
        cls, observation: GovernedReasoningAssessmentObservation
    ) -> None:
        if observation.canonical_authority != cls.CANONICAL_AUTHORITY:
            raise ValueError("retention requires governed_reasoning authority")
        if not observation.read_only or not observation.consultative:
            raise ValueError("retention requires a read-only admitted observation")

    @staticmethod
    def _identity(observation: GovernedReasoningAssessmentObservation) -> str:
        return "|".join(
            (
                observation.quality_assessment_id,
                observation.sufficiency_assessment_id,
                observation.source_reference,
                observation.world_snapshot_id,
                observation.quality_source_fingerprint,
                observation.sufficiency_source_fingerprint,
            )
        )

    @staticmethod
    def _serialize(
        observation: GovernedReasoningAssessmentObservation,
    ) -> dict[str, str]:
        return {
            "quality_assessment_id": observation.quality_assessment_id,
            "quality_status": observation.quality_status.value,
            "sufficiency_assessment_id": observation.sufficiency_assessment_id,
            "sufficiency_status": observation.sufficiency_status.value,
            "source_reference": observation.source_reference,
            "world_snapshot_id": observation.world_snapshot_id,
            "quality_source_fingerprint": observation.quality_source_fingerprint,
            "sufficiency_source_fingerprint": (
                observation.sufficiency_source_fingerprint
            ),
        }

    @staticmethod
    def _deserialize(record: dict[str, Any]) -> GovernedReasoningAssessmentObservation:
        return GovernedReasoningAssessmentObservation(
            quality_assessment_id=str(record["quality_assessment_id"]),
            quality_status=GovernedReasoningQualityStatus(record["quality_status"]),
            sufficiency_assessment_id=str(record["sufficiency_assessment_id"]),
            sufficiency_status=EpistemicSufficiencyStatus(record["sufficiency_status"]),
            source_reference=str(record["source_reference"]),
            world_snapshot_id=str(record["world_snapshot_id"]),
            quality_source_fingerprint=str(record["quality_source_fingerprint"]),
            sufficiency_source_fingerprint=str(
                record["sufficiency_source_fingerprint"]
            ),
        )

    def _read_records(self) -> dict[str, dict[str, Any]]:
        if not self._data_path.exists():
            return {}
        payload = json.loads(self._data_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("retained epistemic observations are invalid")
        return payload

    def _write_records(self, records: dict[str, dict[str, Any]]) -> None:
        temporary_path = self._data_path.with_suffix(".tmp")
        payload = (
            json.dumps(records, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
        )
        temporary_path.write_text(payload, encoding="utf-8")
        temporary_path.replace(self._data_path)
