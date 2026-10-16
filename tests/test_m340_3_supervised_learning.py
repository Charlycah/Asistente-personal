from datetime import datetime, timezone

from app.household_knowledge import HouseholdKnowledgeService

NOW = datetime(2026, 7, 27, 20, 0, tzinfo=timezone.utc)


def service(tmp_path):
    return HouseholdKnowledgeService(str(tmp_path / "knowledge.db"))


def test_learning_requires_confirmation(tmp_path):
    knowledge = service(tmp_path)
    proposed = knowledge.handle("Roby, aprendé que Cristina prefiere té", now=NOW)
    assert proposed.handled
    assert "Propongo aprender" in proposed.response_text
    assert not knowledge.manager.recall("Cristina")
    confirmed = knowledge.handle("confirmar aprendizaje", now=NOW)
    assert "Aprendizaje confirmado" in confirmed.response_text
    assert knowledge.manager.recall("Cristina")


def test_learning_can_be_cancelled(tmp_path):
    knowledge = service(tmp_path)
    knowledge.handle("aprendé que la llave está en el cajón", now=NOW)
    result = knowledge.handle("cancelar aprendizaje", now=NOW)
    assert result.response_text == "Cancelé el aprendizaje pendiente."
    assert not knowledge.manager.recall("llave")


def test_pending_learning_can_be_inspected(tmp_path):
    knowledge = service(tmp_path)
    knowledge.handle("aprendé que el turno es los lunes", now=NOW)
    result = knowledge.handle("qué aprendizaje está pendiente", now=NOW)
    assert "el turno es los lunes" in result.response_text


def test_confirmed_knowledge_can_be_corrected(tmp_path):
    knowledge = service(tmp_path)
    knowledge.handle("aprendé que el service es en marzo", now=NOW)
    knowledge.handle("confirmar aprendizaje", now=NOW)
    proposed = knowledge.handle(
        "corregí el conocimiento service por el service es en abril", now=NOW
    )
    assert "Propongo reemplazar" in proposed.response_text
    knowledge.handle("confirmar aprendizaje", now=NOW)
    assert knowledge.manager.recall("abril")
    assert not knowledge.manager.recall("marzo")


def test_forgetting_requires_confirmation_and_archives(tmp_path):
    knowledge = service(tmp_path)
    knowledge.handle("aprendé que el manual está en la biblioteca", now=NOW)
    knowledge.handle("confirmar aprendizaje", now=NOW)
    proposed = knowledge.handle("olvidá manual", now=NOW)
    assert "Propongo olvidar" in proposed.response_text
    knowledge.handle("confirmar aprendizaje", now=NOW)
    assert not knowledge.manager.recall("manual", status="active")
    assert knowledge.manager.recall("manual", status="archived")


def test_existing_direct_storage_command_remains_compatible(tmp_path):
    knowledge = service(tmp_path)
    result = knowledge.handle("guardá como conocimiento garantía hasta 2028", now=NOW)
    assert "Guardé en el conocimiento" in result.response_text
    assert knowledge.manager.recall("garantía")
