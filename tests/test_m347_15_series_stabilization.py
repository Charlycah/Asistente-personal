import ast
import inspect
from pathlib import Path

from core.cognitive_memory import (
    MemoryWriteDisposition,
    MemoryWriteReason,
)
from core.cognitive_memory_integration import CognitiveMemoryIntegration
from core.cognitive_memory_recall import (
    CognitiveMemoryRecallRequest,
    MemoryRelevanceReason,
    SessionContinuityReason,
)
from core.conversation_strategy import (
    CognitiveAction,
    ConversationContext,
    ConversationStrategyPlanner,
)

ROOT = Path(__file__).resolve().parents[1]


def _class_definitions(class_name: str) -> tuple[Path, ...]:
    definitions: list[Path] = []
    for path in (ROOT / "core").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        if any(
            isinstance(node, ast.ClassDef) and node.name == class_name
            for node in tree.body
        ):
            definitions.append(path.relative_to(ROOT))
    return tuple(definitions)


def test_m347_series_has_complete_milestone_documentation():
    milestone_dir = ROOT / "docs" / "milestones"
    expected = {
        3: "M347_3_BASELINE_VERIFICABLE_M347_2.md",
        4: "M347_4_CLASIFICACION_EXPLICITA_DE_INTENCION.md",
        5: "M347_5_PLANIFICACION_COGNITIVA_BASADA_EN_INTENCION.md",
        6: "M347_6_SELECCION_COGNITIVA_DE_ACCIONES.md",
        7: "M347_7_TRAZABILIDAD_INTERNA_DE_DECISIONES.md",
        8: "M347_8_EXPLICACION_RESUMIDA_PARA_EL_USUARIO.md",
        9: "M347_9_DIAGNOSTICO_DE_DECISIONES_FALLIDAS.md",
        10: "M347_10_MODELO_EXPLICITO_DE_CONTEXTO_CONVERSACIONAL.md",
        11: "M347_11_POLITICA_DE_ESCRITURA_EN_MEMORIA.md",
        12: "M347_12_RECUPERACION_RELEVANTE_DE_MEMORIA.md",
        13: "M347_13_CONTINUIDAD_ENTRE_SESIONES.md",
        14: "M347_14_PRUEBAS_INTEGRALES_COGNITIVAS.md",
        15: "M347_15_ESTABILIZACION_DE_LA_SERIE.md",
    }

    assert all((milestone_dir / name).is_file() for name in expected.values())


def test_m347_15_remains_protected_after_canonical_base_advances():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

    assert "Base canónica actual:** M" in readme
    assert readme.index("## Milestone M347.15") < readme.index("## Milestone M347.14")
    assert changelog.startswith("# M347.15 — Estabilización de la serie")


def test_canonical_m347_authorities_have_single_core_definition():
    expected = {
        "ConversationContext": Path("core/conversation_strategy.py"),
        "ConversationStrategyPlanner": Path("core/conversation_strategy.py"),
        "CognitiveLearningPolicy": Path("core/cognitive_memory.py"),
        "CognitiveMemoryRecall": Path("core/cognitive_memory_recall.py"),
        "CognitiveMemoryIntegration": Path("core/cognitive_memory_integration.py"),
        "MemoryPromptContextBuilder": Path("core/memory_prompt_context.py"),
    }

    for class_name, path in expected.items():
        assert _class_definitions(class_name) == (path,)


def test_public_m347_signatures_keep_compatible_optional_extensions():
    plan = inspect.signature(ConversationStrategyPlanner.plan)
    process_turn = inspect.signature(CognitiveMemoryIntegration.process_turn)
    recall_request = inspect.signature(CognitiveMemoryRecallRequest)

    assert plan.parameters["context"].default is None
    assert process_turn.parameters["recall_limit"].default == 5
    assert process_turn.parameters["enable_learning"].default is True
    assert process_turn.parameters["enable_recall"].default is True
    assert process_turn.parameters["context"].default is None
    assert process_turn.parameters["session_profile"].default is None
    assert recall_request.parameters["strategy"].default is None
    assert recall_request.parameters["limit"].default == 5
    assert recall_request.parameters["minimum_score"].default == 0.35
    assert recall_request.parameters["session_profile"].default is None


def test_m347_canonical_contract_values_remain_stable():
    assert CognitiveAction.ANSWER.value == "answer"
    assert CognitiveAction.REVISE_CONTEXT.value == "revise_context"
    assert MemoryWriteDisposition.WRITE.value == "write"
    assert MemoryWriteDisposition.REVIEW.value == "review"
    assert MemoryWriteDisposition.SKIP.value == "skip"
    assert MemoryWriteReason.DURABLE_CANDIDATE.value == "durable_candidate"
    assert MemoryRelevanceReason.RELEVANT_MEMORY_FOUND.value == "relevant_memory_found"
    assert SessionContinuityReason.CROSS_SESSION_MEMORY.value == "cross_session_memory"

    context = ConversationContext()
    assert context.turn_index == 0
    assert context.has_prior_context is False
