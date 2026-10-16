# M391.6 — Toma de Decisiones Gobernada

## Objetivo

Continuar la Época IV — Inteligencia Continua integrando evidencia ya gobernada
para recomendar entre opciones explícitas sin crear una autoridad de decisión
paralela, sin ejecutar acciones y sin reemplazar la decisión humana final.

## Autoridad

La autoridad canónica continúa siendo `unified_cognitive_coordination`, expuesta
por `CanonicalDecisionFacade`. `GovernedDecisionAdvisor` es un componente puro y
subordinado que no posee `authority_id`, no intercepta el runtime y no reemplaza
al coordinador oficial.

M391.6 amplía `CanonicalDecisionFacade` con `advise(...)`, una operación
consultiva que puede utilizarse incluso sin enlazar el coordinador operativo.
La operación no cambia la precedencia de componentes ni concede permisos.

## Entradas explícitas

Cada `GovernedDecisionOption` contiene una opción identificable y puede enlazar,
de forma explícita, evidencia ya producida por:

- M391.5: `IntelligentPersonalOrganizationReport`;
- M391.3: `GovernedScenarioSimulationReport`;
- M391.4: `GovernedCausalPredictionReport`.

Una preferencia adicional sólo puede participar cuando llega explícitamente en
`explicit_preference`. M391.6 no infiere deseos, utilidad, riesgo, probabilidad o
prioridad ausentes.

## Evaluación

La evaluación conserva cuatro disposiciones: recomendar, diferir, bloquear o
exigir revisión. Un bloqueo o contradicción nunca se suaviza para producir una
recomendación. Evidencia enlazada ausente o no resuelta exige revisión humana.

Cuando varias opciones son recomendables, M391.6 reutiliza primero el
`priority_score` ya calculado por M391.5. Sólo ante igualdad utiliza la preferencia
explícita y finalmente el identificador canónico para obtener determinismo. No
crea otro algoritmo de prioridades ni una función de utilidad oculta.

Una predicción M391.4 sigue siendo inferencia y una hipótesis M391.3 sigue siendo
hipótesis. La recomendación M391.6 no las convierte en hechos.

## Decisión humana y ejecución

`GovernedDecisionAdvisoryReport` es de sólo lectura y mantiene
`human_decision_preserved=True`. `recommended_option_id` significa opción
recomendada, no opción ejecutada ni autorizada.

M391.6 no crea planes, tareas o hechos; no modifica organización, memoria,
aprendizaje o planificación; no persiste resultados; no concede permisos; no
invoca herramientas y no ejecuta acciones.

## Fronteras

M391.6 no crea un `DecisionManager`, un segundo coordinador, un agente de decisión
o un runtime paralelo. Tampoco inicia threads, timers o procesos residentes, no
usa SQLite y no accede a `.roby/credentials.json`.

La autorización operativa y la ejecución permanecen fuera del alcance de este
incremento y bajo las compuertas ya certificadas.

## Resultado

`GovernedDecisionAdvisoryReport` conserva evaluaciones por opción, recomendación
consultiva opcional, evidencia, riesgos y fingerprint reproducible. Es inmutable,
determinista, degradable y no concede autoridad.

## Invariantes

- Autoridad canónica: `unified_cognitive_coordination`.
- Fachada canónica: `CanonicalDecisionFacade`.
- M391.3 conserva hipótesis como hipótesis.
- M391.4 conserva predicciones como inferencias.
- M391.5 conserva `PriorityReasoning` como autoridad de prioridad.
- La decisión humana final permanece explícitamente preservada.
- No crea hechos, planes, tareas, permisos ni acciones.
- Sin persistencia, ejecución, procesos residentes o credenciales.
- `CanonicalCognitiveCore(` conserva su posición contractual.

## Relación con M391.1–M391.5

M391.1 consolida evidencia en inactividad explícita; M391.2 representa el mundo
persistente; M391.3 contrasta escenarios; M391.4 aporta análisis causal y
predictivo; M391.5 organiza y prioriza elementos personales. M391.6 integra sólo
los resultados explícitos de esas autoridades para asistir una elección sin
transformar razonamiento en ejecución.
