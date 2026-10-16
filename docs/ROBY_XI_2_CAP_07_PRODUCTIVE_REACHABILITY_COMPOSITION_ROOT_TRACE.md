# ROBY XI.2 --- CAP-07 Productive Reachability & Composition-Root Trace

**Baseline revisado:** ZIP corregido por line-length e imports
ordenados, recibido como nueva base de trabajo.\
**Baseline funcional declarado:** 13.439 PASS + Ruff limpio.\
**Modo de esta intervención:** auditoría read-only; **no se modificó
código productivo ni tests**.\
**Objetivo:** resolver el residual de reachability detectado en el Deep
Surgical Capability Map de CAP-07 antes de autorizar Hierarchical
Concept Composition.

------------------------------------------------------------------------

## 1. Dictamen ejecutivo

El trace confirma un residual de reachability específico y acotado:

> **`GovernedRelationalAbstractionInducer` existe, está
> arquitectónicamente probado y participa en una cadena de
> aprendizaje/reutilización certificada por tests, pero no está
> conectado al composition root ni a una ruta productiva ordinaria del
> baseline inspeccionado.**

La misma conclusión aplica a:

`GovernedRelationalAbstractionLearningBridge`.

En cambio:

> **`GovernedBoundedSemanticRoleRelationGrounder` sí está
> productivamente conectado y reutilizado por varias rutas reales.**

No se encontró un factory, adapter, dynamic import, capability
registration ni composition-root wiring oculto que construya o invoque
el inducer de abstracción.

Por tanto CAP-07 debe dividirse definitivamente:

-   **Semantic Grounding:** PRODUCTIVELY REACHABLE / SUBSTANTIAL.
-   **Relational Abstraction primitive:** IMPLEMENTED / CONTRACT-TESTED
    / NOT PRODUCTIVELY WIRED.
-   **Abstraction → Learning bridge:** IMPLEMENTED / CLOSED-LOOP TESTED
    / NOT DIRECTLY PRODUCTIVELY WIRED.
-   **Hierarchical Concept Composition:** MISSING.

Esta distinción debe reflejarse en el Master Capability Registry y en el
Inventario Cognitivo para no confundir existencia de foundation con
reachability productiva.

------------------------------------------------------------------------

# 2. Composition root oficial

La fábrica productiva inspeccionada es:

`app/runtime_root_factory.py`

Allí se construye:

`OfficialGovernedReasoningRuntimeGateway()`

y luego:

`CanonicalProductiveReasoningSource(governed_reasoning_runtime)`.

Ese source es introducido en:

`RuntimeCompositionDependencies.governed_reasoning_source`.

El composition root:

`core/runtime_composition_root/root.py`

crea entonces:

`ReasoningRuntimeContributor(dependencies.governed_reasoning_source)`.

La cadena oficial queda:

**Runtime root factory** → `OfficialGovernedReasoningRuntimeGateway` →
`CanonicalProductiveReasoningSource` → `ReasoningRuntimeContributor` →
`CognitiveRuntimeOrchestrator`.

Esta es la ruta canónica de reasoning productivo.

------------------------------------------------------------------------

# 3. Qué ocurre dentro del reasoning runtime productivo

`OfficialGovernedReasoningRuntimeGateway.evaluate_productive_episode(...)`

termina delegando en:

`evaluate_text(...)`.

Cuando existe `scope_reference` y está habilitado el intake productivo:

`evaluate_text` → `observe_productive_temporary_rule_intake` →
`ProductiveTemporaryRuleIntake.observe(...)`.

Ese intake utiliza explícitamente:

`GovernedBoundedSemanticRoleRelationGrounder`.

Después continúa mediante los contratos existentes de:

-   contextual rule interpretation;
-   semantic grounding;
-   compilation;
-   case grounding;
-   projection;
-   temporary rule admission;
-   inference registry.

Finalmente los claims transitorios entran al reasoning canónico.

**Resultado:** semantic grounding sí es parte del lifecycle productivo
real.

------------------------------------------------------------------------

# 4. Ausencia de relational abstraction en el composition root

Se realizó búsqueda directa de:

-   `GovernedRelationalAbstractionInducer`
-   `GovernedRelationalAbstractionCandidate`
-   `RelationalAbstractionExample`
-   `GovernedRelationalAbstractionLearningBridge`

dentro de `core/`, `app/` y los entry/runtime roots.

## Resultado

`GovernedRelationalAbstractionInducer` aparece directamente sólo en:

