from __future__ import annotations

import importlib
import inspect
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.external_retrieval_runtime import OfficialExternalRetrievalRuntimeGateway
from app.unified_retrieval_execution_runtime import (
    OfficialUnifiedRetrievalExecutionRuntimeGateway,
)
from core.governed_local_library import (
    GovernedLocalLibraryCatalogueV1,
    GovernedLocalLibraryConfig,
)
from core.governed_local_library.handoff import (
    GovernedLibrarySelection,
    GovernedLocalDocumentRetrievalRequest,
    GovernedLocalDocumentRetrieverV1,
)
from core.knowledge_retrieval_execution import (
    KnowledgeExecutionStatus,
    KnowledgeRetrievalArtifact,
    KnowledgeRetrievalExecution,
    KnowledgeRetrievalExecutionGateway,
    KnowledgeRetrievalExecutionRequest,
    KnowledgeStepExecutionStatus,
)
from core.knowledge_retrieval_orchestrator import (
    KnowledgeRetrievalOrchestrator,
    KnowledgeRetrievalRequest,
)
from core.knowledge_source_policy import KnowledgeSourceKind
from tests.test_m169_knowledge_source_policy import decide, need

MODULE = "core.governed_local_library.runtime_binding"
NOW = datetime(2026, 8, 31, 18, 0, tzinfo=timezone.utc)


class Reader:
    def __init__(self) -> None:
        self.calls: list[Path] = []

    def read_text(self, path: Path) -> str:
        self.calls.append(path)
        return path.read_text(encoding="utf-8")


class FakeRetriever:
    def __init__(self, content: str = "persistent") -> None:
        self.content = content
        self.calls = []

    def retrieve(self, step):
        self.calls.append(step)
        return KnowledgeRetrievalArtifact(
            source=step.source,
            query=step.query,
            content=self.content,
            references=("ref:persistent",),
        )


def _binding_type():
    module = importlib.import_module(MODULE)
    return module.BoundGovernedLocalDocumentRetrieverV1


def _library(root: Path) -> GovernedLocalLibraryCatalogueV1:
    return GovernedLocalLibraryCatalogueV1(
        GovernedLocalLibraryConfig(root=root, allowed_suffixes=(".txt",))
    )


def _local_plan(query: str = "atlas"):
    decision = decide(
        source_need=need(
            query,
            internal_confidence=0.1,
            local_documents_available=True,
            preferred_sources=(KnowledgeSourceKind.LOCAL_DOCUMENTS,),
        )
    )
    return KnowledgeRetrievalOrchestrator().orchestrate(
        KnowledgeRetrievalRequest(owner="Carlos", source_decision=decision),
        now=NOW,
    )


def _selection_and_request(root: Path, query: str = "atlas"):
    root.mkdir(exist_ok=True)
    (root / "atlas.txt").write_text("Grounded Atlas", encoding="utf-8")
    library = _library(root)
    search = library.search(query, max_results=10)
    entry = search.matches[0]
    selection = GovernedLibrarySelection(
        query=query,
        entry_id=entry.entry_id,
        source_reference=entry.source_reference,
        catalogue_fingerprint=search.catalogue_fingerprint,
    )
    plan = _local_plan(query)
    step = plan.steps[0]
    request = GovernedLocalDocumentRetrievalRequest(
        step=step,
        selection=selection,
    )
    return library, plan, step, selection, request


def _bound(root: Path, query: str = "atlas"):
    library, plan, step, selection, request = _selection_and_request(root, query)
    reader = Reader()
    base = GovernedLocalDocumentRetrieverV1(
        library=library,
        document_reader=reader,
    )
    bound_type = _binding_type()
    bound = bound_type(retriever=base, request=request)
    return bound, reader, plan, step, selection, request


def _execution_request(plan):
    return KnowledgeRetrievalExecutionRequest(owner="Carlos", plan=plan)


def test_cap17_bound_retriever_accepts_only_exact_bound_step_id(tmp_path: Path) -> None:
    bound, _, _, step, _, _ = _bound(tmp_path / "library")
    artifact = bound.retrieve(step)
    assert artifact.source is KnowledgeSourceKind.LOCAL_DOCUMENTS
    assert artifact.query == step.query


def test_cap17_bound_retriever_rejects_another_local_step(tmp_path: Path) -> None:
    bound, _, _, step, _, _ = _bound(tmp_path / "library")
    other = replace(step, query="otro", step_id="")
    with pytest.raises(ValueError, match="bound retrieval step"):
        bound.retrieve(other)


