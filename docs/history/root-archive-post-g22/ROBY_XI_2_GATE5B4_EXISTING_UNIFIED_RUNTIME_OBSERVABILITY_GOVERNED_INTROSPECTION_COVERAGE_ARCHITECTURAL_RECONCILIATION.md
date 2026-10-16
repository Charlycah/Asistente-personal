# ROBY XI.2 — GATE 5.B.4
## Existing Unified Runtime Observability → Governed Introspection Coverage — ARCHITECTURAL RECONCILIATION

### Estado
ARCHITECTURAL RECONCILIATION — preparada sobre la base oficial certificada GATE 5.B.3.1 SURGICAL GREEN.

Baseline certificada de entrada por el usuario:
- M361 regenerado;
- Ruff limpio;
- 14.026 PASS;
- 0 FAIL.

Fuente de verdad de esta reconciliación: ZIP completo de GATE 5.B.3.1 SURGICAL GREEN. La documentación/inventarios se usan como mapa y cada conclusión se verifica contra el código real.

## 1. Propósito
Reconciliar, sin modificar producción, la cobertura introspectiva real disponible después de cerrar G5-R3b en la fuente unificada. El objetivo es separar con precisión:

1. estado ya publicado por `UnifiedRuntimeObservability`;
2. estado ya consumido por las proyecciones PERSONAL / TECHNICAL / ARCHITECTURAL;
3. estado existente bajo otra autoridad pero todavía no publicado mediante un read model canónico;
4. estado no provisionado o sólo calculable mediante ejecución;
5. evidencia offline/documental que no debe convertirse en estado runtime por scanning.

Este Gate no crea una nueva autoridad de Self Model, introspección, diagnostics, episodes, budgets, versions o certification.

## 2. Autoridades canónicas verificadas
### 2.1 Unified runtime observability
`app/unified_runtime_observability.py::UnifiedRuntimeObservability` sigue siendo la única superficie unificada read-only. Su snapshot inmutable publica actualmente:

- `operational`;
- `readiness`;
- `conversation`;
- `capabilities`;
- `registered_capabilities`;
- `capability_registry`;
- `capability_dependencies`;
- `cognitive_core`;
- `self_model`;
- `reflection`;
- `self_diagnostics`;
- `recovery`.

GATE 5.B.3.1 cerró la costura:

`OfficialROBYRuntime.capability_graph`
→ `RuntimeCapabilityGraph.snapshot()`
→ `UnifiedRuntimeObservabilitySnapshot.capability_dependencies`

La proyección conserva `None` para NOT PROVISIONED y `()` para un grafo vacío explícitamente provisionado.

### 2.2 OfficialConversationGateway
`OfficialConversationGateway` continúa siendo la única frontera interactiva y el owner sólo del estado efímero de Analysis Mode por sesión. No es una autoridad de introspección técnica.

`analysis_mode_projection(...)` consume un snapshot de `UnifiedRuntimeObservability` y selecciona secciones por nivel. No ejecuta Reasoning, Planning, Reflection, Self Diagnostics, Memory ni Learning.

### 2.3 Cognitive Self Model
`app/cognitive_self_model.py::CognitiveSelfModel` es una autoridad existente de condición cognitiva acotada. Su snapshot representa, entre otros:

- mode;
- active focus;
- confidence / uncertainty;
- cognitive load;
- stability;
- pending reassessment;
- un conjunto acotado de capacidades cognitivas propias del modelo;
- evidence sources.

No es el registry oficial de capabilities y no debe convertirse en un duplicado del runtime capability registry/graph. En particular, `available_capabilities` del Self Model es un producto de ese modelo cognitivo y no una reconstrucción de `OfficialRuntimeCapabilityRegistry`.

### 2.4 Self Diagnostics
`core.self_diagnostics.GovernedSelfDiagnostics` existe como autoridad técnica read-only y dispone de `diagnose(...)` sobre observaciones explícitas, además de fases posteriores de hipótesis/proof/proposal/review.

Sin embargo, la búsqueda productiva confirma que no existe una instancia `GovernedSelfDiagnostics()` provisionada en `app/` o `core/`. `UnifiedRuntimeObservability` publica honestamente:

