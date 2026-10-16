from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from core.document_classification import DocumentClassification
from core.text_extraction import TextExtraction
from core.visual_code_detection import VisualCodeDetection


@dataclass(frozen=True)
class ExtractedField:
    name: str
    value: str
    confidence: float
    evidence: str

    def __post_init__(self) -> None:
        name = self.name.strip()
        value = self.value.strip()
        evidence = self.evidence.strip()
        if not name or not value or not evidence:
            raise ValueError("document field name, value and evidence are required")
        if not 0 <= self.confidence <= 1:
            raise ValueError("document field confidence must be between zero and one")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "value", value)
        object.__setattr__(self, "evidence", evidence)


@dataclass(frozen=True)
class StructuredDocument:
    document_type: str
    fields: tuple[ExtractedField, ...]
    extractor_name: str

    def __post_init__(self) -> None:
        document_type = self.document_type.strip()
        extractor_name = self.extractor_name.strip()
        if not document_type or not extractor_name:
            raise ValueError("document type and extractor name are required")
        names = tuple(field.name for field in self.fields)
        if len(names) != len(set(names)):
            raise ValueError("structured document field names must be unique")
        object.__setattr__(self, "document_type", document_type)
        object.__setattr__(self, "extractor_name", extractor_name)

    def get(self, name: str) -> ExtractedField | None:
        return next((field for field in self.fields if field.name == name), None)


class StructuredDocumentExtractor(Protocol):
    def extract(
        self,
        *,
        text: TextExtraction,
        classification: DocumentClassification,
        codes: VisualCodeDetection | None = None,
    ) -> StructuredDocument:
        """Extract traceable fields without external validation or actions."""
