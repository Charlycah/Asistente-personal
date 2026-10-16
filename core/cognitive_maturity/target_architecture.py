from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CognitiveNodeRole(str, Enum):
    ENTRY = "entry"
    COORDINATOR = "coordinator"
    AUTHORITY = "authority"
    GATE = "gate"
    ADAPTER = "adapter"
    OBSERVER = "observer"


class CognitiveNodeStatus(str, Enum):
    OPERATIONAL = "operational"
    PARTIAL = "partial"
    CONTRACT_ONLY = "contract_only"


@dataclass(frozen=True)
class TargetCognitiveNode:
    node_id: str
    title: str
    role: CognitiveNodeRole
    status: CognitiveNodeStatus
    existing_authority: str
    depends_on: tuple[str, ...]
    purpose: str
    owns_domain_authority: bool = False
    may_produce_external_effect: bool = False
    grants_action_authority: bool = False

    def __post_init__(self) -> None:
        text = (
            self.node_id,
            self.title,
            self.existing_authority,
            self.purpose,
            *self.depends_on,
        )
        if any(not item.strip() for item in text):
            raise ValueError("target cognitive node text must not be blank")
        if len(self.depends_on) != len(set(self.depends_on)):
            raise ValueError("target cognitive node dependencies must be unique")
        if self.grants_action_authority:
            raise ValueError("target architecture cannot grant action authority")
        if self.role is CognitiveNodeRole.COORDINATOR and self.owns_domain_authority:
            raise ValueError("unified coordinator cannot own domain authority")
        if self.may_produce_external_effect and self.role is not CognitiveNodeRole.GATE:
            raise ValueError("only the action gate may produce an external effect")


@dataclass(frozen=True)
class TargetCognitiveArchitecture:
    nodes: tuple[TargetCognitiveNode, ...]
    entry_node_id: str
    coordinator_node_id: str
    response_node_id: str
    action_gate_node_id: str
    reflection_node_id: str
    diagnostics_node_id: str
    invariants: tuple[str, ...]

    def __post_init__(self) -> None:
        node_ids = tuple(node.node_id for node in self.nodes)
        if not node_ids or len(node_ids) != len(set(node_ids)):
            raise ValueError("target cognitive architecture node ids must be unique")
        node_id_set = set(node_ids)
        references = (
            self.entry_node_id,
            self.coordinator_node_id,
            self.response_node_id,
            self.action_gate_node_id,
            self.reflection_node_id,
            self.diagnostics_node_id,
        )
        if any(reference not in node_id_set for reference in references):
            raise ValueError("target cognitive architecture references unknown nodes")
        if not self.invariants or any(not item.strip() for item in self.invariants):
            raise ValueError("target cognitive architecture requires invariants")
        by_id = {node.node_id: node for node in self.nodes}
        for node in self.nodes:
            if any(dependency not in by_id for dependency in node.depends_on):
                raise ValueError("target cognitive dependency references unknown node")
            if node.node_id in node.depends_on:
                raise ValueError("target cognitive node cannot depend on itself")
        if by_id[self.entry_node_id].role is not CognitiveNodeRole.ENTRY:
            raise ValueError("target cognitive entry must use entry role")
        coordinators = [
            node for node in self.nodes if node.role is CognitiveNodeRole.COORDINATOR
        ]
        if len(coordinators) != 1 or coordinators[0].node_id != (
            self.coordinator_node_id
        ):
            raise ValueError("target architecture requires one unified coordinator")
        if self._has_cycle(by_id):
            raise ValueError("target cognitive turn graph must be acyclic")

    @staticmethod
    def _has_cycle(by_id: dict[str, TargetCognitiveNode]) -> bool:
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(node_id: str) -> bool:
            if node_id in visiting:
                return True
            if node_id in visited:
                return False
            visiting.add(node_id)
            if any(visit(item) for item in by_id[node_id].depends_on):
                return True
            visiting.remove(node_id)
            visited.add(node_id)
            return False

        return any(visit(node_id) for node_id in by_id)

    def node(self, node_id: str) -> TargetCognitiveNode:
        normalized = node_id.strip().casefold()
        for node in self.nodes:
            if node.node_id.casefold() == normalized:
                return node
        raise KeyError(node_id)


