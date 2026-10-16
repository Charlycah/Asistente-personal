# M391.3 — Simulación de Hipótesis y Escenarios Gobernada

## Objetivo

Continuar la Época IV — Inteligencia Continua permitiendo evaluar hipótesis
explícitas contra el modelo persistente del mundo M391.2 sin convertir una
simulación en realidad, sin crear hechos y sin ejecutar consecuencias.

## Autoridad

M391.3 no crea una autoridad nueva. La capacidad pertenece a
`governed_reasoning`, autoridad primaria de razonamiento ya certificada en el
mapa cognitivo. `GovernedScenarioSimulator` es un evaluador puro, consultivo y
subordinado; deliberadamente no posee `authority_id`.

El `CognitiveHypothesisWorkspace` histórico del residente cognitivo no se
modifica, no se promueve a autoridad y no se conecta al runtime mediante este
incremento.

## Entradas explícitas

La simulación recibe exclusivamente:

- un `PersistentWorldSnapshot` producido por M391.2;
- una o más `ScenarioHypothesis` declaradas explícitamente.

M391.3 no consulta repositorios, memoria, hogar, relaciones, sensores ni
conversaciones por su cuenta. La procedencia del mundo continúa bajo M391.2.

Cada hipótesis conserva obligatoriamente `EpistemicLevel.HYPOTHESIS`. El motor
no convierte una hipótesis en hecho, aunque resulte consistente con la evidencia
persistente.

## Evaluación de escenarios

Para una clave explícita del mundo, el simulador puede concluir únicamente:

- `consistent`: la hipótesis coincide con el hecho persistente disponible;
- `contradicted`: la evidencia persistente explícita contradice la suposición;
- `unresolved`: no existe evidencia suficiente o el mundo no permite resolver.

Estas etiquetas describen la relación entre hipótesis y evidencia disponible;
no predicen automáticamente el futuro ni garantizan causalidad.

## Conflictos y ausencia de evidencia

Un conflicto ya visible en `PersistentWorldSnapshot` permanece visible y obliga
a revisión. M391.3 no elige un ganador ni repara el modelo del mundo.

La ausencia de hechos relevantes permanece `insufficient_evidence`; no se
rellenan huecos mediante imaginación, memoria implícita o inferencia oculta.

## Resultado

`GovernedScenarioSimulationReport` es determinista, inmutable y de sólo
lectura. Conserva el snapshot de origen, hipótesis ordenadas, resultados,
códigos de evidencia, riesgos y fingerprint reproducible.

No persiste hipótesis, no crea hechos, no modifica M391.2, memoria, aprendizaje,
planificación, permisos ni ejecución. Tampoco inicia threads, `asyncio`, timers
o procesos residentes.

## Invariantes

- Autoridad única: `governed_reasoning`.
- Sin `ScenarioManager`, segundo razonador ni nuevo cerebro.
- Sin modificación del `CognitiveHypothesisWorkspace` histórico.
- Sin promoción automática de hipótesis a hechos.
- Sin escritura sobre `PersistentWorldSnapshot` o sus fuentes.
- Sin planificación ni ejecución de escenarios simulados.
- Sin resolución silenciosa de contradicciones.
- Sin acceso a `.roby/credentials.json`.
- `CanonicalCognitiveCore(` conserva su posición contractual.

## Relación con M391.1 y M391.2

M391.1 permite consolidar cognitivamente evidencia gobernada durante inactividad
explícita. M391.2 aporta el mundo persistente trazable. M391.3 utiliza ese mundo
como contexto estático para explorar hipótesis sin modificarlo. Ninguna de las
tres capacidades concede autoridad a las otras para persistir o ejecutar.

## Alcance futuro

La comprensión causal y predictiva, simulaciones temporales multietapa,
probabilidades calibradas, planificación contrafactual y activación autónoma
quedan fuera de M391.3 y deberán incorporarse en incrementos separados bajo sus
autoridades certificadas.
