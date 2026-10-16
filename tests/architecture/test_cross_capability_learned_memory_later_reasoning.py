from __future__ import annotations

from pathlib import Path

from app.memory_consolidation import OfficialMemoryGateway
from app.productive_governed_learning_wiring import (
    ProductiveGovernedLearningOutcome,
    ProductiveGovernedLearningWiring,
)
from core.llm_provider import LLMRequest
from core.memory_runtime_integration import (
    MemoryRuntimeConfig,
    MemoryRuntimeIntegration,
)

from .test_post_m409_1_governed_learning_productive_end_to_end_wiring_v1 import (
    _response,
)
from .test_post_m409_1_m369_explicit_human_learning_approval_v1 import (
    _evaluation,
)


def _runtime(root: Path) -> MemoryRuntimeIntegration:
    return MemoryRuntimeIntegration(MemoryRuntimeConfig(root_path=root))


def _learn(runtime: MemoryRuntimeIntegration):
    evaluation = _evaluation()
    wiring = ProductiveGovernedLearningWiring(
        OfficialMemoryGateway(runtime, owner="Carlos")
    )
    return wiring.execute(
        evaluation,
        _response(evaluation),
        current_turn_text="Sí",
    )


def _recall(
    runtime: MemoryRuntimeIntegration,
    text: str,
    *,
    owner: str = "Carlos",
):
    return runtime.enrich(
        owner=owner,
        text=text,
        request=LLMRequest(prompt=text),
    )


def test_cci02_exact_topic_learned_memory_reaches_later_cognitive_request(
    tmp_path: Path,
) -> None:
    runtime = _runtime(tmp_path / "memory")
    learned = _learn(runtime)

    later = _recall(runtime, "¿Cómo prefiero hacer Ruff y pytest?")

    assert learned.outcome is ProductiveGovernedLearningOutcome.STORED
    assert learned.stored_memory_ids == ("private:1",)
    assert later.context_included is True
    assert later.recalled_memory_ids == learned.stored_memory_ids
    assert later.request.metadata["memory_context"] == "included"
    assert "ruff antes de pytest" in later.request.prompt.casefold()


def test_cci02_contextual_reuse_does_not_require_literal_repetition(
    tmp_path: Path,
) -> None:
    runtime = _runtime(tmp_path / "memory")
    learned = _learn(runtime)

    later = _recall(
        runtime,
        "Antes de entregar, ¿qué validación debería ejecutar primero?",
    )

    assert later.context_included is True
    assert later.recalled_memory_ids == learned.stored_memory_ids
    assert "ruff antes de pytest" in later.request.prompt.casefold()


def test_cci02_learned_memory_survives_runtime_reconstruction(
    tmp_path: Path,
) -> None:
    root = tmp_path / "memory"
    first_runtime = _runtime(root)
    learned = _learn(first_runtime)

    later_runtime = _runtime(root)
    later = _recall(later_runtime, "¿Cómo prefiero hacer Ruff y pytest?")

    assert later.context_included is True
    assert later.recalled_memory_ids == learned.stored_memory_ids
    assert "ruff antes de pytest" in later.request.prompt.casefold()


def test_cci02_rejected_learning_cannot_be_recalled_later(
    tmp_path: Path,
) -> None:
    runtime = _runtime(tmp_path / "memory")
    evaluation = _evaluation()
    wiring = ProductiveGovernedLearningWiring(
        OfficialMemoryGateway(runtime, owner="Carlos")
    )
    rejected = wiring.execute(
        evaluation,
        _response(evaluation, "No"),
        current_turn_text="No",
    )

    later = _recall(runtime, "¿Cómo prefiero hacer Ruff y pytest?")

    assert rejected.outcome is ProductiveGovernedLearningOutcome.REJECTED
    assert runtime.count(owner="Carlos") == 0
    assert later.context_included is False
    assert later.recalled_memory_ids == ()


def test_cci02_irrelevant_episode_does_not_receive_learned_memory(
    tmp_path: Path,
) -> None:
    runtime = _runtime(tmp_path / "memory")
    _learn(runtime)

    later = _recall(runtime, "¿Qué prefiero comer hoy?")

    assert later.context_included is False
    assert later.recalled_memory_ids == ()
    assert later.rationale == ("no_relevant_memory",)


def test_cci02_private_owner_scope_is_preserved_across_episode(
    tmp_path: Path,
) -> None:
    runtime = _runtime(tmp_path / "memory")
    _learn(runtime)

    other_owner = _recall(
        runtime,
        "¿Cómo prefiero hacer Ruff y pytest?",
        owner="Cristina",
    )

    assert other_owner.context_included is False
    assert other_owner.recalled_memory_ids == ()
    assert runtime.count(owner="Cristina") == 0


def test_cci02_repeated_approval_is_idempotent_and_preserves_provenance(
    tmp_path: Path,
) -> None:
    runtime = _runtime(tmp_path / "memory")
    first = _learn(runtime)
    second = _learn(runtime)
    records = runtime.search(owner="Carlos", query="ruff", limit=10)

    assert first.outcome is ProductiveGovernedLearningOutcome.STORED
    assert second.outcome is ProductiveGovernedLearningOutcome.ALREADY_STORED
    assert first.stored_memory_ids == second.stored_memory_ids
    assert runtime.count(owner="Carlos") == 1
    assert len(records) == 1
    assert records[0].metadata["approver"] == "Carlos"
    assert records[0].metadata["approval_scope"] == "project"
    assert records[0].metadata["human_response_reference"] == (
        "conversation:approval-answer"
    )
