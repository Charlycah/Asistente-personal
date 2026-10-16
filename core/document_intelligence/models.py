from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from core.document_extraction import StructuredDocument
from core.text_extraction import TextExtraction
from core.visual_code_detection import VisualCodeDetection


@dataclass(frozen=True)
class DocumentIssue:
    code: str
    message: str
    severity: str
    evidence: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.code.strip() or not self.message.strip():
            raise ValueError("document issue code and message are required")
        if self.severity not in {"info", "warning"}:
            raise ValueError("document issue severity must be info or warning")


@dataclass(frozen=True)
class DocumentIntelligence:
    document_type: str
    summary: str
    completeness: float
    consistency: float
    missing_fields: tuple[str, ...]
    issues: tuple[DocumentIssue, ...]
    intelligence_name: str

    def __post_init__(self) -> None:
        if not self.document_type.strip() or not self.summary.strip():
            raise ValueError("document intelligence type and summary are required")
        scores_valid = (
            0 <= self.completeness <= 1 and 0 <= self.consistency <= 1
        )
        if not scores_valid:
            raise ValueError(
                "document intelligence scores must be between zero and one"
            )
        if len(self.missing_fields) != len(set(self.missing_fields)):
            raise ValueError("missing document fields must be unique")


class DocumentIntelligenceAnalyzer(Protocol):
    def analyze(
        self,
        *,
        document: StructuredDocument,
        text: TextExtraction,
        codes: VisualCodeDetection | None = None,
    ) -> DocumentIntelligence:
        """Explain document completeness and consistency without acting."""
