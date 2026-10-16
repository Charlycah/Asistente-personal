from __future__ import annotations

import importlib
import inspect
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

from app.external_retrieval_runtime import OfficialExternalRetrievalRuntimeGateway
from app.governed_independence_authorization_boundary import (
    GovernedIndependenceAuthorizationBoundaryV1,
    GovernedInitiationDecision,
)
from app.governed_local_library_conversation import GovernedLocalLibraryConversationV1
from app.knowledge_runtime import OfficialKnowledgeRuntimeGateway
from app.unified_retrieval_execution_runtime import (
    OfficialUnifiedRetrievalExecutionRuntimeGateway,
)
from core.capability_registry import (
    CapabilityEffectClass,
    CapabilityInitiationPolicy,
    CapabilityInteractionScope,
    CapabilityRegistryManager,
    CapabilityRisk,
    PermissionScope,
)
from core.governed_local_library import (
    GovernedLocalLibraryCatalogueV1,
    GovernedLocalLibraryConfig,
)
from core.knowledge_retrieval_orchestrator import KnowledgeRetrievalStep

NOW = datetime(2026, 8, 31, 21, 45, tzinfo=timezone.utc)
CAPABILITY_NAME = "knowledge.local_library.read"
INITIATIVE_CORE_MODULE = "core.governed_local_library.initiative"
INITIATIVE_APP_MODULE = "app.governed_roby_initiated_library_access"


class Reader:
    def __init__(self) -> None:
        self.calls: list[Path] = []

    def read_text(self, path: Path) -> str:
        self.calls.append(path)
        return path.read_text(encoding="utf-8")


class CountingLibrary:
    def __init__(self, root: Path) -> None:
        root.mkdir(parents=True, exist_ok=True)
        self.delegate = GovernedLocalLibraryCatalogueV1(
            GovernedLocalLibraryConfig(
                root=root,
                allowed_suffixes=(".txt",),
                max_catalogue_entries=20,
            )
        )
        self.search_calls = 0

    def search(self, query: str, *, max_results: int = 5):
        self.search_calls += 1
        return self.delegate.search(query, max_results=max_results)

    def catalogue(self):
        return self.delegate.catalogue()

    def resolve_entry(self, entry_id: str):
        return self.delegate.resolve_entry(entry_id)


def _core_initiative_api():
    module = importlib.import_module(INITIATIVE_CORE_MODULE)
    return module.governed_local_library_read_descriptor


def _app_initiative_api():
    module = importlib.import_module(INITIATIVE_APP_MODULE)
    return (
        module.GovernedRobyInitiatedLibraryAccessStatus,
        module.GovernedRobyInitiatedLibraryAccessV1,
    )


def _direct_request_type():
    module = importlib.import_module(
        "app.governed_independence_authorization_boundary"
    )
    return module.GovernedReadOnlyCapabilityInitiationRequest


def _registry_with_descriptor(**changes) -> CapabilityRegistryManager:
    descriptor_factory = _core_initiative_api()
    descriptor = descriptor_factory()
    if changes:
        descriptor = replace(descriptor, **changes)
    registry = CapabilityRegistryManager()
    registry.register(descriptor)
    return registry


def _request():
    request_type = _direct_request_type()
    return request_type(
        owner="Carlos",
        capability_name=CAPABILITY_NAME,
        reason="La Biblioteca personal puede aportar evidencia local relevante.",
        source_reference="conversation:turn-current",
        world_snapshot_id="world-current",
    )


def _conversation(root: Path, reader: Reader, library: CountingLibrary):
    return GovernedLocalLibraryConversationV1(
        knowledge_runtime=OfficialKnowledgeRuntimeGateway(),
        library=library,
        document_reader=reader,
        unified_runtime=OfficialUnifiedRetrievalExecutionRuntimeGateway(
            OfficialExternalRetrievalRuntimeGateway()
        ),
    )


def _initiative(
    root: Path,
    *,
    registry: CapabilityRegistryManager,
    reader: Reader | None = None,
):
    _, initiative_type = _app_initiative_api()
    actual_reader = reader or Reader()
    library = CountingLibrary(root)
    conversation = _conversation(root, actual_reader, library)
    boundary = GovernedIndependenceAuthorizationBoundaryV1(registry)
    return (
        initiative_type(
            authorization_boundary=boundary,
            library_conversation=conversation,
        ),
        library,
        actual_reader,
        conversation,
    )


def _handle(initiative, *, query: str = "atlas"):
    return initiative.handle_proposal(
        owner="Carlos",
        search_query=query,
        reason="La Biblioteca personal puede aportar evidencia local relevante.",
        source_reference="conversation:turn-current",
        world_snapshot_id="world-current",
        now=NOW,
    )


