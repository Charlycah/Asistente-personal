from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CognitiveMaturityLevel(str, Enum):
    NONEXISTENT = "nonexistent"
    VERY_LOW = "very_low"
    LOW = "low"
    LOW_MEDIUM = "low_medium"
    MEDIUM = "medium"
    MEDIUM_HIGH = "medium_high"
    HIGH = "high"
    NOT_DEMONSTRATED = "not_demonstrated"


class CognitiveMaturityEvidence(str, Enum):
    CONTRACT = "contract"
    UNIT_TEST = "unit_test"
    ARCHITECTURE_TEST = "architecture_test"
    RUNTIME_INTEGRATION = "runtime_integration"
    OPERATIONAL_DIAGNOSTIC = "operational_diagnostic"
    PHYSICAL_CHANNEL_CERTIFICATION = "physical_channel_certification"
    HUMAN_REVIEW = "human_review"


@dataclass(frozen=True)
class CognitiveMaturityCriterion:
    capability_id: str
    title: str
    current_level: CognitiveMaturityLevel
    target_level: CognitiveMaturityLevel
    target_qualification: str
    high_requirements: tuple[str, ...]
    required_evidence: frozenset[CognitiveMaturityEvidence]
    exclusions: tuple[str, ...]

    def __post_init__(self) -> None:
        text_fields = (
            self.capability_id,
            self.title,
            self.target_qualification,
            *self.high_requirements,
            *self.exclusions,
        )
        if any(not item.strip() for item in text_fields):
            raise ValueError("cognitive maturity criterion text must not be blank")
        if not self.high_requirements:
            raise ValueError(
                "cognitive maturity criterion requires observable outcomes"
            )
        if len(self.high_requirements) != len(set(self.high_requirements)):
            raise ValueError("cognitive maturity requirements must be unique")
        if not self.required_evidence:
            raise ValueError("cognitive maturity criterion requires evidence")
