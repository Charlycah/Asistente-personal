# ROBY XI.2 — Long-horizon Curiosity / Investigation
## Contract RED — Passive Durable Checkpoint → Governed Resume Candidate
### Reejecutado sobre ZIP corregido promovido

**Baseline oficial de entrada:** 13.540 PASS + Ruff limpio.

## Verificación de fuente

Este RED fue reejecutado sobre el ZIP corregido entregado como nueva fuente completa.

Se confirmó antes de ejecutar:
- la corrección Ruff de `multistage_causal_path.py` ya está incorporada;
- no existe todavía `app.governed_long_horizon_investigation_continuity`;
- se preservan los contratos históricos de primera línea de README y CHANGELOG.

## Objetivo

Congelar:

`GovernedInvestigationEpisodeState`
→ `GovernedPassiveInvestigationCheckpoint`
→ `GovernedInvestigationResumeCandidate`

sin GREEN, sin background autonomy y sin saltar Memory, Planning, Authorization,
Execution o Reasoning.

## Superficies contractuales esperadas

Módulo esperado:

`app.governed_long_horizon_investigation_continuity`

Contratos:
- `GovernedPassiveInvestigationCheckpoint`
- `GovernedInvestigationResumeCandidate`
- `GovernedLongHorizonInvestigationContinuityV1`
- operación `checkpoint(...)`
- operación `resume(...)`

## Checkpoint

Debe conservar:
- checkpoint/thread/episode IDs;
- originating reasoning;
- source reference;
- historial de snapshots;
- requirements;
- plans;
- authorizations;
- executions;
- reentries;
- adquisiciones consumidas;
- pause reason;
- source fingerprint.

Y debe ser pasivo:
- no autopersistencia;
- no background;
- no capabilities;
- no acciones;
- no Memory mutation;
- no World Model mutation;
- no Planning mutation;
- no authority grant.

## Resume candidate

Debe distinguir:
- snapshot anterior;
- snapshot actual;
- referencia explícita de resume;
- status/rationale/fingerprint.

No puede equivaler a autorización de Planning ni saltar gates.

## Ejecución RED sobre baseline corregida

Resultado:

**6 FAILED + 1 PASSED**

Los fallos siguen siendo exactamente los esperados:
1. módulo long-horizon inexistente;
2. checkpoint inexistente;
3. resume candidate inexistente;
4. gates `checkpoint`/`resume` inexistentes;
5. límites pasivos todavía no codificados;
6. límites contra bypass de Planning/Authorization todavía no codificados.

El PASS confirma que la investigación short-horizon histórica permanece:
- `max_acquisitions = 2`;
- `persists_results = False`;
- `starts_background_process = False`.

Por tanto, el ZIP corregido no altera el diagnóstico ni invalida el RED anterior.

## Regla GREEN

El siguiente GREEN debe cerrarse estrictamente en:

`Episode State → Passive Checkpoint → Governed Resume Candidate`

No debe incluir todavía:
- persistencia automática;
- timers/polling/daemon;
- Planning automático;
- Authorization automática;
- capability execution;
- reasoning rerun;
- Model Vn+1 automático.

La baseline oficial continúa siendo:

**13.540 PASS + Ruff limpio**
