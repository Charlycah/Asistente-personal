from pathlib import Path

from app.health_result_comparison import HistoricalHealthComparisonService
from app.secure_health_checkups import (
    HealthCheckup,
    HealthCheckupRepository,
    LaboratoryResult,
)


def _service(tmp_path: Path) -> HistoricalHealthComparisonService:
    repository = HealthCheckupRepository(tmp_path / "health_checkups.json")
    return HistoricalHealthComparisonService(repository)


def _save(
    service: HistoricalHealthComparisonService,
    records: list[HealthCheckup],
) -> None:
    service.repository.save(records)


def _laboratory(
    record_id: str,
    person: str,
    performed_on: str,
    name: str,
    value: str,
    unit: str = "mg/dL",
    reference_range: str = "70-110",
) -> HealthCheckup:
    return HealthCheckup(
        record_id=record_id,
        person=person,
        study_type="Análisis de sangre",
        performed_on=performed_on,
        category="laboratorio",
        laboratory_results=[
            LaboratoryResult(
                name=name,
                value=value,
                unit=unit,
                reference_range=reference_range,
            )
        ],
    )


def test_m340_10_ordinary_conversation_is_not_intercepted(tmp_path: Path) -> None:
    result = _service(tmp_path).prepare("contame una historia")

    assert result.handled is False


def test_m340_10_results_are_ordered_chronologically(tmp_path: Path) -> None:
    service = _service(tmp_path)
    _save(
        service,
        [
            _laboratory("new", "Carlos", "2026-07-12", "Glucemia", "96"),
            _laboratory("old", "Carlos", "2021-07-11", "Glucemia", "91"),
        ],
    )

    result = service.prepare(
        "comparar resultados de Carlos: resultado=Glucemia"
    )

    assert result.handled is True
    assert result.response.index("2021-07-11") < result.response.index("2026-07-12")
    assert "no constituye un diagnóstico" in result.response


def test_m340_10_aliases_match_glucose_and_glucemia(tmp_path: Path) -> None:
    service = _service(tmp_path)
    _save(
        service,
        [
            _laboratory("one", "Carlos", "2022-01-01", "Glucosa", "92"),
            _laboratory("two", "Carlos", "2023-01-01", "Glucemia", "94"),
        ],
    )

    result = service.prepare(
        "comparar resultados de Carlos: resultado=Glucemia"
    )

    assert "2022-01-01" in result.response
    assert "2023-01-01" in result.response


def test_m340_10_people_are_never_mixed(tmp_path: Path) -> None:
    service = _service(tmp_path)
    _save(
        service,
        [
            _laboratory("carlos", "Carlos", "2024-01-01", "Glucemia", "90"),
            _laboratory("cristina", "Cristina", "2024-02-01", "Glucemia", "99"),
        ],
    )

    result = service.prepare(
        "comparar resultados de Cristina: resultado=Glucemia"
    )

    assert "2024-02-01" in result.response
    assert "2024-01-01" not in result.response


def test_m340_10_incompatible_units_are_reported(tmp_path: Path) -> None:
    service = _service(tmp_path)
    _save(
        service,
        [
            _laboratory("one", "Carlos", "2024-01-01", "Glucemia", "90"),
            _laboratory(
                "two",
                "Carlos",
                "2025-01-01",
                "Glucemia",
                "5.2",
                unit="mmol/L",
            ),
        ],
    )

    result = service.prepare(
        "comparar resultados de Carlos: resultado=Glucemia"
    )

    assert "unidades diferentes" in result.response


def test_m340_10_narrative_reports_are_listed_by_date(tmp_path: Path) -> None:
    service = _service(tmp_path)
    _save(
        service,
        [
            HealthCheckup(
                record_id="later",
                person="Cristina",
                study_type="Ecografía tiroidea",
                performed_on="2024-05-01",
                category="informe",
                report_text="Informe posterior.",
            ),
            HealthCheckup(
                record_id="earlier",
                person="Cristina",
                study_type="Ecografía tiroidea",
                performed_on="2019-05-20",
                category="informe",
                report_text="Informe anterior.",
            ),
        ],
    )

    result = service.prepare(
        "mostrar informes de Cristina: estudio=Ecografía tiroidea"
    )

    assert result.response.index("2019-05-20") < result.response.index("2024-05-01")
    assert "textos originales" in result.response
