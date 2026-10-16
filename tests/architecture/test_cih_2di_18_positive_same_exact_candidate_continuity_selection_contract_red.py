from __future__ import annotations

import hashlib
import importlib
import importlib.util
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

from core.governed_reasoning.longitudinal_intellectual_identity import (
    GovernedLongitudinalIntellectualIdentityFoundationV1,
    LongitudinalIntellectualIdentityStatus,
)

ROOT = Path(__file__).resolve().parents[2]
REASONING_RUNTIME = ROOT / "app/governed_reasoning_runtime.py"
CERTIFIED_REASONING_SHA256 = (
    "f8c96d92c08fff1b9219afd68974b79ba319f087b2fb32fbb20d5856aaa91f2f"
)
CONSUMER_MODULE = "app.positive_same_explanatory_model_continuity_consumer"


def _same_assessment(*, candidate_reference: str = "model-prior-a"):
    return GovernedLongitudinalIntellectualIdentityFoundationV1().assess(
        current_artifact_reference="artifact-current-b",
        candidate_artifact_reference=candidate_reference,
        shared_intellectual_subject_evidence_references=("shared-subject-a-b",),
        directed_prior_state_evidence_references=("directed-prior-b-to-a",),
        relational_evidence_references=("relational-corroboration-a-b",),
    )


def _consumer_class():
    module = importlib.import_module(CONSUMER_MODULE)
    return module.PositiveSameExplanatoryModelContinuityConsumerV1


def _candidate(model_id: str):
    return SimpleNamespace(model=SimpleNamespace(model_id=model_id))


def test_cih_2di_18_residual_requires_explicit_positive_same_consumer() -> None:
    assert importlib.util.find_spec(CONSUMER_MODULE) is not None, (
        "CIH-2DI.18 RED: no productive consumer exists yet for the bounded "
        "SAME -> exact-candidate continuity-selection consequence"
    )


@pytest.fixture(autouse=True)
def _require_residual_surface(request: pytest.FixtureRequest):
    if request.node.name == (
        "test_cih_2di_18_residual_requires_explicit_positive_same_consumer"
    ):
        return
    if importlib.util.find_spec(CONSUMER_MODULE) is None:
        pytest.skip("CIH-2DI.18 RED residual surface is intentionally absent")


def test_cih_2di_18_same_selects_only_exact_bounded_candidate() -> None:
    assessment = _same_assessment(candidate_reference="model-prior-a")
    result = _consumer_class()().consume(
        assessment=assessment,
        bounded_candidate=_candidate("model-prior-a"),
    )

    assert result is not None
    assert result.candidate_model_id == "model-prior-a"
    assert result.assessment_id == assessment.assessment_id
    assert result.selection_status == "selected_continuous_prior"


def test_cih_2di_18_same_candidate_mismatch_fails_closed() -> None:
    result = _consumer_class()().consume(
        assessment=_same_assessment(candidate_reference="model-prior-a"),
        bounded_candidate=_candidate("model-other-b"),
    )

    assert result is None


def test_cih_2di_18_non_same_does_not_select_or_expand_semantics() -> None:
    same = _same_assessment()
    consumer = _consumer_class()()

    for status in (
        LongitudinalIntellectualIdentityStatus.INSUFFICIENT,
        LongitudinalIntellectualIdentityStatus.DISTINCT,
        LongitudinalIntellectualIdentityStatus.AMBIGUOUS,
    ):
        assessment = replace(same, status=status)
        assert consumer.consume(
            assessment=assessment,
            bounded_candidate=_candidate("model-prior-a"),
        ) is None


def test_cih_2di_18_selection_remains_transient_and_non_revisional() -> None:
    assessment = _same_assessment()
    result = _consumer_class()().consume(
        assessment=assessment,
        bounded_candidate=_candidate("model-prior-a"),
    )

    assert result is not None
    assert result.read_only is True
    assert result.consultative is True
    assert result.transient is True
    assert result.persists is False
    assert result.creates_learning is False
    assert result.modifies_memory is False
    assert result.modifies_world_model is False
    assert result.opens_investigation is False
    assert result.authorizes_revision is False
    assert result.creates_initiative is False
    assert result.executes_actions is False
    assert result.grants_authority is False


def test_cih_2di_18_consumer_does_not_own_revision_or_candidate_discovery() -> None:
    consumer = _consumer_class()()

    assert not hasattr(consumer, "revision_authority")
    assert not hasattr(consumer, "revision_registry")
    assert not hasattr(consumer, "candidate_search")
    assert not hasattr(consumer, "candidate_discovery")


def test_cih_2di_18_preserves_certified_reasoning_runtime_byte_identical() -> None:
    assert hashlib.sha256(REASONING_RUNTIME.read_bytes()).hexdigest() == (
        CERTIFIED_REASONING_SHA256
    )
