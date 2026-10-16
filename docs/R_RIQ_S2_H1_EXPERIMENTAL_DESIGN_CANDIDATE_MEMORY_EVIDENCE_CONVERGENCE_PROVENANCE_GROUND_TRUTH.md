# ROBY XI.2 — R-RIQ-S2-H1-EXPERIMENTAL-DESIGN-CANDIDATE
## Memory/Evidence Convergence, Provenance & Independent Ground Truth (Documentary)

**Clase:** diseño científico documental candidato, no protocolo admitido ni resultado experimental.  
**Fecha:** 2026-10-12.  
**Base:** `ultima version corregida(9).zip`; precedencia de `ROBY_XI_2_CURRENT_TRUTH.md`, registro maestro de capacidades **de raíz**, inventarios y reglas arquitectónicas; R-RIQ-00, R-RIQ-S1 y reconciliación POST-H3.  
**Gobierno:** `STOP_PRODUCTIVE: ACTIVE`; sin ejecución, pruebas, lecturas de conversaciones, escrituras, nuevos módulos ni modificación del ZIP. `OWNER_APPROVAL: PENDING`.

## 1. Precedencia, evidencia y límite

La reconciliación POST-H3 selecciona H1 **solo como prioridad de diseño documental**. H2 permanece `INSUFFICIENT_EVIDENCE / STOP_PENDING_NEW_EVIDENCE`; H3 `PARTIALLY_FEASIBLE / EXPERIMENT_NOT_ENABLED`; H4 diferida, no rechazada. La comprobación SHA-256 de POST-H3 acredita identidad del archivo, no aprobación científica formal.

La síntesis R-RIQ-S1 identifica el `memory_gateway` como autoridad de Memory, `knowledge_runtime` como Knowledge consultativo y `governed_reasoning` como única autoridad inferencial. Señala transporte ordinario de evidencia de memoria recuperada y admisión multisource explícita, pero **no** una obligación contractual de uso conjunto ni una mejora demostrada. La inspección focalizada del ZIP confirma que el registro maestro de raíz asigna esas autoridades; existen adaptadores `app/explicit_multisource_evidence_lineage_reentry_adapter.py`, `app/ordinary_turn_multisource_reachability_adapter.py` y contratos `test_post_12776_single_reasoning_multisource_convergence_contract_red.py`. Su existencia no demuestra ejecución experimental, procedencia completa o exposición autorizada de respuestas finales.

No se repiten auditorías R-EVO, H2 ni H3. Este documento define qué sería medible y qué condiciones faltan; no diagnostica un defecto productivo.

## 2. Hipótesis falsable y estimando

**H1:** en un conjunto preregistrado de tareas con fuentes permitidas, el uso gobernado de memoria pertinente y evidencia consultativa, cuando ambas estén disponibles y sean admisibles, produce respuestas mejor sustentadas, con atribuciones verificables y resolución correcta de conflictos, frente a condiciones de control equivalentes, sin aumentar filtraciones, contradicciones ni afirmaciones no sustentadas.

**Hipótesis nula:** no existe mejora significativa o la mejora aparente se explica por selección de casos, información adicional no equivalente, contaminación, diferencias de autorización o cambios de modelo/configuración. **Resultados adversos admisibles:** empeoramiento, beneficio nulo, abstención excesiva, citas inventadas, memoria obsoleta preferida a evidencia vigente, exposición indebida o imposibilidad de observación. Ninguna de estas salidas debe ocultarse.

**Unidad primaria:** un caso de pregunta/tarea con paquete de fuentes permitido y respuesta final evaluable; no confundir evento de recuperación, evidencia intermedia y respuesta. **Unidad de dependencia:** conjunto de casos relacionados por entidad, documento o sesión, agrupado para evitar fuga entre preparación y evaluación.

## 3. Matriz de casos candidata (sin ejecutar)