def test_cap17_bound_retriever_preserves_explicit_selection(tmp_path: Path) -> None:
    bound, _, _, _, selection, request = _bound(tmp_path / "library")
    assert bound.request is request
    assert bound.request.selection is selection


def test_cap17_execution_scoped_local_retriever_is_accepted(tmp_path: Path) -> None:
    bound, _, plan, _, _, _ = _bound(tmp_path / "library")
    gateway = KnowledgeRetrievalExecutionGateway()
    result = gateway.execute(
        _execution_request(plan),
        now=NOW,
        execution_retrievers={KnowledgeSourceKind.LOCAL_DOCUMENTS: bound},
    )
    assert result.status is KnowledgeExecutionStatus.COMPLETED


def test_cap17_execution_scoped_retriever_is_not_persisted(tmp_path: Path) -> None:
    bound, _, plan, _, _, _ = _bound(tmp_path / "library")
    gateway = KnowledgeRetrievalExecutionGateway()
    gateway.execute(
        _execution_request(plan),
        now=NOW,
        execution_retrievers={KnowledgeSourceKind.LOCAL_DOCUMENTS: bound},
    )
    assert KnowledgeSourceKind.LOCAL_DOCUMENTS not in gateway.retrievers


def test_cap17_execution_scoped_retriever_cannot_override_persistent(
    tmp_path: Path,
) -> None:
    bound, _, plan, _, _, _ = _bound(tmp_path / "library")
    persistent = FakeRetriever()
    gateway = KnowledgeRetrievalExecutionGateway(
        {KnowledgeSourceKind.LOCAL_DOCUMENTS: persistent}
    )
    with pytest.raises(ValueError, match="persistent retriever"):
        gateway.execute(
            _execution_request(plan),
            now=NOW,
            execution_retrievers={KnowledgeSourceKind.LOCAL_DOCUMENTS: bound},
        )
    assert persistent.calls == []


def test_cap17_external_m260_retrievers_cannot_be_overridden(tmp_path: Path) -> None:
    bound, _, plan, _, _, _ = _bound(tmp_path / "library")
    external = OfficialExternalRetrievalRuntimeGateway()
    unified = OfficialUnifiedRetrievalExecutionRuntimeGateway(external)
    with pytest.raises(ValueError, match="persistent retriever"):
        unified.execute(
            _execution_request(plan),
            now=NOW,
            execution_retrievers={KnowledgeSourceKind.WEB: bound},
        )


def test_cap17_unified_runtime_preserves_last_execution(tmp_path: Path) -> None:
    bound, _, plan, _, _, _ = _bound(tmp_path / "library")
    unified = OfficialUnifiedRetrievalExecutionRuntimeGateway(
        OfficialExternalRetrievalRuntimeGateway()
    )
    result = unified.execute(
        _execution_request(plan),
        now=NOW,
        execution_retrievers={KnowledgeSourceKind.LOCAL_DOCUMENTS: bound},
    )
    assert unified.last_execution is result


def test_cap17_unified_runtime_increments_evaluations_once(tmp_path: Path) -> None:
    bound, _, plan, _, _, _ = _bound(tmp_path / "library")
    unified = OfficialUnifiedRetrievalExecutionRuntimeGateway(
        OfficialExternalRetrievalRuntimeGateway()
    )
    before = unified.snapshot.evaluations
    unified.execute(
        _execution_request(plan),
        now=NOW,
        execution_retrievers={KnowledgeSourceKind.LOCAL_DOCUMENTS: bound},
    )
    assert unified.snapshot.evaluations == before + 1


def test_cap17_unified_runtime_returns_canonical_execution(tmp_path: Path) -> None:
    bound, _, plan, _, _, _ = _bound(tmp_path / "library")
    unified = OfficialUnifiedRetrievalExecutionRuntimeGateway(
        OfficialExternalRetrievalRuntimeGateway()
    )
    result = unified.execute(
        _execution_request(plan),
        now=NOW,
        execution_retrievers={KnowledgeSourceKind.LOCAL_DOCUMENTS: bound},
    )
    assert isinstance(result, KnowledgeRetrievalExecution)


