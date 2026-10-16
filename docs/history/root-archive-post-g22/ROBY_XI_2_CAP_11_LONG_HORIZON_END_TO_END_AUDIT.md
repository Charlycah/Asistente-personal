# ROBY XI.2 — CAP-11 Long-Horizon Investigation
## Auditoría end-to-end y residual real pendiente

**Baseline certificada de entrada:** 13.669 PASS + Ruff limpio  
**Alcance:** ciclo gobernado long-horizon / CAP-11 Multi-step investigation  
**Regla:** una autoridad por capacidad; no segundo planner, executor, reasoner ni research-agent brain.

## 1. Dictamen ejecutivo

CAP-11 ya dispone de un **ciclo productivo gobernado completo y certificado de dos adquisiciones**. El recorrido efectivo queda cerrado end-to-end:

`R1 → P1 → A1 → E1 → RR1 → R2 → P2 → A2 → E2 → RR2 → CLOSED`

La cadena conserva las autoridades existentes de Planning, Authorization, Execution, Reasoning y Episode. Los bridges long-horizon añadidos no sustituyen esas autoridades: realizan admisión, continuidad, lineage, fail-closed y forwarding de productos exactos.

**Conclusión:** el residual de CAP-11 ya no es “hacer funcionar una investigación multi-step”. Eso está hecho. El residual real es **generalizar el horizonte y enriquecer la continuidad/replanificación sin romper el gobierno existente**.

CAP-11 debe permanecer por ahora como **SUBSTANTIAL / BOUNDED**, pero la palabra *BOUNDED* tiene ahora un significado preciso: el owner de episodio y el checkpoint v1 están fijados estructuralmente a **dos adquisiciones / pasos 1 y 2**.

## 2. Evidencia end-to-end existente

### 2.1 Continuidad y resumability bounded

Existe `GovernedLongHorizonInvestigationContinuityV1`, con checkpoint pasivo y candidato explícito de resume. Existe además `GovernedLongHorizonInvestigationResumeAdmissionV1` y wiring desde resume admitido hacia Planning existente.

Esto significa que **resumability ya existe**, pero sólo dentro del modelo bounded v1 y preservando el presupuesto corto del episodio.

### 2.2 Primera adquisición

La cadena long-horizon ya reconcilia:

- resume/admission;
- Evidence Acquisition Planning mediante el owner existente;
- Authorization mediante la frontera gobernada existente;
- Level-2 read-only Execution mediante el gateway existente;
- admisión de la evidencia adquirida en el episodio exacto.

No se crea planner ni executor paralelo.

### 2.3 Primera reentrada y continuación cognitiva

La evidencia E1 registrada vuelve al Reasoning existente y se registra en el episodio. La reevaluación puede producir exactamente un requisito R2 gobernado; cero requisitos produce cierre canónico y multiplicidad ambigua produce review fail-closed.

### 2.4 Segunda adquisición

R2 entra en el owner histórico P2; P2 entra en A2; A2 entra en E2. La evidencia E2 se registra en el mismo episodio y agota el presupuesto bounded.

### 2.5 Cierre terminal

El E2 exacto entra en `GovernedMultiStepInvestigationReasoningClosureV1`. RR2 se registra una vez y el episodio termina en:

- `CLOSED`;
- `BUDGET_EXHAUSTED`;
- `remaining_acquisitions == 0`;
- sin R3/P3/A3/E3;
- sin retry automático;
- sin mutación lateral de Memory/World Model.

Por tanto, **stopping terminal del ciclo bounded está cerrado**.

## 3. Autoridades: resultado de la auditoría

| Capacidad | Autoridad efectiva | Estado |
|---|---|---|
| Episode state / stopping | `GovernedMultiStepInvestigationEpisodeBoundaryV1` | Única, preservada |
| Planning | Planning existente + reentry adapters existentes | Única, preservada |
| Authorization | Independence Authorization existente | Única, preservada |
| Execution | Level-2 read-only gateway existente | Única, preservada |
| Reasoning re-entry | Level-2 Reasoning existente | Única, preservada |
| Terminal closure | `GovernedMultiStepInvestigationReasoningClosureV1` | Única, preservada |
| Long-horizon continuity | checkpoint/resume pasivo | Complementaria, no reemplaza owners |

**No se detecta necesidad arquitectónica de una nueva autoridad.**

## 4. Residual real pendiente

### R1 — Horizonte verdaderamente mayor que dos adquisiciones — PRIORIDAD ALTA

El límite más concreto está en `GovernedInvestigationEpisodeState`:

- `max_acquisitions` está fijado a `2`;
- `current_step` sólo admite `{1, 2}`.

El checkpoint long-horizon v1 también exige `max_acquisitions == 2` y declara que preserva el presupuesto short-horizon.

Por tanto, el nombre long-horizon describe hoy **continuidad alrededor de un episodio bounded**, no todavía una investigación de N pasos.

**Residual:** generalizar el contrato de horizonte/budget bajo el mismo Episode owner.  
**Prohibido:** resolverlo creando `EpisodeBoundaryV2` paralelo o un research-agent loop independiente.

### R2 — Replanning dinámico real — PRIORIDAD ALTA

Existe una segunda planificación P2 después de RR1, por lo que ya hay replanificación cognitiva **bounded**. Sin embargo no existe todavía un ciclo general que pueda decidir gobernadamente, para N pasos, entre:

- mantener plan;
- revisar plan por nueva evidencia;
- sustituir requisito;
- detener por suficiencia/riesgo/coste;
- continuar con siguiente adquisición.

La arquitectura general de Planning contiene señales de replanning, pero el ciclo CAP-11 no las compone todavía como política dinámica de horizonte largo.

