from __future__ import annotations

import re
from dataclasses import dataclass

from core.document_extraction import StructuredDocument
from core.text_extraction import TextExtraction
from core.visual_code_detection import VisualCodeDetection

from .models import DocumentIntelligence, DocumentIssue


@dataclass(frozen=True)
class DeterministicDocumentIntelligenceAnalyzer:
    intelligence_name: str = "deterministic-document-intelligence-v1"

    _required_by_type = {
        "invoice": ("issuer", "invoice_number", "issue_date", "total_amount"),
        "receipt": ("issuer", "issue_date", "total_amount"),
        "ticket": ("issue_date",),
        "form": (),
        "letter": (),
        "label": (),
        "identity_document": (),
        "unknown": (),
    }

    def analyze(
        self,
        *,
        document: StructuredDocument,
        text: TextExtraction,
        codes: VisualCodeDetection | None = None,
    ) -> DocumentIntelligence:
        names = {field.name for field in document.fields}
        required = self._required_by_type.get(document.document_type, ())
        missing = tuple(name for name in required if name not in names)
        completeness = (
            1.0
            if not required
            else (len(required) - len(missing)) / len(required)
        )
        issues: list[DocumentIssue] = []
        if missing:
            issues.append(
                DocumentIssue(
                    "missing_fields",
                    "Faltan campos esperados para este tipo de documento.",
                    "warning",
                    missing,
                )
            )
        totals = tuple(
            match.group(1).strip()
            for match in re.finditer(
                r"(?im)(?:importe\s+total|total\s+a\s+pagar|total)"
                r"\s*[:\-]?\s*([$€£]?\s*[0-9][0-9.,]*)",
                text.full_text,
            )
        )
        normalized_totals = {value.replace(" ", "") for value in totals}
        if len(normalized_totals) > 1:
            issues.append(
                DocumentIssue(
                    "conflicting_totals",
                    "Se detectaron importes totales diferentes.",
                    "warning",
                    totals,
                )
            )
        code_field = document.get("payment_or_reference_code")
        if codes and codes.regions and code_field is None:
            issues.append(
                DocumentIssue(
                    "unlinked_visual_code",
                    "Hay un código visual que no quedó asociado al documento.",
                    "info",
                    tuple(region.content for region in codes.regions),
                )
            )
        warning_count = sum(issue.severity == "warning" for issue in issues)
        consistency = max(0.0, 1.0 - 0.25 * warning_count)
        available = ", ".join(sorted(names)) or "sin campos estructurados"
        summary = (
            f"Documento {document.document_type}; campos disponibles: {available}; "
            f"faltantes: {', '.join(missing) if missing else 'ninguno'}; "
            f"observaciones: {len(issues)}."
        )
        return DocumentIntelligence(
            document_type=document.document_type,
            summary=summary,
            completeness=round(completeness, 3),
            consistency=round(consistency, 3),
            missing_fields=missing,
            issues=tuple(issues),
            intelligence_name=self.intelligence_name,
        )
