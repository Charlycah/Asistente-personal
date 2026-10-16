# ROBY XI.2 — Inventario Cognitivo Integral

**Baseline auditada:** ZIP completo validado 13.439 PASS + Ruff limpio  
**Objeto:** describir qué clase de sistema cognitivo es ROBY hoy, qué puede hacer realmente,
qué capacidades están cerradas, cuáles son selectivas o parciales y qué no debe confundirse con
una capacidad productiva.

## 1. Dictamen ejecutivo

ROBY XI.2 ya no es sólo un asistente conversacional con funciones agregadas. La arquitectura
auditada contiene un núcleo cognitivo gobernado con fronteras explícitas de entrada, contexto,
memoria, conocimiento, razonamiento, planificación, decisión, ejecución, reflexión, gobierno y
observabilidad.

El propio inventario operacional del repositorio declara una autoridad primaria canónica para cada
una de esas responsabilidades. Esto coincide con la regla arquitectónica de una autoridad por
capacidad.

La madurez no es uniforme: algunas facultades son productivas y visibles; otras son consultivas,
selectivas, transitorias o sólo se activan cuando existe evidencia explícita suficiente. Esa
distinción debe preservarse.

## 2. Escala usada

- **L1 FOUNDATION** — existe el mecanismo.
- **L2 GOVERNED** — está sometido a una autoridad y contrato explícitos.
- **L3 INTEGRATED** — participa del cerebro/composition root común.
- **L4 PRODUCTIVELY REACHABLE** — puede ser alcanzado por el lifecycle productivo correspondiente.
- **L5 CLOSED LOOP** — su resultado puede influir legítimamente en cognición futura sin romper
  gobierno, trazabilidad o autoridad.

Estados complementarios:

- **CLOSED** — el alcance contratado está cerrado.
- **SELECTIVE** — sólo aplica cuando existen condiciones/evidencia explícitas.
- **CONSULTATIVE** — informa o recomienda; no ejecuta.
- **TRANSIENT** — no crea persistencia durable.
- **PERSISTENT** — usa una autoridad de persistencia legítima.
- **PARTIAL** — existe una parte útil pero no debe declararse completa.
- **SHADOW** — observa/evalúa sin gobernar producción.
- **OUT OF SCOPE** — no pertenece al rumbo actual aunque pueda quedar código histórico.

---

# 3. Mapa de autoridades cognitivas

El repositorio conserva once responsabilidades explícitas:

| Autoridad | Primaria canónica | Estado operativo declarado |
|---|---|---|
| Entry | conversation_entry | USER_VISIBLE |
| Context | context_continuity | OPERATIONAL_LIMITED |
| Memory | memory_gateway | OPERATIONAL_LIMITED |
| Knowledge | knowledge_runtime | CONSULTATIVE |
| Reasoning | governed_reasoning | OPERATIONAL_LIMITED |
| Planning | executive_planning | CONSULTATIVE |
| Decision | unified_cognitive_coordination | OPERATIONAL_LIMITED |
| Execution | capability_orchestrator | USER_VISIBLE |
| Reflection | cognitive_core_resident | OPERATIONAL_LIMITED |
| Governance | governed_capability_routing | OPERATIONAL_LIMITED |
| Observability | runtime_observability | OPERATIONAL_LIMITED |

`cognitive_planner_shadow` permanece explícitamente SHADOW y no sustituye la autoridad de
planificación.

**Conclusión:** la arquitectura conserva un único mapa de autoridad cognitiva primaria. No debe
crearse un segundo cerebro para nuevas facultades.

---

# 4. Inventario por dominios humanos

## 4.1 Conversación y continuidad contextual

**Madurez: L4 — PRODUCTIVELY REACHABLE / CLOSED dentro del alcance actual.**

ROBY dispone de una frontera oficial de conversación y continuidad contextual integrada. Puede
mantener relación entre turnos y usar contexto previo sin reducir cada interacción al último
mensaje aislado.

