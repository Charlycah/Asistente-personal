from pathlib import Path

from core.cognitive_memory import LearningAction, LearningCandidate, LearningCategory
from core.cognitive_memory_integration import CognitiveMemoryIntegration
from core.cognitive_memory_store import CognitiveMemoryStore, CognitiveMemoryStoreConfig
from core.cognitive_pipeline import CognitivePipeline
from core.llm_provider import LLMRequest, LLMResponse
from core.llm_service import LLMService
from core.provider_router import ProviderRouter


class RecordingProvider:
    name = "test"

    def __init__(self) -> None:
        self.requests: list[LLMRequest] = []

    def generate(self, request: LLMRequest) -> LLMResponse:
        self.requests.append(request)
        return LLMResponse(text="respuesta cognitiva", provider=self.name)


def make_store(tmp_path: Path) -> CognitiveMemoryStore:
    return CognitiveMemoryStore(
        CognitiveMemoryStoreConfig(db_path=tmp_path / "brain.sqlite")
    )


def make_pipeline(
    tmp_path: Path,
    provider: RecordingProvider | None = None,
) -> CognitivePipeline:
    store = make_store(tmp_path)
    llm_service = None
    if provider is not None:
        llm_service = LLMService(ProviderRouter([provider]))
    return CognitivePipeline(
        CognitiveMemoryIntegration(store),
        llm_service=llm_service,
    )


def seed_memory(store: CognitiveMemoryStore, content: str) -> int:
    return store.store_candidate(
        LearningCandidate(
            content=content,
            category=LearningCategory.PROJECT_CONVENTION,
            action=LearningAction.STORE,
            confidence=0.9,
            reason="project_convention_is_reusable",
            tags=("project_convention", "project_work", "project_focused"),
            metadata={"source": "test"},
        )
    )


def test_cognitive_pipeline_calls_llm_with_plain_prompt(tmp_path: Path):
    provider = RecordingProvider()
    pipeline = make_pipeline(tmp_path, provider)

    result = pipeline.process_turn("Explícame la arquitectura de ROBY")

    assert result.called_llm is True
    assert result.llm_response is not None
    assert result.llm_response.text == "respuesta cognitiva"
    assert provider.requests[0].prompt == "Explícame la arquitectura de ROBY"


def test_cognitive_pipeline_enriches_prompt_with_recalled_memory(tmp_path: Path):
    store = make_store(tmp_path)
    seed_memory(store, "En ROBY usamos milestones con ruff y pytest")
    provider = RecordingProvider()
    pipeline = CognitivePipeline(
        CognitiveMemoryIntegration(store),
        llm_service=LLMService(ProviderRouter([provider])),
    )

    result = pipeline.process_turn("Seguimos con ROBY y los milestones")

    assert result.prompt_context.should_include is True
    assert "Contexto de memoria relevante de ROBY" in result.final_prompt
    assert "ruff y pytest" in result.final_prompt
    assert provider.requests[0].prompt == result.final_prompt


def test_cognitive_pipeline_builds_system_prompt_from_strategy(tmp_path: Path):
    provider = RecordingProvider()
    pipeline = make_pipeline(tmp_path, provider)

    result = pipeline.process_turn("Necesito implementar una clase Python")

    assert "Intención cognitiva: code_request" in result.system_prompt
    assert "Formato: code" in result.system_prompt
    assert provider.requests[0].system_prompt == result.system_prompt


def test_cognitive_pipeline_passes_metadata_to_llm_service(tmp_path: Path):
    provider = RecordingProvider()
    pipeline = make_pipeline(tmp_path, provider)

    pipeline.process_turn("Hablemos de ROBY y Architecture 1.0")

    assert provider.requests[0].metadata["intent"] == "project_work"
    assert provider.requests[0].metadata["memory_included"] == "false"


def test_cognitive_pipeline_stores_learning_candidates(tmp_path: Path):
    provider = RecordingProvider()
    pipeline = make_pipeline(tmp_path, provider)

    result = pipeline.process_turn(
        "En ROBY siempre cerramos milestones con Ruff y pytest"
    )

    assert result.memory_result.learned_something is True
    assert result.memory_result.stored_memory_ids


def test_cognitive_pipeline_can_disable_learning(tmp_path: Path):
    provider = RecordingProvider()
    pipeline = make_pipeline(tmp_path, provider)

    result = pipeline.process_turn(
        "En ROBY siempre cerramos milestones con Ruff y pytest",
        enable_learning=False,
    )

    assert result.memory_result.learned_something is False
    assert result.memory_result.stored_memory_ids == ()


def test_cognitive_pipeline_can_disable_recall(tmp_path: Path):
    store = make_store(tmp_path)
    seed_memory(store, "En ROBY usamos milestones con ruff y pytest")
    provider = RecordingProvider()
    pipeline = CognitivePipeline(
        CognitiveMemoryIntegration(store),
        llm_service=LLMService(ProviderRouter([provider])),
    )

    result = pipeline.process_turn(
        "Seguimos con ROBY y los milestones",
        enable_recall=False,
    )

    assert result.prompt_context.should_include is False
    assert result.prompt_context.reason == "recall_disabled"
    assert result.final_prompt == "Seguimos con ROBY y los milestones"


def test_cognitive_pipeline_skips_llm_when_disabled(tmp_path: Path):
    provider = RecordingProvider()
    pipeline = make_pipeline(tmp_path, provider)

    result = pipeline.process_turn("Explícame ROBY", call_llm=False)

    assert result.called_llm is False
    assert result.skipped_llm_reason == "llm_call_disabled"
    assert provider.requests == []


def test_cognitive_pipeline_skips_llm_for_domestic_strategy(tmp_path: Path):
    provider = RecordingProvider()
    pipeline = make_pipeline(tmp_path, provider)

    result = pipeline.process_turn("Qué hora es")

    assert result.called_llm is False
    assert result.skipped_llm_reason == "strategy_does_not_require_llm"
    assert provider.requests == []


def test_cognitive_pipeline_handles_missing_llm_service(tmp_path: Path):
    pipeline = make_pipeline(tmp_path)

    result = pipeline.process_turn("Explícame la arquitectura de ROBY")

    assert result.called_llm is False
    assert result.skipped_llm_reason == "llm_service_not_configured"
    assert result.final_prompt == "Explícame la arquitectura de ROBY"