- authority implemented = true;
- runtime_provisioned = false;
- current_report = none.

Observability no debe ejecutar `diagnose(...)` para fabricar un reporte.

## 3. Cobertura real por nivel de introspección
### 3.1 PERSONAL
La proyección PERSONAL actual publica:
- cognitive core;
- conversation;
- self model cuando está publicado por el cognitive core.

Estado: **CLOSED dentro del contrato 5.A.2.1 vigente**.

No debe ampliarse el Self Model para absorber capability registry, dependency graph, diagnostics, episodes o certificaciones. Esa información pertenece a otras autoridades y debe seguir componiéndose por introspección subordinada cuando corresponda.

### 3.2 TECHNICAL
La proyección TECHNICAL actual publica:
- operational;
- readiness;
- conversation;
- registered capabilities;
- capability registry;
- cognitive core;
- self-diagnostics availability metadata;
- capability gateway snapshot cuando existe;
- recovery sólo cuando ya está provisionado en el snapshot.

Después de GATE 5.B.3.1 existe ahora una diferencia concreta entre **source coverage** y **consumer coverage**:

- `UnifiedRuntimeObservabilitySnapshot.capability_dependencies` existe y es canónico/read-only;
- `OfficialConversationGateway.analysis_mode_projection(...)` no selecciona todavía `capability_dependencies` en TECHNICAL.

Esto es un residual pequeño de presentación/selección, no una ausencia de autoridad ni de fuente.

Clasificación: **SOURCE CLOSED / TECHNICAL CONSUMER PROJECTION OPEN NARROW**.

### 3.3 ARCHITECTURAL
La proyección ARCHITECTURAL actual publica:
- reflection architecture metadata;
- capability registry;
- self-diagnostics availability metadata;
- reflection published state cuando existe;
- declara `architectural_evidence: not provisioned`.

G5-R4 sigue deliberadamente abierto. No existe una fuente productiva certificada de auditoría viva de repositorio/documentación/tests. `CanonicalReflectionFacade().snapshot` es metadata estructural, no una auditoría de arquitectura viva.

La disponibilidad de `capability_dependencies` no autoriza por sí sola a cerrar G5-R4 ni a crear análisis arquitectónico inferencial. Las dependencies pueden ser metadata útil en un gate de presentación posterior, pero no sustituyen evidencia arquitectónica productiva.

Clasificación: **PUBLISHED METADATA EXISTS / PRODUCTIVE ARCHITECTURAL EVIDENCE NOT PROVISIONED**.

## 4. Episodes y budgets: reconciliación contra código real
El código confirma fuentes reales, pero no un read model unificado listo para Analysis Mode.

### 4.1 Long-horizon investigation
`GovernedInvestigationEpisodeState` es un valor inmutable con lineage y budget explícitos:
- episode id;
- requirement/plan/authorization/execution/reentry ids;
- `consumed_acquisitions`;
- `current_step`;
- status / stopping reason;
- `max_acquisitions`;
- `remaining_acquisitions` derivado.

La autoridad de transición `GovernedMultiStepInvestigationEpisodeBoundaryV1` opera sobre estados suministrados; no mantiene un registry global de episodios activos.

### 4.2 Governed reasoning runtime
`GovernedReasoningRuntime` sí mantiene episodios productivos internos por owner/session/turn y expone getters exactos como `productive_episode(...)` y `productive_epistemic_episode(...)`. Su `snapshot` general, sin embargo, sólo resume evaluaciones/último owner/último estado/confidence/review y no publica un inventario de episodios activos.

El runtime productivo contiene `governed_reasoning_runtime` en `RuntimeCompositionDependencies`, pero `UnifiedRuntimeObservability` no publica sus episodios y no existe un contrato certificado que autorice recorrer sus stores privados.

### Dictamen episodes/budgets
**EXISTING CANONICAL LOCAL STATE + NO CERTIFIED UNIFIED READ-ONLY ACTIVE-EPISODE/BUDGET VIEW.**

