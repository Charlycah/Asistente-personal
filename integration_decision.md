

### Post-M409.1 reasoning event-history micro-lineage retirement
Retired the non-productively-resident application-level reasoning assessment event projector
and admitted event-history reader. Current succession is the neutral
`GovernedReasoningAssessmentObservation.from_assessments(...)` contract plus
`GovernedLongitudinalReasoningAssessmentFoundationV1` under the existing
`governed_reasoning` authority. Historical documents are preserved.
## HCPDQ-v2 — H7 Ground-Truth Scoring + Cognitive Audit

**Estado:** CLOSED / PASS.
Se verificaron los hashes sellados del ground truth y del primary raw run antes
del scoring. Los 12 casos H7V2 coinciden con ground truth en los cuatro campos
congelados de evaluación. Resultado: 12/12, D1 4/4, D2 4/4, D3 4/4. No se
detecta gap cognitivo productivo y no se requiere cambio de producción.

## HCPDQ-v2 — H7 Preflight + Primary Execution

**Estado:** PRIMARY EXECUTION COMPLETE / RAW SEALED.
Antes de ejecutar se congeló y selló ground truth independiente, derivado sólo
de la construcción causal congelada. Luego se ejecutaron exactamente una vez
los 12 casos `V2I-H7V2-*` sin cargar truth ni hacer scoring. Las 12 raw captures
quedaron selladas individualmente y con aggregate SHA-256. La autorización fue
consumida y no es reusable.

## HCPDQ-v2 — H7 Entry-Equivalent Corpus v2

**Estado:** CONSTRUCTED / REAL DRY-PROBE CERTIFIED / FROZEN.
Se creó un namespace independiente `V2I-H7V2` con 12 casos. Cada caso congela
el estado causal productivo necesario y fue reconstruido mediante los tipos
gobernados exactos antes del freeze. El dry probe recorrió las tres topologías:
4 continue/planned, 4 stop/not-eligible y 4 review/not-eligible. No se creó ni
abrió ground truth, no hubo scoring y no se autorizó primary execution.

## HCPDQ-v2 — H7 Primary Run Post-Mortem / Evaluation-Boundary Audit

**Decisión:** EVALUATION DESIGN INVALID / RECONTRACT REQUIRED.
El abort no demuestra fallo cognitivo ni del adapter. Los 12 `requirement_id`
congelados usan `req-h7-*`, incompatible con el constructor productivo, y el
corpus tampoco serializa el estado causal necesario para D2/D3. El dry probe
certificó constructibilidad sin materializar casos por los tipos productivos
exactos. Retry, scoring, truth opening, translation patch y producción: NO-GO.

## HCPDQ-v2 — H7 First Primary Held-Out Execution

**Estado:** ABORTED FAIL-CLOSED / AUTHORIZATION CONSUMED.
La única ejecución autorizada comenzó con `V2I-H7-001` y abortó antes de raw
capture: el frozen `requirement_id=req-h7-001` no satisface el contrato del
tipo productivo `DiscriminatingEvidenceRequirement`, que exige prefijo
`discrimination-requirement-`. No hubo retry, traducción, ground truth, scoring,
learning/writeback ni cambio productivo. El run no es evidencia cognitiva.

## HCPDQ-v2 — H7 Primary Execution Authorization / Go-No-Go

**Decisión:** GO para exactamente una primary run.
Los hashes congelados de corpus/protocol/adapter/recertification y del truth
sellado coinciden exactamente con el manifest. Se autoriza una única ejecución
`HCPDQ-V2-H7-PRIMARY-001`, 12 casos en orden fijo, fresh isolation, 1 attempt y
0 retries. Ground truth, scoring, learning/writeback y segunda ejecución siguen
prohibidos. Este gate no consume la autorización.

## HCPDQ-v2 — H7 Final Preflight / Run Manifest Freeze

**Estado:** PREFLIGHT PASS / MANIFEST FROZEN.
Se congeló `HCPDQ-V2-H7-PRIMARY-001` con 12 casos en orden exacto, hashes de
corpus/protocolo/adapter/recertificación, truth sellado, single-attempt/no-retry,
fresh isolation, raw SHA-256 capture y condiciones fail-closed de abort.
Primary execution continúa NO-GO hasta autorización separada.

## HCPDQ-v2 — H7 Minimal Isolation Adapter Causal / Architectural Recertification

**Decisión:** GO.
El único RED previo era la ausencia del adapter H7 y quedó resuelto por un
único boundary dedicado. La auditoría estática confirma que no posee autoridad
cognitiva/planning, no importa ground truth/scoring y sólo referencia la
superficie productiva existente. Primary execution continúa NO-GO.

## HCPDQ-v2 — H7 Minimal Isolation Adapter Implementation

**Estado:** GREEN / IMPLEMENTED.
Se añadió únicamente `app/hcpdq_v2_h7_isolation_adapter.py`. El adapter es
corpus-only, enforcea un intento y cero retries, sella raw capture por SHA-256
y expone sólo la construcción del entry path productivo existente. No contiene
ground truth, scoring, planning authority ni autorización de primary execution.

## HCPDQ-v2 — H7 Pre-Execution RED / Isolation Contract Tests

**Estado:** EXPECTED RED CONFIRMED.
Se añadieron seis contratos. Resultado: 1 RED esperado + 5 PASS protectivos.
El único RED demuestra que todavía no existe `app.hcpdq_v2_h7_isolation_adapter`.
Los PASS preservan corpus-only, ground-truth exclusion, productive entry path,
single-attempt/no-retry, raw capture y ausencia de scoring/routing/mutación.
No se ejecutó ROBY ni planning.

## HCPDQ-v2 — H7 ROBY Evaluation Run Exposure / Isolation Protocol

**Estado:** PROTOCOL FROZEN.
Se congeló una frontera corpus-only para los 12 casos V2I-H7. El adapter de
evaluación podrá leer únicamente el corpus, usar el entry path productivo
existente y capturar evidencia raw. Ground truth, scoring, learning, writeback,
benchmark routing y creación de autoridad planning quedan prohibidos.
Primary execution continúa NO-GO.

## HCPDQ-v2 — H7 Freeze Certification / Exposure Authorization

**Decisión:** GO limitado.
Los hashes congelados de corpus y ground truth fueron recomputados y coinciden
exactamente. Se autoriza exposición sólo para preparar el boundary/adapter de
evaluación usando exclusivamente el corpus ROBY-facing. Ground truth, ejecución,
planning y scoring permanecen NO-GO.

## HCPDQ-v2 — H7 Independent Corpus Construction / Ground-Truth Freeze

**Estado:** CONSTRUCTED / FROZEN / UNEXPOSED.
Se construyeron 12 casos nuevos `V2I-H7` (D1=4, D2=4, D3=4) y un ground
truth separado (PLANNED=6, FAIL_CLOSED=6). Ambos quedaron sellados por hash.
No hubo invocaciones ROBY/planning, scoring ni exposición. Cualquier cambio de
contenido invalida el freeze y exige uno nuevo.

## HCPDQ-v2 — H7 Independent Corpus Construction Contract / Dry Probe

**Decisión:** GO para construcción independiente.
Se congeló namespace `V2I-H7`, esquema de caso, balance 12 casos (4 D1/4 D2/4
D3; 6 PLANNED/6 FAIL_CLOSED) y guards de independencia. El dry probe fue
puramente estático: 0 invocaciones ROBY, 0 invocaciones planning y ningún caso
held-out materializado. Exposición continúa NO-GO hasta freeze certification.

## HCPDQ-v2 — H7 Hypothesis / Measurable Family Contract

**Decisión:** GO / hypothesis frozen.
H7 mide exclusivamente el re-entry gobernado de planificación multi-step para
adquisición de evidencia mediante la autoridad existente `planning_foundation`.
Éxito exige una única invocación, lineage preservado y cero ejecución/mutación.
No se generaliza H7 a planificación arbitraria. Construcción independiente del
corpus queda autorizada; exposición a ROBY continúa NO-GO.

## HCPDQ-v2 — H7 Independent Cycle Scope / Independence Contract

**Decisión:** GO para iniciar H7 como ciclo independiente.
H7 hereda la baseline productiva actual de ROBY y su arquitectura gobernada,
pero no puede heredar información experimental privilegiada de H6. Corpus,
ground truth, exposición, ejecución y scoring H7 tendrán namespace y freezes
propios. La exposición a ROBY permanece NO-GO hasta freeze certification.

## HCPDQ-v2 — H6 Productive Gap Final Validation / Closure

**Decisión:** CLOSE.
El gap productivo H6 queda formalmente cerrado sobre baseline validada
13.074 PASS · 0 FAIL · Ruff limpio. La regla mínima está implementada,
recertificada y calibrada. El primary histórico 0/12 permanece sellado como
medición pre-fix y no se reejecuta ni rescora.

## HCPDQ-v2 — H6 Calibration / Generalization Certification

**Estado:** CERTIFIED.
Siete casos nuevos y no ligados al corpus H6 certifican que la excepción del
único superviviente de criterios obligatorios generaliza y permanece fail-closed:
múltiples supervivientes, evidencia obligatoria INSUFFICIENT, ausencia de
criterios obligatorios o competidor no bloqueado conservan abstención. No se
modificó producción.

## HCPDQ-v2 — H6 Productive Gap Causal / Architectural Recertification

**Estado:** CAUSAL / ARCHITECTURAL RECERTIFIED.
La corrección E501 validada es semánticamente neutra respecto de la
implementación anterior. El cambio cognitivo permanece localizado únicamente
en `GovernedComplexDecisionReasoningFoundationV1`: recomendación del único
superviviente de criterios obligatorios cuando todos los competidores están
BLOCKED. INSUFFICIENT secundario permanece visible y no se añadió lógica HCPDQ,
ground truth, adapter, entry-path ni dominancia genérica.

## HCPDQ-v2 — H6 Minimal Governed Implementation

**Estado:** GREEN / MINIMAL IMPLEMENTATION COMPLETE.
Se modificó únicamente `core/governed_complex_decision_reasoning.py`. La
autoridad existente puede recomendar al único candidato que satisface
explícitamente todos los criterios obligatorios cuando todos sus competidores
están BLOCKED por un criterio obligatorio. La evidencia no obligatoria
INSUFFICIENT permanece intacta y visible. No se añadió dominancia genérica.

## HCPDQ-v2 — H6 Productive Gap Pre-Implementation RED

**Estado:** EXPECTED RED CONFIRMED / IMPLEMENTATION AUTHORIZED.
Se añadieron seis contratos contra la autoridad productiva existente. Resultado:
1 RED esperado + 5 PASS protectivos. El único fallo demuestra que la opción
`alpha`, única superviviente de un criterio obligatorio explícito, sigue sin
recomendarse cuando falta evidencia secundaria. Los PASS confirman que
INSUFFICIENT sigue visible, el hard constraint sigue BLOCKED, la ambigüedad sin
criterio obligatorio sigue absteniéndose y los límites gobernados permanecen.
No se modificó producción.

## HCPDQ-v2 — H6 Productive Gap Contract / Go-No-Go

**Estado:** LIMITED PRODUCTIVE CHANGE AUTHORIZED / GO.
El gap productivo queda acotado a la autoridad existente de decisión compleja.
Se autoriza únicamente una regla general: si exactamente una opción sobrevive
todos los criterios obligatorios explícitos y todas las demás están BLOCKED por
alguno de ellos, la evidencia faltante en criterios no obligatorios no debe
vetar automáticamente al único superviviente. Missing evidence sigue siendo
INSUFFICIENT, nunca UNFAVORABLE, y debe conservarse visible. No se autoriza una
heurística general de dominancia con evidencia incompleta.

## HCPDQ-v2 — H6 Scoring Post-Mortem / Cognitive Result Audit

**Estado:** PASS / PRODUCTIVE GAP LOCALIZED.
El 0/12 permanece sellado. Un replay causal read-only de los componentes GCDR
productivos reproduce los 12 `insufficient_evidence` sin reejecutar ROBY. La
causa se localiza en la política gobernada de completitud: pares criterio-opción
sin evidencia explícita se vuelven INSUFFICIENT, cualquier INSUFFICIENT vuelve
la opción REVIEW_REQUIRED y cualquier REVIEW_REQUIRED retiene la recomendación.
No es fallo del adapter, entry path, scoring ni ground truth.

## HCPDQ-v2 — H6 First Ground-Truth Scoring Execution

**Estado:** SCORING COMPLETED / RESULTS SEALED.
La autorización de scoring fue consumida una sola vez sobre las 12 capturas raw
ya selladas. El ground truth fue leído read-only y no se reejecutó ROBY.
Resultado bajo la regla congelada: 0 PASS / 12 FAIL. Las 12 respuestas
abstuvieron por evidencia insuficiente y no recomendaron la opción esperada ni
identificaron explícitamente el conjunto de evidencia decisiva congelado.

