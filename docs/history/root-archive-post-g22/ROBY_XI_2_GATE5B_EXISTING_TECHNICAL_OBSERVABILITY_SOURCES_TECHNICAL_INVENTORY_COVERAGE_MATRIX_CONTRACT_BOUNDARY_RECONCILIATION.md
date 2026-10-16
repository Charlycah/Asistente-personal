# ROBY XI.2 — GATE 5.B
## Existing Technical Observability Sources → Technical Inventory Coverage Matrix — CONTRACT BOUNDARY RECONCILIATION

Status: CONTRACT BOUNDARY RECONCILIATION — PENDING LOCAL CERTIFICATION
Baseline de entrada: GATE 5.A.3 certificado — 14,002 PASS + Ruff limpio + 0 FAIL.

## 1. Propósito
Determinar, sin modificar producción, qué información técnica que el roadmap atribuye al nivel TECHNICAL de Analysis Mode existe realmente, bajo qué autoridad, si ya llega a `UnifiedRuntimeObservability`, y qué residual queda antes de cualquier CONTRACT RED.

Este Gate no crea un inventario técnico nuevo. Clasifica cobertura real.

## 2. Autoridades y seams que permanecen canónicos
- `OfficialConversationGateway`: única frontera interactiva oficial y propietario únicamente del estado efímero de Analysis Mode.
- `UnifiedRuntimeObservability`: única fuente read-only unificada certificada consumida por Analysis Mode.
- `RuntimeOperationalSnapshot`: snapshot operacional oficial; expone lifecycle/runtime/residents/errors/issues.
- `RuntimeHealthReadinessReport`: interpretación read-only de health/readiness/blockers/warnings/capability readiness.
- `OfficialRuntimeCapabilityRegistry`: autoridad oficial de registro de capacidades; Analysis Mode consume sólo su snapshot publicado.
- `RuntimeCapabilityGraph`: grafo declarativo de dependencias de capacidades; existe, pero no forma parte del snapshot unificado por defecto.
- `DependencyTrackingAuthority`: autoridad canónica de dependencias de tareas; no es un inventario técnico del runtime.
- Autoridades de Reasoning/Long-Horizon Investigation: poseen episodios y presupuestos propios; no son propiedad de Analysis Mode.

## 3. Matriz de cobertura técnica