Puede:

- aceptar turnos por una entrada oficial;
- conservar continuidad contextual de sesión;
- recuperar contexto relevante;
- mantener conversación cotidiana y contextual;
- aplicar políticas de calidad/respuesta sin otorgarles autoridad cognitiva paralela.

No significa:

- memoria perfecta de todo;
- consciencia subjetiva;
- autorización para convertir conversación en hecho persistente.

## 4.2 Memoria y continuidad autobiográfica

**Madurez: L4/L5 según el tipo de memoria — GOVERNED / PERSISTENT cuando la autoridad lo admite.**

ROBY posee una frontera oficial de memoria y foundations de memoria cognitiva, episódica,
contextual, relacional y autobiográfica.

Puede:

- recuperar recuerdos relevantes por contexto;
- distinguir recuerdos activos, corregidos, reemplazados o conflictivos;
- mantener procedencia y estado epistemológico;
- organizar recuerdos admitidos en continuidad temporal;
- conservar conocimiento aprobado a través de la autoridad de Memory.

El aprendizaje o repetición no convierten automáticamente una experiencia en verdad.

## 4.3 Modelo mental, perfil y modelo persistente del mundo

**Madurez: L4 — GOVERNED / INTEGRATED / PERSISTENT-VIEW.**

ROBY dispone de representación gobernada de usuario, objetivos y conocimiento de proyecto, además
de una vista persistente del mundo que reutiliza autoridades existentes en lugar de duplicar
almacenamiento.

Puede representar, cuando existe evidencia gobernada:

- personas conocidas;
- hogar;
- lugares;
- objetos;
- tiempo;
- contexto;
- relaciones;
- objetivos;
- proyectos;
- estados explícitos relevantes.

Mantiene incertidumbre, procedencia y contradicciones visibles.

No debe inferir identidad, vínculo, estado personal o hecho doméstico sólo a partir de una señal
ambigua.

## 4.4 Organización personal integrada

**Madurez: L4 — PRODUCTIVELY REACHABLE / CLOSED para las fuentes certificadas.**

La integración personal conecta al mismo Cognitive Agenda:

- Goals;
- Projects;
- Tasks;
- Reminders;
- Calendar;
- Notes con seguimiento explícito.

Puede usar esas fuentes para modificar relevancia, foco y deliberación sin quitar autoridad a los
sistemas propietarios.

Ejemplos de criterios ya documentados:

- tareas por bloqueo, importancia, urgencia o deadline;
- recordatorios pendientes/vencidos;
- calendario dentro de ventana relevante;
- notas sólo cuando poseen seguimiento explícito.

No existe autorización implícita para ejecutar tareas o modificar agenda por razonamiento.

## 4.5 Razonamiento gobernado

**Madurez: L4 — PRODUCTIVELY REACHABLE / CANONICAL.**

Existe un `OfficialGovernedReasoningRuntimeGateway` como fuente canónica del episodio de
razonamiento productivo.

ROBY puede:

- reunir contexto;
- realizar inferencia gobernada;
- analizar conflictos;
- abstenerse cuando corresponde;
- producir explicación;
- mantener identidad canónica del episodio;
- reutilizar el mismo episodio entre consumidores del mismo turno en vez de razonar dos veces de
  forma independiente.

La abstención permanece una salida legítima y no se transforma artificialmente en éxito.

## 4.6 Hipótesis, escenarios y causalidad

**Madurez: L4 — PRODUCTIVELY REACHABLE pero SELECTIVE.**

ROBY puede trabajar con hipótesis explícitas y, cuando existe un source certificado junto con el
World Snapshot exacto:

- construir Scenario Hypothesis;
- simular escenarios;
- construir Causal Hypothesis;
- producir predicción causal condicionada;
- conservar simulation_id / analysis_id;
- distinguir asociación de causalidad.

La vía fuerte NO se activa para cualquier texto.

