# ROBY XI.2 — GATE 5.A.2
## Existing Session-Scoped Analysis Mode + UnifiedRuntimeObservability → Governed Level-Specific Read-Only Conversational Projection — CONTRACT BOUNDARY RECONCILIATION

### Estado de entrada
Baseline certificada por el usuario después de GATE 5.A.1 / M395.5 reconciliation:
- M361 sincronizado.
- Ruff limpio.
- pytest: 13,987 PASS.
- 0 FAIL.

Este gate es exclusivamente de reconciliación contractual. No modifica producción.

## 1. Hallazgo material
GATE 5.A.1 cerró correctamente la interacción explícita y el estado efímero por `session_id`, pero `OfficialConversationGateway.analysis_mode_projection(...)` sólo comprueba `status.active` y devuelve el mismo `UnifiedRuntimeObservability().snapshot(runtime)` para PERSONAL, TECHNICAL y ARCHITECTURAL.

Por tanto, existe modo y nivel, pero todavía no existe una proyección diferenciada gobernada por nivel. El residual real G5A-R3 / G5-R2 permanece abierto.

## 2. Autoridades existentes que deben preservarse
- `OfficialConversationGateway`: única frontera oficial de conversación/interacción.
- `UnifiedRuntimeObservability`: única proyección read-only unificada del estado runtime/introspectivo existente.
- `OfficialRuntimeCapabilityRegistry`: autoridad de capacidades; sólo se consume su snapshot ya publicado.
- `CognitiveSelfModel`: sólo se consume el snapshot ya publicado por el cognitive core.
- `CanonicalReflectionFacade`: sólo arquitectura estructural segura + reflexión ya publicada.
- `GovernedSelfDiagnostics`: autoridad existente; Analysis Mode NO ejecuta `diagnose()` para poblar una vista.

No se autoriza crear `AnalysisModeManager`, `AnalysisBrain`, `AnalysisRuntime`, `IntrospectionManager`, otro observability root, otro registry ni otra autoridad cognitiva.

## 3. Naturaleza de la costura mínima
La proyección por nivel debe ser un valor/adaptador subordinado, inmutable y read-only. No posee autoridad, no persiste, no aprende, no ejecuta herramientas y no obtiene información fuera de `UnifiedRuntimeObservabilitySnapshot`.

Flujo canónico:

`OfficialConversationGateway` → estado Analysis Mode de la sesión → `UnifiedRuntimeObservability` → selección read-only por nivel → representación conversacional honesta.

El nivel selecciona qué campos ya publicados se muestran; no cambia qué capacidades puede ejecutar ROBY.

## 4. Contrato PERSONAL
PERSONAL puede proyectar únicamente estado personal/cognitivo ya publicado y seguro, principalmente:
- estado general del cognitive core disponible en observability;
- `self_model` ya publicado;
- contexto conversacional observable cuando sea pertinente.

PERSONAL NO puede:
- consultar Memory automáticamente;
- consultar Learning automáticamente;
- inferir emociones, conciencia o estados subjetivos no publicados;
- exponer chain-of-thought/private reasoning;
- ejecutar reasoning/planning/reflection para completar huecos.

Datos ausentes se representan como `unavailable` / `not provisioned` / equivalente explícito, nunca se inventan.

## 5. Contrato TECHNICAL
TECHNICAL puede seleccionar del snapshot existente:
- `operational`;
- `readiness`;
- `conversation`;
- `capabilities` cuando exista;
- `registered_capabilities`;
- `capability_registry`;
- `cognitive_core`;
- disponibilidad de `self_diagnostics`;
- `recovery` sólo si ya viene publicado en el snapshot recibido; la proyección no debe solicitar/generar un plan.

TECHNICAL NO ejecuta capacidades, recovery, diagnostics, tests, scanners ni introspección adicional.

Episodes, budgets, dependency graph, versions, errors y certifications NO se declaran disponibles salvo que estén explícitamente presentes en la fuente read-only certificada. Este gate no crea esas fuentes.

