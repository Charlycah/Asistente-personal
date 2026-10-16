# ROBY XI.2 — Long-horizon Curiosity / Investigation
## GREEN — Episode State → Passive Checkpoint → Governed Resume Candidate

**Baseline oficial de entrada:** 13.540 PASS + Ruff limpio.

## 1. Cierre implementado

Se añade continuidad temporal pasiva alrededor del lifecycle de investigación existente:

`GovernedInvestigationEpisodeState`
→ `GovernedPassiveInvestigationCheckpoint`
→ `GovernedInvestigationResumeCandidate`

El bloque no añade autonomía de background, no crea un nuevo Investigation Engine y no
modifica el límite histórico de dos adquisiciones del episodio V1.

## 2. Nuevo owner-extension

Nuevo módulo:

`app/governed_long_horizon_investigation_continuity.py`

Contratos:
- `GovernedInvestigationResumeStatus`
- `GovernedPassiveInvestigationCheckpoint`
- `GovernedInvestigationResumeCandidate`
- `GovernedLongHorizonInvestigationContinuityV1`

Operaciones:
- `checkpoint(...)`
- `resume(...)`

## 3. Passive Checkpoint

El checkpoint conserva explícitamente:
- episode/thread/reasoning/source lineage;
- snapshot lineage;
- requirement IDs;
- plan IDs;
- authorization IDs;
- execution IDs;
- reentry IDs;
- adquisiciones consumidas;
- presupuesto original;
- estado y stopping reason del episodio;
- pause reason;
- source fingerprint.

Es un artefacto **durable pero pasivo**:
- no se autopersiste;
- no escribe Memory;
- no escribe World Model;
- no modifica Planning;
- no ejecuta capabilities;
- no ejecuta acciones;
- no realiza Reasoning;
- no inicia procesos de background;
- no concede autoridad.

La futura persistencia real, si se habilita, deberá pasar por la autoridad canónica de
Memory en un bloque independiente.

## 4. Governed Resume Candidate

`resume(...)` exige:
- snapshot actual explícito;
- source reference actual explícita;
- referencia explícita de resume.

Estados posibles:
- `RESUME_CANDIDATE`
- `SNAPSHOT_REVIEW_REQUIRED`
- `SOURCE_LINEAGE_MISMATCH`
- `RESOLVED_INQUIRY`
- `BUDGET_REVIEW_REQUIRED`

### Same snapshot

Si source/snapshot coinciden y el episodio no está resuelto ni agotó presupuesto, se
produce únicamente un `RESUME_CANDIDATE`.

Esto no equivale a `READY_FOR_PLANNING` ni a autorización.

### Changed snapshot

Si cambió el snapshot:
- se conserva `previous_world_snapshot_id`;
- se registra `current_world_snapshot_id`;
- el estado queda `SNAPSHOT_REVIEW_REQUIRED`;
- no existe sustitución silenciosa del lineage histórico.

### Source mismatch

Falla cerrado como `SOURCE_LINEAGE_MISMATCH`.

### Resolved inquiry

Una inquiry cerrada como `RESOLVED` no se reactiva silenciosamente.

### Historical budget exhausted

Si las dos adquisiciones V1 ya fueron consumidas, el resume queda
`BUDGET_REVIEW_REQUIRED`. El bloque no crea presupuesto long-horizon ilimitado.

## 5. Autoridades preservadas

La continuidad conserva `planning_foundation` como autoridad de Planning.

El checkpoint/resume:
- no crea Planning;
- no concede `planning_execution_authorized`;
- no sustituye Authorization;
- no sustituye Execution;
- no rerunea Reasoning;
- no escribe Memory;
- no ejecuta acciones.

Por tanto el siguiente tramo productivo deberá volver a los gates existentes.

## 6. GREEN contractual

El RED oficial anterior ahora pasa sin modificar el contrato.

Tests GREEN adicionales verifican:
1. lineage completo en checkpoint;
2. checkpoint durable pero pasivo;
3. pause reason obligatorio;
4. same-snapshot resume produce sólo candidato;
5. changed snapshot exige review y preserva ambos snapshots;
6. source mismatch falla cerrado;
7. inquiry resuelta no se reactiva;
8. budget agotado requiere gobernanza separada;
9. resume requiere referencia explícita y nunca inicia background;
10. determinismo para entradas idénticas.

## 7. Compatibilidad histórica

Se ejecutó un perímetro ampliado con:
- nuevo GREEN;
- RED contractual externo;
- investigation episode foundation histórica;
- productive continuation;
- planning re-entry;
- authorization re-entry;
- execution re-entry;
- reasoning closure;
- test global de ciclos del production import graph.

Resultado del entorno de construcción:

**86 PASS**

## 8. Alcance deliberadamente excluido

Este GREEN NO implementa todavía:
- persistencia Memory del checkpoint;
- recuperación automática de checkpoints;
- timers/polling/daemon;
- resume automático;
- Planning automático;
- Authorization automática;
- Execution automática;
- reasoning rerun automático;
- Explanatory Model Vn+1 automático.

El siguiente residual queda claramente separado:

`Governed Resume Candidate`
→ `existing Planning/Authorization/Re-entry`
→ `Model Vn+1`

y debe tratarse como otro bloque de reachability.

## 9. Gate oficial

Con 10 tests oficiales nuevos, el baseline esperado tras promoción local es:

**13.550 PASS + Ruff limpio**

Gate:

`ruff check .`
`pytest -q`