| Estrato | Pregunta de evaluación | Resultado de referencia predefinido |
|---|---|---|
| Convergencia concordante | Memoria y fuente externa apoyan la misma respuesta | Respuesta y atribución a cada fuente realmente usada |
| Complementariedad | Cada fuente aporta hechos distintos necesarios | Integración sin extrapolaciones no respaldadas |
| Conflicto temporal | Memoria antigua contradice fuente actual | Preferencia justificada según fecha, autoridad y alcance |
| Conflicto sin resolución | Fuentes autorizadas discrepan sin árbitro | Incertidumbre explícita o abstención apropiada |
| Memoria irrelevante | Recuperación plausible pero no pertinente | No contaminación de la respuesta |
| Evidencia ausente | Falta dato necesario | Reconocimiento de insuficiencia, sin invención |
| Procedencia incompleta | Una fuente no puede verificarse | No atribución ficticia; límite declarado |
| Restricción de acceso | Dato sensible/no autorizado potencialmente útil | Exclusión o denegación gobernada, sin fuga |
| Transferencia acotada | Caso nuevo con estructura comparable | Respuesta fundamentada, sin usar respuestas de evaluación previas |

Los estratos son propuestas de diseño, **no** datos sintéticos creados ni pruebas ejecutadas.

## 4. Ground truth y comparadores independientes

Antes de cualquier experimento, un evaluador independiente de la salida de ROBY deberá fijar para cada caso: identificador seudónimo; versión de consigna; fuentes permitidas y sus versiones/fechas; hechos esperados; conflictos y criterio de precedencia; hechos imposibles de conocer; respuesta admisible o abstención; riesgos; y reglas de adjudicación. La verdad de referencia no puede generarse a partir de la respuesta evaluada ni del mismo recuperador que se intenta validar. Registrar desacuerdos entre adjudicadores y su resolución sin cambiar retroactivamente los criterios.

**Comparadores candidatos, sujetos a factibilidad de la arquitectura existente:** (C0) evidencia consultativa sin memoria recuperada; (C1) memoria autorizada sin fuente consultativa; (C2) ruta conjunta gobernada; (C3) abstención/control sin evidencia suficiente. Solo comparar condiciones efectivamente representables **sin nuevos caminos productivos ni bypass de autorización**. Controlar mismo conjunto de tareas, modelo, versión, presupuesto de contexto, latencia, permisos, configuración y evaluación ciega. No simular una ablación mediante manipulación no autorizada de runtime. Si no hay controles equivalentes, declarar `COMPARATIVE_DESIGN_NOT_ADMISSIBLE`.

No se incluye baseline humano por defecto. Cualquier comparación con humanos requiere cohorte, instrucciones, herramientas, tiempos, condiciones y consentimiento comparables, más aprobación separada; sin ello, ninguna afirmación de superioridad humana.

## 5. Métricas y reglas de interpretación

- **Exactitud sustentada:** casos con conclusión correcta y soporte permitido / casos elegibles evaluables; reportar por estrato.
- **Precisión de atribución:** afirmaciones atribuidas correctamente a una fuente verificable / todas las afirmaciones atribuidas; separar citas inexistentes.
- **Cobertura de evidencia necesaria:** hechos de referencia correctamente sustentados / hechos necesarios de referencia, sin premiar verbosidad.
- **Contradicción no resuelta:** casos con contradicción afirmada sin reconocimiento o justificación / casos con conflicto evaluable.
- **Abstención adecuada y excesiva:** reportar por separado ante información insuficiente y suficiente.
- **Contaminación de memoria:** casos donde material obsoleto, irrelevante o prohibido altera indebidamente la respuesta / casos expuestos al riesgo.
- **Proveniencia y trazabilidad:** proporción con identificadores de fuente, versión, fecha, permiso y correspondencia verificable a afirmaciones finales; ausencia de dato = no demostrado, no éxito.
- **Seguridad/privacidad:** incidentes de divulgación no autorizada; cualquier incidente activa STOP y revisión gobernada.
- **Costo y latencia:** secundarios; nunca compensan fallas de autorización.

Definir denominadores, exclusiones, política de faltantes, umbrales de no inferioridad/mejora, intervalos de confianza, tamaño de muestra y corrección por múltiples métricas **antes** de observar resultados. No hay cifras, umbrales ni resultados estimados en esta etapa.

## 6. Controles de validez y sesgos

