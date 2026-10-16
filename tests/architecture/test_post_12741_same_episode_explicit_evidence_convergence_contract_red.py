from __future__ import annotations

import importlib
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace

import pytest

from core.governed_reasoning.context import ReasoningQuery

ROOT = Path(__file__).resolve().parents[2]

PROTECTED_HASHES = {
    "core/governed_reasoning/context.py": (
        "03cd96b352aefc0062072eb17426445aca590e5300f18b5fd9a520f2742f399b"
    ),
    "core/governed_reasoning/evidence.py": (
        "c24c234c518db24cd38b53bf4c3d994c046919bd499f1cee5cb59d4bd43c40ef"
    ),
    "core/governed_reasoning/orchestrator.py": (
        "56e2b6d9ef608488d383f81920bacadde1bbcb168c160bbefbcf1d9d680d7ddd"
    ),
    "core/governed_reasoning/visual_evidence_relation.py": (
        "0fc5a090bf3976cfd9dba61a14eb51f33f690c14392e6f0e5d747c2919d2debc"
    ),
    "app/personal_document_reasoning_admission_adapter.py": (
        "6e5bd036b26767ca94496584039a76f57aa0dba2520421bd5be794ced3b561d8"
    ),
    "app/governed_local_evidence_reasoning_reentry.py": (
        "cf8c7f87b712515c90028e996097fd8dc3ff8d50b520be1de208543628c6439c"
    ),
    "app/governed_reasoning_runtime.py": (
        "f8c96d92c08fff1b9219afd68974b79ba319f087b2fb32fbb20d5856aaa91f2f"
    ),
}


@dataclass(frozen=True)
class _Reference:
    evidence_id: str


class _Repository:
    def __init__(self, records):
        self.records = records
        self.get_calls = []
        self.list_all_calls = 0

    def get(self, document_id):
        self.get_calls.append(document_id)
        return self.records.get(document_id)

    def list_all(self):
        self.list_all_calls += 1
        raise AssertionError("bounded convergence must not bulk-discover documents")


class _Registry:
    def __init__(self, normalized):
        self.normalized = normalized
        self.normalize_calls = []
        self.registered = []

    def normalize(self, source):
        self.normalize_calls.append(source)
        if source not in self.normalized:
            raise TypeError("unsupported source")
        reference = self.normalized[source]
        self.registered.append(reference)
        return reference

    def register_reference(self, reference, *, source=None):
        self.registered.append(reference)
        return reference


class _Gateway:
    def __init__(self, registry):
        self.orchestrator = SimpleNamespace(
            context_assembler=SimpleNamespace(evidence_registry=registry)
        )
        self.calls = []

    def reason(self, query, **kwargs):
        self.calls.append((query, kwargs))
        return SimpleNamespace(query=query, kwargs=kwargs)


def _adapter_class():
    module = importlib.import_module(
        "app.same_episode_explicit_evidence_convergence_adapter"
    )
    return module.SameEpisodeExplicitEvidenceConvergenceAdapterV1


def _build(*, records=None, normalized=None):
    repository = _Repository(records or {})
    registry = _Registry(normalized or {})
    gateway = _Gateway(registry)
    inbox = SimpleNamespace(repository=repository)
    adapter = _adapter_class()(
        document_inbox=inbox,
        reasoning_gateway=gateway,
    )
    return adapter, repository, registry, gateway


def test_post_12741_external_bounded_same_episode_adapter_exists():
    cls = _adapter_class()
    assert cls.__name__ == "SameEpisodeExplicitEvidenceConvergenceAdapterV1"


def test_post_12741_four_source_inputs_converge_into_one_reasoning_call():
    document = object()
    knowledge = object()
    document_ref = _Reference("document-evidence")
    knowledge_ref = _Reference("knowledge-evidence")
    library_ref = _Reference("library-evidence")
    visual = object()
    adapter, repository, registry, gateway = _build(
        records={"document-1": document},
        normalized={document: document_ref, knowledge: knowledge_ref},
    )

    result = adapter.admit_and_reason(
        text="compare all selected sources",
        owner="Carlos",
        explicit_document_ids=("document-1",),
        explicit_sources=(knowledge,),
        explicit_evidence_references=(library_ref,),
        visual_context_contribution=visual,
        now=datetime(2026, 9, 20, 18, 0, tzinfo=timezone.utc),
    )

    assert result is not None
    assert repository.get_calls == ["document-1"]
    assert registry.normalize_calls == [document, knowledge]
    assert len(gateway.calls) == 1
    query, kwargs = gateway.calls[0]
    assert isinstance(query, ReasoningQuery)
    assert query.evidence_ids == (
        "document-evidence",
        "knowledge-evidence",
        "library-evidence",
    )
    assert kwargs["visual_context_contribution"] is visual


def test_post_12741_personal_documents_are_exact_selection_only():
    selected = object()
    adapter, repository, _, gateway = _build(
        records={"selected": selected, "unselected": object()},
        normalized={selected: _Reference("selected-evidence")},
    )

    adapter.admit_and_reason(
        text="use selected evidence",
        owner="Carlos",
        explicit_document_ids=("selected",),
        explicit_sources=(),
        explicit_evidence_references=(),
        visual_context_contribution=None,
        now=datetime(2026, 9, 20, 18, 1, tzinfo=timezone.utc),
    )

    assert repository.get_calls == ["selected"]
    assert repository.list_all_calls == 0
    assert gateway.calls[0][0].evidence_ids == ("selected-evidence",)


def test_post_12741_absent_explicit_evidence_does_not_reason():
    adapter, repository, registry, gateway = _build()

    result = adapter.admit_and_reason(
        text="nothing explicitly admitted",
        owner="Carlos",
        explicit_document_ids=(),
        explicit_sources=(),
        explicit_evidence_references=(),
        visual_context_contribution=object(),
        now=datetime(2026, 9, 20, 18, 2, tzinfo=timezone.utc),
    )

    assert result is None
    assert repository.get_calls == []
    assert registry.normalize_calls == []
    assert gateway.calls == []


def test_post_12741_unsupported_source_fails_before_reasoning():
    unsupported = object()
    adapter, _, _, gateway = _build()

    with pytest.raises(TypeError):
        adapter.admit_and_reason(
            text="do not synthesize evidence",
            owner="Carlos",
            explicit_document_ids=(),
            explicit_sources=(unsupported,),
            explicit_evidence_references=(),
            visual_context_contribution=None,
            now=datetime(2026, 9, 20, 18, 3, tzinfo=timezone.utc),
        )

    assert gateway.calls == []


def test_post_12741_duplicate_converged_evidence_is_rejected_before_reasoning():
    source = object()
    duplicate = _Reference("same-evidence")
    adapter, _, _, gateway = _build(normalized={source: duplicate})

    with pytest.raises(ValueError):
        adapter.admit_and_reason(
            text="reject duplicate admission",
            owner="Carlos",
            explicit_document_ids=(),
            explicit_sources=(source,),
            explicit_evidence_references=(duplicate,),
            visual_context_contribution=None,
            now=datetime(2026, 9, 20, 18, 4, tzinfo=timezone.utc),
        )

    assert gateway.calls == []


def test_post_12741_non_composition_authorities_remain_byte_identical():
    for relative_path, expected_hash in PROTECTED_HASHES.items():
        payload = (ROOT / relative_path).read_bytes()
        assert sha256(payload).hexdigest() == expected_hash, relative_path