La admisión de `explicit_hypothesis_source` y `hypothesis_world_snapshot` es atómica. Si no existe
el par explícito, la conversación ordinaria continúa sin fabricar Scenario/Causal.

## 4.7 Evaluación epistemológica

**Madurez: L4/L5 — SELECTIVE CLOSED LOOP hacia metacognición estratégica.**

Para un Scenario/Causal legítimo ROBY dispone del recorrido:

Scenario/Causal Report
→ Hypothesis Deepening
→ Epistemic Sufficiency
→ Reasoning Quality
→ Reasoning Method Provenance
→ Reasoning Method Outcome.

Puede evaluar:

- profundidad de la hipótesis;
- suficiencia de evidencia;
- calidad del razonamiento;
- método empleado;
- resultado epistemológico;
- gaps y necesidad de revisión.

No puede convertir `COMPLETED` en `ADEQUATE` por conveniencia ni confianza en suficiencia sin
evidencia.

## 4.8 Concept formation y abstracción

**Madurez: L4 — GOVERNED / SELECTIVE.**

ROBY posee una primitiva de abstracción relacional gobernada.

Puede:

- comparar múltiples ejemplos explícitos;
- inducir un candidato de relación estructural;
- tratar contraejemplos como evidencia de frontera;
- rechazar abstracciones cuando la evidencia o el scope no alcanzan;
- producir candidatos read-only antes de cualquier persistencia.

Una abstracción candidata no es automáticamente verdad ni aprendizaje.

## 4.9 Aprendizaje aprobado y reutilización

**Madurez: L5 en el alcance estructural certificado.**

Existe un closed loop acotado:

abstracción inducida
→ políticas de aprendizaje seguro
→ aprobación humana explícita
→ LearningFoundation
→ OfficialMemoryGateway
→ recall posterior
→ structural transfer en dominio nuevo.

Esto significa que ROBY puede aprender y reutilizar posteriormente una estructura aprobada, pero
no posee aprendizaje autónomo irrestricto.

Las abstracciones rechazadas o controvertidas no deben convertirse en conocimiento durable.

## 4.10 Estrategia e improvisación cognitiva

**Madurez: L4/L5 — GOVERNED / PRODUCTIVE / BOUNDED.**

ROBY puede sintetizar estrategias cognitivas nuevas sin depender exclusivamente de escenarios
hard-coded.

Puede:

- partir de necesidades cognitivas actuales;
- ordenar reasoning/planning/reflection/executive por dependencias;
- bloquear una estrategia si falta una capacidad requerida;
- proyectar una estrategia sobre Cognitive Runtime;
- conservar evidencia exacta de qué stages fueron realmente aplicados;
- distinguir APPLIED, PARTIALLY_APPLIED, BLOCKED y NOT_APPLICABLE.

La estrategia no concede por sí misma autoridad de acción externa.

## 4.11 Metacognición y adaptación futura

**Madurez: L5 — CLOSED LOOP TRANSIENT.**

Ésta es una de las capacidades intelectuales más avanzadas actualmente cerradas.

ROBY puede:

- observar el resultado epistemológico de un método de razonamiento;
- demostrar que ese resultado pertenece exactamente a la estrategia aplicada;
- admitir Strategy Outcome por la autoridad unificada;
- acumular evidencia compatible;
- producir una recomendación metacognitiva acotada;
- influir sobre una estrategia futura elegible.

La influencia futura:

- es transitoria;
- no modifica el planner;
- no escribe Memory;
- no escribe Learning;
- no crea una preferencia durable;
- no agrega necesidades cognitivas que el turno actual no posea.

Por tanto ROBY puede adaptar cómo compone estrategias futuras, pero no reprogramarse libremente.

## 4.12 Reflexión y estado interior funcional

**Madurez: L3/L4 — OPERATIONAL_LIMITED / CONSULTATIVE.**

El proyecto contiene reflexión cognitiva, self-model, thought stream y un mundo interior funcional
simulado.

