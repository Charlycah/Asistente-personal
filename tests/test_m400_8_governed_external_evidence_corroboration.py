from dataclasses import replace
from datetime import timedelta
from pathlib import Path

import pytest

from core.governed_external_intelligence import (
    ExternalEvidenceCorroborationItem,
    ExternalEvidenceCorroborationStatus,
    ExternalEvidenceStance,
    GovernedExternalEvidenceAssessor,
    GovernedExternalEvidenceCorroborator,
    GovernedExternalIntelligenceVerifier,
)
from tests.test_m400_5_governed_external_intelligence_provenance_verification import (
    _provider_envelope,
)
from tests.test_m400_7_governed_external_evidence_assessment import (
    _traced_source_envelope,
)


def _assessed(envelope):
    verification = GovernedExternalIntelligenceVerifier().verify(envelope)
    assessment = GovernedExternalEvidenceAssessor().assess(
        envelope,
        verification,
        assessed_at=envelope.provenance.observed_at + timedelta(minutes=5),
    )
    return verification, assessment


def _item(envelope, stance, proposition_id="prop-1"):
    verification, assessment = _assessed(envelope)
    return ExternalEvidenceCorroborationItem(
        proposition_id=proposition_id,
        envelope=envelope,
        verification=verification,
        assessment=assessment,
        stance=stance,
    )


def test_m400_8_two_independent_supports_are_corroborated() -> None:
    provider = _provider_envelope()
    source = _traced_source_envelope()
    result = GovernedExternalEvidenceCorroborator().corroborate(
        (
            _item(provider, ExternalEvidenceStance.SUPPORT),
            _item(source, ExternalEvidenceStance.SUPPORT),
        )
    )
    assert result.status is ExternalEvidenceCorroborationStatus.CORROBORATED
    assert set(result.independent_actors) == {"nasa", "ollama"}
    assert len(result.supporting_envelopes) == 2
    assert result.contradicting_envelopes == ()
    assert result.truth_certified is False
    assert result.cognitive_authority_granted is False


def test_m400_8_two_independent_contradictions_are_contradicted() -> None:
    result = GovernedExternalEvidenceCorroborator().corroborate(
        (
            _item(_provider_envelope(), "contradict"),
            _item(_traced_source_envelope(), "contradict"),
        )
    )
    assert result.status is ExternalEvidenceCorroborationStatus.CONTRADICTED
    assert len(result.contradicting_envelopes) == 2
    assert "majority_does_not_certify_truth" in result.checks


def test_m400_8_support_and_contradiction_are_mixed() -> None:
    result = GovernedExternalEvidenceCorroborator().corroborate(
        (
            _item(_provider_envelope(), "support"),
            _item(_traced_source_envelope(), "contradict"),
        )
    )
    assert result.status is ExternalEvidenceCorroborationStatus.MIXED
    assert "credible_evidence_is_in_conflict" in result.limitations
    assert result.truth_certified is False


def test_m400_8_one_actor_is_insufficient() -> None:
    provider = _provider_envelope()
    verification, assessment = _assessed(provider)
    duplicate_actor = replace(
        provider,
        request=replace(provider.request, request_id="second-ollama"),
        envelope_id="",
    )
    duplicate_verification = GovernedExternalIntelligenceVerifier().verify(
        duplicate_actor
    )
    duplicate_assessment = GovernedExternalEvidenceAssessor().assess(
        duplicate_actor,
        duplicate_verification,
        assessed_at=(
            duplicate_actor.provenance.observed_at + timedelta(minutes=5)
        ),
    )
    result = GovernedExternalEvidenceCorroborator().corroborate(
        (
            ExternalEvidenceCorroborationItem(
                "prop-1",
                provider,
                verification,
                assessment,
                "support",
            ),
            ExternalEvidenceCorroborationItem(
                "prop-1",
                duplicate_actor,
                duplicate_verification,
                duplicate_assessment,
                "support",
            ),
        )
    )
    assert result.status is ExternalEvidenceCorroborationStatus.INSUFFICIENT
    assert result.independent_actors == ("ollama",)
    assert "independent_corroboration_is_insufficient" in result.limitations