def test_cap17_local_library_capability_uses_official_registry() -> None:
    descriptor_factory = _core_initiative_api()
    registry = CapabilityRegistryManager()
    descriptor = descriptor_factory()
    registry.register(descriptor)
    assert registry.get(CAPABILITY_NAME) is descriptor


def test_cap17_local_library_capability_has_safe_level2_profile() -> None:
    descriptor = _core_initiative_api()()
    assert descriptor.name == CAPABILITY_NAME
    assert descriptor.normalized_risk is CapabilityRisk.LOW
    assert descriptor.normalized_permission_scope is PermissionScope.READ
    assert (
        descriptor.normalized_initiation_policy
        is CapabilityInitiationPolicy.GOVERNED_AUTONOMOUS
    )
    assert descriptor.normalized_effect_class is CapabilityEffectClass.READ_ONLY
    assert (
        descriptor.normalized_interaction_scope
        is CapabilityInteractionScope.INTERNAL
    )
    assert descriptor.requires_confirmation is False


def test_cap17_boundary_exposes_generic_read_only_initiation_request() -> None:
    request = _request()
    assert request.capability_name == CAPABILITY_NAME
    assert request.reason


def test_cap17_boundary_exposes_generic_capability_initiation_entrypoint() -> None:
    assert hasattr(
        GovernedIndependenceAuthorizationBoundaryV1,
        "evaluate_capability_initiation",
    )


def test_cap17_safe_local_library_capability_may_initiate() -> None:
    boundary = GovernedIndependenceAuthorizationBoundaryV1(
        _registry_with_descriptor()
    )
    report = boundary.evaluate_capability_initiation(_request())
    assert report.decision is GovernedInitiationDecision.MAY_INITIATE
    assert report.capability_name == CAPABILITY_NAME
    assert report.execution_authorized is False


def test_cap17_human_approval_requires_ask() -> None:
    boundary = GovernedIndependenceAuthorizationBoundaryV1(
        _registry_with_descriptor(
            initiation_policy=CapabilityInitiationPolicy.HUMAN_APPROVAL
        )
    )
    report = boundary.evaluate_capability_initiation(_request())
    assert report.decision is GovernedInitiationDecision.MUST_ASK


def test_cap17_forbidden_initiation_requires_abstention() -> None:
    boundary = GovernedIndependenceAuthorizationBoundaryV1(
        _registry_with_descriptor(initiation_policy=CapabilityInitiationPolicy.NEVER)
    )
    report = boundary.evaluate_capability_initiation(_request())
    assert report.decision is GovernedInitiationDecision.MUST_ABSTAIN


def test_cap17_undeclared_initiation_requires_review() -> None:
    boundary = GovernedIndependenceAuthorizationBoundaryV1(
        _registry_with_descriptor(
            initiation_policy=CapabilityInitiationPolicy.UNDECLARED
        )
    )
    report = boundary.evaluate_capability_initiation(_request())
    assert report.decision is GovernedInitiationDecision.REVIEW_REQUIRED


def test_cap17_internal_proposal_is_non_executive_until_authorized(
    tmp_path: Path,
) -> None:
    initiative, library, reader, _ = _initiative(
        tmp_path / "library",
        registry=_registry_with_descriptor(
            initiation_policy=CapabilityInitiationPolicy.HUMAN_APPROVAL
        ),
    )
    result = _handle(initiative)
    assert result.authorization.decision is GovernedInitiationDecision.MUST_ASK
    assert library.search_calls == 0
    assert reader.calls == []


def test_cap17_may_initiate_emits_transparent_realization(tmp_path: Path) -> None:
    initiative, _, _, _ = _initiative(
        tmp_path / "library", registry=_registry_with_descriptor()
    )
    result = _handle(initiative)
    assert result.authorization.decision is GovernedInitiationDecision.MAY_INITIATE
    assert result.transparency_message
    assert "biblioteca" in result.transparency_message.casefold()


def test_cap17_must_ask_performs_zero_searches_and_reads(tmp_path: Path) -> None:
    initiative, library, reader, _ = _initiative(
        tmp_path / "library",
        registry=_registry_with_descriptor(
            initiation_policy=CapabilityInitiationPolicy.HUMAN_APPROVAL
        ),
    )
    result = _handle(initiative)
    assert result.status.value == "must_ask"
    assert library.search_calls == 0
    assert reader.calls == []


def test_cap17_must_abstain_performs_zero_searches_and_reads(tmp_path: Path) -> None:
    initiative, library, reader, _ = _initiative(
        tmp_path / "library",
        registry=_registry_with_descriptor(
            initiation_policy=CapabilityInitiationPolicy.NEVER
        ),
    )
    result = _handle(initiative)
    assert result.status.value == "abstained"
    assert library.search_calls == 0
    assert reader.calls == []


