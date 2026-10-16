from __future__ import annotations

import re
from dataclasses import dataclass

from core.document_classification import DocumentClassification
from core.text_extraction import TextExtraction
from core.visual_code_detection import VisualCodeDetection

from .models import ExtractedField, StructuredDocument


@dataclass(frozen=True)
class DeterministicStructuredDocumentExtractor:
    """Local, explainable extraction from OCR and decoded visual codes."""

    extractor_name: str = "deterministic-structured-document-extractor-v1"

    def __post_init__(self) -> None:
        if not self.extractor_name.strip():
            raise ValueError("structured document extractor name must not be blank")

    def extract(
        self,
        *,
        text: TextExtraction,
        classification: DocumentClassification,
        codes: VisualCodeDetection | None = None,
    ) -> StructuredDocument:
        source = text.full_text
        fields: list[ExtractedField] = []
        self._append_match(
            fields,
            "invoice_number",
            source,
            (
                r"(?im)^\s*(?:factura|comprobante|n[úu]mero|nro\.?|n[°º])"
                r"\s*[:#-]?\s*([A-Z0-9-]{4,})\s*$"
            ),
            0.86,
        )
        self._append_match(
            fields,
            "issue_date",
            source,
            (
                r"(?i)(?:fecha(?:\s+de\s+emisi[oó]n)?|emitida?)"
                r"\s*[:\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"
            ),
            0.88,
        )
        self._append_match(
            fields,
            "due_date",
            source,
            r"(?i)(?:vencimiento|vence)\s*[:\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            0.92,
        )
        self._append_match(
            fields,
            "tax_id",
            source,
            r"(?i)(?:CUIT|CUIL|RUT|NIF)\s*[:\-]?\s*([0-9.-]{8,})",
            0.94,
        )
        amount = re.search(
            (
                r"(?im)(?:importe\s+total|total\s+a\s+pagar|total)"
                r"\s*[:\-]?\s*([$€£]?\s*[0-9][0-9.,]*)"
            ),
            source,
        )
        if amount:
            raw = amount.group(1).strip()
            fields.append(ExtractedField("total_amount", raw, 0.93, amount.group(0)))
            currency = self._currency(raw, source)
            if currency:
                fields.append(ExtractedField("currency", currency, 0.86, raw))
        issuer = self._issuer(source)
        if issuer:
            fields.append(issuer)
        if codes and codes.regions:
            region = codes.regions[0]
            fields.append(
                ExtractedField(
                    "payment_or_reference_code",
                    region.content,
                    region.confidence,
                    f"{region.code_type}:{region.content}",
                )
            )
        fields.sort(key=lambda field: field.name)
        return StructuredDocument(
            document_type=classification.primary.document_type.value,
            fields=tuple(fields),
            extractor_name=self.extractor_name,
        )

    @staticmethod
    def _append_match(
        fields: list[ExtractedField],
        name: str,
        source: str,
        pattern: str,
        confidence: float,
    ) -> None:
        match = re.search(pattern, source)
        if match:
            fields.append(
                ExtractedField(name, match.group(1), confidence, match.group(0))
            )

    @staticmethod
    def _currency(raw_amount: str, source: str) -> str | None:
        upper = source.upper()
        if "ARS" in upper or "$" in raw_amount:
            return "ARS"
        if "USD" in upper or "US$" in upper:
            return "USD"
        if "EUR" in upper or "€" in raw_amount:
            return "EUR"
        return None

    @staticmethod
    def _issuer(source: str) -> ExtractedField | None:
        for line in source.splitlines():
            candidate = line.strip()
            has_letters = re.search(r"[A-Za-zÁÉÍÓÚáéíóú]", candidate)
            if 3 <= len(candidate) <= 80 and has_letters:
                lowered = candidate.casefold()
                if not any(
                    token in lowered
                    for token in ("factura", "fecha", "total", "vencimiento")
                ):
                    return ExtractedField("issuer", candidate, 0.62, candidate)
        return None
