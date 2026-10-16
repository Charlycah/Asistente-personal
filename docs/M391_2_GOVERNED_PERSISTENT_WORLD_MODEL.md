# M391.2 — Modelo Persistente del Mundo Gobernado

## Objetivo

Continuar la Época IV — Inteligencia Continua proporcionando a ROBY una vista
persistente, explícita y gobernada del mundo conocido, incluida la información
del hogar, sin crear una segunda memoria, otro repositorio, un nuevo cerebro ni
un gestor paralelo.

## Autoridad

M391.2 **no crea ni introduce una autoridad nueva**. `internal_world_model`, declarada
en M367.1, continúa siendo la única autoridad descriptiva del modelo interno del
mundo. `InternalWorldModelFoundation.persistent_snapshot()` amplía esa misma
superficie y conserva los dominios especializados existentes bajo sus propias
autoridades operativas.

`PersistentWorldModelView` es un evaluador puro y subordinado: no posee
`authority_id`, no escribe y no ejecuta.

## Persistencia gobernada

La palabra *persistente* significa que los hechos representados deben provenir
de una fuente gobernada que ya posea persistencia. M391.2 no añade persistencia
por sí mismo y no duplica datos.

Las fuentes admitidas inicialmente son:

- `PersonalIdentityProfile` para identidad persistente;
- `RelationshipMemoryManager` para relaciones persistentes;
- `CanonicalMemoryFacade` / memoria canónica para hechos persistidos;
- `HouseholdMemory` para conocimiento doméstico persistente.

Las señales ambientales transitorias pueden representarse sólo cuando una
autoridad persistente ya las haya convertido explícitamente en evidencia
admitida. M391.2 no transforma una percepción fugaz en hecho permanente.

## Contrato de hecho mundial

`PersistentWorldFact` conserva:

- identificador estable de la evidencia;
- dominio semántico;
- clave explícita del hecho;
- valor aportado por la fuente;
- autoridad y referencia de procedencia;
- nivel epistemológico M389;
- códigos de evidencia;
- condición de persistencia en la fuente;
- vigencia activa o archivada;
- instante de actualización cuando la fuente lo ofrece.

El contrato es inmutable y exige una fuente persistente gobernada.

## Conocimiento del hogar

`InternalWorldModelFoundation` puede adaptar `HouseholdMemoryEntry` ya existente
a un `PersistentWorldFact`. Esta adaptación:

- reutiliza el `entry_id` original como referencia;
- conserva categoría, fuente, contenido y estado de ciclo de vida;
- mantiene visibles los registros archivados como inactivos;
- no abre SQLite ni crea otro repositorio;
- no almacena una segunda copia persistente.

Por lo tanto `HouseholdMemory` conserva la escritura y M391.2 sólo construye una
vista cognitiva gobernada sobre sus resultados.

## Epistemología y conflictos

M391.2 conserva `EpistemicLevel` sin promoción automática. Una inferencia o
hipótesis nunca se convierte en hecho por ingresar al modelo persistente.

Cuando dos hechos activos clasificados como `fact` comparten dominio y clave
pero contienen valores diferentes, el snapshot pasa a
`conflict_review_required`. El conflicto queda explícito en `conflict_keys` y
`risk_codes`; no se selecciona un ganador ni se modifica ninguna fuente.

## Resultado

`PersistentWorldSnapshot` es determinista, inmutable y de sólo lectura. Puede
estar en estado:

- `complete`;
- `empty`;
- `conflict_review_required`;
- `degraded` reservado para integración segura posterior.

La ausencia de evidencia permanece `empty`: M391.2 no inventa hechos faltantes.

## Invariantes

- Única autoridad: `internal_world_model`.
- Sin nuevo `WorldModelManager` ni gestor equivalente.
- Sin nueva base de datos ni repositorio.
- Sin duplicación de almacenamiento.
- Sin escrituras sobre identidad, relaciones, memoria o hogar.
- Sin inferir hechos ausentes.
- Sin reparar contradicciones automáticamente.
- Sin cambio de runtime.
- Sin threads, `asyncio`, temporizadores o procesos residentes.
- Sin referencia a `.roby/credentials.json`.
- `CanonicalCognitiveCore(` conserva su posición contractual en
  `app/official_conversation_gateway.py`.

## Relación con M391.1

M391.1 define consolidación cognitiva gobernada durante inactividad explícita.
M391.2 aporta una representación persistente y trazable del mundo que podrá ser
consultada por incrementos futuros. En este incremento ambas capacidades
permanecen desacopladas operacionalmente: consolidar no escribe el mundo y el
modelo del mundo no inicia consolidación.

## Alcance futuro

La actualización automática del mundo desde percepción, la caducidad temporal,
la resolución supervisada de conflictos, la construcción de hipótesis y la
predicción causal quedan fuera de M391.2. Esas capacidades deberán ampliarse en
incrementos separados bajo las autoridades certificadas.
