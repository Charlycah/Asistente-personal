# M391.1 — Consolidación Cognitiva Gobernada

## Objetivo

Iniciar la Época IV — Inteligencia Continua extendiendo la autoridad periódica
certificada para evaluar consolidación cognitiva durante períodos de inactividad
**explícitamente declarados**, sin crear un segundo cerebro, gestor, scheduler o
proceso autónomo.

## Autoridad

`PeriodicReflectionAuthority` continúa siendo la única autoridad responsable de
la reflexión periódica. M391.1 amplía esa misma autoridad con `consolidate()` y
`consolidate_safely()`; no introduce otro `authority_id`.

Los contratos y la evaluación subordinada viven en
`core/cognitive_maturity/cognitive_consolidation.py` y no poseen autoridad
propia.

## Inactividad explícita

`CognitiveInactivityContext` representa una ventana de inactividad declarada por
un llamador gobernado. Puede distinguir:

- `manual`;
- `short_idle`;
- `extended_idle`.

El contexto no detecta inactividad, no consulta reloj, no inicia temporizadores,
no crea hilos y no mantiene procesos en segundo plano. Una conversación marcada
como activa invalida el contexto.

## Evidencia admitida

La consolidación puede consumir únicamente resultados ya estructurados y
gobernados:

- `PeriodicReflectionReport` de M389.6 como fuente principal obligatoria;
- `UnifiedEpistemicReport` de M389.8 como evidencia epistemológica opcional;
- `M390IntegralEvidenceReport` como evidencia opcional del mundo interior;
- `ConsolidationAssessment` de M366.6 cuando ya existe un candidato de memoria
  evaluado por esa capacidad;
- `LearningCandidate` de M369.1 cuando ya existe un candidato revisable.

M391.1 no vuelve a leer conversación bruta, no crea candidatos a partir de texto
privado y no reemplaza las autoridades que originaron esas evidencias.

## Resultado

`CognitiveConsolidationReport` es inmutable, determinista y de solo lectura. Sus
estados posibles son:

- `stable`;
- `review_recommended`;
- `memory_candidate_available`;
- `learning_candidate_available`;
- `conflict_present`;
- `insufficient_evidence`;
- `degraded`.

Un candidato disponible significa exclusivamente que una autoridad previa ya
produjo una estructura revisable. M391.1 no promueve memoria, no acepta
aprendizaje y no convierte evidencia en verdad permanente.

## Integración con M366.6 y M369.1

M366.6 conserva la evaluación de candidatos de memoria y
`OfficialMemoryGateway` conserva cualquier escritura operacional autorizada.
M391.1 sólo puede reconocer un `ConsolidationAssessment` existente y exponer que
requiere revisión gobernada.

M369.1 conserva la definición del candidato de aprendizaje. M391.1 puede
reconocer un `LearningCandidate` existente, pero no lo crea, acepta ni persiste.

## Mundo interior M390

La evidencia integral M390.8 es opcional y subordinada. Puede aportar evidencia
o exponer un conflicto, pero nunca basta por sí sola para crear memoria,
aprendizaje, objetivos o acciones. Los conflictos permanecen visibles y no se
reparan automáticamente.

## Invariantes

- Una única autoridad: `PeriodicReflectionAuthority`.
- Sin persistencia de memoria.
- Sin creación ni aceptación automática de aprendizaje.
- Sin modificación de planificación, permisos u objetivos.
- Sin creación de tareas o recordatorios.
- Sin ejecución ni programación de acciones.
- Sin threads, `asyncio`, `sleep` o loops residentes.
- Sin contenido conversacional privado en los informes.
- Sin referencia a `.roby/credentials.json`.
- Degradación segura y sin efectos secundarios.
- `CanonicalCognitiveCore(` conserva su posición contractual en
  `app/official_conversation_gateway.py`.

## Alcance futuro

M391.1 define **qué significa consolidar de forma gobernada**. La detección o
activación real durante períodos de reposo queda fuera de este incremento y sólo
podrá añadirse posteriormente mediante un contrato separado, explícito y
subordinado a las autoridades certificadas.
