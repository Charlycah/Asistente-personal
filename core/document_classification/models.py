from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from core.object_detection import ObjectDetection
from core.text_extraction import TextExtraction
from core.visual_code_detection import VisualCodeDetection


class DocumentType(str, Enum):
    INVOICE = "invoice"
    RECEIPT = "receipt"
    TICKET = "ticket"
    FORM = "form"
    LETTER = "letter"
    LABEL = "label"
    IDENTITY_DOCUMENT = "identity_document"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class DocumentCandidate:
    document_type: DocumentType | str
    confidence: float
    matched_signals: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        document_type = DocumentType(self.document_type)
        if not 0 <= self.confidence <= 1:
            raise ValueError("document confidence must be between zero and one")
        signals = tuple(signal.strip() for signal in self.matched_signals)
        if any(not signal for signal in signals):
            raise ValueError("document signals must not be blank")
        object.__setattr__(self, "document_type", document_type)
        object.__setattr__(self, "matched_signals", signals)


@dataclass(frozen=True)
class DocumentClassification:
    primary: DocumentCandidate
    alternatives: tuple[DocumentCandidate, ...] = ()
    classifier_name: str = "unknown"

    def __post_init__(self) -> None:
        name = self.classifier_name.strip()
        if not name:
            raise ValueError("document classifier name must not be blank")
        types = (self.primary.document_type,) + tuple(
            item.document_type for item in self.alternatives
        )
        if len(types) != len(set(types)):
            raise ValueError("document candidates must be unique")
        object.__setattr__(self, "classifier_name", name)


class DocumentClassifier(Protocol):
    def classify(
        self,
        *,
        text: TextExtraction,
        objects: ObjectDetection | None = None,
        codes: VisualCodeDetection | None = None,
    ) -> DocumentClassification:
        """Classify extracted document evidence without retaining source media."""
