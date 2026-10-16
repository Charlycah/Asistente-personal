"""RED-only contract for bounded, Owner-authorized experimental acquisition.

The future pure validation seam is deliberately absent in RED. No downloads.
"""

from __future__ import annotations

import importlib
import inspect
from dataclasses import replace

MODULE = "core.cognitive_memory_neural_acquisition_authorization_contract"


def _contract():
    return importlib.import_module(MODULE)


def _request(contract):
    return contract.AcquisitionAuthorizationRequest(
        request_id="synthetic-request-1",
        requester="owner",
        approving_owner="owner",
        decision_timestamp="2026-10-09T12:00:00Z",
        expires_at="2026-10-09T13:00:00Z",
        action="MODEL_ACQUISITION",
        repository="BAAI/bge-reranker-v2-m3",
        revision="a" * 40,
        license_id="Apache-2.0",
        license_evidence="revision-bound-synthetic-evidence",
        sources=("https://huggingface.co/BAAI/bge-reranker-v2-m3",),
        artifacts=("config.json", "tokenizer.json", "model.safetensors"),
        destination="isolated/model-evaluation",
        max_bytes=1_000_000_000,
        max_files=3,
        timeout_seconds=60,
        retry_limit=0,
        privacy_public_only=True,
        evidence_ledger="isolated/evidence.json",
    )


def _approval(contract):
    return contract.OwnerAcquisitionApproval(
        request_id="synthetic-request-1",
        owner="owner",
        decision="APPROVE",
        signed_evidence="synthetic-owner-attestation",
        revoked=False,
    )


def test_acquisition_red_requires_explicit_matching_owner_approval():
    contract = _contract()
    request = _request(contract)
    assert contract.acquisition_authorization_decision(request, None) == "DENY"
    assert (
        contract.acquisition_authorization_decision(
            request, replace(_approval(contract), request_id="other")
        )
        == "DENY"
    )
    assert (
        contract.acquisition_authorization_decision(request, _approval(contract))
        == "ELIGIBLE_FOR_SEPARATE_OWNER_INVOKED_ACQUISITION"
    )


def test_acquisition_red_rejects_expired_revoked_or_forged_approval():
    contract = _contract()
    request = _request(contract)
    approval = _approval(contract)
    assert (
        contract.acquisition_authorization_decision(
            request, replace(approval, revoked=True)
        )
        == "DENY"
    )
    assert (
        contract.acquisition_authorization_decision(
            request, replace(approval, signed_evidence="")
        )
        == "DENY"
    )
    assert (
        contract.acquisition_authorization_decision(
            replace(request, expires_at="2026-10-09T11:00:00Z"), approval
        )
        == "DENY"
    )


def test_acquisition_red_rejects_moving_revision_and_license_gap():
    contract = _contract()
    request = _request(contract)
    approval = _approval(contract)
    for changed in (
        replace(request, revision="main"),
        replace(request, revision="b" * 39),
        replace(request, license_evidence=""),
        replace(request, license_id="UNKNOWN"),
    ):
        assert contract.acquisition_authorization_decision(changed, approval) == "DENY"


def test_acquisition_red_rejects_source_and_artifact_scope_expansion():
    contract = _contract()
    request = _request(contract)
    approval = _approval(contract)
    for changed in (
        replace(request, sources=("https://unapproved.invalid/model",)),
        replace(request, artifacts=("config.json", "unexpected.bin")),
        replace(request, artifacts=()),
    ):
        assert contract.acquisition_authorization_decision(changed, approval) == "DENY"


def test_acquisition_red_rejects_destination_escape_and_private_roots():
    contract = _contract()
    request = _request(contract)
    approval = _approval(contract)
    for destination in (
        "../outside",
        "D:\\Biblioteca",
        "/home/user/private",
        "isolated/../outside",
    ):
        assert (
            contract.acquisition_authorization_decision(
                replace(request, destination=destination), approval
            )
            == "DENY"
        )


def test_acquisition_red_requires_bounded_resources_and_public_privacy():
    contract = _contract()
    request = _request(contract)
    approval = _approval(contract)
    for changed in (
        replace(request, max_bytes=0),
        replace(request, max_files=0),
        replace(request, timeout_seconds=0),
        replace(request, retry_limit=-1),
        replace(request, privacy_public_only=False),
    ):
        assert contract.acquisition_authorization_decision(changed, approval) == "DENY"


def test_acquisition_red_requires_auditable_immutable_evidence():
    contract = _contract()
    request = _request(contract)
    approval = _approval(contract)
    assert (
        contract.acquisition_authorization_decision(
            replace(request, evidence_ledger=""), approval
        )
        == "DENY"
    )
    assert (
        contract.acquisition_authorization_decision(
            replace(request, request_id=""), approval
        )
        == "DENY"
    )
    assert (
        contract.acquisition_authorization_decision(
            replace(request, action="ONNX_EXPORT"), approval
        )
        == "DENY"
    )


def test_acquisition_red_is_pure_and_cannot_trigger_network_or_next_phase():
    contract = _contract()
    source = inspect.getsource(contract)
    for forbidden in (
        "requests.get(",
        "urllib.request",
        "huggingface_hub",
        "subprocess.run(",
        "onnxruntime",
        "torch.load(",
        "memory_gateway.write(",
        "socket.create_connection(",
    ):
        assert forbidden not in source
    assert contract.phase_can_authorize_next("MODEL_ACQUISITION") is False
    assert contract.phase_can_authorize_next("VERIFICATION") is False
