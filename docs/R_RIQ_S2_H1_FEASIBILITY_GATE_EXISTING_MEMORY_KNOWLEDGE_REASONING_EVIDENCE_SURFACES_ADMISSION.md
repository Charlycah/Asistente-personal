# ROBY XI.2 — R-RIQ-S2-H1-FEASIBILITY-GATE
## Existing Memory/Knowledge/Reasoning Evidence Surfaces & Admission Decision (Static, Bounded)

**Clase:** acta documental candidata; inspección estática acotada; no admisión experimental.  
**Fecha:** 2026-10-12.  
**Base examinada:** `ultima version corregida(9).zip`, sin modificar, y acta H1 experimental-design candidate.  
**Gobierno:** `STOP_PRODUCTIVE: ACTIVE`; `OWNER_APPROVAL: PENDING`.

## 1. Alcance y precedencia

Se consultaron la verdad actual y el registro maestro **de raíz** del ZIP, el diseño documental H1 previo y las implementaciones focalizadas de `app/knowledge_runtime.py`, `app/ordinary_turn_multisource_reachability_adapter.py`, `app/explicit_multisource_productive_continuity_adapter.py` y `app/explicit_multisource_evidence_lineage_reentry_adapter.py`. No se realizó barrido general de consumidores, auditoría H2/H3, lectura de conversaciones o biblioteca, ejecución de código de ROBY, tests ni experimentos. La verificación de integridad local del diseño H1 fue informada por el Owner, pero no sustituye aprobación formal.

El registro maestro de raíz asigna `memory_gateway` a Memory, `knowledge_runtime` a Knowledge consultativo y `governed_reasoning` a Reasoning. La verdad actual advierte que el transporte explícito multisource no equivale a descubrimiento/adquisición general ni a composición multisource universal.

## 2. Superficies existentes observadas

| Ancla de ZIP | Evidencia estática comprobada | Límite para H1 |
|---|---|---|
| `ROBY_XI_2_MASTER_CAPABILITY_REGISTRY.md` | Autoridades únicas para Memory, Knowledge y Reasoning | Registro de ownership, no medición de resultados |
| `ROBY_XI_2_CURRENT_TRUTH.md` | Alcance acotado de reentrada multisource y fronteras de autorización | No prueba convergencia universal ni acceso científico |
| `app/knowledge_runtime.py` | `KnowledgeRuntime.assess_evidence_requirement()` estructura necesidades de fuente; `external_sources_allowed()` evalúa restricciones expresas de alcance; `assess()` devuelve `KnowledgeRuntimeAssessment` | Evaluación de necesidad y fuentes preferidas no acredita adquisición ni uso de fuente en respuesta final |
| `app/ordinary_turn_multisource_reachability_adapter.py` | `admit_and_reason()` delega al adaptador de mismo episodio si existen documentos/fuentes/referencias explícitas; en caso contrario devuelve `None` | No descubre fuentes ni demuestra convergencia con memoria recuperada |
| `app/explicit_multisource_productive_continuity_adapter.py` | `ExplicitMultisourceProductiveContinuityV1` conserva `owner`, `session_id`, `turn_id` y un `GovernedReasoningResult` ya producido | Identidad de continuidad, no mapa verificable afirmación final ↔ fuente usada |
| `app/explicit_multisource_evidence_lineage_reentry_adapter.py` | `deliver()` transmite identidad y artefactos de reentrada a un consumidor de revisión existente | Contrato de entrega, no evidencia de lectura autorizada ni resultado de respuesta final |

**Distinción crítica:** existencia de identificadores, referencias y artefactos de razonamiento no demuestra que una memoria concreta haya sido usada, que su procedencia sea accesible a investigación, ni que su contribución a una afirmación final sea observable.

## 3. Adjudicación de gates H1

| Gate | Requisito | Estado y fundamento |
|---|---|---|
| G0 — autoridad canónica | Reutilizar Memory/Knowledge/Reasoning sin paralelo | `IDENTIFIED_STATICALLY`; integración experimental no acreditada |
| G1 — acceso autorizado | Permiso específico, minimización, consentimiento si aplica | `NOT_DEMONSTRATED`; ningún contrato revisado concede acceso científico a contenido real |
| G2 — observabilidad E2E | Vínculo verificable memoria/fuente efectivamente usada → razonamiento → afirmación final | `NOT_DEMONSTRATED`; continuidad de identidad no equivale a atribución de afirmaciones |
| G3 — ground truth | Casos y hechos independientes, versiones y adjudicación previa | `NOT_PREPARED`; el diseño define el método, no un corpus aprobado |
| G4 — comparabilidad | Condiciones C0/C1/C2 equivalentes, sin bypass productivo | `NOT_DEMONSTRATED`; no se probó ablación autorizada o controles equivalentes |
| G5 — seguridad y privacidad | Superficie aprobada, acceso mínimo, retención y STOP | `NOT_AUTHORIZED_FOR_RESEARCH` |
| G6 — aprobación | Prerregistro y permiso explícito de ejecución | `NOT_AUTHORIZED` |

**Regla:** si cualquier gate obligatorio no está acreditado, no existe admisión científica. No convertir `NOT_DEMONSTRATED` en `ABSENT` o `DEFECT`; tampoco inferir permiso de una API técnica o de otra investigación.

## 4. Decisión y STOP

`H1_FEASIBILITY: INSUFFICIENT_EVIDENCE_FOR_EXPERIMENTAL_ADMISSION`  
`H1_RESEARCH_ADMISSION: INSUFFICIENT_EVIDENCE`  
`H1_EXPERIMENTS: EXPERIMENT_NOT_ENABLED`  
`H1_BOUNDED_STATIC_REVIEW: COMPLETE_CANDIDATE`  
`H1_REPEAT_STATIC_AUDITS: STOP_RECOMMENDED`  
`H2/H3: PRIOR_STOP_PRESERVED`  
`H4: DEFERRED_NOT_REJECTED`  
`PRODUCTIVE_CHANGES: NONE`  
`TESTS_EXECUTED: NONE`  
`STOP_PRODUCTIVE: ACTIVE`  
`OWNER_APPROVAL: PENDING`

La revisión termina aquí: no abrir una secuencia de búsquedas de callers, observadores o canales sensibles análoga a H2. No hay fundamento para experimentar, activar telemetría, leer conversaciones o alterar código.

## 5. Reapertura estrictamente condicionada

Reabrir solo con evidencia **nueva, concreta y autorizada** de: (a) superficie de acceso científico con autorización y minimización; (b) trazabilidad real de memoria/fuentes usadas a afirmaciones finales; (c) ground truth independiente preregistrado; (d) comparadores equivalentes sin bypass; (e) controles de seguridad y aprobación específica del Owner. Cada evidencia deberá apuntar a autoridad y contrato existente. Una nueva acta de inspección estática sin nuevo material no constituye progreso científico.

## 6. Próximo paso recomendado

`R-RIQ-S2-POST-H1-SCIENTIFIC-RECONCILIATION — H1 Evidence Closure & Master Research Priority Decision (Documentary)` **solo tras verificación local y aprobación del Owner**. Consolidar H1 con H2/H3 y revisar H4 frente al plan maestro, sin apertura automática de auditorías ni experimentos. El siguiente paso es documental, no productivo.

**Control:** el acta es externa al ZIP operativo y su integración en `docs/` no actualiza automáticamente el Master Plan ni acredita aprobación formal.