def test_m400_8_single_evidence_is_insufficient() -> None:
    result = GovernedExternalEvidenceCorroborator().corroborate(
        (_item(_provider_envelope(), "support"),)
    )
    assert result.status is ExternalEvidenceCorroborationStatus.INSUFFICIENT


def test_m400_8_rejected_evidence_cannot_corroborate() -> None:
    envelope = _provider_envelope()
    rejected = replace(envelope, status="rejected", envelope_id="")
    verification = GovernedExternalIntelligenceVerifier().verify(rejected)
    assessment = GovernedExternalEvidenceAssessor().assess(
        rejected,
        verification,
        assessed_at=rejected.provenance.observed_at + timedelta(minutes=1),
    )
    item = ExternalEvidenceCorroborationItem(
        "prop-1",
        rejected,
        verification,
        assessment,
        "support",
    )
    result = GovernedExternalEvidenceCorroborator().corroborate((item,))
    assert result.status is ExternalEvidenceCorroborationStatus.REJECTED
    assert result.aggregate_confidence == 0.0


def test_m400_8_items_require_same_explicit_proposition() -> None:
    with pytest.raises(ValueError, match="share proposition"):
        GovernedExternalEvidenceCorroborator().corroborate(
            (
                _item(_provider_envelope(), "support", "prop-a"),
                _item(_traced_source_envelope(), "support", "prop-b"),
            )
        )


def test_m400_8_rejects_duplicate_evidence() -> None:
    item = _item(_provider_envelope(), "support")
    with pytest.raises(ValueError, match="evidence must be unique"):
        GovernedExternalEvidenceCorroborator().corroborate((item, item))


def test_m400_8_item_requires_consistent_lineage() -> None:
    envelope = _provider_envelope()
    verification, assessment = _assessed(envelope)
    with pytest.raises(ValueError, match="verification lineage mismatch"):
        ExternalEvidenceCorroborationItem(
            "prop-1",
            envelope,
            replace(verification, envelope_id="other", verification_id=""),
            assessment,
            "support",
        )


def test_m400_8_result_is_deterministic_for_same_inputs() -> None:
    items = (
        _item(_provider_envelope(), "support"),
        _item(_traced_source_envelope(), "support"),
    )
    corroborator = GovernedExternalEvidenceCorroborator()
    first = corroborator.corroborate(items)
    second = corroborator.corroborate(items)
    assert first == second
    assert first.corroboration_id == second.corroboration_id


def test_m400_8_corroborator_has_no_external_execution_or_authority() -> None:
    corroborator = GovernedExternalEvidenceCorroborator()
    assert corroborator.corroborator_id == (
        "external_intelligence_evidence_corroborator"
    )
    assert not hasattr(corroborator, "authority_id")
    source = Path(
        "core/governed_external_intelligence/corroboration.py"
    ).read_text(encoding="utf-8")
    for forbidden in (
        ".generate(",
        ".execute(",
        "GovernedProviderRouter(",
        "NasaGovernedSourceAdapter(",
        "urlopen",
        "requests.",
    ):
        assert forbidden not in source


def test_m400_8_documentation_and_governance_are_synchronized() -> None:
    root = Path(__file__).resolve().parents[1]
    document = (
        root / "docs/M400_8_GOVERNED_EXTERNAL_EVIDENCE_CORROBORATION.md"
    ).read_text(encoding="utf-8")
    assert "corroboración ≠ verdad certificada" in document
    assert "mayoría ≠ verdad" in document
    assert "independencia de actor ≠ independencia epistemológica" in document
    assert "no consulta nuevas fuentes" in document
    assert "Milestone M400.8 — Governed External Evidence Corroboration" in (
        root / "README.md"
    ).read_text(encoding="utf-8")
    assert "M400.8 — Governed External Evidence Corroboration" in (
        root / "CHANGELOG.md"
    ).read_text(encoding="utf-8")
    assert "M400.8 — Regla de corroboración gobernada de evidencia externa" in (
        root / "architecture_rules.md"
    ).read_text(encoding="utf-8")
