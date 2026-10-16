# ROBY XI.2 — Governed Resume Candidate → Existing Planning / Authorization / Re-entry → Model Vn+1
## Reconciliación quirúrgica post-13.550

**Baseline oficial de entrada:** 13.550 PASS + Ruff limpio.

## 1. Dictamen

El tramo completo todavía NO debe implementarse como un único puente.

La razón principal es que el nuevo `GovernedInvestigationResumeCandidate` ya resuelve
la continuidad temporal pasiva, pero **todavía no porta el objeto semántico
`DiscriminatingEvidenceRequirement` que el Planning existente necesita**, y además los
gates históricos de multi-step re-entry están deliberadamente especializados en el
**segundo paso del episodio V1**.

Por tanto, el residual real se divide en dos cortes distintos:

1. **Resume Candidate → Governed Requirement Rebinding / Resume Admission**
2. **Resume Admission → Existing Evidence Planning / Authorization / Execution / Re-entry**

El segundo sólo puede reutilizarse sin cambios si se respetan sus precondiciones
históricas. No debe falsificarse un `GovernedMultiStepInvestigationProductiveContinuation`
para hacer entrar al resume.

## 2. Lo que ya existe y debe reutilizarse

### Long-horizon continuity

`app/governed_long_horizon_investigation_continuity.py`

Ya produce:
- `GovernedPassiveInvestigationCheckpoint`
- `GovernedInvestigationResumeCandidate`
- `RESUME_CANDIDATE`
- `SNAPSHOT_REVIEW_REQUIRED`
- `SOURCE_LINEAGE_MISMATCH`
- `RESOLVED_INQUIRY`
- `BUDGET_REVIEW_REQUIRED`

Y preserva el principio correcto:
**resume candidate no equivale a Planning ni Authorization**.

### Evidence Acquisition Planning

`app/governed_evidence_acquisition_productive_consumption.py`

La superficie existente consume directamente un:

`DiscriminatingEvidenceRequirement`

y delega en:

`core/evidence_acquisition_planning.py`

El planner ya conserva:
- requirement ID;
- source reference;
- world snapshot;
- capability candidates;
- evidence outputs;
- estado plannable/partial/ambiguous/unavailable.

No hace falta un nuevo planner.

### Planning re-entry histórico

`app/governed_multistep_investigation_planning_reentry.py`

No acepta un resume candidate. Acepta exclusivamente:

`GovernedMultiStepInvestigationProductiveContinuation`

y exige:
- `CONTINUE_ALLOWED`;
- estado `READY_FOR_PLANNING`;
- `current_step == 2`;
- `remaining_acquisitions == 1`;
- requirement object exacto;
- exact source lineage;
- exact snapshot lineage;
- no autorización ejecutiva previa.

Por tanto esta clase es un **re-entry P2 del episodio corto**, no una entrada genérica
para cualquier investigación reanudada.

### Authorization / Execution / Reasoning closure

Las capas:
- `governed_multistep_investigation_authorization_reentry.py`
- `governed_multistep_investigation_execution_reentry.py`
- `governed_multistep_investigation_reasoning_closure.py`

también están especializadas en:
- step 2;
- una sola adquisición restante;
- segundo plan/authorization/execution;
- cierre obligatorio por `BUDGET_EXHAUSTED`.

No deben reutilizarse artificialmente para representar un horizonte >2.

## 3. Corte de reachability exacto

Hoy existe:

`Episode State`
→ `Passive Checkpoint`
→ `Resume Candidate`

pero desde ahí no existe una superficie que haga:

`Resume Candidate`
+ `exact current DiscriminatingEvidenceRequirement`
→ `validated resumed inquiry admission`

sin planificar ni ejecutar.

El checkpoint sólo conserva `requirement_ids`; no conserva el objeto semántico completo
`DiscriminatingEvidenceRequirement`.

Eso es correcto: el checkpoint no debe serializar ni reconstruir arbitrariamente un
requisito cognitivo a partir de IDs.

El residual inmediato es por tanto un **re-binding explícito y validado** del requirement.

## 4. Por qué no debe reconstruirse el requirement desde IDs

El planner necesita campos semánticos reales del requirement:
- hypothesis IDs;
- missing evidence descriptions;
- source reference;
- world snapshot;
- flags de gobernanza.

Un `requirement_id` no contiene esa información.

Reconstruir el objeto desde el ID:
- inventaría semántica;
- rompería lineage;
- podría introducir evidencia o hipótesis que no existían;
- convertiría el bridge en una autoridad cognitiva paralela.

Por eso el próximo bridge debe recibir el requirement como **input explícito** y sólo
verificar su identidad/compatibilidad con checkpoint + resume candidate.

## 5. Residual recomendado: Governed Resume Admission

Nuevo bloque mínimo recomendado:

**Governed Resume Candidate → Governed Investigation Resume Admission**

Debe consumir:
- checkpoint exacto;
- resume candidate exacto;
- `DiscriminatingEvidenceRequirement` explícito.

Debe validar:
- `resume.status == RESUME_CANDIDATE`;
- checkpoint ID exacto;
- thread ID exacto;
- requirement ID pertenece al checkpoint y es el unresolved/current esperado;
- source reference exacta;
- snapshot exacto para V1 same-snapshot;
- originating reasoning lineage;
- no requirement ya resuelto;
- no budget agotado;
- no prior plan/authorization/execution reuse;
- no mutation, no planning, no execution.

Salida recomendada:
`GovernedInvestigationResumeAdmission`

