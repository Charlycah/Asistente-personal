from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .active_identity import ActiveIdentityRequest
from .conversation_context import (
    ConversationContextPackage,
    ConversationContextPreparer,
)
from .service import BrainQuery


@dataclass(frozen=True)
class ConversationContextDiagnosticFinding:
    """Single read-only observation about a prepared context package."""

    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class ConversationContextDiagnosticReport:
    """Observable integrity report for one prepared conversation package."""

    package: ConversationContextPackage
    actual_item_count: int
    actual_character_count: int
    duplicate_memory_ids: tuple[str, ...]
    disallowed_subjects: tuple[str, ...]
    findings: tuple[ConversationContextDiagnosticFinding, ...]

    @property
    def is_healthy(self) -> bool:
        return not any(finding.severity == "error" for finding in self.findings)

    def to_dict(self) -> dict[str, object]:
        return {
            "status": {
                "healthy": self.is_healthy,
                "finding_count": len(self.findings),
            },
            "observed": {
                "actual_item_count": self.actual_item_count,
                "actual_character_count": self.actual_character_count,
                "duplicate_memory_ids": list(self.duplicate_memory_ids),
                "disallowed_subjects": list(self.disallowed_subjects),
            },
            "package": self.package.to_dict(),
            "findings": [
                {
                    "code": finding.code,
                    "severity": finding.severity,
                    "message": finding.message,
                }
                for finding in self.findings
            ],
        }


class ConversationContextDiagnostic:
    """Prepare and inspect context without changing memory or runtime state."""

    def __init__(self, preparer: ConversationContextPreparer) -> None:
        self.preparer = preparer

    def inspect(
        self,
        *,
        identity_request: ActiveIdentityRequest,
        query: BrainQuery | None = None,
        max_items: int | None = None,
        max_characters: int | None = None,
        now: datetime | None = None,
    ) -> ConversationContextDiagnosticReport:
        package = self.preparer.prepare(
            identity_request=identity_request,
            query=query,
            max_items=max_items,
            max_characters=max_characters,
            now=now,
        )
        return self.inspect_package(package)

    @staticmethod
    def inspect_package(
        package: ConversationContextPackage,
    ) -> ConversationContextDiagnosticReport:
        actual_item_count = len(package.items)
        actual_character_count = sum(len(item.text) for item in package.items)
        duplicate_memory_ids = ConversationContextDiagnostic._duplicates(
            item.memory_id for item in package.items
        )
        allowed = set(package.allowed_subjects)
        disallowed_subjects = tuple(
            sorted(
                {
                    item.subject
                    for item in package.items
                    if item.subject not in allowed
                }
            )
        )
        findings: list[ConversationContextDiagnosticFinding] = []

        def add(code: str, severity: str, message: str) -> None:
            findings.append(
                ConversationContextDiagnosticFinding(
                    code=code,
                    severity=severity,
                    message=message,
                )
            )

        if actual_item_count > package.max_items:
            add(
                "item_limit_exceeded",
                "error",
                "El paquete contiene más elementos que el límite declarado.",
            )
        if actual_character_count > package.max_characters:
            add(
                "character_limit_exceeded",
                "error",
                "El paquete supera el límite de caracteres declarado.",
            )
        if actual_character_count != package.character_count:
            add(
                "character_count_mismatch",
                "error",
                "El conteo de caracteres declarado no coincide con el contenido.",
            )
        if package.omitted_count < 0:
            add(
                "negative_omitted_count",
                "error",
                "El conteo de elementos omitidos no puede ser negativo.",
            )
        if duplicate_memory_ids:
            add(
                "duplicate_memory_ids",
                "error",
                "El paquete contiene identificadores de memoria duplicados.",
            )
        if disallowed_subjects:
            add(
                "disallowed_subjects",
                "error",
                "El paquete contiene sujetos fuera del alcance permitido.",
            )
        if any(not item.text.strip() for item in package.items):
            add(
                "blank_item_text",
                "error",
                "El paquete contiene al menos un texto vacío.",
            )
        if not package.private_context_enabled and package.active_subject is not None:
            add(
                "private_context_disabled_with_active_subject",
                "warning",
                "Existe sujeto activo aunque el contexto privado está deshabilitado.",
            )
        if not findings:
            add(
                "package_integrity_ok",
                "info",
                "El paquete respeta alcance, límites y conteos declarados.",
            )

        return ConversationContextDiagnosticReport(
            package=package,
            actual_item_count=actual_item_count,
            actual_character_count=actual_character_count,
            duplicate_memory_ids=duplicate_memory_ids,
            disallowed_subjects=disallowed_subjects,
            findings=tuple(findings),
        )

    @staticmethod
    def _duplicates(values) -> tuple[str, ...]:
        seen: set[str] = set()
        duplicates: set[str] = set()
        for value in values:
            if value in seen:
                duplicates.add(value)
            seen.add(value)
        return tuple(sorted(duplicates))
