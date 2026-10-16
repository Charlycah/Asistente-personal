from __future__ import annotations

import inspect

from app import governed_reasoning_runtime
from core.governed_reasoning.cross_domain_concept_synthesis import (
    GovernedCrossDomainConceptSynthesisCandidate,
)


def test_agrl_3e_requires_novel_synthesis_governed_hypothesis_admission_red() -> None:
    """RED: productive synthesis cannot yet acquire governed hypothesis identity.

    The missing surface must be a read-only admission/projection inside the existing
    governed-reasoning authority. It must preserve synthesis provenance, must not
    treat synthesis as evidence for itself, and must not acquire planning,
    investigation, execution, memory, learning, or background-process authority.
    """

    admission_type_name = "CanonicalNovelSynthesisGovernedHypothesisAdmission"
    admission_method_name = "admit_novel_synthesis_as_governed_hypothesis"

    admission_type = getattr(governed_reasoning_runtime, admission_type_name, None)
    admission_method = getattr(
        governed_reasoning_runtime.OfficialGovernedReasoningRuntimeGateway,
        admission_method_name,
        None,
    )

    assert admission_type is not None, (
        "AGRL-3E RED confirmed: cross-domain synthesis is productively reachable "
        "inside governed reasoning, but no canonical read-only admission preserves "
        "its synthesis provenance while giving it governed hypothesis identity."
    )
    assert admission_method is not None, (
        "AGRL-3E RED confirmed: OfficialGovernedReasoningRuntimeGateway exposes no "
        "productive synthesis-to-hypothesis admission through the existing "
        "governed-reasoning authority."
    )

    signature = inspect.signature(admission_method)
    assert "synthesis" in signature.parameters
    annotation = signature.parameters["synthesis"].annotation
    assert annotation in (
        GovernedCrossDomainConceptSynthesisCandidate,
        "GovernedCrossDomainConceptSynthesisCandidate",
    )

    required_fields = {
        "synthesis_source_fingerprint",
        "source_domain_reference",
        "target_domain_reference",
        "source_concept_episode_id",
        "target_concept_episode_id",
        "hypothesis_candidate",
        "rationale_codes",
        "canonical_authority",
        "read_only",
        "synthesis_origin",
        "registers_synthesis_as_evidence",
        "invokes_planning",
        "invokes_investigation",
        "invokes_execution",
        "creates_memory",
        "creates_learning_candidate",
        "starts_background_process",
        "grants_authority",
    }
    assert required_fields.issubset(admission_type.__dataclass_fields__)

    assert admission_type.__dataclass_fields__["canonical_authority"].default == (
        "governed_reasoning"
    )
    assert admission_type.__dataclass_fields__["read_only"].default is True
    assert admission_type.__dataclass_fields__["synthesis_origin"].default is True

    forbidden_authority_fields = {
        "registers_synthesis_as_evidence",
        "invokes_planning",
        "invokes_investigation",
        "invokes_execution",
        "creates_memory",
        "creates_learning_candidate",
        "starts_background_process",
        "grants_authority",
    }
    for field_name in forbidden_authority_fields:
        assert admission_type.__dataclass_fields__[field_name].default is False
