from __future__ import annotations

import importlib
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

PROTECTED_HASHES = {
    "app/governed_reasoning_runtime.py": (
        "f8c96d92c08fff1b9219afd68974b79ba319f087b2fb32fbb20d5856aaa91f2f"
    ),
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
    "app/same_episode_explicit_evidence_convergence_adapter.py": (
        "5be01adfe0c0e3a32065bcb15918013d7e20e5cb7e0092072c88df1dea5aef3d"
    ),
}


class _SameEpisodeAdapter:
    def __init__(self, *, result=None, error=None):
        self.result = result
        self.error = error
        self.calls = []

    def admit_and_reason(self, **kwargs):
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error
        return self.result


def _adapter_class():
    module = importlib.import_module(
        "app.ordinary_turn_multisource_reachability_adapter"
    )
    return module.OrdinaryTurnMultisourceReachabilityAdapterV1


def _build(*, result=None, error=None):
    same_episode_adapter = _SameEpisodeAdapter(result=result, error=error)
    adapter = _adapter_class()(
        same_episode_adapter=same_episode_adapter,
    )
    return adapter, same_episode_adapter


def test_post_12748_external_bounded_ordinary_turn_reachability_adapter_exists():
    cls = _adapter_class()
    assert cls.__name__ == "OrdinaryTurnMultisourceReachabilityAdapterV1"


def test_post_12748_explicit_turn_inputs_delegate_once_without_reinterpretation():
    expected = object()
    document_ids = ("document-1",)
    sources = (object(),)
    references = (object(),)
    visual = object()
    now = datetime(2026, 9, 20, 21, 0, tzinfo=timezone.utc)
    adapter, same_episode_adapter = _build(result=expected)

    result = adapter.admit_and_reason(
        text="compare the explicitly selected sources",
        owner="Carlos",
        explicit_document_ids=document_ids,
        explicit_sources=sources,
        explicit_evidence_references=references,
        visual_context_contribution=visual,
        now=now,
    )

    assert result is expected
    assert same_episode_adapter.calls == [
        {
            "text": "compare the explicitly selected sources",
            "owner": "Carlos",
            "explicit_document_ids": document_ids,
            "explicit_sources": sources,
            "explicit_evidence_references": references,
            "visual_context_contribution": visual,
            "now": now,
        }
    ]


def test_post_12748_absent_explicit_evidence_does_not_delegate_or_reason():
    adapter, same_episode_adapter = _build(result=object())

    result = adapter.admit_and_reason(
        text="ordinary turn without explicit evidence",
        owner="Carlos",
        explicit_document_ids=(),
        explicit_sources=(),
        explicit_evidence_references=(),
        visual_context_contribution=None,
        now=datetime(2026, 9, 20, 21, 1, tzinfo=timezone.utc),
    )

    assert result is None
    assert same_episode_adapter.calls == []


def test_post_12748_visual_alone_does_not_activate_explicit_convergence():
    adapter, same_episode_adapter = _build(result=object())

    result = adapter.admit_and_reason(
        text="visual only",
        owner="Carlos",
        explicit_document_ids=(),
        explicit_sources=(),
        explicit_evidence_references=(),
        visual_context_contribution=object(),
        now=datetime(2026, 9, 20, 21, 2, tzinfo=timezone.utc),
    )

    assert result is None
    assert same_episode_adapter.calls == []


def test_post_12748_downstream_rejection_propagates_fail_closed_without_fallback():
    rejection = ValueError("downstream convergence rejected explicit evidence")
    adapter, same_episode_adapter = _build(error=rejection)

    with pytest.raises(ValueError, match="downstream convergence rejected"):
        adapter.admit_and_reason(
            text="do not fall back to another reasoning path",
            owner="Carlos",
            explicit_document_ids=("document-1",),
            explicit_sources=(),
            explicit_evidence_references=(),
            visual_context_contribution=None,
            now=datetime(2026, 9, 20, 21, 3, tzinfo=timezone.utc),
        )

    assert len(same_episode_adapter.calls) == 1


def test_post_12748_transport_seam_requires_existing_same_episode_authority():
    cls = _adapter_class()

    with pytest.raises(TypeError):
        cls(same_episode_adapter=object())


def test_post_12748_existing_authorities_remain_byte_identical():
    for relative_path, expected_hash in PROTECTED_HASHES.items():
        payload = (ROOT / relative_path).read_bytes()
        assert sha256(payload).hexdigest() == expected_hash, relative_path