La documentación es explícita: continuidad funcional, memoria autobiográfica, reflexión o conducta
humana convincente NO constituyen evidencia de consciencia subjetiva.

Debe seguir describiéndose como estado funcional simulado, no como experiencia consciente
demostrada.

## 4.13 Decisión y recomendación

**Madurez: L4 — CONSULTATIVE.**

ROBY puede integrar alternativas, prioridades, escenarios y predicciones para producir
recomendaciones trazables.

La decisión final continúa perteneciendo a Carlos y Cristina.

Razonamiento, planificación y recomendación no equivalen a autorización de ejecución.

---

# 5. Qué puede hacer ROBY hoy, dicho sin nombres de clases

ROBY puede mantener una conversación con continuidad; recordar información admitida; recuperar
recuerdos relevantes; representar partes conocidas de su mundo; relacionar objetivos, proyectos,
tareas, agenda, recordatorios y notas; decidir qué merece atención; razonar y abstenerse cuando no
hay base suficiente; trabajar selectivamente con hipótesis explícitas; explorar escenarios;
realizar análisis causal condicionado; evaluar la suficiencia y calidad de su propio razonamiento;
formar abstracciones relacionales; aprender determinadas estructuras cuando existe aprobación
gobernada; reutilizarlas después; componer estrategias cognitivas nuevas; observar cómo resultaron;
y usar esa experiencia de manera transitoria para influir en estrategias futuras.

La característica más importante no es cada capacidad aislada, sino que una parte significativa de
ellas ya está conectada causalmente dentro del mismo lifecycle cognitivo.

---

# 6. Qué ROBY todavía NO puede afirmar legítimamente

ROBY no debe ser descrito como capaz de:

- aprender cualquier cosa por sí solo y convertirla automáticamente en conocimiento;
- crear hechos a partir de conversación ambigua;
- inferir hipótesis fuertes de cualquier texto y analizarlas como si fueran explícitas;
- demostrar causalidad sólo porque existe asociación;
- modificar libremente su planner o arquitectura;
- convertir metacognición transitoria en preferencia durable sin otro contrato;
- actuar físicamente sólo porque ha recomendado algo;
- reemplazar decisiones humanas;
- poseer consciencia subjetiva demostrada;
- poseer comprensión ilimitada o conocimiento universal;
- mantener continuidad perfecta sin límites de fuente, scope o memoria.

---

# 7. Capacidades parciales o que merecen vigilancia

## 7.1 Open commitments / compromiso personal durable

La documentación de causal closure indica que `open_commitments` continúa como compatibility
consumer hook y que no se demostró una fuente canónica durable de compromiso personal.

**Estado: PARTIAL / NO declarar continuidad durable completa.**

## 7.2 Planner cognitivo shadow

Existe pero permanece deliberadamente SHADOW.

**Estado: SHADOW / no promover a segunda autoridad de planificación.**

## 7.3 Metacognitive persistence

La adaptación estratégica actual es transitoria.

**Estado: DELIBERATELY NON-PERSISTENT.**

Convertirla en aprendizaje durable sería una nueva decisión arquitectónica, no una corrección
pendiente.

## 7.4 Evaluación epistemológica fuerte

Está cerrada productivamente sólo cuando existe source explícito y World Snapshot válido.

**Estado: SELECTIVE, no universal.**

---

# 8. Código histórico fuera del rumbo actual

El ZIP todavía contiene una cantidad considerable de paquetes relacionados con:

- Android;
- mobile companion/runtime/presence;
- device continuity/arbitration;
- residential node/perception/remote presence;
- distributed presence;
- driving;
- peripheral/device integration.

Esto es importante: **presencia de código no equivale a rumbo vigente**.

Según la dirección actual del proyecto, ROBY reside en la laptop y la evolución prioritaria es
intelectual/cognitiva. Por tanto estas familias deben clasificarse para planificación como:

