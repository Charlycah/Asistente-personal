# ROBY XI.2 — R-RIQ-S2-H4-DOCUMENTARY-DESIGN-GATE
## Longitudinal Learning, Transfer & Non-Regression (Bounded)

**Clase:** acta candidata de diseño científico documental, no certificación ni autorización experimental.  
**Fecha:** 2026-10-12.  
**Base:** `ultima version corregida(9).zip` (consulta estática, sin modificación); `R_RIQ_S2_POST_H1_SCIENTIFIC_RECONCILIATION_H1_EVIDENCE_CLOSURE_MASTER_RESEARCH_PRIORITY.md`; registro maestro de capacidades y documentación Post-M409.1 existente.  
**Gobierno:** `STOP_PRODUCTIVE: ACTIVE`; `OWNER_APPROVAL: PENDING`.

## 1. Propósito y límites

Definir una pregunta falsable: **¿existe una mejora longitudinal atribuible a aprendizaje gobernado de ROBY, que se conserve y transfiera a casos no vistos, sin regresiones inaceptables, comparada con referencias independientes?** Esta acta no presupone que tal mejora exista. No ejecuta código, pruebas, experimentos, accesos a conversaciones, mutaciones de memoria ni inspecciones técnicas repetitivas. Es la última apertura documental individual H1–H4 propuesta para R-RIQ-S2.

## 2. Reutilización obligatoria de capacidades existentes

La inspección limitada del snapshot identifica evidencia documental y rutas existentes, **no nuevas autoridades**:

| Evidencia en el ZIP `(9)` | Alcance documentado y límite |
|---|---|
| `docs/ROBY_XI_2_MASTER_CAPABILITY_REGISTRY.md` | Registro de autoridades; se debe verificar y reutilizar el owner canónico de cada capacidad antes de cualquier cambio. |
| `docs/POST_M409_1_GOVERNED_LONGITUDINAL_REASONING_ASSESSMENT_FOUNDATION_V1.md` | Evaluación longitudinal inmutable/read-only bajo `governed_reasoning`; no activa reflexión/aprendizaje ni altera historial. |
| `docs/POST_M409_1_GOVERNED_LEARNING_PRODUCTIVE_END_TO_END_WIRING_V1.md` | Ruta gobernada de aprobación humana explícita hacia `OfficialMemoryGateway.remember_governed_learning`; no crea autoridad o aprobación. |
| `docs/POST_M409_1_APPROVED_LEARNING_MEMORY_MATERIALIZATION_PROPOSAL_V1.md` | Propuesta de materialización de evidencia M369 ya aprobada; v1 limitada a aprendizaje de preferencias, sin escritura por sí sola. |
| `docs/WHOLE_SYSTEM_CROSS_CAPABILITY_COGNITIVE_INTEGRATION_TRANSFER_CERTIFICATION.md` | Certificación previa de rutas parciales e integraciones acotadas; no constituye demostración H4 de mejora causal, transferencia general o ausencia universal de regresiones. |
| `tests/architecture/test_post_m409_1_longitudinal_reasoning_observation_contract_generalization_v1.py` y pruebas de transferencia/aprendizaje existentes | Artefactos de prueba ya presentes; **no ejecutados** en esta etapa, y no deben confundirse con un estudio longitudinal independiente. |

**Regla de precedencia:** documentación maestra, estado actual, inventarios y registro canónico prevalecen sobre inferencias de esta acta. No introducir gestores, memoria, agentes, bucles, evaluadores o repositorios paralelos.

## 3. Diseño candidato: unidades y comparadores

- **Unidad primaria:** tarea/caso con identificador estable, versión del protocolo, autorización, contexto controlado, salida evaluable y procedencia; sin datos personales reales por defecto.
- **Instantes:** T0 baseline congelado, T1 posterior a intervención autorizada y T2 retención diferida. Las duraciones se preregistran; no se inventan aquí.
- **Cohortes:** conjunto de aprendizaje permitido; conjunto de retención; conjunto de transferencia estructural no visto; conjunto de controles negativos y seguridad. Evitar fuga entre conjuntos, repetición literal y contaminación de respuestas.
- **Comparadores independientes:** baseline T0 sin aprendizaje y referencia externa/ground truth definida antes de observar T1/T2; igualdad de tarea, recursos, tiempo y condiciones de acceso. Cualquier comparación humana exige protocolo separado y autorización expresa.
- **Intervención:** solo la ruta de aprendizaje existente, explícitamente autorizada, con registro de aprobación y procedencia. Este documento no autoriza ni ejecuta la intervención.