-   `core/governed_reasoning/relational_abstraction.py`;
-   `tests/architecture/test_hce_governed_relational_abstraction_wave.py`;
-   `tests/architecture/test_hce_abstraction_approved_learning_later_novel_reuse.py`.

`GovernedRelationalAbstractionLearningBridge` aparece directamente sólo
en:

-   `app/governed_relational_abstraction_learning_bridge.py`;
-   `tests/architecture/test_hce_abstraction_approved_learning_later_novel_reuse.py`.

No existe referencia directa desde:

-   `app/runtime_root_factory.py`;
-   `app/official_runtime_composition.py`;
-   `app/governed_reasoning_runtime.py`;
-   `core/runtime_composition_root/root.py`;
-   `core/reasoning_runtime_integration.py`;
-   `core/governed_reasoning/orchestrator.py`;
-   conversation/cognitive runtime roots.

------------------------------------------------------------------------

# 5. No existe productor productivo de `RelationalAbstractionExample`

Este punto es todavía más importante que la ausencia del inducer en el
root.

`RelationalAbstractionExample` exige:

-   `example_id`;
-   `scope_reference`;
-   `relation`;
-   `outcome`;
-   `source_fingerprint`.

En el baseline inspeccionado no se encontró código productivo que
construya esta clase.

Los ejemplos son construidos por las suites arquitectónicas.

Por tanto la ruta:

**productive evidence** → `RelationalAbstractionExample` →
`GovernedRelationalAbstractionInducer`

no existe actualmente como contrato de producción.

Éste es el primer enlace faltante real.

------------------------------------------------------------------------

# 6. No existe consumidor productivo del candidate

El segundo enlace faltante es posterior.

Incluso si un runtime produjera:

`GovernedRelationalAbstractionCandidate`

no existe actualmente en el composition root un consumer registrado para
ese producto.

El único consumidor funcional directo encontrado es:

`GovernedRelationalAbstractionLearningBridge`

pero este bridge tampoco está conectado al runtime productivo.

Por tanto la cadena productiva carece hoy de ambos extremos:

**producer de ejemplos** → **inducer** → **consumer productivo**.

------------------------------------------------------------------------

# 7. Qué demuestra realmente el closed-loop HCE

La suite:

`tests/architecture/test_hce_abstraction_approved_learning_later_novel_reuse.py`

demuestra una cadena arquitectónica fuerte:

relational abstraction\
→ learning evaluation\
→ explicit human approval\
→ structural eligibility/materialization\
→ `OfficialMemoryGateway`\
→ recall\
→ structural projection\
→ novel-domain structural transfer.

Eso prueba:

-   compatibilidad de contratos;
-   lineage;
-   autoridad correcta;
-   persistencia gobernada;
-   reutilización posterior;
-   ausencia de otro Memory/Learning owner.

Pero el test invoca manualmente:

`GovernedRelationalAbstractionInducer()`

y:

`GovernedRelationalAbstractionLearningBridge()`.

Por tanto demuestra:

**closed-loop composability**

pero no demuestra:

**ordinary productive reachability**.

------------------------------------------------------------------------

# 8. Revisión del contrato documental

La documentación HCE de Relational Abstraction dice que la wave:

> introduce la primera primitive bounded de concept formation.

También declara que el candidate es:

-   read-only;
-   session-local;
-   no persistente;
-   sin Memory;
-   sin Learning;
-   sin World Model mutation;
-   sin truth establishment;
-   sin inference authorization.

La wave además declara que se detiene antes del aprendizaje durable.

La wave posterior demuestra el closed loop hacia aprendizaje aprobado y
reutilización.

Nada de ello obliga por sí mismo a que toda conversación ordinaria
active abstracción.

Por tanto:

> **la falta de wiring no invalida el cierre contractual de HCE como
> foundation/closed-loop architecture.**

Sí afecta, en cambio, cualquier clasificación que interprete L4 como
reachability productiva ordinaria de la primitive de abstracción.

------------------------------------------------------------------------

# 9. Reconciliación de madurez recomendada

Para CAP-07 recomendamos registrar:

## Semantic Grounding

**L4 / PRODUCTIVELY REACHABLE / BOUNDED**

## Relational Abstraction

**L3 --- INTEGRATED FOUNDATION / CONTRACT-TESTED / SELECTIVE / NOT
PRODUCTIVELY WIRED**

o una clasificación equivalente que no afirme reachability productiva
que el trace no demuestra.

## Approved Abstraction Learning & Reuse