**OUT OF SCOPE / LEGACY PRESENT IN REPOSITORY**, salvo aquellas dependencias mínimas que todavía
sean requeridas por el runtime laptop.

No recomiendo borrarlas a ciegas. Antes de eliminación física corresponde un dependency/reachability
audit específico que distinga:

1. código realmente muerto;
2. contratos todavía importados;
3. tests históricos;
4. dependencias de composition root;
5. documentación obsoleta.

La decisión funcional de descartarlas ya puede coexistir con una retirada técnica posterior y
segura.

---

# 9. Tamaño y complejidad observada

En el ZIP auditado existen aproximadamente:

- **1.040 Python files** bajo `core/` + `app/`;
- **1.148 Python test files**;
- **1.156 archivos** dentro de `docs/`.

El tamaño confirma que el principal riesgo actual ya no es falta de capacidades sino:

- duplicación histórica;
- documentación acumulativa;
- rutas antiguas todavía presentes;
- dificultad para distinguir capability vigente de foundation histórica;
- riesgo de implementar de nuevo algo que ROBY ya posee.

Por ello el inventario debe convertirse en documento de control previo a cualquier nueva evolución.

---

# 10. Matriz de madurez cognitiva

| Facultad | Nivel | Clasificación |
|---|---:|---|
| Conversación oficial | L4 | CLOSED / USER_VISIBLE |
| Continuidad contextual | L4 | OPERATIONAL_LIMITED |
| Memoria gobernada | L4/L5 | PERSISTENT / GOVERNED |
| Continuidad autobiográfica funcional | L4 | GOVERNED |
| Modelo de usuario/mundo | L4 | GOVERNED |
| Organización personal integrada | L4 | PRODUCTIVE |
| Priorización | L4 | CONSULTATIVE / PRODUCTIVE |
| Razonamiento canónico | L4 | PRODUCTIVE |
| Abstención epistemológica | L4 | CLOSED |
| Hipótesis explícitas | L4 | SELECTIVE |
| Scenario simulation | L4 | SELECTIVE |
| Causal predictive reasoning | L4 | SELECTIVE |
| Epistemic sufficiency | L4 | SELECTIVE |
| Reasoning quality | L4 | SELECTIVE |
| Method provenance/outcome | L4 | SELECTIVE |
| Abstracción relacional | L4 | GOVERNED |
| Approved abstraction learning | L5 | BOUNDED CLOSED LOOP |
| Structural transfer | L5 | BOUNDED CLOSED LOOP |
| Novel strategy synthesis | L4 | PRODUCTIVE / BOUNDED |
| Strategy application evidence | L4 | PRODUCTIVE |
| Strategy outcome attribution | L5 | EXACT-LINEAGE |
| Metacognitive adaptation | L5 | TRANSIENT CLOSED LOOP |
| Future strategy influence | L5 | TRANSIENT / BOUNDED |
| Reflection/self-model | L3/L4 | OPERATIONAL_LIMITED |
| Durable personal commitments | L2/L3 | PARTIAL |
| Autonomous self-modification | — | NOT IMPLEMENTED / NOT AUTHORIZED |
| Subjective consciousness | — | NOT ESTABLISHED |

---

# 11. Mapa A/B/C/D para decidir la próxima evolución

## A — YA EXISTE: no reimplementar

- memoria cognitiva y recuperación contextual;
- modelo mental/mundo gobernado;
- conversación contextual y de largo plazo;
- organización personal integrada;
- razonamiento gobernado;
- hipótesis/scenario/causalidad selectivos;
- evaluación epistemológica;
- abstracción relacional;
- aprendizaje aprobado y structural reuse;
- composición de estrategias;
- outcome attribution;
- metacognición estratégica transitoria.

## B — EXISTE PARCIALMENTE: resolver sólo si aporta valor real

- continuidad durable de compromisos personales;
- síntesis/reducción de código histórico;
- reconciliación documental entre rumbo laptop-only y documentación de fases físicas/distribuidas;
- eventual persistencia metacognitiva, sólo si se diseña como aprendizaje gobernado y no como
  preferencia silenciosa.