def test_cap17_review_required_performs_zero_searches_and_reads(tmp_path: Path) -> None:
    initiative, library, reader, _ = _initiative(
        tmp_path / "library",
        registry=_registry_with_descriptor(
            initiation_policy=CapabilityInitiationPolicy.UNDECLARED
        ),
    )
    result = _handle(initiative)
    assert result.status.value == "review_required"
    assert library.search_calls == 0
    assert reader.calls == []


def test_cap17_may_initiate_preserves_zero_one_many_ambiguity(tmp_path: Path) -> None:
    root = tmp_path / "library"
    initiative, library, reader, _ = _initiative(
        root, registry=_registry_with_descriptor()
    )
    (root / "atlas_alpha.txt").write_text("A", encoding="utf-8")
    (root / "atlas_beta.txt").write_text("B", encoding="utf-8")
    result = _handle(initiative)
    assert result.status.value == "needs_disambiguation"
    assert library.search_calls == 1
    assert reader.calls == []


def test_cap17_unique_candidate_preserves_provenance(tmp_path: Path) -> None:
    root = tmp_path / "library"
    initiative, _, reader, _ = _initiative(root, registry=_registry_with_descriptor())
    (root / "atlas.txt").write_text("Grounded Atlas", encoding="utf-8")
    result = _handle(initiative)
    assert result.status.value == "completed"
    assert result.library_result is not None
    assert result.library_result.artifact is not None
    assert (
        result.library_result.source_reference
        in result.library_result.artifact.references
    )
    assert len(reader.calls) == 1


def test_cap17_unique_candidate_uses_existing_unified_runtime(tmp_path: Path) -> None:
    root = tmp_path / "library"
    initiative, _, _, conversation = _initiative(
        root, registry=_registry_with_descriptor()
    )
    (root / "atlas.txt").write_text("Grounded Atlas", encoding="utf-8")
    before = conversation.unified_runtime.snapshot.evaluations
    result = _handle(initiative)
    assert result.status.value == "completed"
    assert conversation.unified_runtime.snapshot.evaluations == before + 1


def test_cap17_direct_initiation_does_not_require_discriminating_evidence() -> None:
    _direct_request_type()
    signature = inspect.signature(
        GovernedIndependenceAuthorizationBoundaryV1.evaluate_capability_initiation
    )
    assert "consumption" not in signature.parameters
    assert "initiative_proposal" not in signature.parameters


def test_cap17_roby_initiated_adapter_does_not_use_level2_evidence_executor() -> None:
    _, initiative_type = _app_initiative_api()
    source = inspect.getsource(initiative_type)
    assert "GovernedLevel2ReadOnlyExecutionGatewayV1" not in source
    assert "GovernedLocalLibraryConversationV1" in source


def test_cap17_roby_initiated_adapter_has_no_memory_learning_or_background_actions(
) -> None:
    _, initiative_type = _app_initiative_api()
    public = {
        name.casefold() for name in dir(initiative_type) if not name.startswith("_")
    }
    forbidden = {"remember", "learn", "persist", "scan", "poll", "watch"}
    assert public.isdisjoint(forbidden)


def test_cap17_roby_initiated_access_keeps_retrieval_step_schema() -> None:
    _app_initiative_api()
    fields = tuple(inspect.signature(KnowledgeRetrievalStep).parameters)
    assert fields == ("source", "priority", "required", "query", "step_id")


def test_cap17_roby_initiated_decision_is_one_shot_not_reused(tmp_path: Path) -> None:
    root = tmp_path / "library"
    initiative, library, reader, _ = _initiative(
        root, registry=_registry_with_descriptor()
    )
    (root / "atlas.txt").write_text("Grounded Atlas", encoding="utf-8")
    first = _handle(initiative)
    assert first.status.value == "completed"
    assert library.search_calls == 1
    second_registry = _registry_with_descriptor(
        initiation_policy=CapabilityInitiationPolicy.HUMAN_APPROVAL
    )
    initiative.authorization_boundary = GovernedIndependenceAuthorizationBoundaryV1(
        second_registry
    )
    second = _handle(initiative)
    assert second.status.value == "must_ask"
    assert library.search_calls == 1
    assert len(reader.calls) == 1


def test_cap17_no_match_does_not_fall_back_to_web_or_modify_config(
    tmp_path: Path,
) -> None:
    config = Path(".roby/config.json")
    before = config.read_bytes() if config.exists() else None
    initiative, library, reader, conversation = _initiative(
        tmp_path / "library", registry=_registry_with_descriptor()
    )
    external_before = conversation.unified_runtime.external_runtime.snapshot.evaluations
    result = _handle(initiative, query="missing-title")
    assert result.status.value == "no_match"
    assert library.search_calls == 1
    assert reader.calls == []
    assert (
        conversation.unified_runtime.external_runtime.snapshot.evaluations
        == external_before
    )
    after = config.read_bytes() if config.exists() else None
    assert after == before