## 6. Contrato ARCHITECTURAL
ARCHITECTURAL puede seleccionar únicamente metadata arquitectónica ya publicada/certificada en el snapshot existente, incluyendo cuando corresponda:
- `reflection.architecture`;
- `reflection.published_state` ya existente;
- `capability_registry` como inventario oficial de capacidades;
- metadata de disponibilidad de `self_diagnostics`.

ARCHITECTURAL NO es una auditoría viva del repositorio y NO autoriza:
- lectura automática de código/docs/tests;
- escaneo de archivos;
- `GovernedSelfDiagnostics.diagnose()`;
- Ruff/pytest;
- repair/modificación de código;
- inferencias de deuda/duplicación/inconsistencia sin evidencia publicada.

Si no existe evidencia arquitectónica actual en la fuente certificada, la respuesta debe declarar que no está disponible/provisionada.

## 7. Representación conversacional
La salida futura debe ser una proyección entendible, estable y trazable; no el snapshot bruto completo presentado indistintamente en los tres niveles.

La representación puede incluir:
- `level`;
- `available` / disponibilidad explícita;
- secciones/campos seleccionados;
- `unavailable` o razones de no provisión cuando falte una fuente.

No debe reconstruir ni revelar razonamiento privado. Debe distinguir estado publicado de ausencia de evidencia.

## 8. Residuales después de esta reconciliación
- **G5A2-R1 — Level-specific projection contract not implemented.** Falta la selección productiva diferenciada PERSONAL/TECHNICAL/ARCHITECTURAL.
- **G5A2-R2 — Conversational representation not implemented.** Falta una forma estable/read-only de convertir la selección en vista conversacional sin devolver indiscriminadamente el snapshot completo.
- **G5-R3 — Complete technical inventory remains open.** No existe prueba de una fuente única para episodes/budgets/dependencies/versions/errors/certifications. Fuera del GREEN de 5.A.2.
- **G5-R4 — Productive architectural evidence acquisition remains deliberately open.** Requiere contrato independiente y petición explícita; fuera de 5.A.2.

## 9. Clasificación
`EXISTING CERTIFIED SESSION-SCOPED ANALYSIS MODE + EXISTING CERTIFIED UNIFIED READ-ONLY OBSERVABILITY — MINIMAL LEVEL-SPECIFIC SELECTION / CONVERSATIONAL PROJECTION SEAM REQUIRED`

No falta una nueva capacidad cognitiva. Falta una proyección subordinada y gobernada.

## 10. Recomendación para GATE 5.A.2.1 — CONTRACT RED
El RED futuro debe congelar como mínimo:
1. `OfficialConversationGateway` sigue siendo la única frontera interactiva oficial.
2. `UnifiedRuntimeObservability` sigue siendo la única fuente read-only de la proyección.
3. Sólo existen tres niveles: PERSONAL, TECHNICAL, ARCHITECTURAL.
4. La proyección depende efectivamente de `status.level`; los tres niveles no pueden devolver el mismo snapshot bruto indiscriminadamente.
5. PERSONAL sólo usa self-model/cognitive/conversation ya publicados; no Memory/Learning automáticos.
6. TECHNICAL sólo usa campos técnicos ya presentes en observability; no capability/recovery/diagnostics execution.
7. ARCHITECTURAL sólo usa metadata/evidencia ya publicada; no scans, `diagnose()`, Ruff, pytest ni lectura automática del repo.
8. Ausencia de datos se representa honestamente como unavailable/not provisioned.
9. La proyección no llama `.reason(`, `.plan(`, `.reflect(` ni `.diagnose(`.
10. No crea authority/manager/runtime/brain/registry paralelo.
11. No persiste, no aprende y no escribe Memory.
12. No expone chain-of-thought/private reasoning.
13. `analizá X` sigue sin activar Analysis Mode.
14. Estado continúa aislado por `session_id`.
15. `.roby/config.json` permanece byte-identical.
16. `credencial.json` debe preservarse si está presente.

## 11. STOP
GATE 5.A.2 termina aquí como reconciliación contractual.

No escribir CONTRACT RED ni modificar producción hasta certificar esta reconciliación. No abrir todavía inventario técnico productivo ni evidencia arquitectónica.