**Residual:** composición/admisión de replanning sobre el planner existente, nunca un segundo planner.

### R3 — Resumability de horizonte general — PRIORIDAD MEDIA-ALTA

Checkpoint/resume ya existe y es una capacidad real. No debe reimplementarse.

Lo pendiente es ampliar su semántica para un episodio de horizonte general:

- presupuesto no fijado a 2;
- múltiples requisitos/planes/autorizaciones/ejecuciones/reentries;
- reanudación después de más de una frontera intermedia;
- validación de snapshot/lineage para historial N-step;
- política explícita ante cambios de mundo entre pausa y resume.

### R4 — Ledger explícito de gaps/requisitos pendientes — PRIORIDAD MEDIA

El master inventory menciona `unresolved-gap ledger`. Hay estructuras de gaps en Reasoning/Explanatory Model, pero no se observa un **ledger CAP-11 de investigación** que gobierne, a través de múltiples pasos, qué gaps fueron:

- resueltos;
- parcialmente resueltos;
- sustituidos;
- descartados;
- bloqueados;
- pendientes.

**Residual:** componer ese seguimiento con los owners cognitivos existentes. No crear una segunda memoria ni un gestor de curiosidad paralelo.

### R5 — Source diversity / estrategia de adquisición — PRIORIDAD MEDIA

El gateway y registry permiten capacidades/fuentes gobernadas, pero el ciclo actual prueba adquisiciones concretas de una en una. No hay todavía política CAP-11 para diversidad de fuentes, redundancia, corroboración o selección comparativa de evidencia a lo largo de N pasos.

**Residual:** enriquecer Evidence Acquisition Planning/Reasoning con criterios de diversidad y no redundancia, conservando las autoridades existentes.

### R6 — Integración concepto/teoría durante investigación larga — PRIORIDAD MEDIA/POSTERIOR

El inventario maestro pide concept/theory integration. ROBY ya posee piezas de explanatory model y unresolved gaps fuera de CAP-11. Lo pendiente no es inventar un motor teórico nuevo, sino permitir que una investigación larga consuma y refine esos productos bajo el mismo Reasoning.

Debe abordarse **después** de generalizar horizonte/replanning; hacerlo antes aumentaría acoplamiento sobre un episodio todavía fijado a dos pasos.

### R7 — Stopping generalizado — PRIORIDAD BAJA COMO CAPACIDAD NUEVA

Stopping bounded está bien desarrollado: budget exhausted, no new requirement, not authorized, acquisition unavailable/failed, review required, lineage broken, snapshot conflict y manual stop.

Por tanto, **“stopping” ya no es un hueco funcional principal**. El residual es sólo generalizar esas reglas a N pasos y añadir, si se justifica, criterios de suficiencia/coste/riesgo bajo owners existentes.

## 5. Qué NO es residual

No deben reabrirse como nuevas capacidades:

- Planning básico;
- Authorization básica;
- Level-2 read-only Execution;
- Reasoning re-entry;
- Episode recording;
- bounded stopping;
- checkpoint/resume básico;
- RR1→R2;
- P2/A2/E2;
- RR2 terminal closure;
- Curiosity como capacidad separada;
- Memory/World Model writer para “hacer persistente” la investigación.

Tampoco debe añadirse R3 simplemente para demostrar un tercer paso. Primero debe cambiar el **contrato de horizonte**, no duplicarse manualmente la cadena P2/A2/E2 como P3/A3/E3.

## 6. Estado CAP-11 propuesto tras esta auditoría

**Estado recomendado:** `SUBSTANTIAL / BOUNDED — END-TO-END CLOSED FOR 2-ACQUISITION EPISODE`.

Lectura precisa:

- **Productividad end-to-end:** cerrada.
- **Gobierno/autoridades:** cerrado para el ciclo actual.
- **Lineage/fail-closed:** fuerte.
- **Stopping bounded:** cerrado.
- **Resume bounded:** existente y productivo.
- **Long horizon N-step:** pendiente.
- **Dynamic replanning N-step:** pendiente.
- **Gap ledger / source strategy / theory integration:** pendientes de profundización.

## 7. Próximo bloque recomendado

No recomiendo abrir R3.

El siguiente bloque quirúrgico debería ser exclusivamente de **constitución del horizonte**:

> **CAP-11 Governed Horizon Generalization — reconciliación quirúrgica del Episode budget/step model + checkpoint continuity, reutilizando exactamente los owners actuales.**

Objetivo del bloque: determinar cómo pasar de `max_acquisitions == 2` / pasos `{1,2}` a un horizonte gobernado configurable o acotado, **sin implementar todavía P3/A3/E3**.

Debe congelar primero:

1. quién autoriza el budget/horizon;
2. límites máximos y fail-closed;
3. representación de step N;
4. invariantes de lineage N-step;
5. checkpoint/resume N-step;
6. stopping por budget;
7. compatibilidad retroactiva exacta con el episodio v1 de dos adquisiciones.

Sólo después de ese contrato tendría sentido reconciliar un **productive continuation N-step** reutilizando Planning → Authorization → Execution → Reasoning existentes.

## 8. Dictamen final

El ciclo que acabamos de cerrar **no es un prototipo incompleto**: es una investigación multi-step gobernada, productiva y terminalmente cerrada dentro de un presupuesto de dos adquisiciones.

El residual auténtico de CAP-11 es ahora de **profundidad y generalización**, no de completar piezas faltantes del ciclo actual.

La siguiente evolución correcta es hacer que el mismo cerebro gobernado pueda sostener un horizonte mayor, replanificar y reanudarse de forma general, manteniendo las mismas autoridades y los mismos principios fail-closed.
