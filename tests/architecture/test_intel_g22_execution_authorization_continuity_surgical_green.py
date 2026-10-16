from __future__ import annotations

from app.governed_knowledge_revision_request import GovernedKnowledgeRevisionRequest
from app.m369_explicit_human_learning_approval import (
    ExplicitHumanKnowledgeRevisionExecutionAuthorizationResponse,
    M369ExplicitHumanLearningApprovalEvidenceFoundation,
)
from app.productive_governed_learning_wiring import ProductiveGovernedLearningWiring


def _request(suffix: str = "g22") -> GovernedKnowledgeRevisionRequest:
    return GovernedKnowledgeRevisionRequest(
        request_id=f"governed-knowledge-revision-request-{suffix}",
        application_proposal_id=(
            f"governed-knowledge-revision-application-proposal-{suffix}"
        ),
        revision_approval_id=f"m369-human-revision-approved-{suffix}",
        revision_proposal_id=f"governed-knowledge-revision-proposal-{suffix}",
        target_memory_id=f"stable-knowledge-{suffix}",
        target_owner="Carlos y Cristina",
        target_category="STABLE_KNOWLEDGE",
        expected_current_content="version one",
        replacement_content="version two",
        corrective_evidence_ids=(f"corrective-evidence-{suffix}",),
        revision_proposal_fingerprint="1" * 64,
        human_approval_fingerprint="2" * 64,
        application_proposal_fingerprint="3" * 64,
        expected_target_fingerprint="4" * 64,
        replacement_idempotency_key=f"knowledge-revision-replacement-{suffix}",
    )


def _response(
    request: GovernedKnowledgeRevisionRequest, text: str = "Sí, aplicar ahora"
):
    return ExplicitHumanKnowledgeRevisionExecutionAuthorizationResponse(
        authorization_request_id="revision-execution-authorization-g22",
        revision_request_id=request.request_id,
        human_response_reference="human-response-g22",
        response_text=text,
        approver="Carlos",
    )


class _Memory:
    def __init__(self) -> None:
        self.applied = []

    def apply_governed_knowledge_revision(self, request):
        self.applied.append(request)
        return request


def test_g22_exact_apply_now_produces_inert_authorization() -> None:
    request = _request()
    evidence = M369ExplicitHumanLearningApprovalEvidenceFoundation().\
        evaluate_revision_execution_authorization(request, _response(request))
    assert evidence is not None
    assert evidence.revision_request_id == request.request_id
    assert evidence.application_proposal_id == request.application_proposal_id
    assert evidence.revision_approval_id == request.revision_approval_id
    assert evidence.revision_proposal_id == request.revision_proposal_id
    assert evidence.target_memory_id == request.target_memory_id
    assert evidence.target_owner == request.target_owner
    assert evidence.expected_target_fingerprint == request.expected_target_fingerprint
    assert evidence.replacement_idempotency_key == request.replacement_idempotency_key
    assert evidence.read_only is True
    assert evidence.memory_modified is False
    assert evidence.executes_actions is False
    assert evidence.grants_authority is False


def test_g22_content_approval_language_does_not_authorize_execution() -> None:
    request = _request()
    evidence = M369ExplicitHumanLearningApprovalEvidenceFoundation().\
        evaluate_revision_execution_authorization(
            request,
            _response(request, "Apruebo la revisión"),
        )
    assert evidence is None


def test_g22_wrong_request_linkage_abstains() -> None:
    request = _request()
    other = _request("other")
    evidence = M369ExplicitHumanLearningApprovalEvidenceFoundation().\
        evaluate_revision_execution_authorization(request, _response(other))
    assert evidence is None


def test_g22_bare_request_and_wrong_authorization_never_reach_memory() -> None:
    request = _request()
    other = _request("other")
    authority = M369ExplicitHumanLearningApprovalEvidenceFoundation()
    wrong = authority.evaluate_revision_execution_authorization(other, _response(other))
    assert wrong is not None
    memory = _Memory()
    wiring = ProductiveGovernedLearningWiring(memory)
    assert wiring.execute_certified_revision_request(request) is None
    assert wiring.execute_certified_revision_request(request, wrong) is None
    assert memory.applied == []


def test_g22_exact_request_and_authorization_reenter_existing_g17_path() -> None:
    request = _request()
    authority = M369ExplicitHumanLearningApprovalEvidenceFoundation()
    authorization = authority.evaluate_revision_execution_authorization(
        request,
        _response(request),
    )
    assert authorization is not None
    memory = _Memory()
    wiring = ProductiveGovernedLearningWiring(memory)
    result = wiring.execute_certified_revision_request(request, authorization)
    assert result is request
    assert memory.applied == [request]
