from __future__ import annotations

import inspect

from core.governed_reasoning.longitudinal_intellectual_identity import (
    GovernedLongitudinalIntellectualIdentityFoundationV1,
    LongitudinalIntellectualIdentityStatus,
)


def test_cih_2di_16_requires_explicit_positive_same_composition_surface_red() -> None:
    """RED: DH.8 cannot yet receive the three non-circular SAME evidence families."""
    parameters = inspect.signature(
        GovernedLongitudinalIntellectualIdentityFoundationV1.assess
    ).parameters

    required = {
        "shared_intellectual_subject_evidence_references",
        "directed_prior_state_evidence_references",
        "relational_evidence_references",
    }

    assert required <= set(parameters), (
        "CIH-2DI.16 RED confirmed: the canonical DH.8 identity owner exists and "
        "already accepts relational evidence, but it cannot yet receive separately "
        "bounded shared-subject and directed-prior-state evidence required by the "
        "positive-SAME V1 composition contract."
    )


def test_cih_2di_16_incomplete_existing_evidence_remains_insufficient() -> None:
    """Existing generic evidence must not become SAME merely because it is present."""
    assessment = GovernedLongitudinalIntellectualIdentityFoundationV1().assess(
        current_artifact_reference="artifact-current-b",
        candidate_artifact_reference="artifact-prior-a",
        identity_evidence_references=("identity-evidence-1",),
        relational_evidence_references=("relational-evidence-1",),
    )

    assert assessment.status is LongitudinalIntellectualIdentityStatus.INSUFFICIENT
    assert assessment.read_only is True
    assert assessment.consultative is True
    assert assessment.transient is True
    assert assessment.persists is False
    assert assessment.authorizes_revision is False
    assert assessment.executes_actions is False
    assert assessment.grants_authority is False