con:
- thread/checkpoint/resume IDs;
- exact requirement object/reference;
- source/snapshot lineage;
- status `ADMITTED | NOT_ELIGIBLE | REVIEW_REQUIRED`;
- `eligible_for_existing_planning`;
- rationale/fingerprint;
- límites no ejecutivos explícitos.

## 6. Importante: NO reutilizar `GovernedLevel2BProductiveEntryFoundationV1`

`GovernedLevel2BProductiveEntryFoundationV1.admit(...)`:
- crea un episodio nuevo;
- deduplica una admisión inicial;
- inicia estado OPEN;
- fija el budget V1.

Usarlo para resume produciría un episodio nuevo y rompería la continuidad del
`thread_id`/`episode_id`.

Por tanto el resume necesita una **admisión de continuidad**, no una segunda Level2B entry.

## 7. Importante: NO fabricar `GovernedMultiStepInvestigationProductiveContinuation`

Ese objeto representa la transición histórica:

`AWAITING_REQUIREMENT`
→ nueva R2
→ `READY_FOR_PLANNING`
→ step 2

No representa:
- resume temporal;
- recuperación de checkpoint;
- same-step continuation;
- nuevo horizonte.

Fabricarlo para satisfacer `planning_reentry` sería un bypass semántico.

## 8. Snapshot temporal: V1 sólo same-snapshot

El GREEN anterior ya distingue:
- same snapshot → `RESUME_CANDIDATE`;
- changed snapshot → `SNAPSHOT_REVIEW_REQUIRED`.

Por tanto el próximo bloque debe admitir **sólo same-snapshot**.

No conviene todavía adaptar Planning ni Model Revision a snapshot nuevo.

Esto mantiene el próximo GREEN pequeño y demostrable.

## 9. Segundo corte: Model Revision también tiene un límite temporal

`app/governed_explanatory_model_revision.py` exige actualmente:

- reentry source == model V1 source;
- reentry world snapshot == model V1 snapshot;
- revised report source == model V1 source;
- revised report world snapshot == model V1 snapshot;
- mismo conjunto de hipótesis;
- evidencia adquirida aplicada;
- cambio material.

Así que incluso si más adelante se aprueba un resume con **snapshot nuevo**, la revisión
Vn→Vn+1 histórica lo rechazará por `LINEAGE_MISMATCH`.

Esto es correcto para el contrato actual.

Por tanto existen dos futuros:

### Camino A — same-snapshot resume

Puede reutilizar el revision contract actual, una vez que el resume haya pasado por
Planning / Authorization / Execution / Reasoning re-entry de forma gobernada.

### Camino B — changed-snapshot resume

Requerirá otro bloque específico:
**Temporal Model Continuity / Cross-snapshot Revision Review**

No debe mezclarse con el próximo GREEN.

## 10. Budget: otro límite independiente

El episodio histórico fija:
`max_acquisitions = 2`.

El resume GREEN actual devuelve:
`BUDGET_REVIEW_REQUIRED`
si ya se consumieron las dos adquisiciones.

Por tanto un verdadero horizonte >2 todavía no existe.

No debe incrementarse el budget escondidamente desde el resume bridge.

Si se desea más adelante investigación realmente prolongada, hará falta un bloque de:
**Governed Long-horizon Investigation Budget Renewal / New Episode Continuation**

con autoridad y stopping policy explícitos.

## 11. Secuencia correcta desde 13.550

### Bloque inmediato

**Resume Candidate → Governed Requirement Rebinding / Resume Admission**

Sin Planning.

### Bloque siguiente

**Resume Admission → Existing Evidence Acquisition Planning**

Reutilizando el planner existente directamente, con un adapter de admisión estrecho,
no mediante el `planning_reentry` especializado en P2 si sus invariantes no coinciden.

### Después

Reconciliar qué Authorization/Execution gate genérico existente puede recibir ese plan
sin depender artificialmente de `current_step == 2`.

Si no existe uno genérico, extender el owner existente; no crear otra autoridad.

### Finalmente

**Acquired Evidence → Existing Reasoning Re-entry → Existing Model Revision**

para same-snapshot.

## 12. RED recomendado para el próximo bloque

Congelar primero:

1. módulo de resume admission inexistente;
2. consume checkpoint + resume candidate + requirement explícito;
3. sólo `RESUME_CANDIDATE` puede ser admitido;
4. exact checkpoint/thread lineage;
5. exact requirement ID;
6. exact source;
7. exact same snapshot;
8. requirement resuelto/reutilizado falla cerrado;
9. budget agotado falla cerrado;
10. no crea episodio nuevo;
11. no llama Level2B;
12. no llama Planning;
13. no llama Authorization;
14. no ejecuta capability;
15. no rerunea Reasoning;
16. no escribe Memory/World Model;
17. salida sólo `eligible_for_existing_planning`;
18. determinismo.

## 13. Conclusión

El próximo paso NO debería ser todavía:

`Resume Candidate → Planning → Authorization → Execution → Model Vn+1`

como una única implementación.

El corte más seguro y arquitectónicamente correcto es:

**Governed Resume Candidate**
→ **explicit Requirement Rebinding**
→ **Governed Resume Admission**

Ese bloque restaura la semántica cognitiva exacta de la inquiry sin crear nada nuevo.

Sólo después se conecta la admisión al Planning existente.

Esto preserva:
- una autoridad por capacidad;
- el episodio/thread original;
- el requirement real;
- el snapshot real;
- los gates existentes;
- el budget existente;
- y evita convertir la continuidad temporal en un bypass de ejecución.