**L5 CLOSED-LOOP ARCHITECTURE CERTIFIED FOR EXPLICITLY COMPOSED
CANDIDATES**

pero con la anotación:

> upstream productive abstraction production is not wired.

Esto evita declarar menos de lo que existe y también evita declarar más.

------------------------------------------------------------------------

# 10. ¿Es un bug?

No encontramos evidencia suficiente para clasificarlo como regresión o
bug.

La mejor clasificación es:

## **PRODUCTIVE REACHABILITY RESIDUAL / INTENTIONAL-OR-UNFINISHED SELECTIVE WIRING**

La foundation fue creada y cerrada arquitectónicamente.

El runtime oficial nunca fue extendido para decidir:

-   cuándo observar múltiples ejemplos;
-   quién acumula esos ejemplos;
-   cuándo intentar una abstracción;
-   dónde conservar transient evidence;
-   qué consumer debe recibir el candidate.

Por tanto no existe una línea «faltante» que podamos simplemente
conectar.

Falta diseñar un **admission lifecycle**.

------------------------------------------------------------------------

# 11. Consecuencia para Hierarchical Concept Composition

No debemos implementar todavía:

`GovernedHierarchicalConceptCandidate`

y luego conectarlo directamente al runtime.

Eso saltaría una capa que el sistema actual todavía no tiene
productivamente:

**relational abstraction episode admission**.

Antes de jerarquía, ROBY necesita una vía gobernada que responda:

> **¿cuándo existe suficiente evidencia relacional explícita acumulada
> para ejecutar el inducer?**

------------------------------------------------------------------------

# 12. Diseño mínimo recomendado: no implementar aún

El siguiente bloque de diseño debe ser:

# **CAP-07 Governed Productive Abstraction Admission Contract**

No es todavía una implementación.

Debe definir exactamente:

### Source

Qué artefacto productivo puede convertirse en
`RelationalAbstractionExample`.

### Accumulation

Dónde se mantienen múltiples ejemplos antes de inducir.

La recomendación inicial es:

**session-local / transient**, no Memory.

### Trigger

Qué condición intenta abstracción.

No debe ser cada mensaje.

### Scope

Cómo se demuestra que los ejemplos pertenecen al mismo scope.

### Counterexamples

Cómo se incorporan sin reinterpretar texto libre arbitrariamente.

### Identity

Cómo se evita razonar dos veces sobre la misma evidencia.

### Consumer

Quién recibe el candidate.

### Persistence

NONE en la primera ruta.

### Learning

Sólo mediante el bridge existente y el camino aprobado ya certificado.

------------------------------------------------------------------------

# 13. Candidate de source más seguro

El trace indica que el semantic-grounding ecosystem ya está
productivamente reachable.

Por eso la hipótesis arquitectónica más segura para estudiar es:

**certified grounded relational artifacts** → normalization into
`RelationalAbstractionExample` → bounded transient accumulation →
relational abstraction induction.

No:

**conversation text** → guessed relation/outcome → abstraction.

Esto evita crear una vía paralela de interpretación semántica.

------------------------------------------------------------------------

# 14. Dónde NO conectar el inducer

No debe conectarse directamente en:

-   `ReasoningRuntimeContributor`;
-   conversation entry;
-   generic capability routing;
-   Memory;
-   Knowledge persistence;
-   LLM output;
-   every-turn `evaluate_text()` sin admission contract.

El inducer no debe convertirse en un hook universal que intente abstraer
de cada turno.

------------------------------------------------------------------------

# 15. Dónde podría vivir el futuro wiring

La authority debe seguir siendo:

`governed_reasoning`.

La ubicación más coherente para estudiar es dentro del boundary de:

`OfficialGovernedReasoningRuntimeGateway`

o un adapter estrictamente subordinado a ese gateway.

Pero no debe añadirse hasta diseñar:

**productive abstraction admission episode**.

La forma arquitectónica debería parecerse al patrón ya usado por:

`CanonicalProductiveReasoningEpisode`

y:

`CanonicalProductiveEpistemicAssessmentEpisode`.

Es decir:

-   identity exacta;
-   turn/session lineage;
-   canonical authority;
-   read-only;
-   no persistence;
-   fail-closed;
-   explicit source.

------------------------------------------------------------------------

# 16. Primer consumer recomendado

No recomiendo que el primer consumer sea Learning.

Eso mezclaría reachability con persistencia.

Tampoco Structural Transfer.

