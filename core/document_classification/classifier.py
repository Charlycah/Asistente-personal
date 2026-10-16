from __future__ import annotations

import re
from dataclasses import dataclass

from core.object_detection import ObjectDetection
from core.text_extraction import TextExtraction
from core.visual_code_detection import VisualCodeDetection

from .models import (
    DocumentCandidate,
    DocumentClassification,
    DocumentType,
)


@dataclass(frozen=True)
class DeterministicDocumentClassifier:
    """Explainable local classifier based on explicit observable signals."""

    classifier_name: str = "deterministic-document-classifier-v1"
    minimum_confidence: float = 0.45

    def __post_init__(self) -> None:
        if not self.classifier_name.strip():
            raise ValueError("document classifier name must not be blank")
        if not 0 <= self.minimum_confidence <= 1:
            raise ValueError("minimum document confidence must be valid")

    def classify(
        self,
        *,
        text: TextExtraction,
        objects: ObjectDetection | None = None,
        codes: VisualCodeDetection | None = None,
    ) -> DocumentClassification:
        normalized = self._normalize(text.full_text)
        rules = {
            DocumentType.INVOICE: (
                "factura",
                "invoice",
                "vencimiento",
                "importe total",
                "cuit",
            ),
            DocumentType.RECEIPT: (
                "recibo",
                "receipt",
                "recibí de",
                "comprobante de pago",
            ),
            DocumentType.TICKET: (
                "ticket",
                "boleto",
                "entrada",
                "boarding pass",
                "asiento",
            ),
            DocumentType.FORM: (
                "formulario",
                "complete los campos",
                "firma del solicitante",
                "solicitud",
            ),
            DocumentType.LETTER: (
                "estimado",
                "atentamente",
                "dear",
                "sincerely",
            ),
            DocumentType.LABEL: (
                "contenido neto",
                "ingredientes",
                "lote",
                "fecha de elaboración",
            ),
            DocumentType.IDENTITY_DOCUMENT: (
                "documento nacional de identidad",
                "dni",
                "apellido",
                "nacionalidad",
            ),
        }
        candidates: list[DocumentCandidate] = []
        for document_type, keywords in rules.items():
            matches = tuple(keyword for keyword in keywords if keyword in normalized)
            if not matches:
                continue
            confidence = min(0.98, 0.42 + 0.14 * len(matches))
            if codes and codes.regions and document_type in {
                DocumentType.INVOICE,
                DocumentType.TICKET,
                DocumentType.LABEL,
            }:
                confidence = min(0.99, confidence + 0.06)
                matches += ("visual_code_present",)
            if objects and any(
                region.label.lower() in {"document", "paper", "receipt"}
                for region in objects.regions
            ):
                confidence = min(0.99, confidence + 0.03)
                matches += ("document_object_present",)
            candidates.append(DocumentCandidate(document_type, confidence, matches))
        candidates.sort(key=lambda item: (-item.confidence, item.document_type.value))
        if not candidates or candidates[0].confidence < self.minimum_confidence:
            unknown = DocumentCandidate(DocumentType.UNKNOWN, 0.0, ())
            return DocumentClassification(unknown, (), self.classifier_name)
        return DocumentClassification(
            primary=candidates[0],
            alternatives=tuple(candidates[1:3]),
            classifier_name=self.classifier_name,
        )

    @staticmethod
    def _normalize(value: str) -> str:
        lowered = value.casefold()
        return re.sub(r"\s+", " ", lowered).strip()
