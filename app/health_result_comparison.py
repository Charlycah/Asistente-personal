from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

from app.secure_health_checkups import (
    HealthCheckupRepository,
    LaboratoryResult,
)

_ALLOWED_PEOPLE = {"carlos": "Carlos", "cristina": "Cristina"}
_NAME_ALIASES = {
    "glucemia": "glucemia",
    "glucosa": "glucemia",
    "colesterol total": "colesterol total",
    "colesterol hdl": "hdl",
    "hdl": "hdl",
    "colesterol ldl": "ldl",
    "ldl": "ldl",
    "trigliceridos": "trigliceridos",
    "tsh": "tsh",
    "hemoglobina": "hemoglobina",
    "creatinina": "creatinina",
    "psa": "psa",
}
_UNIT_ALIASES = {
    "mg/dl": "mg/dl",
    "g/dl": "g/dl",
    "mmol/l": "mmol/l",
    "mui/l": "mui/l",
    "uiu/ml": "uiu/ml",
    "uui/ml": "uiu/ml",
    "µui/ml": "uiu/ml",
}


@dataclass(frozen=True)
class HealthComparisonResult:
    handled: bool
    response: str = ""


@dataclass(frozen=True)
class _ComparableResult:
    performed_on: str
    study_type: str
    result: LaboratoryResult
    numeric_value: Decimal | None
    normalized_unit: str


class HistoricalHealthComparisonService:
    """Compares confirmed historical results without clinical diagnosis."""

    _REQUEST = re.compile(
        r"^(?:comparar|mostr(?:ar|á) evolución de) resultados de "
        r"(Carlos|Cristina):\s*(.+)$",
        flags=re.IGNORECASE,
    )
    _REPORT_REQUEST = re.compile(
        r"^(?:ordenar|mostrar) informes de (Carlos|Cristina):\s*(.+)$",
        flags=re.IGNORECASE,
    )

    def __init__(self, repository: HealthCheckupRepository | None = None) -> None:
        self.repository = repository or HealthCheckupRepository()

    def prepare(self, text: str) -> HealthComparisonResult:
        normalized = " ".join(text.strip().split())
        match = self._REQUEST.match(normalized)
        if match is not None:
            return self._compare_laboratory(match.group(1), match.group(2))
        report_match = self._REPORT_REQUEST.match(normalized)
        if report_match is not None:
            return self._list_reports(report_match.group(1), report_match.group(2))
        return HealthComparisonResult(handled=False)

    def _compare_laboratory(
        self,
        person: str,
        raw_fields: str,
    ) -> HealthComparisonResult:
        fields = self._split_fields(raw_fields)
        requested_name = fields.get("resultado", fields.get("estudio", "")).strip()
        if not requested_name:
            return HealthComparisonResult(
                handled=True,
                response="Indicá resultado=Nombre, por ejemplo resultado=Glucemia.",
            )
        canonical_person = _ALLOWED_PEOPLE[person.casefold()]
        requested_key = self._normalize_name(requested_name)
        matches = self._find_results(canonical_person, requested_key)
        if not matches:
            return HealthComparisonResult(
                handled=True,
                response=(
                    f"No encontré resultados históricos de {requested_name} "
                    f"para {canonical_person}."
                ),
            )
        rows = [self._render_result(item) for item in matches]
        warnings = self._comparison_warnings(matches)
        suffix = ""
        if warnings:
            suffix = "\nAdvertencias: " + " ".join(warnings)
        return HealthComparisonResult(
            handled=True,
            response=(
                f"Evolución registrada de {requested_name} para "
                f"{canonical_person}:\n"
                + "\n".join(rows)
                + suffix
                + "\nEsta comparación es descriptiva y no constituye un diagnóstico."
            ),
        )

    def _list_reports(
        self,
        person: str,
        raw_fields: str,
    ) -> HealthComparisonResult:
        fields = self._split_fields(raw_fields)
        requested_study = fields.get("estudio", "").strip()
        if not requested_study:
            return HealthComparisonResult(
                handled=True,
                response="Indicá estudio=Nombre del estudio.",
            )
        canonical_person = _ALLOWED_PEOPLE[person.casefold()]
        requested_key = self._fold(requested_study)
        records = [
            record
            for record in self.repository.load()
            if record.person == canonical_person
            and not record.archived
            and record.category == "informe"
            and requested_key in self._fold(record.study_type)
        ]
        records.sort(key=lambda record: record.performed_on)
        if not records:
            return HealthComparisonResult(
                handled=True,
                response=(
                    f"No encontré informes de {requested_study} para "
                    f"{canonical_person}."
                ),
            )
        rows = "\n".join(
            f"- {record.performed_on} · {record.study_type} · {record.record_id}"
            for record in records
        )
        return HealthComparisonResult(
            handled=True,
            response=(
                f"Informes de {requested_study} de {canonical_person}, "
                f"ordenados por fecha:\n{rows}\n"
                "Conservo los textos originales sin reinterpretarlos."
            ),
        )

    def _find_results(
        self,
        person: str,
        requested_key: str,
    ) -> list[_ComparableResult]:
        found: list[_ComparableResult] = []
        for record in self.repository.load():
            if record.person != person or record.archived:
                continue
            for result in record.laboratory_results:
                if self._normalize_name(result.name) != requested_key:
                    continue
                found.append(
                    _ComparableResult(
                        performed_on=record.performed_on,
                        study_type=record.study_type,
                        result=result,
                        numeric_value=self._decimal(result.value),
                        normalized_unit=self._normalize_unit(result.unit),
                    )
                )
        found.sort(key=lambda item: item.performed_on)
        return found

    def _comparison_warnings(self, results: list[_ComparableResult]) -> list[str]:
        warnings: list[str] = []
        units = {item.normalized_unit for item in results if item.normalized_unit}
        if len(units) > 1:
            warnings.append(
                "Hay unidades diferentes; los valores no deben compararse directamente."
            )
        if any(item.numeric_value is None for item in results):
            warnings.append("Algunos resultados son cualitativos o no numéricos.")
        ranges = {
            item.result.reference_range
            for item in results
            if item.result.reference_range
        }
        if len(ranges) > 1:
            warnings.append(
                "Los rangos de referencia cambian entre registros o laboratorios."
            )
        return warnings

    def _render_result(self, item: _ComparableResult) -> str:
        details = f"{item.result.value} {item.result.unit}".strip()
        reference = item.result.reference_range.strip()
        if reference:
            details += f" · referencia {reference}"
        flag = item.result.flag.strip()
        if flag:
            details += f" · marca {flag}"
        return f"- {item.performed_on} · {details} · {item.study_type}"

    def _normalize_name(self, value: str) -> str:
        folded = self._fold(value)
        return _NAME_ALIASES.get(folded, folded)

    def _normalize_unit(self, value: str) -> str:
        folded = self._fold(value).replace(" ", "")
        return _UNIT_ALIASES.get(folded, folded)

    def _fold(self, value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value.casefold())
        return "".join(char for char in normalized if not unicodedata.combining(char))

    def _decimal(self, value: str) -> Decimal | None:
        candidate = value.strip().replace(" ", "").replace(",", ".")
        try:
            return Decimal(candidate)
        except InvalidOperation:
            return None

    def _split_fields(self, value: str) -> dict[str, str]:
        fields: dict[str, str] = {}
        for part in value.split("|"):
            name, separator, content = part.partition("=")
            if separator:
                fields[name.strip().casefold()] = content.strip()
        return fields
