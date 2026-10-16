from __future__ import annotations

import inspect
from dataclasses import fields
from pathlib import Path

from app.approved_learning_memory_materialization import (
    ApprovedLearningEvidence,
    GovernedMemoryMaterializationProposal,
)
from app.approved_learning_memory_write_adapter import GovernedMemoryWriteRequest
from app.curiosity_m369_learning_evaluation import CuriosityLearningKind
from app.m369_explicit_human_learning_approval import (
    ExplicitHumanLearningApprovalResponse,
)
from core.cognitive_memory import LearningCategory

ROOT = Path(__file__).resolve().parents[2]


def _field_names(model) -> set[str]:
    return {field.name for field in fields(model)}


# RED-01 — productive Learning must expose a distinct stable-knowledge kind.
def test_red_01_productive_learning_has_stable_knowledge_kind() -> None:
    assert hasattr(CuriosityLearningKind, "STABLE_KNOWLEDGE")


# RED-02 — approval identity must become typed learning identity, not preference-only.
def test_red_02_approval_response_carries_learning_kind() -> None:
    assert "learning_kind" in _field_names(ExplicitHumanLearningApprovalResponse)


# RED-03 — approved evidence must preserve the same typed learning identity.
def test_red_03_approved_evidence_carries_learning_kind() -> None:
    assert "learning_kind" in _field_names(ApprovedLearningEvidence)


# RED-04 — structural eligibility must have explicit provenance in approved evidence.
def test_red_04_approved_evidence_carries_structural_evidence_fingerprint() -> None:
    assert (
        "structural_evidence_fingerprint"
        in _field_names(ApprovedLearningEvidence)
    )


# RED-05 — materialization must carry semantic category explicitly.
def test_red_05_materialization_proposal_carries_learning_category() -> None:
    assert "learning_category" in _field_names(GovernedMemoryMaterializationProposal)


# RED-06 — materialization must preserve structural eligibility evidence.
def test_red_06_materialization_preserves_structural_evidence_fingerprint() -> None:
    assert (
        "structural_evidence_fingerprint"
        in _field_names(GovernedMemoryMaterializationProposal)
    )


# RED-07 — write request must carry the certified semantic category.
def test_red_07_governed_write_request_carries_learning_category() -> None:
    assert "learning_category" in _field_names(GovernedMemoryWriteRequest)


# RED-08 — write request must preserve structural evidence lineage.
def test_red_08_write_request_carries_structural_evidence_fingerprint() -> None:
    assert (
        "structural_evidence_fingerprint"
        in _field_names(GovernedMemoryWriteRequest)
    )


# RED-09 — governed Memory runtime must accept an explicit certified category.
def test_red_09_governed_memory_runtime_accepts_learning_category() -> None:
    from core.memory_runtime_integration import MemoryRuntimeIntegration

    parameters = inspect.signature(
        MemoryRuntimeIntegration.store_governed_learning
    ).parameters
    assert "learning_category" in parameters


# RED-10 — governed Memory writer must stop hard-coding preference semantics.
def test_red_10_governed_memory_runtime_does_not_hardcode_preference() -> None:
    source = (
        ROOT / "core" / "memory_runtime_integration" / "runtime.py"
    ).read_text(encoding="utf-8")
    method = source.split("def store_governed_learning(", 1)[1].split(
        "\n    def ", 1
    )[0]
    assert "category=LearningCategory.USER_PREFERENCE" not in method
    assert '("governed_learning", "human_approved", "preference")' not in method


# RED-11 — materializer must no longer be structurally preference-only.
def test_red_11_materializer_is_not_preference_identity_only() -> None:
    source = (
        ROOT / "app" / "approved_learning_memory_materialization.py"
    ).read_text(encoding="utf-8")
    assert "approved_preference_learning" not in source
    assert "materialization requires review-authorized M369 preference" not in source


# RED-12 — approval exact linkage must not require preference identity universally.
def test_red_12_approval_linkage_is_not_preference_only() -> None:
    source = (
        ROOT / "app" / "m369_explicit_human_learning_approval.py"
    ).read_text(encoding="utf-8")
    linkage = source.split("def _exactly_linked(", 1)[1].split(
        "\n    def ", 1
    )[0]
    assert "preference = evaluation.preference_candidate" not in linkage
    assert "response.preference_candidate_id == preference.preference_id" not in linkage


# GREEN GUARD-01 — canonical category already exists; do not invent another ontology.
def test_guard_01_existing_stable_knowledge_category_is_reused() -> None:
    assert LearningCategory.STABLE_KNOWLEDGE.value == "stable_knowledge"


# GREEN GUARD-02 — official writer boundary remains the existing Memory gateway.
def test_guard_02_write_request_keeps_official_memory_gateway() -> None:
    assert GovernedMemoryWriteRequest.__dataclass_fields__[
        "writer_component"
    ].default == "OfficialMemoryGateway"


# GREEN GUARD-03 — no second authority/orchestrator is introduced by this RED phase.
def test_guard_03_red_phase_does_not_add_production_authority() -> None:
    prohibited = (
        "structural_knowledge_learning_manager.py",
        "structural_learning_orchestrator.py",
        "stable_knowledge_memory_gateway.py",
    )
    assert all(not (ROOT / "app" / name).exists() for name in prohibited)


# GREEN GUARD-04 — existing preference path remains explicitly represented.
def test_guard_04_existing_preference_kind_remains_available() -> None:
    assert CuriosityLearningKind.PREFERENCE.value == "preference"
