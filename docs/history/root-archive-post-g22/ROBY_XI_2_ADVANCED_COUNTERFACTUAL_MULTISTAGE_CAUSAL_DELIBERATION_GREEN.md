# ROBY XI.2 — Advanced Counterfactual / Multi-stage Causal Deliberation
## GREEN — Multi-stage Causal Path → Counterfactual Path Comparison → Reasoning

**Baseline oficial de entrada:** 13.530 PASS + Ruff limpio.

## Cierre implementado

El bloque cierra productivamente:

`explicit CausalHypothesis stages`
→ `GovernedMultiStageCausalPath`
→ `GovernedCounterfactualPathComparison`
→ `CanonicalProductiveReasoningSource`
→ `ReasoningRuntimeContributor`

sin crear un motor causal paralelo ni trasladar autoridad hacia Decision, Planning,
Memory, Learning o World Model.

## 1. Multi-stage causal path

Nuevo owner-extension:

`core/governed_reasoning/multistage_causal_path.py`

Contratos:
- `MultiStageCausalPathStatus`
- `MultiStageCausalStageStatus`
- `GovernedMultiStageCausalStage`
- `GovernedMultiStageCausalPath`
- `GovernedMultiStageCausalPathComposer`

La composición acepta únicamente etapas causales explícitas ya estructuradas. No genera
hipótesis desde texto libre.

### Continuidad

Para cada par N/N+1 se exige equivalencia exacta normalizada entre:

`effect_domain/effect_key/effect_value` de N

y

`cause_domain/cause_key/cause_value` de N+1.

Una discontinuidad falla cerrada como `BROKEN_CHAIN`.

### Baseline y propagación

La primera etapa se evalúa mediante el `GovernedCausalPredictiveReasoner` existente sobre
el `PersistentWorldSnapshot` real.

Las etapas posteriores no se reinsertan como facts en el World Model. Sólo pueden
marcarse `CONDITIONALLY_PROPAGATED` cuando la etapa anterior tiene soporte condicional
desde baseline.

Si la primera etapa queda unresolved, las siguientes quedan
`BLOCKED_BY_UPSTREAM`. No existe promoción artificial de incertidumbre.

## 2. Counterfactual path comparison

Nuevo owner-extension:

`core/governed_reasoning/counterfactual_path_comparison.py`

Contratos:
- `CounterfactualPathComparisonStatus`
- `CounterfactualPathDivergence`
- `GovernedCounterfactualPathComparison`
- `GovernedCounterfactualPathComparator`

La comparación requiere al menos dos paths distintos, bajo mismo owner/session/baseline,
y todos deben ser `PATH_CANDIDATE`.

Preserva:
- baseline snapshot ID;
- path IDs;
- relation IDs por path;
- divergencias por etapa;
- source fingerprint.

No selecciona winner, no establece preferencia, verdad o causalidad.

## 3. Productive reachability

`OfficialGovernedReasoningRuntimeGateway` añade:

- `bind_productive_multistage_causal_path`
- `productive_multistage_causal_path`
- `productive_multistage_causal_path_reference_ids`
- `bind_productive_counterfactual_path_comparison`
- `productive_counterfactual_path_comparison`
- `productive_counterfactual_path_comparison_reference_ids`

`CanonicalProductiveReasoningSource` añade:

- referencias same-turn de comparación;
- `counterfactual_path_comparison_context_lines`.

`ReasoningRuntimeContributor` consume el hook estructuralmente y sólo añade contexto
consultivo.

## 4. Gobernanza

Ambos artefactos son:
- autoridad canónica `governed_reasoning`;
- read-only;
- consultivos;
- no persistentes.

No:
- crean facts;
- prueban causalidad;
- calibran probabilidad;
- escriben World Model;
- escriben Memory;
- activan Learning;
- modifican Planning;
- registran reglas;
- ejecutan Structural Transfer;
- ejecutan capabilities/actions;
- conceden autoridad.

## 5. GREEN contractual

El antiguo RED ahora pasa dentro del perímetro GREEN.

Además se certifica localmente en el test nuevo:
1. A→B→C produce path candidato.
2. A→B / X→C falla cerrado.
3. upstream unresolved bloquea downstream.
4. la proyección intermedia nunca se vuelve World fact.
5. dos paths forman comparación sin winner.
6. un único path no forma comparación.
7. baseline/path/relation lineage se conserva.
8. límites gobernados completos.
9. gateway productivo expone referencias same-turn.
10. comparison llega a Reasoning sólo como contexto consultivo.

## 6. Validación del entorno de construcción

Perímetro ampliado ejecutado:
- nuevo GREEN;
- M391.4 causal reasoning histórico;
- multi-future prospection histórica;
- Evidence-driven Explanatory Model Revision;
- global production import-graph cycle audit;
- contrato RED externo.

Resultado: **53 PASS**.

`py_compile` limpio para archivos modificados/nuevos y cero líneas >88.

Ruff global no es certificable en este entorno porque no existe un módulo/ejecutable
Ruff utilizable. El gate oficial continúa siendo local:

`ruff check .`
`pytest -q`

Con 10 tests oficiales nuevos, el baseline esperado tras promoción es:

**13.540 PASS + Ruff limpio**.
