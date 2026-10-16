from datetime import datetime
from pathlib import Path

from app.health_orchestrator import HealthOrchestratorService
from app.secure_health_checkups import HealthCheckupRepository
from app.secure_medication_registry import MedicationRegistryRepository
from app.structured_symptom_registry import (
    StructuredSymptomService,
    SymptomEpisode,
    SymptomRepository,
)
from app.vital_sign_history import VitalSignRepository

NOW = datetime(2026, 7, 28, 17, 0)


def _service(tmp_path: Path) -> StructuredSymptomService:
    return StructuredSymptomService(
        SymptomRepository(tmp_path / "symptoms.json"),
        now=lambda: NOW,
    )


def test_ignores_unrelated_requests(tmp_path: Path) -> None:
    assert not _service(tmp_path).prepare("Contame las noticias").handled


def test_requires_confirmation_and_stores_structured_fields(tmp_path: Path) -> None:
    service = _service(tmp_path)

    prepared = service.prepare(
        "registrar síntoma de Carlos: síntoma=dolor de cabeza | "
        "inicio=2026-07-28T09:00 | intensidad=6 | zona=frente | "
        "duración=dos horas | frecuencia=intermitente | evolución=igual | "
        "agravantes=luz | alivio=descanso | acompañantes=náuseas | "
        "signos=presión 128/82 | medicación=paracetamol | notas=sin golpe",
        session_id="carlos",
    )

    assert prepared.handled
    assert service.repository.load() == []
    confirmed = service.prepare("confirmar síntoma", session_id="carlos")
    episodes = service.repository.load()
    assert "Guardé el episodio" in confirmed.response
    assert len(episodes) == 1
    assert episodes[0].person == "Carlos"
    assert episodes[0].intensity == 6
    assert episodes[0].body_area == "frente"
    assert episodes[0].accompanying_symptoms == "náuseas"


def test_rejects_invalid_intensity_without_creating_pending_change(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)

    result = service.prepare(
        "registrar síntoma de Cristina: síntoma=mareo | intensidad=12"
    )

    assert not result.handled
    assert "No hay" in service.prepare("confirmar síntoma").response


def test_cancellation_and_sessions_are_independent(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.prepare(
        "registrar síntoma de Carlos: síntoma=tos",
        session_id="one",
    )
    service.prepare(
        "registrar síntoma de Cristina: síntoma=fiebre",
        session_id="two",
    )

    service.prepare("cancelar síntoma", session_id="one")
    service.prepare("confirmar síntoma", session_id="two")

    episodes = service.repository.load()
    assert [item.person for item in episodes] == ["Cristina"]


def test_keeps_people_separate_and_excludes_archived_episodes(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    service.repository.save(
        [
            SymptomEpisode("carlos01", "Carlos", "tos", "2026-07-28T09:00"),
            SymptomEpisode(
                "cristi01",
                "Cristina",
                "mareo",
                "2026-07-28T10:00",
            ),
            SymptomEpisode(
                "cristi02",
                "Cristina",
                "fiebre",
                "2026-07-28T11:00",
                archived=True,
            ),
        ]
    )

    response = service.prepare("síntomas activos de Cristina").response

    assert "mareo" in response
    assert "tos" not in response
    assert "fiebre" not in response


def test_updates_evolution_and_closes_disappeared_episode(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.repository.save(
        [SymptomEpisode("abcd1234", "Carlos", "dolor", "2026-07-28T09:00")]
    )

    prepared = service.prepare(
        "actualizar síntoma abcd1234: evolución=desapareció"
    )
    assert "Confirmá la evolución" in prepared.response
    service.prepare("confirmar síntoma")

    episode = service.repository.load()[0]
    assert episode.evolution == "desapareció"
    assert episode.status == "cerrado"
    assert episode.closed_at == "2026-07-28T17:00"


def test_closes_and_archives_only_after_confirmation(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.repository.save(
        [SymptomEpisode("abcd1234", "Carlos", "dolor", "2026-07-28T09:00")]
    )

    service.prepare("cerrar episodio de síntoma abcd1234")
    assert service.repository.load()[0].status == "activo"
    service.prepare("confirmar síntoma")
    assert service.repository.load()[0].status == "cerrado"

    service.prepare("archivar episodio de síntoma abcd1234")
    service.prepare("confirmar síntoma")
    assert service.repository.load()[0].archived


def test_history_filters_by_period(tmp_path: Path) -> None:
    service = _service(tmp_path)
    service.repository.save(
        [
            SymptomEpisode("recent01", "Carlos", "mareo", "2026-07-27T09:00"),
            SymptomEpisode("old00001", "Carlos", "tos", "2026-06-01T09:00"),
        ]
    )

    response = service.prepare(
        "historial de síntomas de Carlos de los últimos 7 días"
    ).response

    assert "mareo" in response
    assert "tos" not in response
    assert "sin interpretación clínica" in response


def test_emits_explicit_alarm_without_diagnosis(tmp_path: Path) -> None:
    service = _service(tmp_path)

    response = service.prepare(
        "registrar síntoma de Cristina: síntoma=dolor de pecho | "
        "acompañantes=falta de aire"
    ).response

    assert "señal de alarma" in response
    assert "asistencia médica inmediata" in response
    assert "diagnóstico" not in response.casefold()


def test_orchestrator_includes_only_active_symptoms(tmp_path: Path) -> None:
    symptoms = SymptomRepository(tmp_path / "symptoms.json")
    symptoms.save(
        [
            SymptomEpisode(
                "active01",
                "Cristina",
                "mareo",
                "2026-07-28T10:00",
                intensity=4,
                evolution="igual",
            ),
            SymptomEpisode(
                "closed01",
                "Cristina",
                "fiebre",
                "2026-07-27T10:00",
                status="cerrado",
            ),
        ]
    )
    service = HealthOrchestratorService(
        MedicationRegistryRepository(tmp_path / "medications.json"),
        HealthCheckupRepository(tmp_path / "checkups.json"),
        now=lambda: NOW,
        vital_repository=VitalSignRepository(tmp_path / "vitals.json"),
        symptom_repository=symptoms,
    )

    response = service.prepare("resumen de salud de Cristina").response

    assert "Síntomas activos" in response
    assert "mareo" in response
    assert "intensidad 4/10" in response
    assert "fiebre" not in response