## C — NO EXISTE COMO FACULTAD COMPLETA Y ENCAJA CON EL RUMBO INTELECTUAL

Candidatos razonables para estudio futuro, no autorización de implementación:

- construcción jerárquica de conceptos más allá de la abstracción relacional acotada;
- analogía estructural multi-concepto;
- modelos explicativos más ricos y revisión de teorías;
- deliberación contrafactual multi-etapa;
- planificación intelectual de largo horizonte con revisión de supuestos;
- curiosity/question generation gobernada orientada a cerrar gaps reales;
- síntesis de conocimiento entre dominios con trazabilidad epistemológica;
- aprendizaje metacognitivo durable con aprobación y reversibilidad, si alguna vez se decide que
  aporta suficiente valor.

## D — NO IMPLEMENTAR dentro del rumbo actual

- ROBY distribuido entre varias PCs;
- ROBY móvil como segundo cerebro;
- autonomía física doméstica general;
- control de periféricos por novedad;
- ejecución autónoma sin consentimiento;
- aprendizaje irrestricto;
- auto-modificación arquitectónica autónoma.

---

# 12. Diagnóstico de evolución

ROBY se encuentra en una etapa distinta de la de hace muchas fases.

El cuello de botella ya no parece ser «darle más módulos».

El núcleo posee suficientes primitives para:

**recordar → representar → razonar → hipotetizar → evaluar → abstraer → aprender con aprobación →
transferir → componer estrategia → observar resultado → adaptar estrategia futura.**

La siguiente evolución debería aumentar la **profundidad intelectual de esas operaciones**, no el
número de dispositivos ni la cantidad de managers.

La prioridad arquitectónica inmediata debería ser mantener control del sistema:

1. usar este inventario como mapa maestro;
2. certificar zero-residual del arco Higher Cognitive Evolution;
3. auditar legacy físico/distribuido antes de retirarlo del código;
4. escoger sólo después una facultad intelectual nueva;
5. exigir para ella desde el inicio authority, source, reachability, outcome y closed-loop contract.

---

# 13. Conclusión

ROBY XI.2 puede describirse hoy como un **asistente cognitivo personal gobernado, local-first y
centrado en continuidad**, con memoria, representación del mundo, organización personal,
razonamiento, abstracción, aprendizaje aprobado, estrategia y metacognición acotada.

No es un sistema autónomo general, no posee autoridad humana, no aprende libremente y no existe
base técnica para afirmar consciencia subjetiva.

Su avance más importante es arquitectónico: varias de sus facultades intelectuales ya no son
módulos aislados, sino partes trazables del mismo ciclo cognitivo.

**Recomendación de dirección:** congelar expansión lateral y orientar la siguiente etapa a
profundidad intelectual, simplificación arquitectónica y eliminación segura de legado fuera de
scope.


---

## CAP-08 — Rich Hierarchical Structural Analogy update

After HCC Productivo Ordinario, ROBY can compare two canonical productive
hierarchical concept episodes as bounded multi-component structures. The comparison
is read-only and non-authoritative. It does not itself execute structural transfer.

The pre-existing structural-transfer closed loop remains separate and stricter:
executable transfer requires recalled durable-rule compilation, target structural
projection, role bindings, transfer instantiation and canonical temporary admission.
HCC analogy does not fabricate those prerequisites.

## CAP-05 — Explanatory Model Composition update

The former explanatory-theory residual is now partially closed by a bounded
multi-hypothesis explanatory model representation. Multiple governed hypotheses can
be held together with local evidence, epistemic gaps and discrimination relations
and exposed productively as consultative context. This does not establish truth or
causality and does not authorize persistence, Learning, Memory, transfer or action.
A future residual, if justified, is ordinary runtime reachability from naturally
multi-hypothesis productive episodes and later governed model revision across new
evidence; neither is implied by this block.