## HCPDQ-v2 — H6 Ground-Truth Scoring Authorization / Go-No-Go

**Estado:** GO / GROUND-TRUTH SCORING AUTHORIZED.
El boundary audit es válido, las 12 capturas siguen selladas, el ground truth
conserva su hash congelado y sus case_id coinciden con el manifest. Se autoriza
una única pasada read-only de scoring sobre esas capturas existentes. ROBY no
puede reejecutarse y capturas/truth no pueden mutarse. Este gate no puntúa.

## HCPDQ-v2 — H6 Primary Post-Mortem / Evaluation-Boundary Audit

**Estado:** BOUNDARY AUDIT PASS / SCORING GATE ELIGIBLE.
La ejecución primaria queda ligada a manifest y autorización, consumida una
sola vez y no repetible. Las 12 capturas raw son hash-consistentes, selladas,
single-attempt y sin errores de infraestructura. No hubo ground-truth access,
scoring, learning, memory writeback ni feedback durante la ejecución. Este
gate no puntúa ni autoriza por sí mismo scoring.

## HCPDQ-v2 — H6 First Primary Held-Out Execution

**Estado:** PRIMARY RUN COMPLETED / RAW CAPTURES SEALED.
La autorización primaria fue consumida una sola vez. Los 12 casos
V2E-H6-001..012 se ejecutaron en el orden congelado, con contexto fresco y un
intento por caso. Se sellaron 12/12 respuestas raw, sin errores de
infraestructura, retries, ground-truth access ni scoring. La autorización no es
reutilizable. No se abre scoring hasta el post-mortem de frontera.

## HCPDQ-v2 — H6 Primary Execution Authorization / Go-No-Go

**Estado:** GO / PRIMARY EXECUTION AUTHORIZED.
Los bindings del run manifest contra corpus, ground truth, adapter, protocolo y
recertificación coinciden. Se autoriza exactamente una ejecución primaria H6
de 12 casos, en el orden congelado y con un intento por caso. Ground truth,
scoring, learning, memory writeback y feedback permanecen fuera de ejecución.
Este gate no ejecutó held-out.

## HCPDQ-v2 — H6 Final Preflight / Run Manifest Freeze

**Estado:** RUN MANIFEST FROZEN / PRIMARY EXECUTION NOT YET AUTHORIZED.
Se congeló el manifiesto definitivo para 12 casos H6 en orden V2E-H6-001 a
V2E-H6-012, sin shuffle, con un intento, contexto fresco y captura raw
inmutable/no puntuada. Corpus, ground truth, adapter, protocolo y
recertificación quedaron hash-bound. Ground truth y scoring permanecen fuera
de ejecución. Este gate no ejecutó held-out.

## HCPDQ-v2 — H6 Isolation Adapter Causal / Architectural Recertification

**Estado:** CAUSAL / ARCHITECTURAL RECERTIFIED.
El adapter mínimo reutiliza `OfficialConversationGateway` y no construye
CanonicalDecisionFacade, CognitivePlanner ni otra autoridad paralela. No
referencia archivos de corpus/ground truth, no contiene scoring ni APIs de
escritura persistente y mantiene primary execution fail-closed. El held-out no
fue ejecutado en este gate.

## HCPDQ-v2 — H6 Minimal Isolation Adapter Implementation

**Estado:** IMPLEMENTED / pendiente de gate global.
Se implementó únicamente `app.hcpdq_v2_h6_entry_path_isolation_adapter.py`.
Los 9 RED pasan a GREEN reutilizando `OfficialConversationGateway`. El adapter
expone sólo case_id+prompt, contexto efímero por caso, un único intento y raw
capture inmutable. No carga ground truth, no puntúa, no aprende, no escribe
memoria ni persistencia y mantiene primary execution bloqueada.

## HCPDQ-v2 — H6 Pre-Execution RED

**Estado:** RED CONTRACT CERTIFIED / IMPLEMENTATION AUTHORIZED. Nueve contratos fallan exclusivamente porque `app.hcpdq_v2_h6_entry_path_isolation_adapter` todavía no existe. No hubo exposición held-out ni ground truth.

## HCPDQ-v2 — H6 ROBY Exposure / Isolation Protocol

**Estado:** PROTOCOL FROZEN / PRE-EXECUTION RED TESTS REQUIRED.
La frontera de exposición queda congelada antes de implementar adapter alguno:
sólo case_id + prompt congelado, entrada productiva H6 existente, contexto
fresco por caso, un único intento y captura inmutable sin scoring. Ground truth
queda fuera del adapter. Learning, memory writeback, feedback, retries,
mutaciones y primary execution siguen NO-GO. Este gate no expuso held-out.

## HCPDQ-v2 — H6 Freeze Certification / Exposure Authorization

**Estado:** FREEZE CERTIFIED / EXPOSURE AUTHORIZED.
Corpus y ground truth conservan exactamente los hashes congelados, los 12
case_id permanecen únicos y alineados y los 12 prompts son COMPLETE para el
intake H6 certificado. No hubo exposición previa. Se autoriza únicamente la
primera exposición read-only de prompts por la ruta productiva H6 existente.
Ground truth, scoring, adaptación y primary execution continúan NO-GO.

## HCPDQ-v2 — H6 Independent Corpus / Ground-Truth Freeze

**Estado:** CORPUS + GROUND TRUTH FROZEN / EXPOSURE NOT AUTHORIZED.
Se construyeron 12 casos H6 nuevos (6 standard, 6 hard) usando exclusivamente
el intake Decisión/Criterios/Evidencia. Se construyó y congeló ground truth
alineado por case_id. Corpus y truth quedaron hash-bound e inmutables. No se
ejecutó ni expuso ROBY. El próximo gate debe certificar el freeze antes de
autorizar exposición.

## HCPDQ-v2 — H6 Dry-Probe Certification / Construction Authorization

**Estado:** DRY PROBES CERTIFIED / CONSTRUCTION AUTHORIZED.
Tres probes sintéticos no-held-out atravesaron el intake exacto
Decisión/Criterios/Evidencia, fueron COMPLETE/EXPLICIT en sus tres evidencias y
alcanzaron una respuesta productiva con runtime fallback armado para fallar
cerrado. Esto certifica reachability del entry path, no performance cognitiva.
Se autoriza construir un nuevo corpus H6 y ground truth independiente bajo el
contrato congelado. Exposición held-out y ejecución siguen NO-GO.

## HCPDQ-v2 — H6 Entry-Path Equivalent Corpus Freeze Contract

**Estado:** CONTRACT FROZEN / CONSTRUCTION NOT YET AUTHORIZED.
El nuevo corpus H6 deberá usar exclusivamente el intake productivo existente
Decisión/Criterios/Evidencia, con casos e IDs nuevos y sin reutilizar,
parafrasear ni reescribir semánticamente el held-out consumido. Ground truth
deberá congelarse antes de exposición. Antes de construir casos held-out se
requiere un gate separado de dry probes no-held-out que certifique la ruta.

## HCPDQ-v2 — Entry-Path Equivalent Evaluation Recontract Scope

**Estado:** SCOPE FROZEN — H6 GO / H7 NO-GO.
H6 puede recontractarse usando exclusivamente el intake productivo estructurado
Decisión/Criterios/Evidencia ya existente. H7 queda fuera del nuevo freeze hasta
que exista y se certifique una ruta real de entrada de usuario hacia
planning_foundation; el re-entry interno no es equivalente. Este gate no crea
casos ni ground truth y no expone material held-out.

## HCPDQ-v2 — Evaluation Entry-Path Equivalence Contract / Go-No-Go

**Estado:** NO-GO / REFREEZE REQUIRED.
Entry-path equivalence pasa a ser precondición obligatoria antes de exposición
held-out. H6 y H7 fallan esta equivalencia bajo el freeze consumido. No se
autoriza retry, traducción/router benchmark-specific, semantic rewrite ni cambio
productivo. Se autoriza únicamente recontractar la evaluación y construir un
nuevo freeze independiente usando formas ya aceptadas por rutas productivas
existentes.

## HCPDQ-v2 — H6/H7 Primary Run Post-Mortem / Evaluation-Boundary Audit

**Estado:** EVALUATION DESIGN INVALID / RECONTRACT REQUIRED.
El primary run no es evidencia de performance cognitiva. H6: los 15 prompts
held-out son `NOT_ENVELOPE` para la gramática productiva estricta que sí fue
certificada en calibración. H7: la calibración certificó un re-entry interno a
planning_foundation, no una ruta conversacional equivalente; la
CanonicalPlanningFacade del gateway está unbound. La falla común es que nunca se
congeló equivalencia de entry path entre calibración y held-out.
No se autoriza retry, router benchmark-specific ni cambios productivos.

## HCPDQ-v2 — H6/H7 First Primary Held-Out Execution

**Estado:** EXECUTED ONCE / FAIL-CLOSED EVALUATION-BOUNDARY INVALID.
La autorización single-use fue consumida. Los 30 casos se intentaron exactamente
una vez, sin retries. Ningún prompt congelado produjo un raw response válido
dentro de las rutas productivas H6/H7 previamente certificadas; los 30 fallaron
cerrados en la frontera de evaluación. No se cargó ground truth y no se realizó
scoring. Este run no es evidencia de calidad cognitiva: es evidencia de una
incompatibilidad entre el corpus congelado y la frontera productiva certificada.

## HCPDQ-v2 — H6/H7 Primary Execution Authorization / Go-No-Go

**Estado:** GO — SINGLE PRIMARY HELD-OUT EXECUTION AUTHORIZED.
El gate autoriza exactamente una ejecución primaria bajo el run manifest
congelado. No autoriza retries, reuso de autorización, acceso a ground truth,
aprendizaje, adaptación, persistencia, cambios productivos ni comparación humana.
No se ejecutó ningún caso durante este gate.

## HCPDQ-v2 — H6/H7 Final Preflight / Run Manifest Freeze

**Estado:** RUN MANIFEST FROZEN / EXECUTION AUTHORIZATION PENDING.
El manifest definitivo fija scope H6/H7, 30 casos, orden lexicográfico por
case_id, cero retries, fresh context por caso, cero cross-case visibility,
subject envelope mínimo, raw capture antes de scoring y hashes de corpus,
ground truth, freeze/certification y adapter recertification. El freeze del
manifest no se autoautoriza: primary execution permanece NO-GO hasta un gate
explícito de autorización.

## HCPDQ-v2 — H6/H7 Minimal Isolation Adapter Causal / Architectural Recertification

**Estado:** CAUSALLY RECERTIFIED / PRIMARY EXECUTION NO-GO.
Los seis RED→GREEN se atribuyen exclusivamente a la incorporación del adapter
mínimo de aislamiento. El adapter conserva envelope mínimo, cero writes,
ausencia de loaders de ground truth, ausencia de autoridad cognitiva nueva,
aislamiento cross-case y raw-capture-before-scoring. Primary held-out execution
permanece bloqueado.

## HCPDQ-v2 — H6/H7 Minimal Isolation Adapter Implementation

**Estado:** IMPLEMENTED / pendiente de gate global oficial.
Se implementa únicamente `app.hcpdq_v2_h6_h7_isolation_adapter.py`.
Los seis RED de aislamiento pasan a GREEN por la misma causa arquitectónica.
El adapter sólo construye/valida el envelope sujeto, mantiene contexto efímero
por caso, captura raw output y mantiene scoring y ground truth fuera de su
frontera. No introduce autoridad cognitiva, persistencia, aprendizaje,
adaptación ni ejecución primaria.

## HCPDQ-v2 — H6/H7 Pre-Execution RED / Isolation Contract Tests

**Estado:** RED CONFIRMED / MINIMAL ISOLATION ADAPTER AUTHORIZED.
Se congelaron 6 RED contract tests. Los seis fallan por una única causa
arquitectónica deliberada: todavía no existe
`app.hcpdq_v2_h6_h7_isolation_adapter`. El RED exige envelope mínimo, rechazo de
ground truth, cero writes/adaptation, aislamiento entre casos, raw capture antes
de scoring y bloqueo de primary execution. Se autoriza sólo implementación
mínima del adapter; primary execution continúa NO-GO.

## HCPDQ-v2 — H6/H7 ROBY Evaluation Exposure / Isolation Protocol

**Estado:** PROTOCOL FROZEN / PRE-EXECUTION RED AUTHORIZED.
El subject envelope queda limitado a case_id, family, difficulty y prompt.
Ground truth y scoring permanecen fuera de la frontera del sujeto. Se exige
contexto fresco por caso, cero retries y ninguna visibilidad cross-case. Memory,
learning, adaptation, persistence, production mutation y primary execution
permanecen NO-GO. Se autoriza únicamente el siguiente gate RED de aislamiento.

