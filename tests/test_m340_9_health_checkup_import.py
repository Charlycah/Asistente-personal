from pathlib import Path

from app.health_checkup_import import AssistedHealthCheckupImportService
from app.secure_health_checkups import HealthCheckupRepository


def _service(tmp_path: Path) -> AssistedHealthCheckupImportService:
    repository = HealthCheckupRepository(tmp_path / "health_checkups.json")
    return AssistedHealthCheckupImportService(repository)


def test_m340_9_ordinary_conversation_is_not_intercepted(tmp_path: Path) -> None:
    result = _service(tmp_path).prepare("contame una historia")

    assert result.handled is False


def test_m340_9_laboratory_import_requires_review(tmp_path: Path) -> None:
    source = tmp_path / "laboratorio.txt"
    source.write_text(
        "Glucemia | 96 | mg/dL | 70-110 | normal\n"
        "TSH | 2.1 | uUI/mL | 0.4-4.0 | normal",
        encoding="utf-8",
    )
    service = _service(tmp_path)

    result = service.prepare(
        f"importar chequeo de Carlos: archivo={source} | "
        "estudio=Análisis de sangre | fecha=2022-08-15 | tipo=laboratorio",
        session_id="carlos",
    )

    assert result.handled is True
    assert "2 resultados detectados" in result.response
    assert service.repository.load() == []


def test_m340_9_confirmed_laboratory_import_is_structured(tmp_path: Path) -> None:
    source = tmp_path / "laboratorio.txt"
    source.write_text(
        "Glucemia | 96 | mg/dL | 70-110 | normal",
        encoding="utf-8",
    )
    service = _service(tmp_path)
    service.prepare(
        f"importar chequeo de Carlos: archivo={source} | "
        "estudio=Análisis de sangre | fecha=2021-07-11 | tipo=laboratorio",
        session_id="carlos",
    )

    confirmation = service.prepare(
        "confirmar importación",
        session_id="carlos",
    )
    record = service.repository.load()[0]

    assert "Guardé la importación" in confirmation.response
    assert record.performed_on == "2021-07-11"
    assert record.laboratory_results[0].name == "Glucemia"
    assert record.laboratory_results[0].unit == "mg/dL"


def test_m340_9_narrative_report_preserves_original_text(tmp_path: Path) -> None:
    source = tmp_path / "ecografia.txt"
    source.write_text(
        "Tiroides de tamaño conservado. Sin nódulos dominantes.",
        encoding="utf-8",
    )
    service = _service(tmp_path)
    service.prepare(
        f"importar chequeo de Cristina: archivo={source} | "
        "estudio=Ecografía tiroidea | fecha=2019-05-20 | tipo=informe",
        session_id="cristina",
    )
    service.prepare("confirmar importación", session_id="cristina")

    record = service.repository.load()[0]

    assert record.person == "Cristina"
    assert record.report_text == source.read_text(encoding="utf-8")
    assert record.source_file == str(source.resolve())


def test_m340_9_unrecognized_lines_are_reported(tmp_path: Path) -> None:
    source = tmp_path / "laboratorio.txt"
    source.write_text(
        "Encabezado del laboratorio\nGlucemia | 96 | mg/dL | 70-110 | normal",
        encoding="utf-8",
    )
    service = _service(tmp_path)

    result = service.prepare(
        f"importar chequeo de Carlos: archivo={source} | "
        "estudio=Laboratorio | fecha=2020-01-02 | tipo=laboratorio"
    )

    assert "1 líneas requieren revisión" in result.response


def test_m340_9_import_can_be_cancelled(tmp_path: Path) -> None:
    source = tmp_path / "informe.txt"
    source.write_text("Informe narrativo.", encoding="utf-8")
    service = _service(tmp_path)
    service.prepare(
        f"importar chequeo de Carlos: archivo={source} | "
        "estudio=Radiografía | fecha=2018-03-04 | tipo=informe"
    )

    cancelled = service.prepare("cancelar importación")

    assert "no guardé datos" in cancelled.response
    assert service.repository.load() == []