| Dominio técnico | Evidencia/autoridad existente | Estado read-only oficial para Analysis Mode | Cobertura actual en TECHNICAL | Clasificación Gate 5.B |
|---|---|---|---|---|
| Runtime/lifecycle | `RuntimeOperationalSnapshot` | Sí, vía `UnifiedRuntimeObservability.operational` | Sí | PUBLISHED_SAFE |
| Resident components | `ResidentOperationalSnapshot` dentro de operational | Sí | Sí: estado, health, last_error, criticality, counts | PUBLISHED_SAFE |
| Errors/issues | `lifecycle_failure`, resident `last_error`, `issues` | Sí | Sí | PUBLISHED_SAFE |
| Health/readiness | `RuntimeHealthReadinessReport` | Sí, vía `.readiness` | Sí: level, health, blockers, warnings, capability readiness cuando fue evaluada | PUBLISHED_SAFE |
| Capability registry | `OfficialRuntimeCapabilityRegistry` / `RuntimeCapabilityView` | Sí | Sí: names + interface snapshot | PUBLISHED_SAFE |
| Capability gateway snapshot | `OfficialCapabilityGatewaySnapshot` | Condicional: puede ser `None` | Sí cuando existe; ausencia ya se declara `unavailable` | PUBLISHED_CONDITIONAL |
| Cognitive core operational presence | `CognitiveCoreObservabilitySnapshot` | Sí | Sí | PUBLISHED_SAFE |
| Conversation gateway state | `OfficialConversationGatewaySnapshot` | Sí | Sí | PUBLISHED_SAFE |
| Self-diagnostics availability | `SelfDiagnosticsObservabilitySnapshot` | Sí, metadata solamente | Sí: authority/implemented/runtime_provisioned/current_report | PUBLISHED_METADATA_ONLY |
| Recovery plan | `RuntimeRecoveryPlan` | Sólo si el caller suministra explícitamente `RuntimeCapabilityGraph`; Analysis Mode actual no lo hace | `not provisioned` en TECHNICAL | NOT_PROVISIONED_BY_ANALYSIS_MODE |
| Capability dependency graph | `RuntimeCapabilityGraph` | Existe como objeto declarativo, pero no está publicado en `UnifiedRuntimeObservabilitySnapshot` | No | EXISTING_NOT_PUBLISHED_TO_ANALYSIS_MODE |
| Task dependencies | `DependencyTrackingAuthority` | Existe bajo autoridad de planificación/tareas, requiere `TaskGraph` + completed ids para evaluar | No | EXISTING_DIFFERENT_DOMAIN_NOT_TECHNICAL_RUNTIME_INVENTORY |
| Reasoning episodes | `GovernedReasoningGateway` y estructuras de episodios productivos | Existen internamente/por turn; no hay snapshot técnico unificado certificado | No | EXISTING_NOT_UNIFIED_READ_ONLY |
| Long-horizon investigation episodes | autoridades `governed_multistep_investigation_*` / long-horizon | Existen con lineage/state/checkpoints | No snapshot técnico unificado certificado | EXISTING_NOT_UNIFIED_READ_ONLY |
| Budgets | presupuestos/restricciones en investigación, conversación y otras autoridades | Distribuidos y semánticamente locales a cada autoridad | No | EXISTING_DISTRIBUTED_NO_CANONICAL_TECHNICAL_VIEW |
| Schema/module versions | numerosos `SCHEMA_VERSION` / `schema_version` | Distribuidos; no hay catálogo runtime canónico certificado | No | EXISTING_DISTRIBUTED_NO_CANONICAL_RUNTIME_CATALOG |
| Project/app version | No se demuestra en este Gate una autoridad única publicada en observability | No | No | UNAVAILABLE_AS_CERTIFIED_TECHNICAL_SOURCE |
| Certifications | `docs/quality/*`, M361 y harnesses/scripts de certificación | Artefactos documentales/offline; no autoridad runtime read-only certificada | No | OFFLINE_EVIDENCE_OUTSIDE_RUNTIME_OBSERVABILITY |
| Test/Ruff status | M361 y resultados de ejecución externa/local | No son estado runtime publicado | No | OUTSIDE_ANALYSIS_MODE_RUNTIME_SOURCE |
| Dependency/version/certification repo scan | posible sólo leyendo archivos/repositorio | Prohibido por boundary actual | No | EXPLICITLY_OUT_OF_SCOPE |

## 4. Hallazgo principal
G5-R3 no es un único agujero que pueda cerrarse agregando campos a `analysis_mode_projection`.

La parte operacional de la vista TECHNICAL ya está sustancialmente cubierta y certificada. El residual se concentra en información que cae en tres clases diferentes:

1. **Existente pero no publicada a la fuente unificada:** p. ej. `RuntimeCapabilityGraph`.
2. **Existente pero distribuida y propiedad de otras autoridades:** episodios, budgets, task dependencies, schema versions.
3. **Offline/documental y no runtime:** certificaciones, M361, Ruff/pytest.

Mezclar estas tres clases en un `TechnicalInventoryManager` o hacer que Analysis Mode escanee el proyecto violaría la arquitectura gobernada.

## 5. Decisiones contractuales
### 5.1 Lo ya cerrado
El nivel TECHNICAL de Analysis Mode puede seguir proyectando sin cambios:
- operational;
- readiness;
- conversation;
- capabilities cuando esté publicado;
- registered_capabilities;
- capability_registry;
- cognitive_core;
- self_diagnostics availability metadata;
- recovery sólo si ya estuviera presente en el snapshot recibido, sin provocarlo.

