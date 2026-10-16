from __future__ import annotations

import re
import textwrap
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from app.health_orchestrator import HealthOrchestratorService

_ALLOWED_PEOPLE = {"carlos": "Carlos", "cristina": "Cristina"}


@dataclass(frozen=True)
class MedicalPdfExportResult:
    handled: bool
    response: str = ""
    output_path: Path | None = None


class MedicalPdfExportService:
    """Exports a local PDF snapshot built from confirmed health records."""

    _REQUEST = re.compile(
        r"^(?:exportar|generar|crear) (?:informe|resumen|reporte|exportación|"
        r"exportacion) médic[oa](?: integral)? de (Carlos|Cristina) "
        r"(?:en |a )?PDF$|^(?:exportación|exportacion) médica en PDF de "
        r"(Carlos|Cristina)$",
        flags=re.IGNORECASE,
    )

    def __init__(
        self,
        orchestrator: HealthOrchestratorService | None = None,
        output_directory: Path | None = None,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self.orchestrator = orchestrator or HealthOrchestratorService()
        self.output_directory = output_directory or Path(
            ".roby/exports/medical"
        )
        self._now = now or datetime.now

    def prepare(self, text: str) -> MedicalPdfExportResult:
        normalized = " ".join(text.strip().split())
        match = self._REQUEST.fullmatch(normalized)
        if match is None:
            return MedicalPdfExportResult(handled=False)
        person = next(group for group in match.groups() if group is not None)
        canonical = _ALLOWED_PEOPLE[person.casefold()]
        return self._export(canonical)

    def _export(self, person: str) -> MedicalPdfExportResult:
        snapshot = self.orchestrator.prepare(
            f"orquestador integral de salud de {person}"
        )
        if not snapshot.handled:
            return MedicalPdfExportResult(
                handled=True,
                response="No fue posible preparar el informe médico local.",
            )
        generated_at = self._now()
        filename = (
            f"informe_medico_{person.casefold()}_"
            f"{generated_at.strftime('%Y%m%d_%H%M%S')}.pdf"
        )
        output_path = self.output_directory / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        lines = self._document_lines(person, generated_at, snapshot.response)
        _SimplePdfWriter.write(output_path, lines)
        return MedicalPdfExportResult(
            handled=True,
            output_path=output_path,
            response=(
                f"Exportación médica en PDF de {person} creada correctamente: "
                f"{output_path}. El documento reúne datos confirmados del registro "
                "local y no reemplaza una evaluación profesional."
            ),
        )

    @staticmethod
    def _document_lines(
        person: str,
        generated_at: datetime,
        snapshot: str,
    ) -> list[str]:
        lines = [
            "ROBY XI.2 - Informe médico personal",
            f"Persona: {person}",
            f"Generado: {generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
        ]
        snapshot_lines = snapshot.splitlines()
        if snapshot_lines and snapshot_lines[0].startswith(
            "Orquestador integral de salud"
        ):
            snapshot_lines = snapshot_lines[1:]
        lines.extend(snapshot_lines)
        lines.extend(
            [
                "",
                "Advertencia:",
                "Este documento organiza información confirmada del registro local.",
                "No constituye diagnóstico, receta ni indicación de tratamiento.",
                "Ante una urgencia, contacte los servicios oficiales de su zona.",
            ]
        )
        return lines


class _SimplePdfWriter:
    PAGE_WIDTH = 595
    PAGE_HEIGHT = 842
    MARGIN_X = 50
    TOP_Y = 790
    LINE_HEIGHT = 13
    MAX_LINES = 54
    WRAP_WIDTH = 88

    @classmethod
    def write(cls, path: Path, source_lines: list[str]) -> None:
        wrapped = cls._wrap(source_lines)
        pages = [
            wrapped[index : index + cls.MAX_LINES]
            for index in range(0, len(wrapped), cls.MAX_LINES)
        ] or [[]]
        path.write_bytes(cls._build_pdf(pages))

    @classmethod
    def _wrap(cls, source_lines: list[str]) -> list[str]:
        result: list[str] = []
        for line in source_lines:
            if not line:
                result.append("")
                continue
            subsequent = "  " if line.startswith("-") else ""
            result.extend(
                textwrap.wrap(
                    line,
                    width=cls.WRAP_WIDTH,
                    subsequent_indent=subsequent,
                    break_long_words=False,
                    break_on_hyphens=False,
                )
                or [""]
            )
        return result

    @classmethod
    def _build_pdf(cls, pages: list[list[str]]) -> bytes:
        page_count = len(pages)
        font_id = 3 + page_count * 2
        objects: dict[int, bytes] = {
            1: b"<< /Type /Catalog /Pages 2 0 R >>",
            2: (
                f"<< /Type /Pages /Count {page_count} /Kids ["
                + " ".join(f"{3 + index * 2} 0 R" for index in range(page_count))
                + "] >>"
            ).encode("ascii"),
            font_id: (
                b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica "
                b"/Encoding /WinAnsiEncoding >>"
            ),
        }
        for index, lines in enumerate(pages):
            page_id = 3 + index * 2
            content_id = page_id + 1
            content = cls._page_stream(lines, index + 1, page_count)
            objects[page_id] = (
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 "
                f"{cls.PAGE_WIDTH} {cls.PAGE_HEIGHT}] /Resources "
                f"<< /Font << /F1 {font_id} 0 R >> >> /Contents "
                f"{content_id} 0 R >>"
            ).encode("ascii")
            objects[content_id] = (
                f"<< /Length {len(content)} >>\nstream\n".encode("ascii")
                + content
                + b"\nendstream"
            )
        return cls._serialize(objects)

    @classmethod
    def _page_stream(
        cls,
        lines: list[str],
        page_number: int,
        page_count: int,
    ) -> bytes:
        commands = [
            "BT",
            "/F1 10 Tf",
            f"{cls.LINE_HEIGHT} TL",
            f"{cls.MARGIN_X} {cls.TOP_Y} Td",
        ]
        for index, line in enumerate(lines):
            if index:
                commands.append("T*")
            commands.append(f"({cls._escape(line)}) Tj")
        commands.extend(
            [
                "ET",
                "BT",
                "/F1 8 Tf",
                f"{cls.MARGIN_X} 30 Td",
                f"(Página {page_number} de {page_count}) Tj",
                "ET",
            ]
        )
        return "\n".join(commands).encode("cp1252", errors="replace")

    @staticmethod
    def _escape(value: str) -> str:
        encoded = value.encode("cp1252", errors="replace")
        result = []
        for byte in encoded:
            if byte in (40, 41, 92):
                result.append("\\" + chr(byte))
            elif byte < 32 or byte > 126:
                result.append(f"\\{byte:03o}")
            else:
                result.append(chr(byte))
        return "".join(result)

    @staticmethod
    def _serialize(objects: dict[int, bytes]) -> bytes:
        data = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = [0]
        max_id = max(objects)
        for object_id in range(1, max_id + 1):
            offsets.append(len(data))
            data.extend(f"{object_id} 0 obj\n".encode("ascii"))
            data.extend(objects[object_id])
            data.extend(b"\nendobj\n")
        xref_offset = len(data)
        data.extend(f"xref\n0 {max_id + 1}\n".encode("ascii"))
        data.extend(b"0000000000 65535 f \n")
        for offset in offsets[1:]:
            data.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
        data.extend(
            (
                f"trailer\n<< /Size {max_id + 1} /Root 1 0 R >>\n"
                f"startxref\n{xref_offset}\n%%EOF\n"
            ).encode("ascii")
        )
        return bytes(data)
