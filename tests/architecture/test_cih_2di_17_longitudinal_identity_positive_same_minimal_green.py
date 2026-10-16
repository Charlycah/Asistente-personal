from __future__ import annotations

import pytest

from core.governed_reasoning.longitudinal_intellectual_identity import (
    GovernedLongitudinalIntellectualIdentityFoundationV1,
    LongitudinalIntellectualIdentityStatus,
)


def _assess(
    *,
    shared: tuple[str, ...] = (),
    directed: tuple[str, ...] = (),
    relational: tuple[str, ...] = (),
):
    return GovernedLongitudinalIntellectualIdentityFoundationV1().assess(
        current_artifact_reference="artifact-current-b",
        candidate_artifact_reference="artifact-prior-a",
        shared_intellectual_subject_evidence_references=shared,
        directed_prior_state_evidence_references=directed,
        relational_evidence_references=relational,
    )


def test_cih_2di_17_complete_positive_same_composition_is_same() -> None:
    assessment = _assess(
        shared=("shared-subject-evidence-a-b",),
        directed=("directed-prior-state-evidence-b-to-a",),
        relational=("governed-relational-corroboration-a-b",),
    )

    assert assessment.status is LongitudinalIntellectualIdentityStatus.SAME
    assert assessment.rationale_codes == (
        "longitudinal_identity:positive_same_composition_satisfied",
    )
    assert assessment.read_only is True
    assert assessment.consultative is True
    assert assessment.transient is True
    assert assessment.persists is False
    assert assessment.authorizes_revision is False
    assert assessment.executes_actions is False
    assert assessment.grants_authority is False


@pytest.mark.parametrize(
    ("shared", "directed", "relational"),
    (
        (("shared",), (), ()),
        ((), ("directed",), ()),
        ((), (), ("relational",)),
        (("shared",), ("directed",), ()),
        (("shared",), (), ("relational",)),
        ((), ("directed",), ("relational",)),
    ),
)
def test_cih_2di_17_incomplete_positive_composition_is_insufficient(
    shared: tuple[str, ...],
    directed: tuple[str, ...],
    relational: tuple[str, ...],
) -> None:
    assessment = _assess(
        shared=shared,
        directed=directed,
        relational=relational,
    )

    assert assessment.status is LongitudinalIntellectualIdentityStatus.INSUFFICIENT
    assert assessment.status is not LongitudinalIntellectualIdentityStatus.DISTINCT