## HCPDQ-v2 — H6/H7 Held-Out Freeze Certification / Exposure Authorization

**Estado:** CERTIFIED / CONTROLLED READ-ONLY EXPOSURE AUTHORIZED.
El corpus congelado H6/H7 conserva hashes, scope, balance, ground truth e
independencia, sin exposición previa ni ejecución. Se autoriza únicamente
exposición controlada read-only para preparar el protocolo de evaluación.
Primary held-out execution, ground-truth visibility, adaptación, cambios
productivos y human comparison permanecen NO-GO.

## HCPDQ-v2 — H6/H7 Held-Out Corpus Construction / Ground-Truth Freeze

**Estado:** FROZEN / PENDING INDEPENDENT FREEZE CERTIFICATION.
Se construyó un corpus nuevo de 30 casos, limitado a H6/H7: 15 por familia y
10 por dificultad D1/D2/D3. Los casos y ground truth tienen hashes congelados.
No se reutilizaron casos v1 ni prompts de calibración. ROBY no fue expuesto ni
ejecutado. Exposure/execution/human comparison permanecen NO-GO hasta una
certificación independiente del freeze.

## HCPDQ-v2 — Final Measurable Family Scope Freeze / Held-Out Readiness

**Estado:** FINAL SCOPE FROZEN / GO FOR HELD-OUT CONSTRUCTION+FREEZE ONLY.
El measurable set HCPDQ-v2 queda definitivamente limitado a H6/H7. H1/H2/H3/
H4/H5/H8 quedan explícitamente excluidas. Se autoriza construir un corpus held-out
nuevo e independiente H6/H7 y congelar su ground truth antes de exposición.
ROBY exposure, execution y human comparison permanecen NO-GO.

## HCPDQ-v2 — H1/H3 Shadow Observability Existing-Path Audit

**Estado:** RESOLVED / EXCLUDE H1-H3 FROM V2 MEASURABLE SCOPE.
`CognitivePlannerShadowRuntime` es real, read-only y está cableado a turnos
productivos: observa plan, selección contextual y selección de capacidad. Sin
embargo, sus records no exponen la semántica causal completa requerida por H1
(reasoning path) ni H3 (negation/quoted-span/distractor). No se autoriza RED ni
instrumentación benchmark-specific para fabricar esa evidencia.

## HCPDQ-v2 — Measurable Family Set Scope Freeze / Held-Out Readiness

**Estado:** SCOPE PARTIALLY FROZEN / HELD-OUT NO-GO.
H6 y H7 son las únicas familias actualmente certificadas como medibles.
H2/H8 quedan excluidas por ausencia de productive causal lineage; H4/H5 por
ausencia de productive exposure. H1/H3 no se excluyen todavía porque existe
`CognitivePlannerShadowRuntime`, una superficie observacional existente que debe
auditarse antes del freeze definitivo. No se autoriza held-out ni cambios de producción.

## HCPDQ-v2 — H2/H8 Causal-Lineage Exposure Gap Contract / Go-No-Go

**Estado:** NO-GO / EXCLUDE H2-H8 FROM V2 MEASURABLE SCOPE.
H2 y H8 poseen componentes existentes, pero no un productive causal join
observable. Añadir IDs a los records no demostraría causalidad: fabricaría una
correlación evaluativa. No se autoriza RED ni implementación productiva para
crear el join. Ambos quedan `NOT_VALIDLY_MEASURABLE_UNDER_HCPDQ_V2`, sin afirmar
ausencia de capacidad.

## HCPDQ-v2 — H7/H2/H8 Exposure Calibration Certification

**Estado:** PARTIAL CERTIFICATION / HELD-OUT NO-GO.
H7 queda certificado mediante un probe sintético que recorre el existing
productive planning re-entry y observa `planning_foundation`, lineage y una única
invocación, sin ejecución ni mutación. H2 y H8 conservan sus componentes
productivos existentes, pero no exponen hoy un shared causal-lineage record que
una epistemic sufficiency con ResponseDecision ni provenance con conflict
resolution. Ambos fallan cerrado; no se modifica producción para forzar el join.

## HCPDQ-v2 — H7/H2/H8 Exposure Causal / Architectural Recertification

**Estado:** CAUSALLY RECERTIFIED / HELD-OUT NO-GO.
La capa H7/H2/H8 queda recertificada como infraestructura read-only sin
autoridad propia. H7 conserva `planning_foundation`; H2 exige join entre
epistemic sufficiency y la ResponseDecision existente; H8 exige join entre
provenance y conflict-resolution existente. No hay direct internal
instantiation, semantic prompt routing, ground truth, persistencia o adaptación.

## HCPDQ-v2 — H7/H2/H8 Minimal Read-Only Causal Exposure Implementation

**Estado:** IMPLEMENTED — pendiente de gate global oficial.
Se añade exclusivamente
`scripts/hcpdq_v2_h7_h2_h8_existing_authority_exposure.py`.
La capa contiene evidence records frozen y predicates read-only para causal join:
H7 conserva `planning_foundation` + lineage + invocation_count=1; H2 mantiene
epistemic sufficiency separado de ResponseDecision y exige join existente; H8
mantiene provenance separado de conflict resolution y exige evidencia existente.
No instancia autoridades ni decide, ejecuta, selecciona, persiste o adapta.

## HCPDQ-v2 — H7/H2/H8 Existing-Authority Exposure Pre-Implementation RED

**Estado:** PRE-IMPLEMENTATION RED / 12 fallos intencionales.
Los RED exigen causal join read-only específico para H7, H2 y H8:
H7 planning lineage + exactamente una invocación existing planning; H2 join
entre epistemic sufficiency y ResponseDecision existente; H8 join entre
provenance y conflict-resolution ya producido. Se preservan zero authority,
ground-truth firewall, metadata-only mapping, fail-closed y held-out NO-GO.
Producción no se modifica.

## HCPDQ-v2 — H7/H2/H8 Existing-Authority Exposure Contract / Go-No-Go

**Estado:** CONDITIONAL GO → PRE-IMPLEMENTATION RED ONLY.
H7 queda acotado al existing planning re-entry de `planning_foundation`; H2 a la
observación conjunta pero causalmente separada de epistemic sufficiency y la
decisión productiva ANSWERED/ABSTAINED; H8 a provenance más conflict-resolution
ya producido por governed reasoning. Metadata sola nunca certifica participación.
No se autoriza implementación productiva todavía, nueva authority, binding para
benchmark, direct internal instantiation, held-out ni human comparison.

## HCPDQ-v2 — Remaining Families Existing-Authority Exposure Audit / Prioritization

**Estado:** AUDITED / PRIORITIZED / HELD-OUT NO-GO.
Prioridad congelada: H7 → H2 → H8 → H1 → H3 → H4 → H5.
Wave 1 (contract): H7/H2/H8 por disponer de productive consumers o superficies
existentes más cercanas a exposición causal. Wave 2: H1/H3 requieren primero
auditar shadow observability existente. H4/H5 se difieren o excluyen salvo que
aparezca un productive consumer legítimo; no se crearán facades de benchmark.

## HCPDQ-v2 — Evaluation Exposure Causal / Architectural Recertification

**Estado:** CAUSALLY RECERTIFIED / HELD-OUT NO-GO.
La capa `scripts/hcpdq_v2_evaluation_exposure.py` queda certificada como
infraestructura read-only de autoridad efectiva cero: no instancia autoridades
cognitivas, no hace semantic prompt routing, no recibe ground truth, no permite
persistencia/adaptación y conserva shadow-equivalence. H6 reutiliza su
certificación existente; H1/H2/H3/H4/H5/H7/H8 siguen fail-closed.

## HCPDQ-v2 — Minimal Read-Only Evaluation Exposure Infrastructure

**Estado:** IMPLEMENTED — pendiente de gate global oficial.
Se añade exclusivamente `scripts/hcpdq_v2_evaluation_exposure.py` como
infraestructura experimental read-only. Implementa política de autoridad cero,
request/evidence immutable, registry family-metadata-only, causal evidence
requirement, shadow equivalence, family exclusion fail-closed y held-out gate.
H6 reutiliza su certificación existente; H1/H2/H3/H4/H5/H7/H8 permanecen
uncertified/calibration-only. No se modifica semántica cognitiva ni producción.

## HCPDQ-v2 — Evaluation Exposure Gap Pre-Implementation RED

**Estado:** PRE-IMPLEMENTATION RED / 15 fallos intencionales.
Se congelan E1-E10 y cinco invariantes transversales: zero authority, identidad
de autoridad existente, no instanciación interna, metadata-only family mapping,
ground-truth firewall, zero persistence/adaptation, evidencia causal obligatoria,
shadow equivalence, exclusión fail-closed y held-out NO-GO. H6 se reutiliza y
H1/H2/H3/H4/H5/H7/H8 comienzan uncertified/calibration-only. Producción no se
modifica.

## HCPDQ-v2 — Remaining H1/H2/H3/H4/H5/H7/H8 Existing-Path Resolution

**Estado:** RESOLVED / 0 nuevas familias certificadas / held-out NO-GO.
La resolución distingue existencia de autoridad, superficie productiva y
exposición completa de la semántica HCPDQ. H2/H7/H8 poseen superficies
productivas parciales pero no ejecutores certificados de abstention/planning/
conflict-resolution completos. H1 conserva composición cognitiva coarse.
H3/H4/H5 poseen mecanismos internos certificados pero no una exposición
productiva read-only oficial para benchmark. No se autoriza nueva authority ni
cambio productivo para forzar cobertura.

## HCPDQ-v2 — Calibration Path-Coverage Certification

**Estado:** PARTIAL CERTIFICATION / HELD-OUT NO-GO.
**Resultado:** H6 certifica un path productivo real mediante
`OfficialConversationGateway` → explicit complex-decision intake → productive
GCDR integration → governed complex decision reasoning, sin runtime fallback.
H1/H2/H3/H4/H5/H7/H8 permanecen fail-closed hasta demostrar su path mediante
calibration/synthetic probes. No se autoriza corpus held-out ni cambio cognitivo.

## HCPDQ-v2 — Minimal Observability / Path-Coverage Infrastructure

**Estado:** IMPLEMENTED — pendiente de gate global oficial.
**Decisión:** añadir exclusivamente `scripts/hcpdq_v2_evaluation_boundary.py`
como infraestructura experimental read-only. La capa preserva status,
response_path, degradation_reason, rationale, flags de runtime y evidencia del
CognitiveTurnDossier existente; separa measurement validity de cognitive
scoring; impone timeout mecánico; verifica identidad final exacta; y conserva
el mapa H1-H8 P1/P2/P1/P1/P1/P3/P2/P2 en modo calibration-only/fail-closed.
Sin cambios productivos y sin corpus held-out HCPDQ-v2.

## HCPDQ-v2 — Evaluation-Boundary Observability / Path-Coverage RED Contract

**Estado:** PRE-IMPLEMENTATION RED — 13 fallos intencionales, 0 inesperados en
validación focal.
**Decisión:** exigir una capa experimental read-only que preserve status,
response_path, degradation_reason, rationale, runtime flags y evidencia del
dossier cognitivo existente; separar validez de medición de scoring cognitivo;
imponer timeout mecánico; verificar identidad final exacta; congelar el mapa
H1-H8 P1/P2/P3; y prohibir persistencia/adaptación/held-out. Producción no se
modifica y HCPDQ-v2 held-out sigue NO-GO.

## HCPDQ-v1 — ROBY Evaluation Run Final Preflight / Run Manifest Freeze

**Estado:** PRE-EXPOSURE FROZEN — pendiente de gate global oficial.
**Decisión:** congelar `HCPDQ-V1-ROBY-XI2-PRIMARY-001` contra la baseline
12.808 PASS, con package SHA-256, fingerprints HCPDQ-v1, orden estable de
120 casos, cero retries, timeout uniforme de 30 s, aislamiento por caso y
prohibición de feedback/persistencia/adaptación. Ningún held-out fue ejecutado.

## HCPDQ-v1 — ROBY Evaluation Run Minimal Isolation Adapter

**Estado:** IMPLEMENTED — pendiente de gate global oficial.
**Decisión:** implementar exclusivamente un adapter experimental read-only en
`scripts/hcpdq_v1_roby_evaluation_run.py`, usando `OfficialConversationGateway`
como frontera productiva existente. El adapter verifica fingerprints congelados,
limita el subject payload, fija cero retries/orden estable, separa captura raw de
scoring y prohíbe writes/adaptación. Esta implementación no ejecuta el held-out.

## HCPDQ-v1 — Held-Out Corpus Construction / Independent Ground-Truth Freeze

