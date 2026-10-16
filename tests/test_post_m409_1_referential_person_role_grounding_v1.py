from datetime import datetime, timezone

from core.conversational_grounding_intelligence import (
    ConversationalGroundingIntelligence,
    ConversationalGroundingRuntimeContributor,
    ConversationGroundingState,
)
from core.llm_provider import LLMRequest
from core.turn_local_person_perspective import (
    PersonPerspectiveEvidenceStatus,
    TurnLocalPersonPerspectiveEvidenceProducer,
)

NOW = datetime(2026, 8, 16, 10, 0, tzinfo=timezone.utc)
PRODUCER = TurnLocalPersonPerspectiveEvidenceProducer()


def test_explicit_third_person_attribution_is_detected() -> None:
    evidence = PRODUCER.analyze("Marta compró un libro.")
    assert evidence.status is PersonPerspectiveEvidenceStatus.THIRD_PERSON_EXPLICIT
    assert evidence.third_person_mentions == ("Marta",)
    assert evidence.supports_referential_grounding is True


def test_coordinated_third_person_mentions_are_preserved() -> None:
    evidence = PRODUCER.analyze("Marta compró un libro y Elena una lámpara.")
    assert evidence.third_person_mentions == ("Marta", "Elena")
    assert evidence.supports_referential_grounding is True


def test_first_person_only_does_not_create_third_person_constraint() -> None:
    evidence = PRODUCER.analyze("Yo compré un libro.")
    assert evidence.status is PersonPerspectiveEvidenceStatus.FIRST_PERSON_ONLY
    assert evidence.third_person_mentions == ()
    assert evidence.supports_referential_grounding is False


def test_implicit_first_person_without_named_third_person_abstains() -> None:
    evidence = PRODUCER.analyze("Compré un libro.")
    assert evidence.status is PersonPerspectiveEvidenceStatus.NO_SIGNAL
    assert evidence.supports_referential_grounding is False


def test_mixed_interlocutor_and_third_person_perspective_is_detected() -> None:
    evidence = PRODUCER.analyze("Marta me llamó.")
    assert evidence.status is PersonPerspectiveEvidenceStatus.MIXED_PERSPECTIVE
    assert evidence.third_person_mentions == ("Marta",)
    assert evidence.first_person_present is True


def test_identity_claims_defer_to_existing_identity_authority() -> None:
    for text in ("Soy Marta.", "Yo soy Marta.", "Me llamo Marta."):
        evidence = PRODUCER.analyze(text)
        assert evidence.status is PersonPerspectiveEvidenceStatus.IDENTITY_CLAIM
        assert evidence.explicit_identity_claim is True
        assert evidence.supports_referential_grounding is False


def test_ambiguous_third_person_pronoun_abstains() -> None:
    evidence = PRODUCER.analyze("Marta dijo que ella compró el libro.")
    assert evidence.status is PersonPerspectiveEvidenceStatus.AMBIGUOUS
    assert evidence.ambiguous_reference is True
    assert evidence.supports_referential_grounding is False


def test_explicit_relationship_is_preserved_without_persistence_authority() -> None:
    evidence = PRODUCER.analyze("Juan es mi hermano.")
    assert evidence.status is PersonPerspectiveEvidenceStatus.MIXED_PERSPECTIVE
    assert evidence.relationship_explicit is True
    assert evidence.creates_relationship is False
    assert evidence.persists_results is False


def test_plain_third_person_location_does_not_infer_relationship() -> None:
    evidence = PRODUCER.analyze("Juan está en Rosario.")
    assert evidence.status is PersonPerspectiveEvidenceStatus.THIRD_PERSON_EXPLICIT
    assert evidence.relationship_explicit is False
    assert "no_relationship_to_interlocutor_established" in evidence.evidence_codes


def test_evidence_is_deterministic_and_non_authoritative() -> None:
    first = PRODUCER.analyze("Marta compró un libro.")
    second = PRODUCER.analyze("Marta compró un libro.")
    assert first == second
    assert first.source_fingerprint == second.source_fingerprint
    assert first.read_only is True
    assert first.transient is True
    assert first.creates_person is False
    assert first.creates_memory is False
    assert first.modifies_identity is False
    assert first.uses_provider is False
    assert first.uses_retrieval is False
    assert first.executes_actions is False
    assert first.grants_authority is False


def test_m198_canonical_state_is_unchanged_by_referential_projection() -> None:
    intelligence = ConversationalGroundingIntelligence()
    assessment = intelligence.assess(
        owner="Carlos",
        session_id="main",
        text="Marta compró un libro.",
        now=NOW,
    )
    assert assessment.state is ConversationGroundingState.ALIGNED
    assert all("Grounding referencial" not in line for line in assessment.prompt_lines)


def test_m198_contributor_adds_single_referential_line_when_supported() -> None:
    contributor = ConversationalGroundingRuntimeContributor(
        ConversationalGroundingIntelligence()
    )
    contribution = contributor.contribute(
        owner="Carlos",
        session_id="main",
        text="Marta compró un libro y Elena una lámpara.",
        request=LLMRequest(prompt="base"),
        now=NOW,
    )
    referential = [
        line
        for line in contribution.prompt_lines
        if line.startswith("Grounding referencial")
    ]
    assert len(referential) == 1
    assert "terceras personas" in referential[0]
    assert len(contribution.reference_ids) == 2


def test_m198_contributor_does_not_project_on_identity_claim_or_ambiguity() -> None:
    contributor = ConversationalGroundingRuntimeContributor(
        ConversationalGroundingIntelligence()
    )
    for text in ("Soy Marta.", "Marta dijo que ella compró el libro."):
        contribution = contributor.contribute(
            owner="Carlos",
            session_id="main",
            text=text,
            request=LLMRequest(prompt="base"),
            now=NOW,
        )
        assert all(
            "Grounding referencial" not in line for line in contribution.prompt_lines
        )
        assert len(contribution.reference_ids) == 1
