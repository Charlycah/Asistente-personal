"""RC-01B isolated tests; no filesystem roots or capabilities are invoked."""
from app.cross_domain_context_resolver import (
    ContextAntecedent,
    ContextDecision,
    ContextDomain,
    resolve_cross_domain_reference,
)


def turn(
    domain, sequence, *, owner="owner", session="s1",
    authorized=True, provenance="runtime"
):
    return ContextAntecedent(
        turn_id=f"turn-{sequence}",
        owner=owner,
        session_id=session,
        domain=domain,
        sequence=sequence,
        provenance=provenance,
        authorized=authorized,
    )


def resolve(text, turns, **kwargs):
    return resolve_cross_domain_reference(
        text,
        turns,
        owner=kwargs.get("owner", "owner"),
        session_id=kwargs.get("session_id", "s1"),
    )


def test_library_follow_up():
    result = resolve(
        "¿Y cuáles son los más recientes?",
        [turn(ContextDomain.LIBRARY, 1)],
    )
    assert (
        result.decision, result.domain, result.antecedent_turn_id
    ) == (
        ContextDecision.CONTINUE, ContextDomain.LIBRARY, "turn-1"
    )


def test_resume_library_after_music():
    turns = [
        turn(ContextDomain.LIBRARY, 1),
        turn(ContextDomain.MUSIC, 2),
    ]
    result = resolve("Volvamos a los libros", turns)
    assert (
        result.decision, result.antecedent_turn_id
    ) == (ContextDecision.RESUME, "turn-1")


def test_recent_music_follow_up():
    turns = [
        turn(ContextDomain.LIBRARY, 1),
        turn(ContextDomain.MUSIC, 2),
    ]
    result = resolve("¿Y otras?", turns)
    assert (
        result.decision, result.domain
    ) == (ContextDecision.CONTINUE, ContextDomain.MUSIC)


def test_documents_reference():
    result = resolve(
        "¿Qué dice el segundo?",
        [turn(ContextDomain.DOCUMENTS, 4)],
    )
    assert result.domain == ContextDomain.DOCUMENTS


def test_development_reference():
    result = resolve(
        "¿Cómo lo mejorarías?",
        [turn(ContextDomain.DEVELOPMENT, 3)],
    )
    assert result.domain == ContextDomain.DEVELOPMENT


def test_explicit_topic_change():
    result = resolve(
        "Cambiemos de tema",
        [turn(ContextDomain.LIBRARY, 1)],
    )
    assert result.decision == ContextDecision.TOPIC_CHANGE


def test_cross_session_excluded():
    result = resolve(
        "¿Y los más recientes?",
        [turn(ContextDomain.LIBRARY, 1, session="other")],
    )
    assert result.decision == ContextDecision.UNRESOLVED


def test_cross_owner_excluded():
    result = resolve(
        "¿Y los más recientes?",
        [turn(ContextDomain.LIBRARY, 1, owner="other")],
    )
    assert result.decision == ContextDecision.UNRESOLVED


def test_unauthorized_excluded():
    result = resolve(
        "¿Y los más recientes?",
        [turn(ContextDomain.LIBRARY, 1, authorized=False)],
    )
    assert result.decision == ContextDecision.UNRESOLVED


def test_missing_provenance_excluded():
    result = resolve(
        "¿Y los más recientes?",
        [turn(ContextDomain.LIBRARY, 1, provenance="")],
    )
    assert result.decision == ContextDecision.UNRESOLVED


def test_ambiguous_domain_reference():
    turns = [
        turn(ContextDomain.LIBRARY, 1),
        turn(ContextDomain.MUSIC, 2),
    ]
    result = resolve(
        "Volvamos a los libros y la música", turns
    )
    assert result.decision == ContextDecision.CLARIFY


def test_unspecified_resume_clarifies():
    result = resolve(
        "Volvamos a eso",
        [turn(ContextDomain.LIBRARY, 1)],
    )
    assert result.decision == ContextDecision.CLARIFY


def test_ambiguous_same_sequence():
    turns = [
        turn(ContextDomain.LIBRARY, 1),
        turn(ContextDomain.MUSIC, 1),
    ]
    result = resolve("¿Y los más recientes?", turns)
    assert result.decision == ContextDecision.CLARIFY


def test_no_reference_no_action():
    result = resolve(
        "Buenas tardes",
        [turn(ContextDomain.LIBRARY, 1)],
    )
    assert result.decision == ContextDecision.UNRESOLVED


def test_no_history():
    result = resolve("¿Y los más recientes?", [])
    assert result.decision == ContextDecision.UNRESOLVED


def test_new_domain_request_is_not_hijacked():
    result = resolve(
        "Mostrame libros de Asimov",
        [turn(ContextDomain.LIBRARY, 1)],
    )
    assert result.decision == ContextDecision.UNRESOLVED

def test_natural_music_followup():
    result = resolve(
        "Seguimos con aquella obra",
        [turn(ContextDomain.MUSIC, 1)],
    )
    assert result.decision == ContextDecision.CONTINUE
    assert result.domain == ContextDomain.MUSIC
    assert result.antecedent_turn_id == "turn-1"

def test_invalid_owner_type():
    antecedent = turn(ContextDomain.LIBRARY, 1)
    from dataclasses import replace
    malformed = replace(antecedent, owner=None)
    result = resolve("¿Y los más recientes?", [malformed])
    assert result.decision == ContextDecision.UNRESOLVED


def test_invalid_turn_id_type():
    antecedent = turn(ContextDomain.LIBRARY, 1)
    from dataclasses import replace
    malformed = replace(antecedent, turn_id=None)
    result = resolve("¿Y los más recientes?", [malformed])
    assert result.decision == ContextDecision.UNRESOLVED


def test_invalid_provenance_type():
    antecedent = turn(ContextDomain.LIBRARY, 1)
    from dataclasses import replace
    malformed = replace(antecedent, provenance=None)
    result = resolve("¿Y los más recientes?", [malformed])
    assert result.decision == ContextDecision.UNRESOLVED