**Estado:** IMPLEMENTED / FREEZE READY — pendiente de gate global oficial.
**Decisión:** congelar un corpus comparativo experimental separado del código productivo: 30 casos de calibración y 120 held-out, con 15 casos por cada una de ocho familias y 5 D1 + 5 D2 + 5 D3 por familia. Ground truth y rubrics permanecen en artefactos separados; el payload del sujeto excluye respuestas, scoring y expected outcomes. El freeze se identifica mediante fingerprints deterministas y no autoriza aprendizaje, tuning, nueva authority ni ejecución cognitiva del held-out.

## Advanced Capability 4A — Governed Advanced Reasoning Quality Benchmark

**Estado:** Implementado como diagnóstico; pendiente de validación global oficial.
**Decisión:** medir transversalmente las capabilities existentes con un corpus determinista de 80 casos y ground truth previo. 4A no modifica reasoning productivo ni introduce otra authority. Sus resultados sólo pueden abrir un Audit → Contract / Go-No-Go posterior; nunca una reparación automática.

## Decisión M399.2 — Governed Self-Diagnostics Foundation

**Base:** M399.1 certificada (10.829 tests, Ruff limpio, M361 sincronizada, 0 regresiones)  
**Decisión:** incorporar `GovernedSelfDiagnostics` como autoridad técnica `self_diagnostics` que recibe series homogéneas de observaciones explícitas, conserva su linaje, calcula tendencia y sólo declara anomalía frente a umbrales explícitos. Se rechaza crear un monitor residente, un segundo diagnóstico cognitivo o cualquier mecanismo de reparación. `UnifiedBrain.diagnostics` / M387.9 conserva su ámbito; las hipótesis, proposals, sandbox y cambios de código permanecen fuera de M399.2.

## Decisión M399.1 — Governed Current Location Audit & Activation

**Base:** M398.10 certificada (10.812 tests, Ruff limpio, M361 sincronizada, 0 regresiones)  
**Decisión:** introducir `CurrentLocationAuthority` como única autoridad semántica de ubicación actual y ampliar `OfficialDeviceGateway` únicamente como receptor de evidencia Android registrada. La autoridad no adquiere hardware: consume `AndroidLocationObservation`, exige consentimiento, permiso, frescura y confianza explícita y sólo proyecta evidencia válida a `GeoPointSignal`. Nominatim permanece geocoder, Maps consumidor, M397/M398 transporte y Android Sensors no absorbe GPS. La activación de M399.1 es contractual e integrada; no se afirma GPS físico operativo hasta que un proveedor Android real produzca observaciones detrás de esta frontera.

## Decisión M395.1 — Fronteras y contratos neutrales

**Base:** M394.8 + auditoría M394.A  
**Estado:** Implementación de consolidación estructural  

**Decisión:** neutralizar contratos compartidos que producían dependencias `core -> app`, `infrastructure -> app` y `core -> infrastructure`, preservando las autoridades existentes. `CameraFrame`, Cognitive Agenda, Priority Reasoning y Response Model pasan a contratos neutrales; Android activation recibe sólo un protocolo mínimo de consulta de dispositivo. Los imports históricos necesarios permanecen como shims/reexports de compatibilidad. No se añaden capacidades ni I/O.

## M393.8 — Decisión de integración

**Base certificada:** M393.7 — 10200 pruebas.

Se aprueba cerrar la serie M393 sin añadir capacidad productiva. La estabilización se limita a contratos integrales, pruebas y documentación bajo la autoridad existente `RelationshipMemoryManager`.

## M393.7 — Decisión de integración

La auditoría se integra como método puro de `RelationshipMemoryManager` y consume `RelationshipTraceabilityView`. Se rechaza crear un auditor o gestor paralelo, persistencia adicional o inferencia semántica nueva.

## M393.6 — Decisión de integración

**Base:** M393.5 (10184 tests, Ruff limpio)

**Decisión:** ampliar `RelationshipMemoryManager` con `traceability_view()` como vista diagnóstica de solo lectura. Se reutilizan evidencia, consolidación, consistencia y evolución existentes; se rechaza crear `RelationshipTraceManager`, almacenamiento adicional o lógica de resolución automática.

## Decisión M393.1 — Enriquecimiento bajo la autoridad relacional existente

**Base:** M392.8 certificada.  
**Decisión:** ampliar `RelationshipMemoryManager` con una vista de evidencia explícita en lugar de crear otro gestor o repositorio relacional. El enriquecimiento es de sólo lectura, conserva el registro fuente intacto y rechaza enlaces a registros inexistentes o duplicados. Persistencia, inferencia, consolidación automática, runtime y ejecución quedan fuera de alcance.

## M392.8 — Decisión de estabilización integral

M392.8 se integra como diagnóstico puro bajo `InternalWorldModelFoundation`. Se rechaza crear un gestor de estabilización, persistencia adicional o reparación automática. El cierre sólo audita el snapshot M392.7 y conserva intactas las seis representaciones fuente.

## M392.7 — Decisión de integración del mundo

M392.7 se integra como composición pura bajo `InternalWorldModelFoundation`. Se rechaza crear `WorldManager`, repositorio unificado adicional o autoridad paralela. Las seis representaciones M392 conservan sus contratos y fuentes; la integración sólo las expone juntas.

## M392.6 — Decisión de integración contextual

M392.6 se integra como vista especializada bajo `InternalWorldModelFoundation`. Se rechaza crear `ContextManager`, otro repositorio o una autoridad paralela. El blackboard y el contexto ambiental conservan sus responsabilidades; el modelo del mundo sólo proyecta evidencia explícita y gobernada.

## M392.5 — Decisión de integración temporal

La línea temporal se integra como vista subordinada a `InternalWorldModelFoundation` y reutiliza `ExecutiveEvent` como contrato fuente. No se autoriza un gestor temporal paralelo ni persistencia adicional.

## M392.4 — Decisión de integración

M392.4 se integra como vista especializada bajo `InternalWorldModelFoundation`. Se rechaza crear `ObjectManager`, otro repositorio, detector o autoridad paralela. `object_knowledge` conserva su responsabilidad y el modelo del mundo sólo proyecta resultados explícitos.

## M392.3 — Decisión de integración

M392.3 se integra como vista especializada bajo `InternalWorldModelFoundation`. Se rechaza crear `PlacesManager`, otro resolver, geocodificador, repositorio o autoridad paralela. `location_resolution` y `places_knowledge` conservan sus responsabilidades; el modelo del mundo sólo proyecta sus resultados explícitos.
## M392.2 — Decisión de integración

M392.2 se integra como vista especializada bajo `InternalWorldModelFoundation`. Se rechaza crear `PeopleManager`, otro perfil persistente o una autoridad paralela. Identidad y relación conservan sus fuentes canónicas; el modelo del mundo sólo las proyecta de forma explícita y de solo lectura.

## M392.1 — Decisión de integración

M392.1 se integra como una vista especializada bajo `InternalWorldModelFoundation`. Se rechaza crear `HouseManager`, `WorldManager`, otro repositorio o una segunda autoridad. `HouseholdMemory` mantiene la persistencia y `internal_world_model` mantiene la representación canónica.

## M391.8 — Decisión de estabilización

**Base:** M391.7 (10020 tests, Ruff limpio)

**Decisión:** cerrar la primera serie de Época IV con un diagnóstico integral puro que valide presencia, autoridades y linajes explícitos sin crear nueva autoridad ni comportamiento operativo. Se corrigen referencias documentales de raíz y se preservan intactas las capacidades M391.1–M391.7.

## M391.7 — Predicción Gobernada

Predicción explícita y gobernada sobre M391.4 bajo `governed_reasoning`, sin hechos futuros, probabilidades inventadas, persistencia ni ejecución.

## M391.6 — Decisión de integración

**Base:** M391.5 (9982 tests, Ruff limpio)

**Decisión:** ampliar `CanonicalDecisionFacade` con `advise(...)` y añadir `GovernedDecisionAdvisor` como apoyo puro subordinado a `unified_cognitive_coordination`. Se reutilizan resultados M391.3–M391.5 sin crear otra autoridad, función de utilidad, prioridad paralela, persistencia o ejecución. Bloqueos y revisión conservan precedencia y la decisión humana final permanece explícitamente preservada.

## M391.5 — Decisión de integración

**Base:** M391.4 (9964 tests, Ruff limpio)

**Decisión:** extender la organización personal mediante `IntelligentPersonalOrganizationView`, subordinada a `PersonalOrganizationAuthority`, y reutilizar `PriorityReasoning` para ordenar ítems explícitos. Se rechaza crear `PersonalOrganizerManager`, otro planificador, persistencia adicional o automatización. Las autoridades de agenda, tareas, recordatorios, objetivos, proyectos y notas conservan sus fronteras operativas.

## M391.4 — Decisión de integración

La comprensión causal y predictiva se integra en `governed_reasoning` mediante `GovernedCausalPredictiveReasoner`, sin nueva autoridad ni gestor paralelo. Consume el mundo M391.2 explícito, conserva relaciones causales como hipótesis y predicciones como inferencias; no modifica M391.3, runtime, memoria, aprendizaje, planificación ni ejecución.

## M391.3 — Decisión de integración

**Base:** M391.2 (9929 tests, Ruff limpio)

**Decisión:** incorporar `GovernedScenarioSimulator` dentro del dominio de `governed_reasoning` y mantenerlo como evaluador puro, sin `authority_id`, persistencia ni conexión de runtime. Sólo recibe `PersistentWorldSnapshot` M391.2 e hipótesis explícitas; toda salida conserva `EpistemicLevel.HYPOTHESIS`. Se rechaza promover el `CognitiveHypothesisWorkspace` histórico o crear un `ScenarioManager`.

## M391.2 — Decisión de integración

**Base:** M391.1 (9913 tests, Ruff limpio)

**Decisión:** extender `internal_world_model` mediante una vista persistente sobre fuentes que ya poseen persistencia gobernada. Se rechaza crear otra base de datos, repositorio o gestor mundial. `HouseholdMemory`, memoria canónica, relaciones e identidad conservan sus fronteras de escritura.

## M390.8 — Decisión de estabilización y evidencia integral

**Base:** M390.7 (9892 tests, Ruff limpio)

**Decisión:** cerrar M390 mediante `M390IntegralEvidenceDiagnostic`, diagnóstico subordinado y de solo lectura que comprueba la cadena explícita formada por estado interior, continuidad, regulación, reflexión y modulación expresiva. No se crea autoridad nueva, no se modifica runtime y no se agregan capacidades conductuales. Las ausencias quedan como `incomplete` y los desacuerdos de linaje como `conflict`; nunca se reparan de forma implícita.

## M390.7 — decisión de integración

**Base:** M390.6 (9885 tests, Ruff limpio)

La reflexión sobre estado interior se integra extendiendo `ConversationReflectionAuthority` M389.2. Se rechaza crear una autoridad específica para reflexión interior. Las entradas M390 son opcionales y explícitas; continuidad y regulación sólo se observan con un snapshot interior asociado. Sin snapshot M390, la ruta histórica de M389.2 se conserva exactamente.

## M390.6 — Decisión de regulación funcional simulada

**Base:** M390.5 (9873 tests, Ruff limpio)

**Decisión:** incorporar `SimulatedFunctionalRegulation` como evaluador puro que opera únicamente sobre el snapshot interior actual y una continuidad M390.3 suministrada explícitamente. El resultado es un dictamen de regulación, no un nuevo estado interior. La única integración productiva interna de este incremento extiende M390.5 para permitir que el dictamen limite la señal afectiva a `careful`; M377 conserva la autoridad exclusiva sobre el perfil expresivo. No se introduce persistencia, reloj, aprendizaje, objetivos, ejecución ni runtime nuevo.

## M390.5 — Decisión de modulación expresiva gobernada

**Base:** M390.4 (9863 tests, Ruff limpio)

**Decisión:** ampliar mínimamente `AdaptivePersonalityRequest` para admitir una señal afectiva simulada trazable y utilizar `GovernedExpressiveModulation` como adaptador puro desde M390. `AdaptivePersonalityAuthority` permanece como única autoridad de modulación expresiva. La señal M390.5 sólo puede sugerir tonos neutrales, cálidos o cuidadosos y nunca modifica directamente texto, identidad, rasgos, detalle o estructura solicitados.

## M390.4 — Decisión de integración

La integración relacional del mundo interior se realiza exclusivamente a partir de `CognitiveCycleNodeRecord` del nodo `relational_affective_context`. No se conectan directamente snapshots de relación, perfiles, conversación ni runtime. La decisión preserva una única autoridad por capacidad y evita un gestor relacional/emocional paralelo.

