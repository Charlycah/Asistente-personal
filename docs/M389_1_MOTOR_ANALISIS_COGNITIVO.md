# M389.1 — Motor de Análisis Cognitivo

## Objetivo

M389.1 incorpora `CognitiveAnalysisAuthority` como única autoridad de análisis
cognitivo. Produce un informe técnico a partir del expediente inmutable M387.2
cuando el turno y su reflexión ya terminaron y el ciclo fue sellado.

El análisis describe lo observado. No vuelve a razonar, decidir ni responder.

## Integración posterior al turno

`UnifiedBrain` solicita el último `CognitiveTurnDossier` sólo después de que
`OfficialConversationGateway` devuelve el turno y sella su ciclo. El resultado
queda disponible en `UnifiedBrain.cognitive_analysis` como diagnóstico separado.

La integración no modifica `OfficialConversationGateway`; por eso
`CanonicalCognitiveCore(` permanece exactamente en la línea 52 de
`app/official_conversation_gateway.py`.

## Informe

`CognitiveAnalysisReport` contiene exclusivamente metadatos estructurados:

- linaje y huellas deterministas del expediente;
- resultado del ciclo;
- autoridades que participaron;
- nodos visitados, degradados, bloqueados o sin evidencia;
- códigos de contradicción y riesgo ya derivados de evidencia técnica;
- resumen epistemológico separado entre hecho, inferencia, hipótesis y
  desconocimiento.

No contiene texto de usuario o respuesta, recuerdos, planes, permisos,
candidatos de aprendizaje ni razonamiento privado. No usa una hora de análisis,
porque un valor temporal ajeno al expediente rompería la repetibilidad.

## Contrato de solo lectura

La autoridad es pura y no conserva estado mutable. Recibe un expediente de solo
lectura y devuelve dataclasses inmutables. No importa gateways de memoria,
planificación, decisión, herramientas o aprendizaje; no persiste archivos y no
produce efectos externos.

Carlos y Cristina mantienen copropiedad y autoridad exactamente iguales. M389.1
no utiliza ni reintroduce una identidad técnica `Familia`.

## Determinismo

El orden procede del grafo canónico. La huella SHA-256 se calcula sólo con el
esquema M389.1 y los campos técnicos del expediente. El mismo expediente produce
un informe exactamente igual, incluida su huella.

## Degradación segura

Si falta el expediente o la autoridad lanza una excepción, `UnifiedBrain`
conserva el turno y su respuesta sin cambios. Expone un
`CognitiveAnalysisResult` degradado con el código técnico
`analysis:internal_failure`, sin propagar el fallo al usuario y sin fabricar un
informe parcial.

## Límites permanentes

M389.1 no puede:

- escribir o recuperar memoria;
- crear o activar aprendizaje;
- planificar, decidir o cambiar permisos;
- modificar la respuesta;
- ejecutar acciones internas o externas;
- cambiar estado productivo;
- sustituir una autoridad existente o crear otro cerebro.

## Pruebas

La suite `test_m389_1_*.py` certifica autoridad única, estructura y privacidad
del informe, solo lectura, degradación segura, consistencia epistemológica,
repetibilidad, ausencia de efectos ocultos y preservación de la línea 52.