## 4. Hipótesis falsables y medición

| Dimensión | Pregunta | Métrica candidata / criterio de fallo |
|---|---|---|
| Aprendizaje | ¿Mejora T1 frente a T0 y controles? | Diferencia pareada de exactitud/resultado sustentado, con intervalos de incertidumbre; fallo si no supera umbral preregistrado. |
| Retención | ¿Persiste la mejora en T2? | Fracción de mejoras T1 retenidas en casos equivalentes; fallo por caída mayor que tolerancia preregistrada. |
| Transferencia | ¿Generaliza a casos nuevos sin repetición literal? | Rendimiento en familias estructuralmente nuevas vs baseline independiente; fallo por ausencia de ganancia o fuga. |
| No regresión | ¿Se preservan capacidades y límites? | Tasas de fallos críticos, incumplimientos de autorización, degradación por categoría y controles negativos; un fallo crítico activa STOP. |
| Causalidad | ¿Puede atribuirse la diferencia a aprendizaje? | Control de versión, modelo, herramientas, fuentes, dificultad, semillas y permisos; si no son comparables, resultado `INDETERMINATE`. |
| Procedencia | ¿Se reconstruye la cadena autorizada? | Vínculo entre evidencia, evaluación, aprobación, materialización y uso posterior; si falta, no computar éxito atribuible. |

Los umbrales, tamaños de muestra, reglas estadísticas y periodos **no están fijados**; deben preregistrarse en una autorización experimental posterior. No atribuir al proyecto métricas ejecutadas.

## 5. Gates de admisión científica

| Gate | Evidencia exigida | Estado actual |
|---|---|---|
| H4-G0 autoridad canónica | Mapa aprobado de owners y rutas sin duplicación | `EXISTING_DOCUMENTARY_BASIS` |
| H4-G1 observabilidad longitudinal | Identidad comparable T0/T1/T2, evidencia y salida atribuible | `NOT_DEMONSTRATED_FOR_H4` |
| H4-G2 intervención gobernada | Consentimiento/aprobación específicos y trazabilidad de cada cambio | `PATH_DOCUMENTED; RESEARCH_AUTHORIZATION_MISSING` |
| H4-G3 ground truth/baselines | Referencias independientes preregistradas | `NOT_PREPARED` |
| H4-G4 retención/transferencia | Conjuntos no vistos, separación y anti-contaminación | `NOT_PREPARED` |
| H4-G5 no regresión y seguridad | Umbrales, STOP, reversibilidad y controles negativos | `NOT_PREPARED_FOR_STUDY` |
| H4-G6 Owner | Aprobación expresa del protocolo, acceso y ejecución | `NOT_AUTHORIZED` |

**Admisión actual:** `H4_RESEARCH_ADMISSION: INSUFFICIENT_EVIDENCE`; `H4_EXPERIMENTS: EXPERIMENT_NOT_ENABLED`. Es un juicio de preparación de estudio, **no** una refutación de H4 ni una declaración de defecto de producto.

## 6. Decisión STOP y siguientes condiciones

No iniciar otra cadena de auditorías estáticas de H4. Reabrir solo con evidencia concreta nueva: protocolo preregistrado, comparadores independientes, superficie de observación gobernada, permisos de investigación, límites de privacidad y aprobación expresa del Owner. Si falta cualquier gate crítico, detener la ejecución y documentar `INDETERMINATE`/`NOT_ADMITTED`, nunca imputar éxito. No usar historial de conversaciones reales o memoria personal sin autorización específica.

**Próxima fase propuesta:** `R-RIQ-S2-GLOBAL-SCIENTIFIC-RECONCILIATION — H1–H4 Evidence Portfolio, Admission Barriers & Master Plan Return (Documentary)`. Consolidación única; no otra auditoría de consumidores ni apertura automática de experimentos.

## 7. Estado

`H4_DOCUMENTARY_DESIGN_GATE: DOCUMENT_PREPARED_CANDIDATE`  
`H4_RESEARCH_ADMISSION: INSUFFICIENT_EVIDENCE`  
`H4_EXPERIMENTS: NOT_AUTHORIZED`  
`H1/H2/H3: PRIOR_STOPS_PRESERVED`  
`OWNER_APPROVAL: PENDING`  
`TESTS_EXECUTED: NONE`  
`PRODUCTIVE_CHANGES: NONE`  
`STOP_PRODUCTIVE: ACTIVE`
