# ROBY XI.2 — Advanced Counterfactual / Multi-stage Causal Deliberation
## Reconciliación quirúrgica post-13.530

**Baseline oficial de entrada:** 13.530 PASS + Ruff limpio (certificación local del usuario).

## 1. Dictamen

CAP-06 ya posee una base causal/prospectiva sustancial y gobernada, pero no existe todavía
una representación productiva de **trayectoria causal multietapa** ni una comparación
contrafactual explícita de trayectorias completas.

El residual real NO es crear otro motor causal, Scenario Manager, Counterfactual Engine,
Planner o Decision Engine. Es una extensión/composición bajo `governed_reasoning`, con
salida consultiva hacia la autoridad de decisión existente cuando corresponda.

## 2. Lo que ya existe

### Scenario Simulation
`core/governed_reasoning/scenario_simulation.py`

- `ScenarioHypothesis` admite `temporal_scope="future"`.
- Dos futuros alternativos pueden coexistir sobre el mismo estado actual.
- Un futuro alternativo no se trata automáticamente como contradicción del hecho actual.
- La simulación es read-only, no crea hechos y no modifica World Model.

### Causal Prediction
`core/governed_reasoning/causal_prediction.py`

- `CausalHypothesis` representa una relación explícita causa → efecto.
- `GovernedCausalPredictiveReasoner` produce evaluación causal conservadora y predicción
  condicional.
- La coexistencia sólo produce `association_compatible`; no demuestra causalidad.
- La predicción permanece inferencia, no hecho futuro.
- El propio documento M391.4 declara fuera de alcance la **predicción multietapa** y la
  **planificación contrafactual ejecutable**.

### Multi-future prospection / decision advisory
`tests/architecture/test_post_hcpdq_causal_prospection_8_case_multi_future_challenge.py`
demuestra que:
- se pueden comparar futuros alternativos;
- las consecuencias proyectadas pueden cambiar una recomendación;
- la incertidumbre obliga a abstenerse;
- todo permanece consultivo/no ejecutor.

`core/governed_decision_advisory.py` ya consume Scenario/Causal evidence bajo
`unified_cognitive_coordination`, pero cada `GovernedDecisionOption` referencia como máximo
un `scenario_hypothesis_id` y un `causal_relation_id`.

## 3. Corte exacto de reachability

La arquitectura actual puede expresar:

`estado actual → hipótesis futura`

y:

`causa A → efecto B`

y puede comparar varias alternativas A/B como opciones.

No encontré una autoridad/productive artifact que represente y valide explícitamente:

`A → B → C`

donde la salida condicional de una etapa sea la entrada hipotética de la siguiente, con
lineage por etapa y sin escribir B en el World Model.

Tampoco existe una comparación contrafactual de trayectorias completas:

`factual baseline`
↔ `counterfactual path A: A1 → A2 → A3`
↔ `counterfactual path B: B1 → B2 → B3`

preservando por separado supuestos, consecuencias condicionales, puntos no resueltos,
evidencia y riesgos.

## 4. Residual mínimo recomendado

### Advanced Counterfactual / Multi-stage Causal Deliberation — Governed Productive Reachability

Debe reutilizar:

- `PersistentWorldSnapshot` como baseline explícita;
- `ScenarioHypothesis`;
- `CausalHypothesis`;
- `GovernedScenarioSimulator`;
- `GovernedCausalPredictiveReasoner`;
- la autoridad `governed_reasoning`;
- `GovernedDecisionAdvisor` / `CanonicalDecisionFacade` sólo para consumo consultivo
  posterior, sin trasladar la autoridad causal a Decision.

El nuevo contrato debe ser una **composición de trayectoria**, no un razonador paralelo.

## 5. Semántica necesaria

Una trayectoria multietapa debe:

1. recibir etapas causales explícitas, no inventarlas desde free text;
2. exigir continuidad estructural entre etapas:
   `effect(domain,key,value)` de etapa N debe corresponder a
   `cause(domain,key,value)` de etapa N+1;
3. conservar el `PersistentWorldSnapshot` original como baseline;
4. NO materializar consecuencias hipotéticas como hechos del World Model;
5. distinguir:
   - etapa soportada condicionalmente;
   - etapa no resoluble;
   - cadena rota;
   - contradicción con baseline;
6. propagar incertidumbre: una etapa no soportada no puede convertirse mágicamente en
   soporte fuerte para etapas posteriores;
7. conservar lineage por relación y por etapa;
8. producir una trayectoria consultiva reproducible.

## 6. Contrafactual

Una comparación contrafactual debe requerir al menos dos trayectorias explícitas y
distinguir claramente:

- baseline factual;
- supuesto/intervención hipotética inicial;
- consecuencias condicionales derivadas;
- divergencias entre trayectorias;
- puntos donde la evidencia deja de discriminar.

`counterfactual` aquí significa **comparación intelectual de mundos hipotéticos**, no
modificación del mundo real ni autorización de intervención.

## 7. Límites de autoridad

El bloque debe permanecer:

- `canonical_authority = "governed_reasoning"`;
- read-only / consultative;
- sin crear hechos;
- sin probar causalidad;
- sin probabilidades inventadas;
- sin Memory writes;
- sin World Model writes;
- sin Learning;
- sin Planning mutation;
- sin reglas;
- sin Structural Transfer;
- sin ejecución;
- sin acciones;
- sin nueva autoridad.

Si posteriormente una comparación llega a Decision, debe hacerlo como evidencia
consultiva a la autoridad existente `unified_cognitive_coordination`.

## 8. Lo que NO conviene tocar

- No repurposear `core/cross_domain_coordination.py`.
- No ampliar `PersistentWorldSnapshot` para guardar futuros simulados.
- No convertir `GovernedCausalPredictiveReasoner` en un planificador.
- No convertir `GovernedDecisionAdvisor` en razonador causal.
- No crear `CounterfactualEngine`, `CausalChainManager`, `FutureWorldModel` ni otro cerebro.
- No mezclar este bloque con ejecución contrafactual o autonomía.

## 9. RED recomendado

Antes de GREEN, congelar contractualmente al menos:

1. `A → B → C` válido produce una trayectoria multietapa consultiva.
2. Una cadena con discontinuidad `A → B`, `X → C` falla cerrada.
3. Una consecuencia intermedia hipotética no aparece como hecho persistente.
4. Una etapa unresolved impide promover etapas posteriores como establecidas.
5. Dos trayectorias explícitas pueden compararse sin declarar una verdadera.
6. La comparación conserva baseline + path lineage + relation IDs.
7. Un único camino no se presenta como comparación contrafactual.
8. El resultado no prueba causalidad, no modifica memoria/mundo/planning y no ejecuta.
9. Reachability productiva llega a Reasoning como contexto consultivo.
10. Si se conecta a Decision, sólo entra como evidencia advisory y no autoriza acción.

## 10. Conclusión

La reconciliación confirma el residual histórico de CAP-06:
**multi-stage counterfactual chains**.

La base de prospección multi-futuro ya existe y es más madura de lo que sugería el nombre
del residual. El hueco exacto está entre relaciones causales de una sola etapa y una
trayectoria causal/contrafactual gobernada con lineage explícito.

**Siguiente paso recomendado:** RED contractual de
`Multi-stage Causal Path → Counterfactual Path Comparison → consultative Reasoning
reachability`, sin implementar GREEN todavía.