Prerregistro de casos y versiones; separación por documento/entidad entre preparación y evaluación; bloqueo de fuentes posteriores a la fecha de corte; anonimización y minimización; aleatorización o contrabalanceo si se autorizan condiciones; adjudicación ciega; trazas completas y auditables solo en superficie explícitamente autorizada; reporte de todos los casos, rechazos y faltantes; sensibilidad por fecha, dominio y disponibilidad de fuente. La mera correlación entre recuperación y acierto no demuestra causalidad de la convergencia.

## 7. Puertas de admisión obligatorias

| Gate | Evidencia requerida antes de ejecutar | Estado hoy |
|---|---|---|
| G0 — Autoridades canónicas | Reutilización de Memory, Knowledge y Reasoning conforme registro maestro, sin rutas paralelas | Identificadas documentalmente; integración experimental no acreditada |
| G1 — Acceso autorizado | Permiso concreto para datos/casos, minimización y consentimiento cuando corresponda | `NOT_DEMONSTRATED` |
| G2 — Observabilidad de extremo a extremo | Vincular fuente/memoria efectivamente usada, decisión inferencial y respuesta final sin canal sensible improvisado | `NOT_DEMONSTRATED` |
| G3 — Referencia independiente | Casos, hechos, conflictos, evaluadores y versiones fijados antes de resultados | `NOT_PREPARED` |
| G4 — Comparabilidad | Controles realizables sin cambiar comportamiento gobernado, con condiciones equivalentes | `NOT_DEMONSTRATED` |
| G5 — Privacidad y seguridad | Límites, retención, control de acceso, STOP por incidentes | `NOT_AUTHORIZED_FOR_RESEARCH` |
| G6 — Protocolo y aprobación | Prerregistro, plan estadístico y autorización explícita del Owner para cada ejecución | `NOT_AUTHORIZED` |

**Admisión:** todos los gates satisfechos y acreditados con evidencia concreta. Si alguno falla: `H1_RESEARCH_ADMISSION: INSUFFICIENT_EVIDENCE; EXPERIMENT_NOT_ENABLED`. No trasladar autorizaciones de H2/H3 ni de interfaces de diagnóstico. No utilizar conversaciones reales ni biblioteca local por inferencia de acceso.

## 8. Límites, STOP y próximo paso máximo

- No abrir nuevos repositorios de memoria, recuperadores, gestores, observadores, planners ni autoridades. No restaurar proyecciones epistemológicas retiradas.
- No inspeccionar conversaciones, prompts, datos privados o contenido de biblioteca; no invocar capacidades productivas ni escribir memoria o Learning.
- No realizar tests, simulaciones, experimentos, benchmarking ni instrumentación sin aprobación separada.
- Si la ruta de observación autorizada no existe o no se demuestra con evidencia nueva, cerrar H1 con `INSUFFICIENT_EVIDENCE`, sin repetir la cadena H2.
- Cualquier cambio productivo eventual requiere inventario, prueba de reutilización, residual exacto, RED contractual, certificación local, GREEN quirúrgico, ZIP completo y nueva certificación.

**Siguiente puerta propuesta (no iniciada):** `R-RIQ-S2-H1-FEASIBILITY-GATE — Existing Memory/Knowledge/Reasoning Evidence Surfaces & Admission Decision (Static, Bounded)`. Debe ser **una sola revisión documental/estática limitada** de superficies ya identificadas, orientada a decidir si G1–G4 son demostrables. Si no aporta nueva evidencia, STOP sin auditorías encadenadas. Requiere integridad local y aprobación formal de esta acta.

## 9. Dictamen

`H1_EXPERIMENTAL_DESIGN: DOCUMENT_PREPARED_CANDIDATE`  
`H1_FEASIBILITY: NOT_YET_ADJUDICATED`  
`H1_RESEARCH_ADMISSION: NOT_GRANTED`  
`H1_EXPERIMENTS: NOT_AUTHORIZED`  
`H2/H3: PRIOR_STOP_PRESERVED`  
`H4: DEFERRED_NOT_REJECTED`  
`OWNER_APPROVAL: PENDING`  
`TESTS_EXECUTED: NONE`  
`PRODUCTIVE_CHANGES: NONE`  
`STOP_PRODUCTIVE: ACTIVE`

**Nota de control:** este archivo es externo al ZIP operativo (9). Su incorporación local y hash no sustituyen la aprobación del Owner ni actualizan automáticamente el Master Plan.