No corresponde agregar fields a observability leyendo `_productive_episodes`, inventar `EpisodeRegistry`, fusionar episodios cognitivos/Reasoning/long-horizon, ni calcular un presupuesto global.

G5-R3c permanece **OPEN DEFERRED** y requiere reconciliación separada por autoridad/read-model si se decide abrirlo.

## 5. Versions: reconciliación contra código real
El repositorio contiene numerosos `schema_version` / `SCHEMA_VERSION` distribuidos (centenares de archivos en `app/` y `core/`). Esto demuestra versionado local de contratos, no un catálogo runtime canónico.

No se identificó una autoridad productiva única que publique un inventario de versiones a `OfficialROBYRuntime` o `UnifiedRuntimeObservability`.

Dictamen: **DISTRIBUTED CONTRACT VERSIONING / NO CANONICAL RUNTIME VERSION CATALOG.**

G5-R3d permanece **OPEN DEFERRED**. Prohibido resolverlo mediante scans/import introspection desde Analysis Mode.

## 6. Certifications / quality: reconciliación refinada
El código contiene capacidades históricas de certificación, por ejemplo:
- `certify_runtime_execution(...)`;
- `OperationalReliabilityCertifier`;
- `ProductionReadinessAssessor`;
- `ROBYArchitectureCertifier`.

Además, `RuntimeCompositionDependencies` declara slots opcionales para algunos certifiers/assessors.

Pero el factory productivo actual no asigna `operational_reliability_certifier`, `production_readiness_assessor` ni `roby_architecture_certifier`. Por tanto, esos slots permanecen no provisionados en la composición oficial construida actualmente.

`certify_runtime_execution(...)` es una función de certificación que calcula un resultado cuando se invoca; no es un estado runtime ya publicado que Observability pueda leer sin ejecutar certificación.

M361, Ruff, pytest y los documentos de gates siguen siendo evidencia offline/local de calidad, no estado runtime vivo.

Dictamen: **CERTIFICATION LOGIC EXISTS + PRODUCTIVE RUNTIME CERTIFICATION SOURCE NOT PROVISIONED/PUBLISHED + QUALITY BASELINE REMAINS OFFLINE.**

G5-R3e permanece fuera de la observabilidad runtime actual. No ejecutar certifiers, M361, Ruff o pytest desde Analysis Mode.

## 7. Capability dependencies: estado post-5.B.3.1
G5-R3b ya no es un problema de reachability o source publication.

Estado real:
- graph canónico: existente;
- ownership opcional por `OfficialROBYRuntime`: certificado;
- provisioning sólo desde declarations explícitas: certificado;
- snapshot read-only canónico: certificado;
- publication en `UnifiedRuntimeObservability`: certificado;
- consumo por Analysis Mode TECHNICAL: todavía ausente.

Por tanto se refina:

**G5-R3b-source: CLOSED.**

**G5-R3b-consumer: OPEN NARROW — existing canonical unified field not yet selected by TECHNICAL Analysis Mode.**

## 8. Matriz post-5.B.3.1

| Dominio | Autoridad real | UnifiedRuntimeObservability | Analysis Mode | Estado |
|---|---|---|---|---|
| operational/lifecycle/errors | RuntimeOperationalSnapshot | publicado | TECHNICAL | CLOSED |
| health/readiness | RuntimeHealthReadinessReport | publicado | TECHNICAL | CLOSED |
| capability registry | OfficialRuntimeCapabilityRegistry | publicado | TECHNICAL + ARCHITECTURAL | CLOSED |
| capability dependencies | RuntimeCapabilityGraph | publicado canónicamente | no seleccionado | SOURCE CLOSED / CONSUMER OPEN NARROW |
| cognitive condition/self-model | CognitiveSelfModel vía cognitive core | publicado cuando existe | PERSONAL | CLOSED dentro del contrato actual |
| reflection metadata | CanonicalReflectionFacade + published cognitive state | publicado | ARCHITECTURAL | METADATA PUBLISHED |
| self diagnostics | GovernedSelfDiagnostics | metadata de disponibilidad | TECHNICAL + ARCHITECTURAL | IMPLEMENTED / NOT PROVISIONED |
| reasoning episodes | GovernedReasoningRuntime | no inventario unificado | no | DEFERRED |
| long-horizon episodes/budgets | GovernedInvestigationEpisodeState + boundaries | no | no | DEFERRED |
| versions | contratos locales distribuidos | no | no | DEFERRED |
| runtime certifications | lógica existente, certifiers no provisionados | no | no | NOT PROVISIONED |
| M361/Ruff/pytest/gate certification | quality/offline | no | no | OUTSIDE RUNTIME |
| live architectural evidence | no fuente productiva certificada | no | `not provisioned` | G5-R4 OPEN |