## Decisión M390.3 — Continuidad interior sólo con snapshots explícitos

**Base:** M390.2 (9847 tests, Ruff limpio)

**Decisión:** incorporar `ExplicitInnerContinuityEvaluator` como componente puro y subordinado que compara exclusivamente un snapshot anterior y uno actual entregados explícitamente. No mantiene historial, no usa reloj, no persiste, no reconstruye períodos faltantes y no crea una autoridad paralela. `SimulatedInnerStateAuthority` continúa siendo la única autoridad que construye el estado interior simulado.

## Decisión M390.2 — Evaluación afectiva como adaptador subordinado

**Estado:** Implementada y pendiente de validación completa  
**Base:** M390.1 (9838 tests, Ruff limpio)

**Decisión:** incorporar `GovernedAffectiveEvaluator` como componente puro que transforma exclusivamente reportes certificados de M389.4, M389.5 y M389.8 en señales tipadas para M390.1. No se crea una nueva autoridad emocional: `SimulatedInnerStateAuthority` conserva la responsabilidad exclusiva de construir el snapshot interior. El evaluador no accede a conversación bruta, no persiste, no aprende, no modifica personalidad y no se integra todavía al runtime.

## Decisión M379 — Fundación unificada de organización personal

**Estado:** Aprobada

Se declara `PersonalOrganizationAuthority` como única fachada para la Fase IV. La decisión prioriza integrar agenda, tareas, recordatorios, objetivos, proyectos, notas y priorización existentes antes de crear nuevos componentes. Las autoridades internas conservan sus contratos; la nueva fachada no ejecuta, persiste ni modifica el runtime.

## Decisión M377 — Expresión adaptativa bajo una identidad estable

**Estado:** Implementado  
**Base:** M376 (9129 tests, Ruff limpio)

**Decisión:** conservar `StablePersonalityEngine` y `StablePersonalitySnapshot` como fundamento de identidad y rasgos estables, y formalizar `AdaptivePersonalityAuthority` como única autoridad de modulación expresiva. La autoridad sólo ajusta tono de entrega, detalle y estructura mediante señales explícitas y deterministas. No crea otra personalidad, identidad, agente, memoria, planificador, cerebro o runtime; tampoco aprende ni persiste preferencias.

## Decisión M376 — Archivo conversacional separado de memoria cognitiva

**Estado:** Implementado  
**Base:** M375 (9121 tests, Ruff limpio)

**Decisión:** formalizar `LongTermConversationAuthority` como única autoridad para archivar y recuperar registros conversacionales resumidos. Los registros conservan contexto estructurado y un resumen explícito, nunca el transcript bruto. `OfficialMemoryGateway` no es invocado: archivo conversacional y memoria cognitiva permanecen responsabilidades distintas. Persistencia de producción, resumen automático, LLM, búsqueda semántica, RAG e integración al runtime quedan fuera de alcance.

## Decisión M375 — Autoridad única de conversación contextual

**Estado:** Implementado  
**Base:** M374 (9113 tests, Ruff limpio)

**Decisión:** formalizar `ConversationContextAuthority` como única autoridad para crear, consultar, actualizar y cerrar el contexto conversacional inmediato. La autoridad reutiliza el modelo canónico `ConversationContext`, recibe `ConversationTurn` explícitos y mantiene estados aislados por conversación. La resolución básica de referencias es determinista y sólo usa entidades activas ya declaradas. Persistencia, historial completo, LLM, memoria de largo plazo, personalidad adaptativa e integración automática con el runtime quedan fuera de alcance.

## Decisión M374 — Sensores bajo la autoridad oficial de dispositivos

**Estado:** Cerrado  
**Base:** M373 (9102 tests, Ruff limpio)  

**Decisión:** ampliar `OfficialDeviceGateway` para admitir snapshots inmutables de sensores Android. No se crea una autoridad paralela. La capacidad exige un dispositivo móvil registrado con `android.sensors`; las observaciones permanecen sensibles, de solo lectura y no ejecutables. Listeners, polling, ubicación, acceso real al hardware, persistencia, automatización e integración cognitiva automática quedan fuera de alcance.

---

## Decisión M372 — Portapapeles bajo la autoridad oficial de dispositivos

**Fecha:** 2026-08-01  
**Base:** M371 (9081 tests, Ruff limpio)  

**Decisión:** ampliar `OfficialDeviceGateway` para admitir snapshots inmutables del portapapeles Android. No se crea una autoridad paralela. La capacidad exige un dispositivo móvil registrado con `android.clipboard` y conserva el contenido como dato sensible, de solo lectura y no ejecutable. La lectura real, escritura, limpieza, sincronización, persistencia e integración cognitiva automática quedan fuera de alcance.

## M367.3 — Project Knowledge Model

Decisión: reconciliar autoridades existentes de proyectos bajo `project_knowledge_model`; no crear store, planner ni runtime paralelo.

# ROBY XI.2 — integration_decision.md

## Decisión M370.1 — Estado Android bajo la autoridad oficial de dispositivos

**Fecha:** 2026-08-01  
**Base:** M369.7 (9060 tests)  
**Estado:** Aprobada  
**Decisión:** ampliar `OfficialDeviceGateway` para admitir observaciones normalizadas de estado Android. No se crea un gateway Android Device State separado. El agregado es inmutable, de solo lectura y no ejecutable; exige registro previo y declaración de `android.device_state`. La adquisición real, el transporte y cualquier integración cognitiva quedan fuera de este incremento.


> **Registro canónico de decisiones sobre integraciones externas**

## Decisión M365.3 — Frontera de transporte Android no operativa

**Fecha:** 2026-07-31  
**Base:** M365.2 (8731 tests)  
**Estado:** Aprobada  
**Decisión:** introducir un protocolo de transporte reemplazable que sólo describe disponibilidad y compatibilidad. M365.3 no incorpora operaciones de conexión, envío o recepción. Los adaptadores reales se añadirán en incrementos posteriores y permanecerán subordinados a la activación gobernada y a `ToolGatewayManager`.

## Decisión M360.0.d — Autoridad de planificación de la Fase II

**Fecha:** 2026-07-31  
**Base:** M360.0.c (8669 tests)  
**Estado:** Aprobada  
**Decisión:** conservar las decisiones anteriores como historial y establecer `docs/M360_0E_PHASE_II_MASTER_PLAN.md` como única autoridad de prioridades posteriores a la auditoría M360.0.

Calendar y Gmail no se consideran nuevas brechas. Vision y Desktop deben consolidarse antes de crear integraciones físicas. Android Bridge precede al Samsung Watch Gateway. MCP y Home Assistant deberán incorporarse como gateways gobernados, nunca como autoridades cognitivas paralelas.

## Decisión M348.1 — Primera brecha real

**Fecha:** 2026-07-30  
**Base:** M347.15 (8494 tests)  
**Estado:** Aprobada  
**Decisión:** Seleccionar Google Calendar como primera brecha real de la serie
M348.

## 1. Contexto

El inventario inicial consideró como candidatas:

- Calendario;
- correo electrónico;
- Home Assistant;
- Ollama / LLM local;
- MCP.

La inspección del proyecto mostró que Gmail y el proveedor LLM local ya poseen
implementación y gobernanza maduras. Por lo tanto, no deben tratarse como nuevas
brechas.

Las brechas reales restantes son:

1. Calendario con proveedor real.
2. Home Assistant.
3. MCP.

## 2. Decisión

Se selecciona **Google Calendar**.

ROBY ya reconoce la capacidad de calendario en su arquitectura. La serie M348
deberá completar el recorrido hacia un proveedor real sin crear otra autoridad
cognitiva ni otro gestor de herramientas.

## 3. Justificación

Google Calendar presenta:

- alto valor cotidiano para Carlos y Cristina;
- información estructurada;
- operaciones de lectura y escritura claramente delimitadas;
- reutilización potencial del patrón OAuth y de integración de Gmail;
- bajo riesgo de afectar el núcleo cognitivo;
- posibilidad de activación controlada;
- pruebas deterministas con dobles y validación manual separada;
- utilidad como patrón para integraciones posteriores.

## 4. Alternativas no seleccionadas

### Home Assistant

Se posterga porque su primera implementación requiere resolver múltiples clases
de dispositivos, estados, servicios, escenas, permisos y acciones sensibles.

### MCP

Se posterga porque es un protocolo transversal para exponer múltiples recursos y
herramientas. Conviene abordarlo después de estabilizar más integraciones
concretas.

### Gmail

No se selecciona porque ya está implementado y gobernado.

### Ollama / LLM local

No se selecciona porque ya existe un proveedor local compatible con OpenAI,
routing y controles de disponibilidad.

## 5. Autoridades a reutilizar

La integración deberá localizar y reutilizar, según corresponda:

- `ConversationContext`
- `ConversationStrategyPlanner`
- `ToolGatewayManager`
- registro canónico de capacidades;
- contratos existentes de acciones gobernadas;
- `DecisionTrace`;
- gobernanza de configuración;
- gobernanza OAuth y almacenamiento seguro de credenciales;
- políticas de consentimiento para operaciones de escritura;
- mecanismos de readiness, recuperación y observabilidad.

Esta lista deberá verificarse contra el código antes de M348.2. No autoriza a
crear equivalentes.

## 6. Componentes prohibidos

M348 no deberá crear:

- otro planner;
- otro núcleo cognitivo;
- otro gateway de conversación;
- otro gestor general de herramientas;
- otro sistema de credenciales;
- otro registro global de capacidades;
- una conexión directa entre planner y Google Calendar;
- una activación automática no gobernada;
- escritura en calendario sin consentimiento o política explícita.

## 7. Alcance siguiente

M348.2 deberá realizar el inventario técnico exacto de contratos existentes y
definir la extensión mínima requerida.

No deberá implementar todavía OAuth real ni llamadas de red si el contrato
mínimo no ha sido previamente validado.

## 8. Criterio de reversión

Esta decisión sólo podrá revisarse si la inspección de M348.2 demuestra que:

- el calendario ya está completamente integrado;
- existe una incompatibilidad arquitectónica no resoluble mediante extensión;
- el proveedor elegido exige romper una regla canónica;
- una nueva evidencia cambia materialmente el inventario.

Toda revisión deberá documentarse aquí y en `CHANGELOG_ARCHITECTURE.md`.


## Decisión M348.2 — Contrato o extensión mínima

**Fecha:** 2026-07-30  
**Estado:** Implementada y pendiente de validación completa

La inspección confirmó que Calendar ya está representado en `CapabilityKind`,
`ToolRequirement`, el planner y la preparación gobernada. No se crea una nueva
autoridad ni se modifica el núcleo cognitivo.

Se incorpora únicamente un contrato neutral del proveedor en
`infrastructure/calendar/calendar_contract.py`, compuesto por:

- `CalendarTimeRange`;
- `CalendarEvent`;
- `CalendarEventDraft`;
- `CalendarAvailability`;
- `CalendarProvider`.

El contrato cubre sólo las tres operaciones mínimas necesarias para la brecha
seleccionada: listar eventos, consultar disponibilidad y crear un evento.

Quedan expresamente fuera de M348.2:

- Google Calendar API;
- OAuth real;
- configuración;
- registro en `ToolGatewayManager`;
- llamadas de red;
- actualización o eliminación de eventos;
- persistencia de tokens;
- modificación de `.roby/credentials.json`.

M348.3 deberá implementar un adaptador de Google Calendar que satisfaga este
contrato sin filtrar tipos del SDK hacia el núcleo de ROBY.

## Resultado M348.3 — Adaptador del proveedor

M348.3 implementa el adaptador concreto `GoogleCalendarAdapter`, que satisface
el contrato `CalendarProvider` definido en M348.2.

El adaptador: 

- utiliza una fábrica inyectable para construir el cliente Google Calendar API v3;
- traduce modelos neutrales de ROBY a payloads Google y viceversa;
- mantiene los tipos del SDK fuera de las capas cognitivas;
- normaliza errores del proveedor;
- admite eventos con horario y de día completo;
- no realiza activación OAuth ni cableado de runtime.

La siguiente etapa, M348.4, deberá resolver configuración y activación controlada
reutilizando la gobernanza OAuth y de credenciales existente.

## 9. Ejecución de M348.4 — Configuración y activación controlada

M348.4 incorpora el runtime controlado de Google Calendar sin habilitar todavía
su uso conversacional.

La activación queda gobernada por:

- `ROBY_CALENDAR_ENABLED`;
- `ROBY_CALENDAR_ACCOUNT_FINGERPRINT` (opcional, valor por defecto `primary`);
- `ROBY_CALENDAR_ALLOW_INTERACTIVE_OAUTH` (deshabilitada por defecto);
- `GOOGLE_TOKEN_FILE` y `GOOGLE_CLIENT_SECRET_FILE`, leídos mediante la
  autoridad canónica de credenciales.

