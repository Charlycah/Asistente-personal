from __future__ import annotations

import importlib
import inspect
from datetime import datetime, timezone

import pytest

from app.governed_reasoning_runtime import (
    GovernedCreativeCandidateCriticalDisposition,
    GovernedCreativeCandidateCriticalDispositionStatus,
)
from domain.governed_proposal import GovernedProposal, ProposalState
from domain.governed_proposal_inbox import GovernedProposalInbox

SEAM_MODULE = "app.governed_creative_disposition_proposal_projection"
SEAM_TYPE = "GovernedCreativeDispositionProposalProjection"
NOW = datetime(2026, 10, 4, 19, 30, tzinfo=timezone.utc)
FINGERPRINT = "a" * 64


def _disposition() -> GovernedCreativeCandidateCriticalDisposition:
    return GovernedCreativeCandidateCriticalDisposition(
        disposition_id="creative-candidate-disposition-e1b-contract-red",
        status=GovernedCreativeCandidateCriticalDispositionStatus.REVIEW_REQUIRED,
        synthesis_source_fingerprint=FINGERPRINT,
        hypothesis_candidate_id="governed-hypothesis-candidate-e1b",
        hypothesis_source_claim_fingerprint=FINGERPRINT,
        critical_evaluation_reference_ids=(),
        rationale_codes=(
            "creative_candidate:tentative_hypothesis_preserved",
            "creative_candidate:independent_evidence_required",
            "creative_candidate:proposal_boundary_not_entered",
        ),
    )


def test_red_creative_disposition_to_existing_proposal_reachability_contract() -> None:
    """RED: explicit human promotion reaches only existing Proposal authorities."""
    try:
        module = importlib.import_module(SEAM_MODULE)
    except ModuleNotFoundError:
        pytest.fail(
            "RED: the exact E1-A creative critical disposition has no bounded "
            "explicit-human-promotion projection into the existing Proposal stack"
        )

    seam_type = getattr(module, SEAM_TYPE, None)
    assert seam_type is not None, "RED: bounded creative Proposal projection missing"

    source = inspect.getsource(seam_type)
    lowered = source.casefold()

    # The projection is subordinate: existing Proposal authorities remain canonical.
    assert "GovernedProposalModel" in source
    assert "GovernedProposalInbox" in source
    assert "GovernedProposal(" not in source
    assert "ProposalState.PENDING" not in source

    inbox = GovernedProposalInbox()
    model = importlib.import_module("domain.governed_proposal").GovernedProposalModel()
    projector = seam_type(proposal_model=model, proposal_inbox=inbox)
    disposition = _disposition()

    # REVIEW_REQUIRED is not proposal-creation authorization by itself.
    assert disposition.read_only is True
    assert disposition.creates_proposal is False
    assert projector.promote(
        disposition=disposition,
        session_id="session-e1b",
        human_confirmation=False,
        promotion_attempt_id="attempt-e1b-no-confirmation",
        observed_at=NOW,
    ) is None
    assert inbox.snapshot.total_proposals == 0

    # Exact explicit human promotion delegates creation/admission to existing owners.
    proposal = projector.promote(
        disposition=disposition,
        session_id="session-e1b",
        human_confirmation=True,
        promotion_attempt_id="attempt-e1b-confirmed",
        observed_at=NOW,
    )
    assert isinstance(proposal, GovernedProposal)
    assert proposal.state is ProposalState.PENDING
    assert inbox.find(proposal.proposal_id) is proposal

    metadata = proposal.metadata
    assert metadata["disposition_id"] == disposition.disposition_id
    assert metadata["synthesis_source_fingerprint"] == FINGERPRINT
    assert metadata["hypothesis_candidate_id"] == disposition.hypothesis_candidate_id
    assert metadata["hypothesis_source_claim_fingerprint"] == FINGERPRINT
    assert metadata["disposition_status"] == "review_required"
    assert metadata["canonical_source_authority"] == "governed_reasoning"
    assert metadata["independent_evidence_required"] == "true"
    assert "proposal_boundary_not_entered" in metadata["rationale_codes"]

    # Replay of one promotion attempt cannot create a duplicate proposal.
    replay = projector.promote(
        disposition=disposition,
        session_id="session-e1b",
        human_confirmation=True,
        promotion_attempt_id="attempt-e1b-confirmed",
        observed_at=NOW,
    )
    assert replay is proposal
    assert inbox.snapshot.total_proposals == 1

    # Translation only: no downstream authority may be acquired here.
    forbidden = (
        "governedproposallifecycle",
        ".accept(",
        ".dismiss(",
        "planning",
        "authorization",
        "execution",
        "officialmemorygateway",
        "knowledge",
        "learning",
        "subprocess",
        "requests.",
        "self_modif",
        "relevanceevaluator",
        "should_share",
    )
    assert not any(token in lowered for token in forbidden)


def test_red_productive_composition_must_reuse_gateway_proposal_instances() -> None:
    """RED: official composition reuses the gateway's canonical Proposal owners."""
    composition_module = importlib.import_module("app.official_runtime_composition")
    composition_source = inspect.getsource(
        composition_module.build_official_runtime_from_environment
    )

    assert "GovernedCreativeDispositionProposalProjection" in composition_source
    assert "proposal_model=conversation._governed_proposal_model" in composition_source
    assert "proposal_inbox=conversation._governed_proposal_inbox" in composition_source
