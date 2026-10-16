from __future__ import annotations

import json
from dataclasses import asdict
from enum import Enum
from pathlib import Path, PurePosixPath

from .models import (
    DiagnosticProofResult,
    DiagnosticProofSpecification,
    DiagnosticProofStatus,
    DiagnosticProposal,
    DiagnosticProposalRequest,
    DiagnosticProposalStatus,
)

PROPOSAL_REVIEW_ROOT = PurePosixPath(".roby/review/proposals")


def _prepare_isolated_proposal(
    proof: DiagnosticProofSpecification,
    result: DiagnosticProofResult,
    request: DiagnosticProposalRequest,
) -> DiagnosticProposal:
    """Freeze an explicit remediation intent without applying any change."""

    if result.proof_id != proof.proof_id:
        raise ValueError("diagnostic proposal proof result must match proof")
    if result.hypothesis_id != proof.hypothesis.hypothesis_id:
        raise ValueError("diagnostic proposal hypothesis must match proof")
    if result.status is not DiagnosticProofStatus.REPRODUCED:
        raise ValueError("diagnostic proposal requires reproduced proof")
    if result.evidence_digest != proof.evidence_digest:
        raise ValueError("diagnostic proposal evidence digest must match proof")

    proposal_path = PROPOSAL_REVIEW_ROOT / request.proposal_id / "proposal.json"
    return DiagnosticProposal(
        proposal_id=request.proposal_id,
        status=DiagnosticProposalStatus.DRAFT,
        proof_id=proof.proof_id,
        hypothesis_id=proof.hypothesis.hypothesis_id,
        source_authority=proof.source_authority,
        metric=proof.metric,
        evidence_digest=proof.evidence_digest,
        title=request.title,
        change_intent=request.change_intent,
        affected_files=request.affected_files,
        validation_tests=request.validation_tests,
        risk_notes=request.risk_notes,
        review_path=proposal_path.as_posix(),
        rationale=(
            "proposal_derived_from_reproduced_diagnostic_proof",
            "remediation_intent_was_explicit_not_inferred",
            "proposal_is_isolated_from_operational_code",
            "proposal_does_not_authorize_application",
            "human_decision_required_before_any_change",
            "prediction_is_not_certainty",
        ),
    )


def _write_isolated_proposal(
    proposal: DiagnosticProposal,
    *,
    project_root: Path,
) -> Path:
    """Persist only the inert proposal artifact under the governed review root."""

    root = project_root.resolve()
    review_root = (root / PROPOSAL_REVIEW_ROOT).resolve()
    destination = (root / proposal.review_path).resolve()
    try:
        destination.relative_to(review_root)
    except ValueError as exc:
        raise ValueError("diagnostic proposal must remain inside review root") from exc
    if destination.exists():
        raise FileExistsError("diagnostic proposal artifact already exists")

    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = _json_safe(asdict(proposal))
    destination.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return destination


def _json_safe(value: object) -> object:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value