Eso mezclaría concept formation con analogy/transfer.

El primer consumer debería ser:

> **el mismo governed reasoning/cognitive runtime en modo consultivo,
> mediante una proyección read-only del candidate.**

El objetivo sería demostrar que una abstracción canónica puede influir
legítimamente en razonamiento posterior o en el mismo episodio elegible
**sin persistirla**.

Sólo después estudiar:

abstraction → explicit learning review.

------------------------------------------------------------------------

# 17. RED evidence requerido para reachability

Antes de producción deberían existir RED tests que demuestren:

1.  grounded relational evidence elegible puede convertirse en examples
    canónicos;
2.  una sola observación NO dispara abstracción;
3.  evidencia de scope distinto no se acumula junta;
4.  evidencia repetida/idempotente no aumenta falsamente support;
5.  dos ejemplos compatibles permiten inducción;
6.  counterexample compatible produce `CONTESTED`;
7.  text-only/no grounded evidence no activa el camino;
8.  el episode es session-local;
9.  no escribe Memory/Learning;
10. el mismo evidence set produce identidad estable;
11. el candidate puede ser consumido read-only por una ruta canónica;
12. no se ejecuta Structural Transfer automáticamente;
13. no se llama al learning bridge automáticamente.

------------------------------------------------------------------------

# 18. Verification del ZIP recibido

Sobre el ZIP recibido se ejecutó el siguiente perímetro focal:

-   HCE governed relational abstraction wave;
-   HCE abstraction → approved learning → later novel reuse;
-   bounded semantic role/relation grounding;
-   structural knowledge transfer candidate.

Resultado:

**33 PASS**

No se observaron fallos en ese perímetro.

No se modificó el ZIP.

------------------------------------------------------------------------

# 19. Observación documental del ZIP recibido

El ZIP inspeccionado contiene:

-   `INVENTARIO_COGNITIVO_INTEGRAL_ROBY_XI_2.md`;
-   HCE final closure certification;
-   documentación raíz histórica.

No se encontraron dentro de esta versión del ZIP los documentos
recientes generados durante nuestra reconciliación:

-   Master Capability Registry;
-   Cognitive Inventory Reconciliation Master Surgical Guide;
-   CAP-07 Deep Surgical Capability Map.

Esto no constituye un fallo de código.

Pero antes de la próxima promoción deberemos decidir incorporarlos a
raíz como documentación canónica, preservando los contratos históricos
de encabezados ya protegidos por tests.

------------------------------------------------------------------------

# 20. Surgical decision

## CAP-07 PRODUCTIVE REACHABILITY TRACE: COMPLETE

### Confirmado

-   `governed_reasoning` continúa siendo la authority correcta.
-   Semantic grounding tiene reachability productiva.
-   Relational abstraction no tiene wiring productivo directo.
-   No existe producer productivo de `RelationalAbstractionExample`.
-   No existe consumer productivo del abstraction candidate.
-   El learning bridge no está productivamente wired.
-   No existe wiring dinámico oculto detectado.
-   La cadena HCE demuestra composabilidad closed-loop, no reachability
    ordinaria.
-   El residual es real pero no debe tratarse como bug trivial.

### NO autorizado todavía

-   Hierarchical Concept Composition.
-   Concept Memory.
-   nuevo Learning path.
-   nuevo Analogy Engine.
-   conexión directa del inducer a cada turno.

### Siguiente paso autorizado

# **CAP-07 Governed Productive Abstraction Admission Contract & RED Evidence**

Ese contrato debe cerrar primero:

**grounded evidence** → **canonical examples** → **transient
accumulation** → **selective induction** → **read-only productive
consumption**

sin Memory, sin Learning automático y sin segunda authority.

Sólo después tendrá sentido construir:

**Hierarchical Concept Composition**.

------------------------------------------------------------------------

# 21. Conclusión

El nuevo método quirúrgico evitó una implementación prematura.

Antes del trace parecía que el siguiente paso era extender
inmediatamente la primitive hacia conceptos jerárquicos.

Ahora sabemos que existe un problema más fundamental:

> **la primitive de abstracción existe, pero el cerebro productivo
> todavía no posee un episodio gobernado que la alcance desde evidencia
> real.**

Por eso el orden correcto es:

**productive reachability** → **canonical relational abstraction
episode** → **read-only consumption** → **hierarchical concept
composition** → **rich structural mapping** → **eventual governed
learning**.

Éste es el camino con menor duplicación y menor riesgo arquitectónico.