def test_cap17_local_step_succeeds_with_canonical_artifact(tmp_path: Path) -> None:
    bound, _, plan, _, _, _ = _bound(tmp_path / "library")
    unified = OfficialUnifiedRetrievalExecutionRuntimeGateway(
        OfficialExternalRetrievalRuntimeGateway()
    )
    result = unified.execute(
        _execution_request(plan),
        now=NOW,
        execution_retrievers={KnowledgeSourceKind.LOCAL_DOCUMENTS: bound},
    )
    step_result = result.steps[0]
    assert step_result.status is KnowledgeStepExecutionStatus.SUCCEEDED
    assert isinstance(step_result.artifact, KnowledgeRetrievalArtifact)
    assert step_result.artifact.source is KnowledgeSourceKind.LOCAL_DOCUMENTS


def test_cap17_provenance_survives_unified_execution(tmp_path: Path) -> None:
    bound, _, plan, _, selection, _ = _bound(tmp_path / "library")
    unified = OfficialUnifiedRetrievalExecutionRuntimeGateway(
        OfficialExternalRetrievalRuntimeGateway()
    )
    result = unified.execute(
        _execution_request(plan),
        now=NOW,
        execution_retrievers={KnowledgeSourceKind.LOCAL_DOCUMENTS: bound},
    )
    assert result.steps[0].artifact.references == (selection.source_reference,)


def test_cap17_selection_identity_mismatch_fails_governedly(tmp_path: Path) -> None:
    bound, _, plan, step, _, _ = _bound(tmp_path / "library")
    mismatched = replace(step, query="otro", step_id="")
    bad_plan = replace(plan, steps=(mismatched,), plan_id="")
    unified = OfficialUnifiedRetrievalExecutionRuntimeGateway(
        OfficialExternalRetrievalRuntimeGateway()
    )
    result = unified.execute(
        _execution_request(bad_plan),
        now=NOW,
        execution_retrievers={KnowledgeSourceKind.LOCAL_DOCUMENTS: bound},
    )
    assert result.status is KnowledgeExecutionStatus.FAILED
    assert result.steps[0].rationale == ("knowledge_retriever_failed:ValueError",)


def test_cap17_no_selection_produces_no_implicit_local_acquisition(
    tmp_path: Path,
) -> None:
    _binding_type()
    _, plan, _, _, _ = _selection_and_request(tmp_path / "library")
    unified = OfficialUnifiedRetrievalExecutionRuntimeGateway(
        OfficialExternalRetrievalRuntimeGateway()
    )
    result = unified.execute(_execution_request(plan), now=NOW)
    assert result.status is KnowledgeExecutionStatus.FAILED
    assert result.steps[0].rationale == ("knowledge_retriever_not_registered",)


def test_cap17_prior_binding_is_not_reused_by_next_execution(
    tmp_path: Path,
) -> None:
    bound, reader, plan, _, _, _ = _bound(tmp_path / "library")
    unified = OfficialUnifiedRetrievalExecutionRuntimeGateway(
        OfficialExternalRetrievalRuntimeGateway()
    )
    first = unified.execute(
        _execution_request(plan),
        now=NOW,
        execution_retrievers={KnowledgeSourceKind.LOCAL_DOCUMENTS: bound},
    )
    second = unified.execute(_execution_request(plan), now=NOW.replace(second=1))
    assert first.status is KnowledgeExecutionStatus.COMPLETED
    assert second.status is KnowledgeExecutionStatus.FAILED
    assert len(reader.calls) == 1


def test_cap17_transport_exposes_no_memory_or_learning_actions(tmp_path: Path) -> None:
    bound, _, _, _, _, _ = _bound(tmp_path / "library")
    public = {name.casefold() for name in dir(bound) if not name.startswith("_")}
    assert "remember" not in public
    assert "learn" not in public
    assert "admit" not in public
    assert "persist" not in public


def test_cap17_transport_does_not_modify_roby_config(tmp_path: Path) -> None:
    config = Path(".roby/config.json")
    before = config.read_bytes() if config.exists() else None
    bound, _, plan, _, _, _ = _bound(tmp_path / "library")
    unified = OfficialUnifiedRetrievalExecutionRuntimeGateway(
        OfficialExternalRetrievalRuntimeGateway()
    )
    unified.execute(
        _execution_request(plan),
        now=NOW,
        execution_retrievers={KnowledgeSourceKind.LOCAL_DOCUMENTS: bound},
    )
    after = config.read_bytes() if config.exists() else None
    assert after == before


def test_cap17_does_not_change_knowledge_retrieval_step_schema() -> None:
    _binding_type()
    from core.knowledge_retrieval_orchestrator import KnowledgeRetrievalStep

    fields = tuple(inspect.signature(KnowledgeRetrievalStep).parameters)
    assert fields == ("source", "priority", "required", "query", "step_id")
