# ROBY XI.2 — Long-horizon Curiosity / Investigation
## Reconciliación quirúrgica post-13.540

**Baseline oficial de entrada:** 13.540 PASS + Ruff limpio.

## 1. Dictamen

ROBY ya posee una curiosidad epistémica gobernada y una investigación multistep real,
pero ambas están deliberadamente acotadas a horizontes cortos y artefactos no persistentes.

El residual real de "long-horizon" NO es crear otro Curiosity Engine ni otro
Investigation Engine. Es añadir **continuidad temporal gobernada de una investigación
ya existente**, preservando el dueño actual de cada capacidad.

## 2. Curiosity ya existente

### `core/cognitive_maturity/governed_epistemic_curiosity.py`

La curiosidad ya puede:
- reconocer un gap explícito;
- evaluar relevancia explícita;
- abstenerse cuando falta gobernanza;
- producir un `GovernedEpistemicQuestionCandidate`;
- suprimir repetición mediante `prior_question_reference`;
- distinguir hypothesis-check / clarification / learning.

Su contrato es deliberadamente:
- read-only;
- no persistente;
- sin Memory;
- sin Learning candidate;
- sin Knowledge mutation;
- sin background process;
- sin acciones;
- sin nueva autoridad.

Por tanto **no falta curiosidad básica**.

También existe adaptación desde gaps de hipótesis:
`core/cognitive_maturity/hypothesis_gap_curiosity_evidence.py`
y consumo productivo en:
`app/hypothesis_gap_curiosity_productive_consumption.py`.

## 3. Investigation ya existente

### `app/governed_multistep_investigation_episode.py`

Existe un lifecycle explícito con:
- reasoning/source/world-snapshot lineage;
- requirement IDs;
- plan IDs;
- authorization IDs;
- execution IDs;
- reentry IDs;
- stopping reasons;
- revisión de lineage/snapshot;
- manual stop;
- budget stop;
- continuación sólo cuando aparece un nuevo requirement.

Pero Foundation V1 fija:

- `max_acquisitions = 2`;
- `current_step` sólo puede ser 1 o 2;
- `persists_results = False`;
- `starts_background_process = False`.

Es decir: es realmente multistep, pero no long-horizon.

## 4. Cadena productiva existente

Ya está repartida entre owners existentes:

`DiscriminatingEvidenceRequirement`
→ Evidence Acquisition Planning
→ authorization
→ read-only execution
→ reasoning re-entry
→ revised discrimination/model
→ optional next requirement
→ multi-step continuation/stopping.

El cierre Evidence-driven Explanatory Model Revision ya permite que nueva evidencia
produzca V2. Por tanto el problema ya no es "investigar una vez y no aprender nada";
el problema es **mantener una investigación gobernada más allá del episodio corto**.

## 5. Longitudinal Reasoning no resuelve este residual

Existe:

`core/governed_reasoning/longitudinal_reasoning_assessment.py`

y su consumo productivo.

Puede evaluar patrones a través de una serie explícitamente suministrada de episodios.
Sin embargo, por contrato:
- no recupera historia por sí mismo;
- no persiste resultados;
- no rerunea reasoning;
- no autoriza review/stopping;
- no modifica hipótesis;
- no inicia background process.

Además declara explícitamente:
`longitudinal:not_temporal_trend`.

Por ello no debe confundirse con un gestor long-horizon de investigación.

## 6. Corte exacto de reachability

Actualmente ROBY puede hacer:

`gap ahora`
→ `pregunta/requisito`
→ `investigación bounded`
→ `evidencia`
→ `re-entry`
→ `V2`
→ `una segunda adquisición`
→ `stop`.

No encontré una representación productiva que permita:

`investigation episode`
→ `defer / await future evidence`
→ `resume later`
→ `validate changed world/source lineage`
→ `continue same inquiry`

a través de distintos turnos/sesiones o un intervalo temporal real.

Tampoco encontré una autoridad que conserve explícitamente un **investigation thread**
durable sin convertirlo en background autonomy.

## 7. Residual mínimo recomendado

### Governed Long-horizon Investigation Thread

Debe ser una composición/continuidad de artefactos existentes, no un nuevo cerebro.

Debe preservar:
- inquiry/thread ID;
- originating reasoning/model lineage;
- current unresolved requirement(s);
- completed episode IDs;
- evidence/reentry/model-revision lineage;
- owner/session scope policy;
- source reference;
- world snapshot history, sin exigir falsamente un snapshot idéntico para siempre;
- explicit pause/resume reason;
- budget acumulado gobernado;
- stopping criteria.