### 5.2 Lo que NO debe inferirse como faltante productivo
No se autoriza crear:
- `TechnicalInventoryManager`;
- `TechnicalObservabilityRegistry`;
- `EpisodeRegistry` para Analysis Mode;
- `VersionRegistry` derivado de scans;
- `CertificationRegistry` derivado de documentos;
- un segundo dependency graph/manager;
- un segundo observability runtime.

### 5.3 RuntimeCapabilityGraph
Existe una fuente real y canónica de dependencias de capacidades. Sin embargo, `UnifiedRuntimeObservability.snapshot()` sólo la recibe opcionalmente para producir recovery y no publica el grafo mismo. Antes de decidir una costura productiva debe reconciliarse si el runtime oficial ya posee/provisiona un `RuntimeCapabilityGraph` canónico accesible sin construirlo, evaluarlo o escanear nada.

Por tanto, este Gate NO autoriza todavía exponer dependencies.

### 5.4 Episodes y budgets
Su existencia no autoriza una agregación transversal. Primero habría que demostrar un snapshot/read model ya existente y estable por cada autoridad relevante. Si no existe, crear uno sería una decisión arquitectónica separada, no una extensión automática de Analysis Mode.

### 5.5 Versions
Los `SCHEMA_VERSION` demuestran versionado local de contratos, no un catálogo técnico global. Analysis Mode no debe enumerar módulos ni inspeccionar código para fabricar uno.

### 5.6 Certifications / quality
Los artefactos de `docs/quality` y scripts certifican el proyecto fuera del runtime. Analysis Mode no debe leerlos automáticamente, ejecutar harnesses, Ruff o pytest, ni presentar una certificación histórica como estado runtime vivo.

## 6. Residual reconciliado
- **G5-R3a — operational/errors/health/readiness/capabilities:** CLOSED dentro del snapshot certificado actual.
- **G5-R3b — capability dependencies:** OPEN NARROW — existe `RuntimeCapabilityGraph`, falta determinar provisioning/reachability read-only oficial.
- **G5-R3c — episodes/budgets:** OPEN DEFERRED — fuentes distribuidas, sin read model técnico unificado certificado.
- **G5-R3d — versions:** OPEN DEFERRED — versionado distribuido, sin catálogo canónico runtime.
- **G5-R3e — certifications/quality:** OUTSIDE CURRENT RUNTIME OBSERVABILITY — evidencia offline, no debe autoingerirse.
- **G5-R4 — productive architectural evidence:** DELIBERATELY OPEN y no se toca en Gate 5.B.

## 7. Clasificación
**SUBSTANTIAL TECHNICAL OBSERVABILITY ALREADY PUBLISHED + ONE NARROW EXISTING CAPABILITY-DEPENDENCY REACHABILITY QUESTION + DISTRIBUTED/OFFLINE RESIDUALS THAT MUST NOT BE COLLAPSED INTO A NEW AUTHORITY**

## 8. Próximo paso recomendado
No corresponde CONTRACT RED general de “technical inventory”.

El único siguiente paso suficientemente estrecho es:

**GATE 5.B.1 — Existing RuntimeCapabilityGraph + Official Runtime Provisioning → Read-Only Capability Dependency Reachability — SURGICAL RECONCILIATION**

Objetivo: demostrar si el runtime oficial ya posee un grafo canónico que pueda publicarse/read-only sin nueva autoridad, sin evaluación productiva adicional y sin scans. Sólo después de esa reconciliación se decidirá si existe un CONTRACT RED real.

Episodes/budgets, versions y certifications quedan explícitamente fuera de 5.B.1.

## 9. STOP
Gate 5.B termina en reconciliación documental. No modificar producción. No crear RED todavía. No abrir G5-R4. No agregar registries/managers. No autoejecutar diagnostics, Reasoning, Planning, Reflection, Memory, Learning, Ruff, pytest o scanners. No leer automáticamente documentación/código para completar campos ausentes.