Estados oficiales:

- `disabled`: Calendar no fue habilitado;
- `degraded`: fue habilitado, pero falta configuración, credenciales válidas o
  scopes suficientes;
- `ready`: configuración completa y credenciales utilizables.

Scopes mínimos adoptados:

- `https://www.googleapis.com/auth/calendar.events`;
- `https://www.googleapis.com/auth/calendar.events.freebusy`.

El runtime se agrega al `RuntimeCompositionRoot`, pero no se conecta aún con el
planner, el diálogo ni el `ToolGatewayManager`. Esa conexión deberá realizarse
en un milestone posterior, con consentimiento explícito para operaciones de
escritura.

## 10. Ejecución de M348.5 — Errores, readiness y recuperación

M348.5 completa la frontera operativa de Calendar antes de su exposición al
planner o al `ToolGatewayManager`.

Se incorpora un diagnóstico neutral y libre de secretos que distingue:

- `disabled`: la capacidad no fue habilitada y no bloquea al resto de ROBY;
- `blocked`: Calendar fue habilitado, pero existe un impedimento operativo;
- `ready`: el proveedor puede utilizarse.

Los planes de recuperación son deterministas y siempre explícitos. Ningún plan
se ejecuta automáticamente durante el arranque. La recuperación de credenciales
reutiliza `GoogleOAuthDeploymentAdapter.activate()` y conserva sus políticas de
scopes, autorización interactiva y persistencia gobernada.

Las acciones posibles incluyen habilitar, configurar, autorizar, refrescar o
autorizar, conceder scopes, reintentar más tarde, revisar la solicitud o requerir
revisión manual.

La información de estado no contiene tokens, rutas privadas ni material de
credenciales. `.roby/credentials.json` permanece intacto.


## M348.6 — ToolGateway y planner

Calendar queda registrado detrás del gateway oficial con lectura controlada de eventos y disponibilidad. La escritura se declara para preservar el contrato futuro, pero permanece deshabilitada y requiere confirmación. El planner sólo recibe una capacidad `calendar` de lectura cuando el runtime está listo.

## M348.7 — Consulta conversacional completa

La capacidad de lectura de Calendar interpreta referencias temporales cotidianas
de forma determinista y timezone-aware. La resolución temporal permanece dentro
del interceptor conversacional y entrega exclusivamente `CalendarTimeRange` al
contrato neutral. No se agregan escrituras, automatismos ni una segunda autoridad
de Calendar.

## M348.8 — Decisión de escritura gobernada de Calendar

La creación de eventos usa un protocolo obligatorio de dos turnos: borrador y
confirmación explícita. El primer turno sólo interpreta, valida y comprueba
conflictos. El segundo revalida disponibilidad y recién entonces invoca el
provider-neutral `create_event`. El pendiente se aísla por propietario/sesión y
puede cancelarse sin efectos externos.

## M365.2 — Decisión de configuración y activación Android

Se amplía el contrato Android existente con un proveedor que transforma el árbol de configuración oficial ya cargado. No se añade un lector de archivos, almacén, gateway ni composition root alternativo. La política de activación sólo evalúa habilitación, protocolo, agente permitido y registro en `OfficialDeviceGateway`; incluso el estado `READY` conserva `executable=False`.


## M365.4 — Android Bridge Readiness, Authentication & Recovery

La readiness combina exclusivamente las evaluaciones gobernadas existentes. La autenticación es declarativa y no conserva secretos ni pruebas. La recuperación es un plan determinista, no un mecanismo operativo; no abre conexiones, no duerme y no reintenta.


## M365.6
El catálogo Android es declarativo, pasivo y no ejecutable. Su registro usa exclusivamente ToolGatewayManager.

## M365.7 — Android Bridge Capability Selection & Stabilization

La selección es descriptiva, no ejecutable y permanece detrás de las autoridades canónicas.

## M367.7 — Mental Model Stabilization

Decisión: integrar una auditoría de solo lectura sobre las autoridades M367. No se incorpora un nuevo modelo operativo ni se modifica el runtime.


## Decisión M371 — Notificaciones bajo la autoridad oficial de dispositivos

M371 amplía `OfficialDeviceGateway` en lugar de crear una autoridad paralela. La capacidad acepta snapshots inmutables sólo cuando el dispositivo móvil está registrado y declara `android.notifications`. El contenido permanece descriptivo, no ejecutable y sin transporte real. Ninguna observación autoriza abrir, responder, descartar, marcar, persistir ni alimentar automáticamente otras capacidades cognitivas.


## Decisión M373 — Archivos bajo la autoridad oficial de dispositivos

**Fecha:** 2026-08-01  
**Base:** M372 (9091 tests, Ruff limpio)  
**Estado:** Implementada, pendiente de validación local completa  
**Decisión:** ampliar `OfficialDeviceGateway` para admitir snapshots inmutables de metadatos de archivos Android. No se crea un gateway paralelo. La capacidad exige un dispositivo móvil registrado con `android.files`; conserva toda observación como sensible por defecto, de solo lectura y no ejecutable. El acceso físico, contenido, mutaciones, indexación, persistencia e integración cognitiva automática quedan fuera de alcance.

## Decisión M378 — Explicación pública sobre decisiones existentes

**Fecha:** 2026-08-01  
**Base:** M377 (9137 tests, Ruff limpio)  
**Estado:** Implementada, pendiente de validación local completa  
**Decisión:** incorporar `IntelligentExplanationAuthority` como única autoridad para componer explicaciones públicas a partir de hechos ya decididos y evidencia explícita. La autoridad consume el perfil adaptativo M377 para ajustar detalle y estructura, pero no vuelve a decidir, no llama a un LLM, no revela razonamiento interno privado, no inventa causas y no modifica memoria, planificación, políticas, personalidad ni runtime.

## Decisión M380 — Trabajo organizado bajo una única fachada

**Fecha:** 2026-08-01  
**Base:** M379 (9153 tests, Ruff limpio)  
**Decisión:** incorporar una vista canónica de objetivos, proyectos y tareas subordinada a `PersonalOrganizationAuthority`. La integración conserva las autoridades existentes y expresa únicamente relaciones trazables. No introduce CRUD, persistencia, ejecución, memoria, LLM, agentes, planificadores paralelos ni cambios de runtime.

## Decisión M390.1 — Fundamento del Mundo Interior Simulado

**Fecha:** 2026-08-07  
**Base:** M389.8 certificada (9824 tests, Ruff limpio)  
**Estado:** Implementada, pendiente de validación local completa  
**Decisión:** incorporar `SimulatedInnerStateAuthority` dentro de `core.cognitive_maturity` como única autoridad para construir snapshots de estado afectivo funcional simulado. La autoridad acepta exclusivamente señales codificadas con procedencia y categoría epistemológica existente, no reanaliza contenido ni crea otro clasificador, personalidad, memoria o cerebro. Los conflictos entre señales permanecen explícitos y el snapshot declara que la representación es simulada, sin afirmar consciencia, experiencia subjetiva o emoción real. M390.1 no se cablea al runtime, no persiste, no aprende, no modifica planificación, personalidad o permisos y no ejecuta acciones.


## Decisión M394.1 — Registro Gobernado de Recursos Externos

**Fecha:** 2026-08-08  
**Base:** M393.8 certificada (10208 tests, Ruff limpio, baseline M361 reproducible)  
**Decisión:** iniciar M394 con una capacidad estrictamente registral y una única autoridad `ExternalResourceRegistryAuthority`. El registro sólo declara recursos conocidos y referencia, sin absorber la autoridad de `OfficialDeviceGateway` ni de otras capacidades existentes. M394.1 no descubre, conecta, autoriza, activa, persiste ni ejecuta recursos; no modifica `.roby/credentials.json`, runtime ni la posición contractual de `CanonicalCognitiveCore(`.

## Decisión M394.2 — Identidad Gobernada de Recursos Externos

**Decisión:** ampliar `ExternalResourceRegistryAuthority` en lugar de crear una autoridad de identidad separada. `ExternalResourceIdentity` proporciona una clave canónica estable y resoluble, con compatibilidad hacia atrás para registros M394.1. La identidad permanece puramente declarativa: no modifica `OfficialDeviceGateway`, `.roby/credentials.json`, runtime ni la posición contractual de `CanonicalCognitiveCore(`, y no introduce estados operacionales más allá de `known`.

## Decisión M394.3 — Estado Gobernado de Recursos Externos

**Decisión:** ampliar la misma `ExternalResourceRegistryAuthority` con estado descriptivo en lugar de crear un gestor de estado paralelo. M394.3 admite únicamente `known`, `available` y `unavailable`; `declare_state()` actualiza representación interna sin I/O ni efectos externos. Se preservan `OfficialDeviceGateway`, `.roby/credentials.json`, el runtime existente y la posición contractual de `CanonicalCognitiveCore(`.

## Decisión M394.4 — Autorizaciones Gobernadas de Recursos Externos

**Fecha:** 2026-08-08  
**Base:** M394.3 certificada (10243 tests, Ruff limpio, baseline M361 reproducible)  
**Decisión:** ampliar la misma `ExternalResourceRegistryAuthority` con decisiones explícitas de autorización en lugar de crear un gestor paralelo. `unknown` representa ausencia de decisión; `authorized` y `denied` requieren evidencia explícita y se conservan en historial inmutable y revisionado. M394.4 no autentica, conecta, activa ni ejecuta recursos, no modifica `OfficialDeviceGateway` ni `.roby/credentials.json`, y preserva la posición contractual de `CanonicalCognitiveCore(`.

## Decisión M394.5 — Conectividad Gobernada de Recursos Externos

**Base:** M394.4 certificada (10255 tests, Ruff limpio, baseline M361 reproducible)  
**Decisión:** ampliar la misma `ExternalResourceRegistryAuthority` con perfiles descriptivos de conectividad en lugar de introducir un gestor de conexiones. `configured` significa sólo que existe una descripción gobernada de transporte y endpoint; M394.5 no abre conexiones, no autentica, no escanea red, no activa recursos y no modifica `OfficialDeviceGateway`, `.roby/credentials.json` ni la posición contractual de `CanonicalCognitiveCore(`.


## Decisión M394.6 — Auditoría Gobernada de Recursos Externos

**Base:** M394.5 certificada (10268 tests, Ruff limpio, baseline M361 reproducible)  
**Decisión:** ampliar la misma `ExternalResourceRegistryAuthority` con un historial de auditoría explícito, inmutable y append-only. `record_audit_event()` conserva evidencia declarada sin modificar el recurso, sin reloj propio, persistencia, I/O ni gestores paralelos. Se preservan `OfficialDeviceGateway`, `.roby/credentials.json` y la posición contractual de `CanonicalCognitiveCore(`.

## Decisión M394.7 — Recuperación Segura de Recursos Externos

**Base:** M394.6 certificada (10279 tests, Ruff limpio, baseline M361 reproducible)  
**Decisión:** ampliar la misma `ExternalResourceRegistryAuthority` con recuperación cognitiva de solo lectura en lugar de crear un gestor de restauración. `recover_resource_snapshot()` reconstruye el conocimiento gobernado actual y referencia la auditoría disponible; `validate_recovery()` detecta snapshots obsoletos. M394.7 no persiste snapshots, no restaura hardware, no conecta, no autentica, no activa ni ejecuta recursos, no modifica `.roby/credentials.json` y preserva la posición contractual de `CanonicalCognitiveCore(`.


## Decisión M394.8 — Estabilización Integral de Recursos Externos

**Base:** M394.7 funcionalmente validada (10291 tests; corrección de orden de imports aplicada antes del cierre)  
**Decisión:** cerrar la serie M394 sin añadir capacidad productiva nueva. Se congela la API pública de `ExternalResourceRegistryAuthority`, se consolidan los contratos de M394.1–M394.7 y se preservan `OfficialDeviceGateway`, `.roby/credentials.json` y `CanonicalCognitiveCore(`. Tras la certificación local de M394.8 se realizará una auditoría arquitectónica integral antes de iniciar una nueva etapa.

## M396.2 — Decisión de integración

Se aprueba `core.residence_domain` como paquete de modelos puro y subordinado a la
constitución M396.1. No se conecta todavía a `runtime_root_factory`, Presence,
`OfficialDeviceGateway`, `ExternalResourceRegistryAuthority`, `device_continuity` ni
`context_transfer`. La ausencia de wiring es intencional: M396.2 establece lenguaje de
dominio antes de integrar evidencia productiva. No se crea una nueva autoridad.

## M396.3 — Decisión de integración: Authority Preservation