## 9. Hallazgo arquitectónico principal
Después de GATE 5.B.3.1 no falta una nueva “Governed Introspection Authority”. La composición introspectiva correcta ya existe y debe seguir siendo `UnifiedRuntimeObservability`.

Tampoco corresponde convertir `CognitiveSelfModel` en un super-modelo que copie estados técnicos. Ese modelo posee una semántica cognitiva distinta.

El único residual suficientemente pequeño y ya respaldado por una fuente canónica publicada es la selección conversacional de `capability_dependencies` para el nivel TECHNICAL.

Episodes/budgets, versions, certifications y G5-R4 requieren decisiones separadas y no deben agruparse en el mismo GREEN.

## 10. Próximo gate recomendado
La reconciliación demuestra un seam contractual estrecho:

**GATE 5.B.4.1 — UnifiedRuntimeObservability Canonical Capability Dependencies → Analysis Mode TECHNICAL Read-Only Projection — CONTRACT RED**

El CONTRACT RED debería congelar exclusivamente:

1. TECHNICAL consume el `capability_dependencies` ya publicado por `UnifiedRuntimeObservability`;
2. `None` se representa honestamente como `capability_dependencies: not provisioned`;
3. `()` se representa como sección disponible y vacía, no como NOT PROVISIONED;
4. una tupla no vacía se expone sin reconstrucción ni inferencia;
5. preservación exacta de capability ids y required/optional edges;
6. cero lectura directa de registry/graph desde `OfficialConversationGateway`;
7. cero `readiness_graph(...)` / `recovery_plan(...)` para producir dependency presentation;
8. cero ejecución de diagnostics/Reasoning/Planning/Reflection/Memory/Learning;
9. no modificar PERSONAL ni ARCHITECTURAL dentro de este GREEN;
10. no abrir episodes/budgets, versions, certifications ni G5-R4;
11. no crear manager/registry/graph/runtime paralelo;
12. `.roby/config.json` y las autoridades existentes permanecen preservadas.

La implementación futura, si el RED se certifica, debe ser una selección/presentación en la proyección TECHNICAL; no una nueva fuente de datos.

## 11. Cambios productivos
Ninguno.

GATE 5.B.4 es exclusivamente reconciliación arquitectónica/documental.

## 12. STOP
No crear CONTRACT RED automáticamente dentro de esta reconciliación. No modificar producción. No modificar PERSONAL/ARCHITECTURAL. No abrir G5-R4. No crear un Self Model nuevo ni ampliar el existente para copiar authorities. No crear `EpisodeRegistry`, `BudgetManager`, `VersionRegistry`, `CertificationRegistry`, `IntrospectionManager` o segundo observability runtime. No ejecutar Self Diagnostics, certifiers, Reasoning, Planning, Reflection, Memory, Learning, repair, repo scans, quality tools o background monitoring. No Planning N+1. No autonomía adicional.

## 13. Clasificación final
**UNIFIED GOVERNED INTROSPECTION SOURCE IS SUBSTANTIALLY ESTABLISHED + CAPABILITY DEPENDENCY SOURCE IS NOW CLOSED + ONE NARROW TECHNICAL CONSUMER PROJECTION GAP EXISTS + EPISODES/BUDGETS/VERSIONS/CERTIFICATIONS REMAIN SEPARATE DEFERRED/NON-PROVISIONED DOMAINS + G5-R4 REMAINS DELIBERATELY OPEN.**