## 8. Distinción crítica: persistencia ≠ background autonomy

Para ser realmente long-horizon, alguna forma de estado durable será necesaria.

Eso NO implica:
- polling autónomo;
- timers propios;
- daemon;
- capability execution en background;
- búsqueda sin autorización;
- iniciativa irrestricta.

La forma correcta es un **checkpoint durable y pasivo** que sólo puede reabrirse mediante
un evento/turno/trigger ya gobernado por las autoridades existentes.

El thread recuerda dónde quedó la investigación; no "trabaja solo" mientras espera.

## 9. Cambio de snapshot

El contrato actual de investigación corta exige el mismo `world_snapshot_id` para la
continuación. Eso es correcto dentro del episodio V1.

Para horizonte largo, reutilizar literalmente esa igualdad sería incorrecto:
un nuevo día o nueva evidencia puede implicar un snapshot distinto.

Por tanto hace falta una transición explícita:

`previous snapshot`
→ `resume candidate with new snapshot`
→ lineage/compatibility review`

sin sobrescribir el snapshot histórico y sin aceptar silenciosamente cualquier mundo nuevo.

Esto es uno de los residuales arquitectónicos principales.

## 10. Curiosity long-horizon

Curiosity no necesita otro generador de preguntas.

El residual es poder distinguir:
- gap nuevo;
- gap ya preguntado;
- gap pendiente;
- gap parcialmente resuelto;
- gap reabierto por nueva evidencia;
- gap cerrado.

Hoy existe `prior_question_reference`, pero no un lifecycle durable completo del gap/inquiry.

Ese lifecycle debe estar subordinado a la investigación/epistemic governance existente,
no convertirse en una memoria o agenda paralela.

## 11. Límites de autoridad

El futuro bloque debe:
- mantener Curiosity bajo su owner cognitivo actual;
- mantener Reasoning en `governed_reasoning`;
- mantener Planning en `planning_foundation`;
- mantener ejecución bajo gateways/authorization existentes;
- usar Memory sólo mediante su autoridad canónica si un checkpoint durable debe persistir.

No debe:
- crear otro Memory;
- escribir World Model arbitrariamente;
- aprender automáticamente;
- ejecutar capacidades;
- hacer polling;
- crear background workers;
- autorizarse a sí mismo;
- convertir una inquiry pendiente en tarea ejecutable sin gate.

## 12. RED recomendado

Antes de GREEN, congelar:

1. Un episodio cerrado/pausado puede producir un checkpoint pasivo con lineage completo.
2. El checkpoint no ejecuta, no planifica y no inicia background work.
3. Puede reanudarse en un turno posterior sólo mediante un resume explícito/gobernado.
4. Resume con snapshot idéntico conserva continuidad.
5. Resume con snapshot nuevo exige compatibility/review, nunca sustitución silenciosa.
6. Evidence/model-revision lineage previo se conserva.
7. Requirement resuelto no se vuelve a preguntar/reinvestigar sin razón de reapertura.
8. Un gap pendiente puede permanecer pendiente sin fabricar una pregunta nueva.
9. Budget long-horizon no equivale a ilimitado; requiere límite y stopping policy.
10. Owner/source lineage mismatch falla cerrado.
11. Persistencia, si existe, pasa por Memory authority; el thread no se autopersiste.
12. No timer, polling, daemon, capability invocation ni acción.
13. El resultado reanudado puede volver al pipeline existente de Planning/Authorization,
    pero no saltarse ninguno de sus gates.
14. Explanatory Model Vn puede continuar a Vn+1 mediante nueva evidencia sin reemplazar
    silenciosamente hypothesis lineage.
15. Ordinary Reasoning recibe sólo estado consultivo del inquiry/thread.

## 13. Prioridad recomendada

El próximo bloque NO debería intentar "investigación autónoma de largo plazo" completa.

Primero cerrar sólo:

**Investigation Episode → Passive Durable Checkpoint Contract → Governed Resume Candidate**

Esto resolvería el corte temporal fundamental sin introducir autonomía de background.

Después, en un bloque separado y sólo si la arquitectura lo justifica:
**Reopened Inquiry → Existing Planning/Authorization/Re-entry → Model Vn+1**.

## 14. Conclusión

Long-horizon Curiosity / Investigation permanece como residual real, pero ya no es un
problema de curiosidad ni de investigación básica.

El hueco exacto es:

**continuidad temporal durable, pasiva y gobernada de una inquiry existente**.

La arquitectura correcta debe extender owners existentes y convertir el tiempo en una
dimensión de lineage, no en una nueva autoridad.