No se integra Residence en `runtime_root_factory` ni se crea una autoridad nueva.
Se preservan `ExternalResourceRegistryAuthority`, `OfficialDeviceGateway`,
`OfficialPresenceRuntimeGateway`, `OfficialContextContinuityRuntimeGateway`,
`CognitiveAuthorityMap`, capability routing y `ResidentComponentRegistry`. Residence
solo aporta evidencia contextual y deberá ser consumido, cuando corresponda, desde
fronteras gobernadas existentes o futuras explícitamente aprobadas.

## M396.4 — Explicit Admission

Decisión: implementar I04 dentro del modelo declarativo existente y no mediante una
nueva autoridad. La observación queda separada de la pertenencia: candidatos y records
de decisión son evidencia; una residencia extendida sólo puede representarse con
proveniencia explícita de admisión. Sin wiring de runtime en este incremento.


## Decisión M396.5 — Stable Residence Identity

Se preserva `ResidenceId` como identidad canónica y se añade únicamente un anchor de
proveniencia inmutable. No se deriva identidad desde red/hardware y no se cablea el
dominio Residence al runtime ni a las autoridades existentes.

## Decisión M405 — Information Classification Formal Closure

**Fecha:** 2026-08-11  
**Base:** M405.1 certificada (**11,161 tests**, Ruff limpio, M361 sincronizada)  
**Decisión:** cerrar Information Classification como foundation neutral y subordinada. `InformationClassification` conserva exclusivamente el vocabulario canónico de sensibilidad y M403 lo consume mediante una policy outbound opcional sin modificar `GovernedSyncEnvelope`, codecs ni transporte M397. No se crea una autoridad/manager/classifier global. Receiver-side enforcement queda diferido hasta que exista un consumidor cross-residence real que necesite transportar classification; esa futura necesidad deberá reabrirse mediante un gate específico de schema/compatibilidad y no autoriza M405.2 por continuidad.

## M406.1 — Decisión de integración Web Panel

**EXTENDER MÍNIMAMENTE / GO.** Se crea una proyección read-only de aplicación y un adapter HTTP stdlib local. No se crea autoridad Web, segundo runtime, nuevo composition root ni reutilización de M398. La expansión a HTML, LAN, remoto o control requiere gates separados.

## M406.2 — Decisión de integración Human Dashboard

**EXTENDER PRESENTACIÓN / GO.** Se añade únicamente un renderer HTML server-side y `GET /` al `LocalWebPanelHttpService` existente. El renderer consume `GovernedWebPanelSnapshot`; no se agrega otra API, source, authority, runtime o lifecycle. Se preservan `127.0.0.1`, read-only, M405 classification, `/api/status` y las exclusiones de M406.1. JavaScript/polling, LAN/remoto, autenticación y control permanecen fuera de alcance.

## Decisión M406 — Governed Web Panel Formal Closure

**Fecha:** 2026-08-11  
**Base:** M406.3 certificada (**11.199 tests**, Ruff limpio, M361 sincronizada)  
**Decisión:** cerrar M406 para el alcance local, read-only y productivamente integrado. M406 conserva ownership únicamente de proyección/exposure/presentación; los facts siguen perteneciendo a sus authorities canónicas y el lifecycle permanece subordinado al único `OfficialROBYRuntime`. No se autoriza M406.4 por continuidad. LAN, autenticación/TLS, remoto, streaming y control requieren gates futuros separados.

## Decisión M407.2 — Conectividad como task opcional del proceso residencial existente

**Decisión:** reutilizar `ResidentRuntimeService` y el entrypoint M402.3 para alojar M407.1
como una única task opt-in. Se rechaza crear otro runtime, supervisor o authority. La
activación exige configuración completa y dependencias M396/M397 gobernadas; la baseline no
contiene un autenticador productivo concreto y M407.2 no sustituye esa ausencia con confianza
implícita. Los failure facts de carrier continúan perteneciendo a M398 y deben suministrarse
explícitamente al wiring antes de recovery.

## M408.1 — Decisión de integración

**GO cerrado para foundation software mínima de Remote Presence.** La única capability
introducida es still-image on-demand, gobernada antes y después de la captura y entregada
como media `SENSITIVE` transitoria. M394/M397/M404/M405/M61/M63 conservan sus authorities y
M398 no se modifica. Conversación, Web Panel, red remota pública/privada y deployment físico
permanecen gates posteriores separados.

## M409.1 — Integration decision

Integrar el accepted-carrier/session handoff en `application.residential_remote_presence` como composición subordinada. No modificar M398 ni M408.2. El Session Host posee lifecycle físico, single-reader y write serialization; M397 continúa autenticando/admitiendo la sesión y el execution adapter implementa el port M408.2 sobre el mismo carrier. No añadir segundo socket, nueva authority, session persistence, VPN ni exposición pública.

## Post-M409.1 — Shared Co-Owner Conversation Context — Integration Decision

GO implementado como extensión mínima de `IdentityContextAccessGate`: una decisión específica para contexto conversacional compartido y la decisión histórica separada para contexto privado. `EndToEndLocalConversation._recent_context()` migra a la decisión shared; memory enrichment/recording permanece sobre `private_context_allowed`. No se autoriza nueva authority ni ampliación de privacidad fuera de la sesión compartida coincidente.

## Post-M409.1 — Conditional Action Routing — Integration Decision

GO implementado como refinamiento local del PRIMARY `ExecutiveConversationPlanner`. La sintaxis condicional por sí sola deja de ser criterio suficiente: solo un consecuente con efecto operativo explícito puede abrir un plan. Consecuentes hipotéticos, epistémicos o puramente conversacionales producen `None` y preservan el fallback oficial. No se crea classifier/authority nuevo, no se altera la precedencia del registry y la autorización/risk de ejecución permanece intacta.

## Post-M409.1 — Diagnostic Session Isolation — Desktop Existing-Runtime Injection Seam + Guide v2 Isolated Harness

**Decision:** reuse the existing `build_official_runtime_from_environment(local_conversation=...)` seam and expose it minimally through `build_unified_desktop_app(*, local_conversation=None)`. Diagnostic sessions are created only by the external harness before Desktop composition, with the shared owner preserved and one session per Guide v2 case/run. The production call remains argument-free. No `.env` or household identity mutation, `coowners-main` reset, new journal, new session authority, provider change or cognitive behavior change is authorized.

## Post-M409.1 — Weather Intent Routing — Integration Decision

GO implementado como refinamiento mínimo de `WeatherConversationInterceptionPort.is_weather_request()`. `weather.household` conserva su authority, adapter y precedencia pre-provider; vocabulario meteorológico aislado dentro de proposiciones deja de ser criterio suficiente. Se preservan peticiones explícitas, pronóstico, elipsis cortas y formas ambientales históricas. No se autoriza nuevo classifier, cambio de registry, provider, journal, reasoning ni Evidence Revision.


Regression fix autorizado dentro del mismo ownership: `cómo viene` ya no es señal Weather suficiente sin `clima`/`tiempo`/`pronóstico`. Current Affairs permanece sin cambios; no se añade classifier ni se altera precedencia.

## Post-M409.1 — Conversational Commitment Productive Consumption + Governed Cognitive System Guidance v1 — Integration Decision

**Decisión:** integrar por reutilización exacta de instancias, no por duplicación. `runtime_root_factory` conecta `conversation_intelligence_runtime.adaptive/repair/grounding/commitment/consolidation` a los seams M196–M200 ya soportados por `RuntimeCompositionRoot`. El contexto cognitivo gobernado se conserva en el prompt textual de compatibilidad y además se expresa mediante `LLMRequest.system_prompt`; `messages` permanece intacto. El provider local compone su system style configurado con la guía del request. Se rechazan nueva autoridad, post-provider regex/rewrite, expansión de permisos o ejecución para hacer verdaderas promesas del modelo.

## Post-M409.1 — Referential Person-Role Grounding — Turn-Local Evidence + M198 Productive Consumption v1 — Integration Decision

**Decision:** integrate as subordinate evidence + existing M198 productive projection.

- Canonical grounding authority remains M198.
- The evidence producer is deterministic, transient, read-only and non-authoritative.
- Identity declarations defer to the existing identity flow; ambiguous pronouns abstain.
- No persistence, person creation, relationship inference, memory, retrieval, LLM parsing, execution or new registered capability is introduced.
- Productive guidance reuses the already-governed cognitive system-guidance path.

## Post-M409.1 — M198 Evidence-Bounded Conversational Elaboration — Productive Guidance v1 — Integration Decision

**Decision:** extend only the existing M198 productive projection. `ConversationGroundingAssessment`, its states/actions and M198 ownership remain unchanged. `ConversationalGroundingRuntimeContributor` adds one universal evidence-bounded guidance line through the already-certified cognitive system-guidance path. Unsupported contextual additions must not be asserted as facts; hypotheses, possibilities, uncertainty, questions and reasonably derived safety advice remain valid when explicitly modalized. No new evidence producer, runtime interceptor, post-provider checker, parser, memory, persistence, execution or authority is introduced.

Colección candidata tras el incremento: **12.002 tests**; promoción oficial sujeta a `ruff check .` + `pytest -q` en el entorno local certificado.

## Post-M409.1 — Effective Provider Payload Observability Contract v1

**Base:** M198 Semantic Strength v1 (12014 tests, Ruff limpio)

**Decisión:** extender la observabilidad existente del provider para distinguir explícitamente el request estructurado pre-adapter del payload efectivo post-adapter. `LocalProviderRuntimeAdapter` produce un snapshot no sensible y `GovernedProviderExecutionAdapter` lo conserva en el resultado para Development Console / Guide v2. No se modifica M198, routing, policy, contenido conversacional ni autoridad cognitiva; no se registran secretos ni contenido adicional.

## Post-M409.1 — Guide v2 I–L Diagnostic Extension — Integration Decision

**Decision:** GO sólo para extensión diagnóstica. Añadir I–L al `CASES` del harness existente, preservar D–H sin cambios y reutilizar la misma composición Desktop, aislamiento por sesión y observabilidad post-adapter. I–L debe medir significado conversacional, no frases literales, y sus resultados se clasificarán como PASS, quality/style, provider variance, contract gap o capability gap antes de cualquier implementación. No se autoriza modificar M198, routing, memoria, reasoning, provider policy ni crear una nueva authority.

## Post-M409.1 — Governed Complex Decision Reasoning Foundation v1 — GO / IMPLEMENTED FOUNDATION ONLY

Audit demonstrated a narrow representational gap in M391.6: governed advisory could combine organization/scenario/causal signals and explicit option preference, but could not preserve explicit multicriterion structure, hard constraints, criterion-specific uncertainty, trade-offs or criterion-level provenance without flattening them into existing signals.

The approved implementation closes only that gap through `core/governed_complex_decision_reasoning.py`. It reuses `GovernedDecisionOption`, remains subordinate to `unified_cognitive_coordination` / `CanonicalDecisionFacade`, and adds no authority or productive wiring. Comparison is non-additive: hard constraints and insufficiency precede Pareto dominance; explicit criterion importance may resolve a trade-off lexicographically, while absent/equal importance and non-dominance preserve review.

NO-GO remains in force for gateway/runtime integration, automatic criterion extraction, inferred weights/preferences, persistence, Memory/Learning writes, World Model or Planning mutation, organization/task mutation, evidence acquisition, tools/network, execution/actions, permissions and background behavior. Productive integration requires a separate Audit → Contract / Go-No-Go after Foundation certification.

## Explicit Complex Decision Criteria Evidence Foundation v1 — integration decision

Decision: **FOUNDATION-ONLY GO / PRODUCTIVE INTEGRATION DEFERRED**.

The demonstrated GCDR productive-integration gap is narrowed by adding deterministic current-turn criterion evidence only. The Foundation extracts explicit criteria, explicit mandatory-criterion declarations and explicit pairwise importance relations with exact source provenance. It does not produce option×criterion assessments and therefore does not make GCDR productively callable from conversation.

`OfficialConversationGateway`, `CanonicalDecisionFacade`, M391.6 and the existing explicit-deliberation productive wiring remain unchanged. The next integration decision must audit how explicit or already-governed option×criterion evidence can be linked without inference, evidence fabrication or authority gain.

## Option/Criteria Certified Linkage Foundation v1 — integration decision

GO implemented only for pure certified linkage. No productive gateway/facade/GCDR integration is authorized by this increment. A separate Audit / Contract / Go-No-Go is required before any adapter creates `GovernedOptionCriterionAssessment` from certified bindings.

## Criterion Importance Compatibility Foundation v1 — integration boundary

The compatibility Foundation is non-productive and does not call GCDR. It may preserve certified ordinal criterion-importance relations, but must emit no synthetic cardinal importance, rank, normalized weight, inferred transitive relation, or utility value. Productive composition remains NO-GO until a separate Complete Input Assembly Audit / Contract / Go-No-Go.

