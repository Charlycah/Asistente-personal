# M391.4 — Comprensión Causal y Predictiva Gobernada

## Objetivo

Continuar la Época IV — Inteligencia Continua incorporando una capacidad
consultiva para evaluar relaciones causales explícitamente hipotéticas y emitir
predicciones condicionales sin convertir correlación en causa, predicción en
hecho ni razonamiento en acción.

## Autoridad

M391.4 no crea una autoridad nueva. La capacidad pertenece a
`governed_reasoning`, autoridad primaria de razonamiento ya certificada.
`GovernedCausalPredictiveReasoner` es un evaluador puro, determinista,
subordinado y deliberadamente no posee `authority_id`.

M391.3 conserva su `GovernedScenarioSimulator` sin modificaciones. M391.4 no
crea un segundo workspace, motor de escenarios, planificador ni cerebro.

## Entradas explícitas

La capacidad recibe exclusivamente:

- un `PersistentWorldSnapshot` M391.2 suministrado explícitamente;
- una o más `CausalHypothesis` declaradas explícitamente.

Cada relación debe conservar `EpistemicLevel.HYPOTHESIS`. El razonador no
consulta repositorios, memoria, hogar, relaciones, sensores ni conversación por
su cuenta.

## Comprensión causal conservadora

M391.4 distingue la compatibilidad observada de la causalidad demostrada. La
coexistencia de un hecho de causa y un hecho de efecto sólo puede producir
`association_compatible`. Ese resultado no demuestra causalidad y mantiene la
relación en nivel epistemológico de hipótesis.

También puede registrar causa contradicha, efecto contradicho o evidencia
insuficiente. Las contradicciones permanecen visibles y no se reparan en
silencio.

## Predicción gobernada

Una predicción derivada de una hipótesis causal explícita se representa como
`EpistemicLevel.INFERENCE`. Puede quedar `conditionally_expected`,
`currently_contradicted` o `unresolved`.

Una predicción no es un hecho futuro, no constituye probabilidad calibrada y no
autoriza persistencia, planificación o ejecución. M391.4 no asigna porcentajes
ni aprende causalidad por repetición.

## Conflictos

Si `PersistentWorldSnapshot` contiene conflictos, el reporte exige revisión.
M391.4 no elige una versión del mundo ni modifica M391.2.

## Resultado

`GovernedCausalPredictionReport` conserva hipótesis, evaluaciones causales,
predicciones, evidencia, riesgos y fingerprint reproducible. Es inmutable,
determinista y de sólo lectura.

No crea hechos, no demuestra causalidad automáticamente, no calibra
probabilidades, no persiste resultados, no modifica memoria, aprendizaje,
planificación, mundo, permisos ni ejecución y no inicia procesos residentes.

## Invariantes

- Autoridad única: `governed_reasoning`.
- Sin `CausalManager`, `PredictionManager` ni razonador paralelo.
- Correlación o coexistencia no equivalen a causalidad.
- Toda relación causal permanece hipótesis salvo revisión por otra autoridad
  futura explícitamente certificada.
- Toda predicción permanece inferencia y nunca se presenta como hecho futuro.
- Sin persistencia, aprendizaje causal automático, planificación o ejecución.
- Sin acceso a `.roby/credentials.json`.
- `CanonicalCognitiveCore(` conserva su posición contractual.

## Relación con M391.1–M391.3

M391.1 consolida evidencia gobernada durante inactividad explícita. M391.2
aporta el mundo persistente trazable. M391.3 evalúa escenarios hipotéticos.
M391.4 añade una lectura causal y predictiva conservadora sobre el mundo
explícito, sin otorgar a ninguna de estas capacidades autoridad para escribir o
ejecutar.

## Alcance futuro

Causalidad experimental, series temporales, probabilidades calibradas,
modelos estadísticos, aprendizaje causal, predicción multietapa y planificación
contrafactual ejecutable quedan fuera de M391.4.
