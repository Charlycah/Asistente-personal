# ROBY XI.2 — GATE 5.C

## Existing Governed Investigation Episode/Budget Authorities → Unified Read-Only Technical Introspection — ARCHITECTURAL RECONCILIATION

### Estado de entrada

Base oficial certificada por el usuario:

- GATE 5.B.4.1 — SURGICAL GREEN — CERTIFIED AND CLOSED.
- 14.034 PASS.
- Ruff limpio.
- 0 FAIL.

Este gate es exclusivamente reconciliatorio. No modifica producción y no abre
CONTRACT RED automáticamente.

## 1. Pregunta arquitectónica

Después de cerrar G5-R3b (capability dependencies), determinar si G5-R3c
(episodes/budgets) posee una costura real que pueda llevar estado canónico
read-only hasta `UnifiedRuntimeObservability` y luego TECHNICAL sin crear un
EpisodeRegistry, BudgetManager, segundo runtime ni autoridad paralela.

## 2. Estado real verificado en código

### 2.1 Autoridad de episodios de investigación multistep

`app.governed_multistep_investigation_episode` define:

- `GovernedInvestigationEpisodeState`, dataclass frozen;
- lineage explícito de requirement/plan/authorization/execution/local execution/reentry;
- `consumed_acquisitions`;
- `max_acquisitions`;
- `current_step`;
- status y stopping reason;
- `remaining_acquisitions`;
- hard cap `GOVERNED_INVESTIGATION_MAX_ACQUISITIONS = 4`.

`GovernedMultiStepInvestigationEpisodeBoundaryV1` es la autoridad de transición.
Opera sobre estados suministrados. No mantiene un registry global de episodios.

Por tanto el budget no es una autoridad global separada: forma parte del estado
canónico de cada episodio.

### 2.2 Owner productivo alcanzable

`OfficialGovernedReasoningRuntimeGateway` mantiene los episodios productivos
internos por owner/session y ofrece getters gobernados exactos, incluyendo
`productive_episode(...)`.

Su snapshot general `GovernedReasoningRuntimeSnapshot`, sin embargo, sólo
publica:

- evaluations;
- last_owner;
- last_status;
- last_confidence;
- last_requires_human_review.

No publica un read-model de episodios activos ni budget.

### 2.3 Reachability desde el runtime oficial

`RuntimeCompositionDependencies` ya contiene
`governed_reasoning_runtime: object | None`.

`runtime_root_factory` provisiona allí la misma instancia
`OfficialGovernedReasoningRuntimeGateway` utilizada por el runtime productivo.

Por tanto existe reachability oficial al owner. No hace falta crear otro
registry/runtime/manager.

### 2.4 UnifiedRuntimeObservability

El snapshot unificado actual no contiene episodes/budgets y no lee stores
privados de Reasoning.

Esto es correcto. Observability no debe recorrer `_productive_episodes`, ni
reconstruir estados, ni ejecutar Reasoning para obtener introspección.

## 3. Dictamen G5-R3c

Clasificación:

**CANONICAL PRODUCTIVE OWNER EXISTS + OFFICIAL RUNTIME REACHABILITY EXISTS +
CANONICAL IMMUTABLE EPISODE STATE EXISTS + OWNER-LEVEL READ-ONLY ACTIVE
EPISODE/BUDGET READ MODEL IS MISSING.**

El residual real está un nivel antes de `UnifiedRuntimeObservability`.

No corresponde empezar agregando `episodes` o `budgets` directamente a
Analysis Mode. Primero el owner canónico debe exponer una vista read-only
explícita y acotada.

## 4. Frontera recomendada

La cadena correcta futura es:

`OfficialGovernedReasoningRuntimeGateway`
→ owner-level immutable read-only episode/budget view
→ `UnifiedRuntimeObservability`
→ Analysis Mode TECHNICAL

Nunca:

Analysis Mode
→ `_productive_episodes`

ni:

UnifiedRuntimeObservability
→ private-store scan / reconstruction

ni:

EpisodeRegistry / BudgetManager paralelo.

## 5. Semántica que debe congelar el próximo RED

El próximo RED debe limitarse al primer seam:

**canonical Governed Reasoning owner → immutable read-only active
investigation episode/budget view.**

Debe demostrar, como mínimo:

1. la fuente es exclusivamente `OfficialGovernedReasoningRuntimeGateway`;
2. no se crea registry/manager/runtime paralelo;
3. no se expone el dict privado `_productive_episodes`;
4. la vista es immutable/read-only;
5. preserva IDs y lineage canónicos, sin inferencia;
6. preserva `consumed_acquisitions`, `max_acquisitions`,
   `remaining_acquisitions`, `current_step`, status y stopping reason;
7. no calcula un budget global;
8. no fusiona episodios cognitivos, epistemic episodes, concept episodes ni
   long-horizon structures bajo una falsa autoridad común;
9. no ejecuta Reasoning, Planning, Authorization, Execution, Reflection,
   Memory o Learning para producir la vista;
10. una ausencia real se representa honestamente como ausencia, no como
    episodio sintético;
11. el acceso debe ser scoped por las identidades canónicas que el owner ya
    gobierna; no enumerar indiscriminadamente stores privados;
12. `.roby/config.json` permanece sin cambios.

## 6. Qué NO debe abrir este bloque

- no `UnifiedRuntimeObservability` GREEN todavía;
- no Analysis Mode TECHNICAL episode projection todavía;
- no G5-R3d versions;
- no G5-R3e certifications/quality;
- no G5-R4 architectural evidence;
- no PERSONAL;
- no ampliación del Cognitive Self Model;
- no Memory/Learning;
- no Planning N+1;
- no autonomía adicional;
- no scans de repositorio/documentación/tests;
- no background monitoring.

## 7. Versions / certifications / G5-R4

Permanecen separados:

- G5-R3d: distributed contract versioning, sin catálogo runtime canónico;
- G5-R3e: certification logic/offline quality existe, pero no hay estado
  runtime certificado publicado;
- G5-R4: no existe fuente productiva certificada de evidencia arquitectónica
  viva.

Ninguno debe resolverse incidentalmente dentro de episodes/budgets.

## 8. Próximo gate recomendado

**GATE 5.C.1 — Official Governed Reasoning Runtime Canonical Investigation
Episode/Budget State → Scoped Immutable Read-Only Introspection View —
CONTRACT RED**

Sólo después de certificar ese owner-level seam deberá reconciliarse un gate
posterior para su publicación en `UnifiedRuntimeObservability`. La proyección
TECHNICAL será un consumidor posterior, no el lugar donde se crea la fuente.

## 9. STOP

Esta reconciliación termina aquí.

No CONTRACT RED automático.
No GREEN.
No cambio productivo.

## Dictamen final

**G5-R3b CLOSED + G5-R3c HAS A REAL OWNER-LEVEL READ-MODEL GAP + NEXT SAFE
SEAM IS REASONING-OWNER READ-ONLY EPISODE/BUDGET INTROSPECTION, NOT ANALYSIS
MODE AND NOT A NEW REGISTRY.**