## Post-M409.1 — GCDR Complete Input Assembly v1

Complete-input assembly is derivational and read-only. It may only combine already-certified option adaptation, explicit criterion evidence, assessment adaptation and criterion-importance compatibility with matching provenance. It must preserve `explicit_importance=None`, keep ordinal importance separate, require the complete option×criterion matrix, and must not call GCDR or productive runtime/facade/gateway paths. Productive execution requires a later explicit Go/No-Go.

## Post-M409.1 — Productive GCDR Advisory Wiring v1 — GO / GATEWAY DEFERRED

Decision: GO for a minimal productive advisory wiring that consumes only a certified complete GCDR assembly and delegates to the existing governed complex-decision reasoner. The wiring may expose the resulting structured advisory report with end-to-end lineage and no new authority.

Gateway decision: DEFER / NO-GO in this increment. Static contract review demonstrated that the closed explicit-deliberation producer requires the whole current turn to match its bounded grammar, while explicit criteria and option×criterion evidence require additional text. Therefore no currently certified single current turn can activate the full chain without relaxing a closed parser or introducing multi-turn/context resolution. `OfficialConversationGateway` remains unchanged. The next required front is Explicit Complex Decision Intake/Envelope — Audit → Contract / Go-No-Go.

## Advanced Capability 3A — Governed Information Scale Benchmark

**Estado:** Implementado; pendiente de validación global en el entorno oficial  
**Base:** 12.517 tests + Ruff limpio

**Decisión:** certificar escala antes de optimizar. Se incorpora un benchmark diagnóstico en `scripts/advanced_capability_3a_scale_benchmark.py` que reutiliza exclusivamente la cadena gobernada existente de fuentes, query contract/executor, normalización y relevancia. Se preserva el límite productivo de 100 items por query y la escala se recorre por chunks bounded. No se crea `HighScaleProcessor`, nueva authority, storage, paralelismo, cache productiva, red, providers, Memory, Learning, world-model ni acciones. La primera corrida diagnóstica alcanzó 50.000 items con provenance íntegra y recall 5/5; el resultado queda ligado al entorno registrado y no constituye una garantía de escala ilimitada.

## Advanced Capability 4B — Decisión de integración

Se aprueba únicamente una evaluación diagnóstica independiente. Corpus y ground truth
se almacenan como datos versionados; un runner read-only produce observaciones sin leer
respuestas esperadas y un scorer separado realiza la comparación. Se rechaza cualquier
cambio productivo de reasoning, nueva authority, aprendizaje durante la prueba o tuning
automático.

## Reconciliación actual — retiro de autoridad histórica M375

**Decisión vigente:** la implementación fundacional
`core.contextual_conversation:ConversationContextAuthority` queda retirada de la
arquitectura ejecutable. La decisión M375 original se conserva arriba como
historia y no gobierna el estado actual.

La continuidad contextual operacional actual reside en
`app.context_continuity_runtime:OfficialContextContinuityRuntimeGateway`, con
`core.conversational_context_continuity`, curación y sanitización como seams
inferiores. `ConversationContext` permanece como contrato compartido actual.

No se crea otra autoridad, store, persistencia ni runtime. Esta reconciliación
sustituye únicamente la residencia/autoridad histórica M375; no reescribe su
evidencia histórica.


## Reconciliación actual — retiro de autoridad global histórica M378

**Decisión vigente:** la implementación fundacional
`core.intelligent_explanations:IntelligentExplanationAuthority` queda retirada
de la arquitectura ejecutable. La decisión M378 original se conserva como
historia y no gobierna el estado actual.

La explicabilidad actual es propiedad de la autoridad fuente que produjo la
decisión, estado o resultado explicado. Las superficies especializadas de
Governed Reasoning, Cognitive Planning, Controlled Autonomy y Trust conservan
sus límites y no se unifican bajo una nueva autoridad global. Una capa de
presentación puede estructurar evidencia explicativa explícita, pero no volver a
decidir, inventar evidencia/razones, ocultar incertidumbre ni adquirir autoridad
de ejecución, persistencia, memoria o aprendizaje.

## M378.1 — CCI-08 source-owned explainability certification evidence reconciliation

Decision: reconcile the diagnostic CCI-08 evidence after retirement of the historical global M378 explanation authority. CCI-08 remains a by-design boundary proof and must not be interpreted as productive Adaptive Personality -> explainability wiring. Current evidence combines the bounded adaptive-delivery contract with a source-owned explanation surface derived from immutable canonical decision evidence. No production bridge or new authority is authorized by this decision.


## Decisión de reconciliación M376 — retiro de archivo conversacional histórico no realizado

**Estado:** Implementado / pendiente de certificación del propietario

**Decisión:** la decisión histórica M376 se conserva como trazabilidad, pero ya no representa autoridad current. `LongTermConversationAuthority` nunca alcanzó residencia productiva, persistencia de producción ni integración al runtime y se retira sin reemplazo. El journal conversacional operacional, Living Conversation y Cognitive Memory conservan responsabilidades separadas. Ninguna conversación o resumen se admite automáticamente en Memory; `OfficialMemoryGateway` continúa como autoridad durable existente.

## Decisión de reconciliación documental post-M376

**Estado:** CLOSED / CERTIFIED — owner baseline **12,513 PASS · 0 FAIL · Ruff clean**.

**Decisión:** la certificación del propietario cierra formalmente el retiro M376 y actualiza la metadata documental current. Las baselines históricas de hitos anteriores se conservan como trazabilidad y no prevalecen sobre Current Truth. Esta reconciliación no crea ni mueve autoridades, no modifica runtime, persistencia, Memory, Living Conversation ni el journal conversacional.


## Post-M376 — M17/M19 legacy auxiliary foundation retirement

A governed reachability/genealogy review confirmed that the historical M17 Event Publisher and M19 Memory Pipeline lost all productive consumers with the retirement of `core.roby`. The disconnected modules and their direct historical tests were retired without replacement. Existing current event/observability and Cognitive Memory authorities remain unchanged; conversation occurrence does not imply automatic Memory admission. Historical milestone and audit evidence is preserved. Status: **CLOSED / CERTIFIED — owner baseline 12,508 PASS · 0 FAIL · Ruff clean**.


## Post-M17/M19 — M27/M28 Agent Runtime / Agent Loop legacy execution retirement

**Estado:** CLOSED / CERTIFIED — owner baseline **12,487 PASS · 0 FAIL · Ruff clean**; certified input baseline **12,508 PASS · 0 FAIL · Ruff clean**.

**Decisión:** retire the disconnected M27 `AgentRuntime` and M28 `AgentLoop` execution lineage, including the M32 LLM and M40 CognitivePipeline bridges only at the AgentLoop boundary. Preserve `LLMService`, `ProviderRouter`, and `CognitivePipeline` as independent compatibility/architectural contracts. The official runtime remains the existing Runtime Composition Root/governed runtime lineage; no replacement execution authority is created.


## Post-M27/M28 documentary certification reconciliation

Owner certification closed the M27/M28 Agent Runtime / Agent Loop legacy execution lineage retirement at **12,487 PASS · 0 FAIL · Ruff clean**. Current baseline/status metadata was synchronized across Current Truth, architecture rules, Master Capability Registry and mirror, Cognitive Inventory master guide, Vision, decision ledger, changelogs, and the M27/M28 validation record. Historical milestone baselines remain unchanged. No production code, tests, runtime wiring, authority, persistence, or compatibility surface changed in this documentary reconciliation.

## Post-M27/M28 — M17-era generic trace contract residue retirement

**Estado:** CLOSED / CERTIFIED — owner baseline **12,488 PASS · 0 FAIL · Ruff clean**; certified input baseline **12,487 PASS · 0 FAIL · Ruff clean**.

**Decisión:** retire only the disconnected historical `core.tracing` generic
`TraceRecorder` / `NullTraceRecorder` contract and the unused
`tests/fakes/fake_trace_recorder.py` fixture. Preserve the current productive
`core.operational_trace_model` lineage unchanged. No replacement recorder,
adapter, manager, registry, authority, runtime path, or compatibility shim is
created. The M17 milestone remains byte-identical historical evidence.


## Post-M17-era Trace — M22 standalone cache contract retirement

**Estado:** CLOSED / CERTIFIED — owner baseline **12,483 PASS · 0 FAIL · Ruff clean**.
Certified input baseline: **12,488 PASS · 0 FAIL · Ruff clean**. Owner result:
**12,483 passed in 263.92s**.

**Decisión:** retire the disconnected historical `core.cache` standalone M22
contract and its six direct component tests. Reconcile the earlier provisional
preservation guardrail. Preserve capability-local caches and Working Memory under
their existing owners; they are not M22 replacements. Do not create a global cache
authority, manager, registry, store, writer, adapter or compatibility shim.

## Post-M22 — M391.8 historical closure diagnostic executable residency retirement

**Estado:** IMPLEMENTED / PENDING OWNER CERTIFICATION. Certified input baseline:
**12,483 PASS · 0 FAIL · Ruff clean**. Expected owner collection: **12,469**.

**Decisión:** retire only the disconnected executable M391.8 closure diagnostic
and its 15 self-contained certification tests. Preserve M391.1–M391.7 current
capability surfaces, M390.8 and historical M391.8 evidence unchanged. The
historical closure invariants remain valid but do not require permanent executable
diagnostic residency. No replacement evidence authority, manager, registry,
coordinator, runtime service, store, writer or persistence path is authorized.


## Living Conversation runtime neutral projection contract reconciliation

Reconciled the M105/M190/M253 runtime seam without authority succession or physical package movement. M190 now consumes immutable neutral `LivingConversationRuntimeProjection` evidence; M253 returns that typed projection instead of a productive `SimpleNamespace`; canonical M105 evidence can project through a pure adapter. Stable Personality remains distinct from M105, explicit-only activation is preserved, and no new authority/store/registry/persistence/runtime is introduced. Status: **IMPLEMENTED / PENDING OWNER CERTIFICATION**; certified input **12,469 PASS · 0 FAIL · Ruff clean**; expected owner collection **12,471**.


## M367 historical inventory retirement — contract reconciliation decision

**Decision:** retire only M367.2/.3/.4/.5/.7 executable inventory/diagnostic surfaces after re-pointing current contracts to existing owners. Preserve M367.1 because its surface was evolved by M391/M392 into the current World Model façade, and preserve M367.6 because Priority Reasoning remains productively used. M368.1 remains the single PlanningFoundation authority; M379 personal GOALS reuse `HouseholdGoalManager`; CCI-03 uses the current MentalModel causal path. No replacement umbrella authority, registry, manager, store, persistence or Composition Root is permitted. Status: **IMPLEMENTED / PENDING OWNER CERTIFICATION** from certified input **12,471 PASS · 0 FAIL · Ruff clean**.


### Post-M409.1 method-analysis productive-projection retirement
Inspection of the certified 12,410 baseline confirmed zero productive Python consumers for the app-level outcome-association, effectiveness-awareness, and comparative-awareness projection wrappers. The wrappers and their positive historical tests are retired; source Foundations remain under `core.governed_reasoning`. No other productive-consumption surface is included.


## Post-M409.1 reasoning-quality productive-projection retirement

The historical app-level Reasoning Quality productive projection was retired after
canonical carrier residency and import-boundary reconciliation. Current authority
remains in `core.governed_reasoning`; no replacement authority was created.

## CIH certification decision — canonical reasoning seam into Living Companion

Decision: **CERTIFIED / CLOSE THE SEAM RESIDUAL**.

Owner full gate established **12,506 PASS · 0 FAIL · Ruff clean**. The existing canonical
`GovernedReasoningSource` is now composition-injected into `LivingCompanionRuntime`.
No new authority, permission, persistence path, Memory/Learning writer, executive autonomy
or composition root is introduced.

Do not reopen this seam on the basis of the remaining semantic abstention. That is a
separate residual: canonical reasoning may abstain when governed evidence is insufficient.
Future work must prove that residual causally before any additional RED or surgery.



## Post-12.648 longitudinal usefulness closure decision

Decision: **CLOSE the demonstrated longitudinal-intellectual-usefulness integration
residual at the current bounded contract.**

The accepted architecture preserves Cognitive Memory as recall authority,
`governed_reasoning` as semantic admission/reconstruction authority, an external bounded
adapter as zero-authority productive transport, and Composition Root as wiring only. The
protected reasoning runtime is not extended. No further product surgery is authorized for
this residual after Owner certification at **12,648 PASS · 0 FAIL · Ruff clean**.

This decision does not authorize positive-SAME identity, exact prior-state restoration,
synthetic evidence, durable reasoning history, cumulative autonomous learning,
metacognitive self-modification, initiative, Planning or Execution.
