# ROBY XI.2 — Advanced Counterfactual / Multi-stage Causal Deliberation
## Contract RED Evidence

**Baseline oficial de entrada:** 13.530 PASS + Ruff limpio.

## Objetivo contractual

Congelar el residual productivo identificado por la reconciliación quirúrgica:

`explicit causal stages`
→ `Governed Multi-stage Causal Path`
→ `Governed Counterfactual Path Comparison`
→ `ordinary Reasoning consultative reachability`

sin implementar GREEN y sin crear una nueva autoridad cognitiva.

## Contratos que RED exige

### 1. Multi-stage causal path
Módulo esperado bajo la autoridad existente:

`core.governed_reasoning.multistage_causal_path`

Superficies mínimas:
- `GovernedMultiStageCausalPath`
- `GovernedMultiStageCausalPathComposer`

La futura semántica GREEN deberá exigir continuidad estructural entre etapas:
el effect de N debe corresponder al cause de N+1. La trayectoria será explícita,
read-only y consultiva.

### 2. Counterfactual path comparison
Módulo esperado:

`core.governed_reasoning.counterfactual_path_comparison`

Superficies mínimas:
- `GovernedCounterfactualPathComparison`
- `GovernedCounterfactualPathComparator`

Debe comparar al menos dos trayectorias explícitas preservando baseline y lineage.
La comparación no puede declarar una trayectoria verdadera ni convertir una consecuencia
hipotética en hecho.

### 3. Productive reachability
`OfficialGovernedReasoningRuntimeGateway` deberá ofrecer:
- `bind_productive_multistage_causal_path(...)`
- `bind_productive_counterfactual_path_comparison(...)`

`CanonicalProductiveReasoningSource` deberá ofrecer:
- `counterfactual_path_comparison_context_lines(...)`

La salida sólo llegará a Reasoning como contexto consultivo.

## Invariantes GREEN que este RED congela

El GREEN posterior deberá probar además:

1. A→B→C válido forma una trayectoria multietapa.
2. A→B seguido de X→C falla cerrado por discontinuidad.
3. Una etapa unresolved no puede promover etapas posteriores como establecidas.
4. Las consecuencias intermedias siguen siendo hipótesis/inferencias, no facts.
5. Dos caminos explícitos pueden compararse sin declarar ganador verdadero.
6. Un único camino no basta para una comparación contrafactual.
7. Baseline, relation IDs, path IDs y stage lineage permanecen explícitos.
8. No hay Memory write, World Model write, Learning, Planning mutation, regla,
   Structural Transfer, ejecución o acción.
9. No se establece causalidad.
10. No se inventan probabilidades.
11. La reachability ordinaria es same-turn/session y consultiva.
12. Decision, si consume el resultado en el futuro, mantiene su autoridad separada.

## Ejecución RED

Resultado:

**5 FAILED + 1 PASSED**

Los cinco fallos son deliberados y corresponden exactamente a:
- ausencia de composición multietapa;
- ausencia de comparación contrafactual de trayectorias;
- ausencia de binding productivo de causal path;
- ausencia de binding productivo de comparación;
- ausencia de contexto consultivo hacia ordinary Reasoning.

El test que pasa confirma que `CausalHypothesis` continúa siendo una primitive causal
de una sola etapa y no ha sido convertida accidentalmente en un nuevo dueño de cadenas
causales ni en una autoridad causal automática.

Las advertencias de pytest son únicamente del cache temporal del entorno de ejecución
(`/mnt/data/.pytest_cache`) y no pertenecen a ROBY ni al contrato.

## Regla de admisión GREEN

No se debe debilitar este RED para hacerlo pasar. GREEN debe satisfacerlo reutilizando
las autoridades existentes, manteniendo el grafo productivo acíclico y preservando
todos los límites cognitivos certificados.

La baseline oficial permanece **13.530 PASS + Ruff limpio** hasta la certificación local
del futuro GREEN.
