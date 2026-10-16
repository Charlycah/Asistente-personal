from __future__ import annotations

import ast
import inspect
from pathlib import Path

from app.governed_knowledge_revision_request import GovernedKnowledgeRevisionRequest
from app.m369_explicit_human_learning_approval import (
    M369ExplicitHumanLearningApprovalEvidenceFoundation,
)
from app.official_conversation_gateway import OfficialConversationGateway
from app.productive_governed_learning_wiring import ProductiveGovernedLearningWiring


def _certified_request() -> GovernedKnowledgeRevisionRequest:
    return GovernedKnowledgeRevisionRequest(
        request_id="governed-knowledge-revision-request-contractred",
        application_proposal_id=(
            "governed-knowledge-revision-application-proposal-contractred"
        ),
        revision_approval_id="m369-human-revision-approved-contractred",
        revision_proposal_id="governed-knowledge-revision-proposal-contractred",
        target_memory_id="stable-knowledge-contractred",
        target_owner="Carlos y Cristina",
        target_category="STABLE_KNOWLEDGE",
        expected_current_content="ROBY utiliza conocimiento durable versión uno.",
        replacement_content="ROBY utiliza conocimiento durable versión dos.",
        corrective_evidence_ids=("corrective-evidence-contractred",),
        revision_proposal_fingerprint="1" * 64,
        human_approval_fingerprint="2" * 64,
        application_proposal_fingerprint="3" * 64,
        expected_target_fingerprint="4" * 64,
        replacement_idempotency_key="knowledge-revision-replacement-contractred",
    )


class _RecordingMemoryGateway:
    def __init__(self) -> None:
        self.applied: list[GovernedKnowledgeRevisionRequest] = []

    def remember_governed_learning(self, request):  # pragma: no cover
        raise AssertionError("POST-G21 contract does not exercise learning writes")

    def apply_governed_knowledge_revision(self, request):
        self.applied.append(request)
        return request


def test_post_g21_existing_human_authority_exposes_execution_authorization_types() -> (
    None
):
    module = __import__(
        "app.m369_explicit_human_learning_approval",
        fromlist=["M369ExplicitHumanLearningApprovalEvidenceFoundation"],
    )
    assert hasattr(
        module,
        "ExplicitHumanKnowledgeRevisionExecutionAuthorizationResponse",
    ), "POST-G21 seam missing: explicit apply-now response type is required"
    assert hasattr(
        module,
        "AuthorizedKnowledgeRevisionExecutionEvidence",
    ), "POST-G21 seam missing: inert exact-linked execution evidence is required"


def test_post_g21_existing_human_authority_evaluates_exact_g16_execution() -> None:
    method = getattr(
        M369ExplicitHumanLearningApprovalEvidenceFoundation,
        "evaluate_revision_execution_authorization",
        None,
    )
    assert method is not None, (
        "POST-G21 seam missing: existing human authority must evaluate "
        "explicit execution authorization for one exact G16 request"
    )
    signature = inspect.signature(method)
    assert "request" in signature.parameters
    assert "response" in signature.parameters


def test_post_g21_revision_execution_seam_requires_exact_authorization() -> None:
    method = getattr(
        ProductiveGovernedLearningWiring,
        "execute_certified_revision_request",
        None,
    )
    assert method is not None
    signature = inspect.signature(method)
    assert "authorization" in signature.parameters, (
        "POST-G21 hard boundary missing: certified request alone must not "
        "be sufficient for durable execution"
    )


def test_post_g21_certified_request_alone_cannot_mutate_memory() -> None:
    memory = _RecordingMemoryGateway()
    wiring = ProductiveGovernedLearningWiring(memory)
    request = _certified_request()

    wiring.execute_certified_revision_request(request)

    assert memory.applied == [], (
        "POST-G21 hard boundary missing: bare G16 request reached Memory "
        "without exact execution authorization"
    )


def test_post_g21_official_conversation_requires_execution_authorization_seam() -> None:
    signature = inspect.signature(OfficialConversationGateway.submit)
    assert (
        "knowledge_revision_execution_authorization" in signature.parameters
        or "knowledge_revision_execution_authorization_response" in signature.parameters
    ), (
        "POST-G21 conversation seam missing: G18 reachability must require "
        "explicit execution authorization material"
    )


def test_post_g21_contract_introduces_no_duplicate_authority_or_writer() -> None:
    project = Path(__file__).resolve().parents[2]
    app_sources = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in (project / "app").glob("*.py")
    )
    forbidden = (
        "class RevisionExecutionApprovalManager",
        "class KnowledgeRevisionExecutionAuthority",
        "class RevisionExecutionManager",
        "class ProductiveKnowledgeRevisionWiring",
        "class RevisionMemoryGateway",
    )
    for declaration in forbidden:
        assert declaration not in app_sources

    wiring_tree = ast.parse(
        (project / "app/productive_governed_learning_wiring.py").read_text(
            encoding="utf-8"
        )
    )
    declared = [
        node.name
        for node in wiring_tree.body
        if isinstance(node, ast.ClassDef)
        and node.name == "ProductiveGovernedLearningWiring"
    ]
    assert declared == ["ProductiveGovernedLearningWiring"]


def test_post_g21_g17_remains_the_only_durable_revision_writer_path() -> None:
    method = ProductiveGovernedLearningWiring.execute_certified_revision_request
    source = inspect.getsource(method)
    assert "apply_governed_knowledge_revision(request)" in source
    assert "GovernedKnowledgeRevisionRequestFoundation" not in source
    assert ".certify(" not in source

    gateway_source = inspect.getsource(OfficialConversationGateway.submit)
    assert "apply_governed_knowledge_revision(" not in gateway_source