TARGET_COGNITIVE_ARCHITECTURE = TargetCognitiveArchitecture(
    nodes=(
        TargetCognitiveNode(
            "conversation_ingress",
            "Entrada conversacional oficial",
            CognitiveNodeRole.ENTRY,
            CognitiveNodeStatus.OPERATIONAL,
            "app.official_conversation_gateway:OfficialConversationGateway",
            (),
            "Recibir un turno por la única frontera conversacional pública.",
        ),
        TargetCognitiveNode(
            "unified_coordination",
            "Coordinación cerebral unificada",
            CognitiveNodeRole.COORDINATOR,
            CognitiveNodeStatus.OPERATIONAL,
            "app.unified_brain:UnifiedBrain",
            ("conversation_ingress",),
            "Coordinar el recorrido sin absorber autoridades de dominio.",
        ),
        TargetCognitiveNode(
            "identity_and_context",
            "Identidad y contexto",
            CognitiveNodeRole.AUTHORITY,
            CognitiveNodeStatus.OPERATIONAL,
            "canonical identity and conversation context authorities",
            ("unified_coordination",),
            "Resolver copropiedad, interlocutor, sesión y contexto inmediato.",
            owns_domain_authority=True,
        ),
        TargetCognitiveNode(
            "perception_and_evidence",
            "Percepción y evidencia",
            CognitiveNodeRole.GATE,
            CognitiveNodeStatus.PARTIAL,
            "multimodal observation contracts and governed evidence",
            ("unified_coordination",),
            "Admitir solo observaciones reales, consentidas y trazables.",
            owns_domain_authority=True,
        ),
        TargetCognitiveNode(
            "memory_recall",
            "Recuperación de memoria",
            CognitiveNodeRole.AUTHORITY,
            CognitiveNodeStatus.OPERATIONAL,
            "app.canonical_memory_facade:CanonicalMemoryFacade",
            ("identity_and_context", "perception_and_evidence"),
            "Recuperar recuerdos conjuntos pertinentes sin escribir memoria.",
            owns_domain_authority=True,
        ),
        TargetCognitiveNode(
            "knowledge_retrieval",
            "Recuperación de conocimiento",
            CognitiveNodeRole.AUTHORITY,
            CognitiveNodeStatus.PARTIAL,
            "core.knowledge_retrieval_execution:KnowledgeRetrievalExecutionGateway",
            ("identity_and_context", "perception_and_evidence"),
            "Obtener conocimiento con fuente, vigencia y alcance gobernado.",
            owns_domain_authority=True,
        ),
        TargetCognitiveNode(
            "epistemic_classification",
            "Clasificación epistemológica",
            CognitiveNodeRole.GATE,
            CognitiveNodeStatus.CONTRACT_ONLY,
            "core.cognitive_maturity.epistemic:EpistemicClassifier",
            ("memory_recall", "knowledge_retrieval", "perception_and_evidence"),
            "Separar hechos, inferencias, hipótesis y desconocimiento.",
        ),
        TargetCognitiveNode(
            "cognitive_state",
            "Estado cognitivo",
            CognitiveNodeRole.AUTHORITY,
            CognitiveNodeStatus.PARTIAL,
            "app.canonical_cognitive_state_facade:CanonicalCognitiveStateFacade",
            ("identity_and_context", "memory_recall"),
            "Aportar atención, objetivos, dudas y pendientes de forma explícita.",
            owns_domain_authority=True,
        ),
        TargetCognitiveNode(
            "relational_affective_context",
            "Contexto relacional y afectivo simulado",
            CognitiveNodeRole.ADAPTER,
            CognitiveNodeStatus.PARTIAL,
            "relationship model and adaptive personality authorities",
            ("identity_and_context", "memory_recall", "cognitive_state"),
            "Ajustar acompañamiento y expresión sin autoridad decisoria.",
        ),
        TargetCognitiveNode(
            "intent_and_reasoning",
            "Intención y razonamiento",
            CognitiveNodeRole.AUTHORITY,
            CognitiveNodeStatus.OPERATIONAL,
            "core.governed_reasoning:GovernedReasoningManager",
            (
                "epistemic_classification",
                "cognitive_state",
                "relational_affective_context",
            ),
            "Interpretar la necesidad y derivar conclusiones gobernadas.",
            owns_domain_authority=True,
        ),
        TargetCognitiveNode(
            "planning",
            "Planificación",
            CognitiveNodeRole.AUTHORITY,
            CognitiveNodeStatus.OPERATIONAL,
            "app.canonical_planning_facade:CanonicalPlanningFacade",
            ("intent_and_reasoning",),
            "Preparar alternativas y planes sin convertirlos en autorización.",
            owns_domain_authority=True,
        ),
        TargetCognitiveNode(
            "safety_permissions",
            "Seguridad, alcance y permisos",
            CognitiveNodeRole.GATE,
            CognitiveNodeStatus.OPERATIONAL,
            "scope guard, permission consent and M386 boundaries",
            ("planning", "epistemic_classification"),
            "Aplicar límites, consentimiento, riesgo y degradación segura.",
            owns_domain_authority=True,
        ),
        TargetCognitiveNode(
            "decision",
            "Decisión cognitiva",
            CognitiveNodeRole.AUTHORITY,
            CognitiveNodeStatus.OPERATIONAL,
            "app.canonical_decision_facade:CanonicalDecisionFacade",
            ("planning", "safety_permissions"),
            "Seleccionar respuesta, propuesta, abstención o acción autorizable.",
            owns_domain_authority=True,
        ),
        TargetCognitiveNode(
            "response_composition",
            "Composición de respuesta",
            CognitiveNodeRole.AUTHORITY,
            CognitiveNodeStatus.OPERATIONAL,
            "core.operational_response_assembly:OperationalResponseAssembler",
            ("decision", "relational_affective_context"),
            "Generar una respuesta honesta, proporcional y trazable.",
            owns_domain_authority=True,
        ),
        TargetCognitiveNode(
            "action_gate",
            "Compuerta de acción",
            CognitiveNodeRole.GATE,
            CognitiveNodeStatus.PARTIAL,
            "controlled autonomy gate and official tool gateway",
            ("decision", "safety_permissions"),
            "Delegar solo acciones preconvalidadas sin ampliar alcance.",
            owns_domain_authority=True,
            may_produce_external_effect=True,
        ),
        TargetCognitiveNode(
            "post_turn_reflection",
            "Reflexión posterior",
            CognitiveNodeRole.OBSERVER,
            CognitiveNodeStatus.OPERATIONAL,
            "app.canonical_reflection_facade:CanonicalReflectionFacade",
            ("response_composition", "action_gate"),
            "Evaluar resultado, límites y degradación sin reescribir la decisión.",
            owns_domain_authority=True,
        ),
        TargetCognitiveNode(
            "learning_candidate",
            "Candidato de aprendizaje",
            CognitiveNodeRole.ADAPTER,
            CognitiveNodeStatus.PARTIAL,
            "governed learning and evolution guard",
            ("post_turn_reflection",),
            "Proponer aprendizaje revisable sin activarlo automáticamente.",
        ),
        TargetCognitiveNode(
            "unified_diagnostics",
            "Diagnóstico cognitivo unificado",
            CognitiveNodeRole.OBSERVER,
            CognitiveNodeStatus.PARTIAL,
            "app.unified_brain:UnifiedBrainDiagnosticSnapshot",
            ("post_turn_reflection", "learning_candidate"),
            "Exponer cobertura, salud y brechas sin contenido sensible.",
        ),
    ),
    entry_node_id="conversation_ingress",
    coordinator_node_id="unified_coordination",
    response_node_id="response_composition",
    action_gate_node_id="action_gate",
    reflection_node_id="post_turn_reflection",
    diagnostics_node_id="unified_diagnostics",
    invariants=(
        "Existe una sola entrada conversacional y un solo coordinador.",
        "El coordinador no absorbe memoria, decisión, permisos ni ejecución.",
        "Evidencia y clasificación epistemológica preceden al razonamiento.",
        "Seguridad y permisos preceden a decisión, respuesta y acción.",
        "Solo la compuerta oficial puede producir un efecto externo.",
        "Reflexión y aprendizaje ocurren después de respuesta o acción.",
        "El aprendizaje produce candidatos y nunca cambia conducta automáticamente.",
        "El diagnóstico observa metadatos sin contenido sensible ni autoridad.",
    ),
)

