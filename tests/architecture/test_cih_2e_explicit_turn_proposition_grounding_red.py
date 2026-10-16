from core.governed_reasoning import (
    ExplicitTurnPropositionGroundingStatus,
    GovernedBoundedExplicitTurnPropositionGrounder,
)

GROUNDER = GovernedBoundedExplicitTurnPropositionGrounder()
SOURCE = "conversation:cih-2e/turn:test"
SCOPE = "session:cih-2e"


def _ground(text: str):
    return GROUNDER.ground(
        text,
        source_reference=SOURCE,
        scope_reference=SCOPE,
    )


def test_witness_turn_projects_only_explicit_bounded_propositions() -> None:
    text = "Mañana viene alguien a casa y todavía me falta organizar varias cosas."

    result = _ground(text)

    assert result.status is ExplicitTurnPropositionGroundingStatus.GROUNDED
    assert result.canonical_authority == "governed_reasoning"
    assert result.read_only is True
    assert result.session_local is True
    assert result.transient is True
    assert result.establishes_truth is False
    assert result.persists_results is False
    assert result.registers_claims is False
    assert result.authorizes_inference is False
    assert result.executes_actions is False
    assert result.grants_authority is False
    assert len(result.propositions) == 2

    first, second = result.propositions
    assert (first.subject, first.predicate, first.object_value) == (
        "alguien",
        "viene_a_casa",
        "mañana",
    )
    assert first.source_text == "Mañana viene alguien a casa"
    assert text[first.start_offset : first.end_offset] == first.source_text

    assert (second.subject, second.predicate, second.object_value) == (
        "interlocutor",
        "falta_organizar",
        "varias cosas",
    )
    assert second.source_text == "todavía me falta organizar varias cosas"
    assert text[second.start_offset : second.end_offset] == second.source_text


def test_question_is_not_projected_as_assertion() -> None:
    result = _ground("¿Mañana viene alguien a casa?")
    assert result.status is ExplicitTurnPropositionGroundingStatus.UNSUPPORTED
    assert result.propositions == ()


def test_supposition_is_not_projected_as_assertion() -> None:
    result = _ground("Supongamos que mañana viene alguien a casa.")
    assert result.status is ExplicitTurnPropositionGroundingStatus.UNSUPPORTED
    assert result.propositions == ()


def test_ambiguous_person_reference_fails_closed() -> None:
    result = _ground("Ella viene mañana.")
    assert result.status is ExplicitTurnPropositionGroundingStatus.AMBIGUOUS
    assert result.propositions == ()


def test_blank_turn_is_insufficient() -> None:
    result = _ground("   ")
    assert result.status is ExplicitTurnPropositionGroundingStatus.INSUFFICIENT
    assert result.propositions == ()
