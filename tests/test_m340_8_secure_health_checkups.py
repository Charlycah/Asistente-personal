from pathlib import Path

from app.secure_health_checkups import (
    HealthCheckupRepository,
    SecureHealthCheckupService,
)


def _service(tmp_path: Path) -> SecureHealthCheckupService:
    repository = HealthCheckupRepository(tmp_path / "health_checkups.json")
    return SecureHealthCheckupService(repository)


def test_m340_8_ordinary_conversation_is_not_intercepted(tmp_path: Path) -> None:
    result = _service(tmp_path).prepare("contame una historia")

    assert result.handled is False


def test_m340_8_laboratory_results_require_confirmation(tmp_path: Path) -> None:
    service = _service(tmp_path)
    result = service.prepare(
        "registrar chequeo de Carlos: estudio=Análisis de sangre | "
        "fecha=2026-07-12 | resultados=Glucemia~96~mg/dL~70-110~normal; "
        "TSH~2.1~uUI/mL~0.4-4.0~normal",
        session_id="carlos",
    )

    assert result.handled is True
    assert "2 resultados estructurados" in result.response
    assert service.repository.load() == []


def test_m340_8_confirmed_laboratory_results_are_structured(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    service.prepare(
        "registrar chequeo de Carlos: estudio=Análisis de sangre | "
        "fecha=2026-07-12 | institución=Laboratorio Central | "
        "resultados=Glucemia~96~mg/dL~70-110~normal",
        session_id="carlos",
    )

    confirmation = service.prepare("confirmar chequeo", session_id="carlos")
    records = service.repository.load()

    assert confirmation.handled is True
    assert len(records) == 1
    assert records[0].person == "Carlos"
    assert records[0].laboratory_results[0].name == "Glucemia"
    assert records[0].laboratory_results[0].reference_range == "70-110"


def test_m340_8_narrative_report_is_kept_separate(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.prepare(
        "registrar chequeo de Cristina: estudio=Ecografía tiroidea | "
        "fecha=2026-06-03 | informe=Tiroides de tamaño conservado.",
        session_id="cristina",
    )
    service.prepare("confirmar chequeo", session_id="cristina")

    record = service.repository.load()[0]

    assert record.person == "Cristina"
    assert record.category == "informe"
    assert record.report_text == "Tiroides de tamaño conservado."
    assert record.laboratory_results == []


def test_m340_8_profiles_are_listed_without_mixing(tmp_path: Path) -> None:
    service = _service(tmp_path)
    for person in ("Carlos", "Cristina"):
        service.prepare(
            f"registrar chequeo de {person}: estudio=Radiografía de tórax | "
            "fecha=2026-05-01 | informe=Sin hallazgos agudos.",
            session_id=person,
        )
        service.prepare("confirmar chequeo", session_id=person)

    result = service.prepare("mostrar chequeos de Carlos")

    assert "Carlos" in result.response
    assert "Cristina" not in result.response
    assert result.response.count("Radiografía de tórax") == 1


def test_m340_8_records_can_be_archived_and_deleted(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.prepare(
        "registrar chequeo de Carlos: estudio=Ecoestrés | "
        "fecha=2026-04-09 | informe=Informe cardiológico.",
        session_id="carlos",
    )
    service.prepare("confirmar chequeo", session_id="carlos")
    record_id = service.repository.load()[0].record_id

    archived = service.prepare(f"archivar chequeo {record_id}")
    listed = service.prepare("listar chequeos de Carlos")
    deleted = service.prepare(f"eliminar chequeo {record_id}")

    assert "Archivé" in archived.response
    assert "No hay chequeos activos" in listed.response
    assert "Eliminé definitivamente" in deleted.response
    assert service.repository.load() == []
