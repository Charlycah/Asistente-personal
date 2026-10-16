# ROBY XI.2 — D:\Roby Explicit Owner Development History Consultation
## PRE-RED Reconciliation

## 1. Estado de entrada

Baseline Owner-certified:

- `13373 passed`;
- Ruff clean;
- `GOVERNED_DEVELOPMENT_HISTORY_SOURCE: CLOSED / OWNER-CERTIFIED`;
- `DevelopmentHistorySourceAdapter` productivo y read-only;
- runtime reachability de Development History todavía no productiva.

Este bloque es exclusivamente de reconciliación PRE-RED.

`PRODUCT_CHANGE: NONE`

`TEST_CHANGE: NONE`

## 2. Regla de precedencia

Se mantiene:

`CURRENT EXECUTABLE TRUTH + LATEST OWNER GATE > STALE HISTORICAL STATUS LABEL`

Y:

`INVENTORY BEFORE SURGERY -> REUSE PROOF -> RESIDUAL -> CONTRACT -> RED -> GREEN`

No se crea una nueva autoridad cuando existe una frontera canónica reutilizable.

## 3. Residual heredado

La reconciliación anterior seleccionó:

`EXPLICIT_OWNER_DEVELOPMENT_HISTORY_CONSULTATION_ADMISSION_AND_PRESENTATION`

La fuente filesystem ya resuelve:

`configured root -> bounded discovery -> candidate -> explicit candidate id`
`-> selected-source revalidation -> bounded historical read -> observation`.

Lo ausente es reachability conversacional explícita.

## 4. Autoridad de entrada conversacional

`OfficialConversationGateway` sigue siendo la única frontera oficial de los turnos
interactivos.

El runtime compuesto entrega las solicitudes operacionales al
`OfficialRuntimeCapabilityRegistry`, que ya funciona como interceptor oficial de
capabilities conversacionales.

Por tanto Development History no necesita un segundo conversation gateway.

Decisión:

`CONVERSATION_ENTRY_AUTHORITY: EXISTING / UNCHANGED`

`NEW_CONVERSATION_GATEWAY: FORBIDDEN`

## 5. Precedente local de selección y follow-up

`GovernedLocalLibraryConversationInterceptionPort` demuestra un patrón productivo
válido para una capability local Owner-driven:

- admisión conversacional explícita;
- interceptor registrado en el runtime capability registry;
- estado de follow-up efímero por `session_id`;
- TTL acotado;
- presentación de candidatos;
- disambiguación humana;
- cancelación;
- respuesta por `GovernedOperationalInterception`.

Se reutiliza el patrón arquitectónico, no la autoridad de Biblioteca ni sus tipos.

`LOCAL_LIBRARY_PATTERN: REUSABLE PRECEDENT`

`LOCAL_LIBRARY_AUTHORITY: NOT_REASSIGNED`

## 6. Level-2 no es el owner de esta primera consulta

`GovernedLevel2ReadOnlyExecutionGatewayV1` es una frontera canónica válida para
adquisición de evidencia gobernada derivada de:

- discriminating evidence requirement;
- evidence acquisition planning;
- independence authorization;
- capability evidence output.

Una orden explícita del Owner para consultar su historia de desarrollo no nace de
esa cadena.

Fabricar requirement, planning y independence authorization para una consulta
humana directa introduciría Reasoning semantics que este residual no necesita.

Decisión:

`LEVEL2_READ_ONLY_GATEWAY: EXISTING / NOT_SELECTED_FOR_OWNER_DIRECT_CONSULTATION`

Esto no reduce ni reemplaza Level-2 para sus casos legítimos.

## 7. Governed Source Query tampoco es el owner

`GovernedSourceQueryExecutor` opera fuentes de información declaradas mediante
source topics, regions y query semantics.

Development History es un filesystem histórico privado con selección explícita de
artefactos y trust class histórica.

No se reclasifica como fuente editorial, institucional u oficial externa.

`GOVERNED_SOURCE_QUERY_EXECUTOR: NOT_SELECTED`

## 8. Composición canónica seleccionada

La composición mínima es:

`explicit Owner conversation turn`
`-> OfficialConversationGateway`
`-> OfficialRuntimeCapabilityRegistry`
`-> Development History consultation interception port`
`-> existing DevelopmentHistorySourceAdapter.discover()`
`-> candidate presentation / explicit human selection`
`-> existing DevelopmentHistorySourceAdapter.read_selected()`
`-> bounded historical text presentation`
`-> STOP`.

El interception port es un colaborador subordinado de reachability.

No es una nueva authority, manager, brain, planner, repository ni evidence owner.

## 9. Provisioning

La capability sólo puede existir productivamente cuando
`build_development_history_source_from_environment()` devuelve un source válido.

La configuración continúa siendo exclusivamente:

`ROBY_DEVELOPMENT_HISTORY_ROOT`.

No se hardcodea `D:\Roby`.

Si el root no está configurado, la capability no se registra como operativa.

Si la configuración es inválida, debe fallar cerrada y no ofrecer acceso.

## 10. Capability registry

La consulta explícita debe registrarse en el
`OfficialRuntimeCapabilityRegistry` existente.

No requiere un nuevo registry.

El descriptor debe declarar semántica local y read-only.

La capability propuesta conceptualmente es:

`development_history.consult`

Su interceptor debe ser el único punto conversacional productivo de esta consulta.

No se registra `evidence_reader` en este primer contrato porque la capability no
está siendo usada como adquisición Level-2.

## 11. Admisión explícita

La primera versión debe admitir sólo lenguaje que identifique inequívocamente la
fuente histórica, por ejemplo familias equivalentes a:

- `consultá el historial de desarrollo`;
- `buscá en el historial de desarrollo`;
- `consultá D:\Roby`;
- `buscá en D:\Roby`.

No debe interceptar menciones genéricas a:

- historia;
- código;
- archivos;
- ROBY;
- desarrollo.

`EXPLICIT_SOURCE_REFERENCE_REQUIRED: YES`

No se habilita consulta autónoma ni implícita.

## 12. Consulta inicial

La intención explícita debe contener un término de búsqueda o provocar una única
solicitud de aclaración.

La búsqueda de esta primera versión no es semantic search.

Debe operar sólo sobre el resultado bounded de `discover()` y filtrar de forma
determinista por texto normalizado contenido en:

- `relative_path`;
- filename derivado de `relative_path`.

No lee contenidos para buscar coincidencias.

`CONTENT_SEARCH: FORBIDDEN`

`BACKGROUND_INDEX: FORBIDDEN`

## 13. Resultado sin coincidencias

Si no hay candidatos visibles compatibles, la capability responde que no encontró
coincidencias dentro del discovery histórico gobernado.

No amplía automáticamente `max_candidates`.

No ejecuta una segunda búsqueda oculta.

No consulta ZIP internamente.

## 14. Coincidencia única

Si existe exactamente un candidato DIRECT compatible, puede ejecutarse
`read_selected(candidate_id)` dentro del mismo turno explícito.

La lectura conserva todas las revalidaciones y límites del source Owner-certified.

Si el candidato es `OPAQUE_ARCHIVE`, sólo se presenta como artefacto histórico
opaco y no se intenta leer.

## 15. Múltiples coincidencias

Si existen varias coincidencias, el interceptor presenta una lista determinista y
solicita selección humana.

La presentación expone sólo información mínima:

- `relative_path`;
- `kind` cuando sea necesario para distinguir un archive opaco;
- opcionalmente `size_bytes` si ayuda a desambiguar.

No presenta:

- root absoluto;
- `source_reference` interno;
- candidate id completo;
- credenciales ni paths excluidos.

## 16. Selección explícita

La selección posterior sólo puede resolver contra los candidatos presentados en la
última consulta pendiente de esa misma sesión.

La primera versión puede aceptar:

- número ordinal visible de la opción;
- `relative_path` visible exacto.

No acepta un candidate id arbitrario suministrado externamente.

Después de resolver la opción, siempre se llama al
`DevelopmentHistorySourceAdapter.read_selected()` existente.

Por tanto la selección no evita la revalidación del source.

## 17. Estado pendiente

El único estado nuevo permitido es efímero y process-local:

- keyed por `session_id`;
- candidatos ya presentados;
- timestamp de solicitud;
- sin texto leído persistido.

Debe poseer TTL finito. El precedente de Biblioteca usa cinco minutos y constituye
un límite razonable para el CONTRACT RED.

Al completar, cancelar o expirar la consulta se elimina el estado pendiente.

No se crea repository, DB, Memory record ni Knowledge record.

## 18. Follow-up compatible

Mientras existe una selección pendiente, sólo un follow-up compatible puede ser
interpretado como selección.

Una pregunta conversacional claramente no relacionada debe dejar de ser tratada
como selección histórica.

Debe existir cancelación explícita.

Esto evita capturar turnos ordinarios de conversación.

## 19. Presentación de lectura

Una lectura DIRECT exitosa puede presentarse como texto histórico al Owner.

La respuesta debe conservar semántica de origen, por ejemplo indicando que el
contenido proviene del historial de desarrollo y no representa automáticamente el
estado actual.

No debe afirmar que el contenido leído es Current Truth.

La presentación no transforma el texto en evidencia actual.

## 20. Trust barrier

Se mantienen obligatoriamente:

`HISTORICAL_PRESENTATION != CURRENT_TRUTH`

`HISTORICAL_PRESENTATION != DIAGNOSTIC_PROJECT_EVIDENCE`

`HISTORICAL_PRESENTATION != REASONING_ADMISSION`

`HISTORICAL_PRESENTATION != MEMORY_WRITE`

`HISTORICAL_PRESENTATION != KNOWLEDGE_WRITE`

`HISTORICAL_PRESENTATION != LEARNING_ADMISSION`

`HISTORICAL_PRESENTATION != PROPOSAL_AUTHORIZATION`

`HISTORICAL_PRESENTATION != CODE_MUTATION`

## 21. No modificación del source

El source Owner-certified ya posee las garantías necesarias de filesystem.

El próximo contrato no debe cambiar `app/development_history_source.py` salvo que
un fallo contractual demuestre una incompatibilidad real no conocida hoy.

La expectativa arquitectónica es:

`SOURCE_OWNER: UNCHANGED`

`REACHABILITY_COLLABORATOR: NEW / SUBORDINATE`

## 22. Placement previsto

Antes de GREEN el CONTRACT RED deberá volver a comprobar nombres existentes.

Con la evidencia actual, el placement mínimo admisible es un módulo `app/`
dedicado a la consulta conversacional de Development History, análogo en rol de
reachability a otros interception ports locales.

Nombre conceptual:

`app.development_history_consultation`

Tipo conceptual:

`DevelopmentHistoryConsultationInterceptionPort`.

Estos nombres pueden fijarse en CONTRACT RED si la reconciliación final de símbolos
no encuentra colisión.

## 23. Runtime wiring previsto

`runtime_root_factory` es el composition root que ya:

- construye el `OfficialRuntimeCapabilityRegistry`;
- provisiona la Biblioteca local;
- provisiona Local Music;
- registra capabilities conversacionales.

El GREEN futuro, sólo después de RED Owner-certified, podría:

1. construir el source desde environment;
2. construir el interception port subordinado;
3. registrar `development_history.consult` si el source está disponible.

No se modifica `OfficialConversationGateway` para crear una ruta paralela.

## 24. Reasoning y self-improvement

No forman parte del contrato siguiente.

Si una lectura histórica sugiere que un comportamiento podría seguir existiendo,
una futura capacidad separada deberá reacquirir evidencia desde el proyecto actual.

Se mantiene:

`HISTORICAL_CLUE -> POSSIBLE FUTURE CURRENT-EVIDENCE QUESTION`

pero nunca:

`HISTORICAL_CLUE -> CURRENT FACT`.

## 25. CONTRACT RED readiness

Las decisiones observables necesarias ya quedaron determinadas:

- autoridad de entrada: existente Official Conversation Gateway;
- routing: existing Official Runtime Capability Registry;
- capability: local explicit read-only consultation;
- source owner: existing DevelopmentHistorySourceAdapter;
- admission: explicit source reference only;
- search: metadata-only over bounded discovery;
- selection: explicit ordinal or exact presented relative path;
- pending state: ephemeral per-session with finite TTL;
- presentation: relative paths only, historical disclaimer;
- archives: opaque metadata only;
- final action: presentation / STOP;
- Reasoning, Memory, Knowledge, Learning and self-improvement: excluded.

Por tanto ya no quedan decisiones esenciales que deban inventarse dentro del test.

`CONTRACT_RED_AUTHORIZED: YES`

## 26. Mínimo contrato RED

El próximo RED debe demostrar al menos:

1. source ausente => capability no provisionada/registrada;
2. root configurado => consulta local read-only provisionable;
3. admisión sólo ante referencia explícita a Development History / `D:\Roby`;
4. query ausente => aclaración acotada;
5. metadata filtering determinista sin content search;
6. no-match fail closed sin ampliar discovery;
7. unique DIRECT match => existing `read_selected()`;
8. multiple matches => relative-path-only disambiguation;
9. follow-up selection sólo contra opciones presentadas de la misma sesión;
10. ordinal y exact relative path seleccionables;
11. arbitrary candidate id no aceptado;
12. TTL/cancelación limpian pending state;
13. unrelated turn no es capturado como selection;
14. OPAQUE_ARCHIVE nunca se lee ni extrae;
15. presentación marca contenido como histórico/no-current;
16. no absolute root/source_reference leakage;
17. no Memory/Knowledge/Learning/Reasoning/proposal side effects;
18. source module permanece sin modificación contractual;
19. capability usa el registry existente y no un gateway paralelo;
20. no hardcoded `D:\Roby`.

## 27. Scope negativo del CONTRACT RED

No autoriza:

- semantic content search;
- archive extraction;
- watcher/background scan;
- durable index;
- autonomous consultation;
- Level-2 evidence acquisition para esta ruta Owner-driven;
- direct Reasoning admission;
- current-project evidence synthesis;
- Memory/Knowledge/Learning writes;
- proposal generation;
- code mutation;
- nueva cognitive authority;
- reapertura de D:\Documentos;
- B2/B3/B4.

## 28. Estado final

`D_ROBY_SOURCE: CLOSED / OWNER-CERTIFIED`

`EXPLICIT_OWNER_HISTORY_CONSULTATION: RECONCILED`

`CONVERSATION_ENTRY_AUTHORITY: EXISTING / UNCHANGED`

`RUNTIME_CAPABILITY_REGISTRY: EXISTING / SELECTED`

`LEVEL2_GATEWAY: EXISTING / NOT_SELECTED_FOR_DIRECT_OWNER_ROUTE`

`GOVERNED_SOURCE_QUERY: EXISTING / NOT_SELECTED`

`SOURCE_OWNER: DevelopmentHistorySourceAdapter / UNCHANGED`

`NEW_REACHABILITY_AUTHORITY: NONE`

`PROVEN_RESIDUAL:`
`EXPLICIT_OWNER_DEVELOPMENT_HISTORY_CONSULTATION_ADMISSION_AND_PRESENTATION`

`CONTRACT_RED_AUTHORIZED: YES`

`PRODUCT_CHANGE: NONE`

`TEST_CHANGE: NONE`

`B2: STOP`

`B3: STOP`

`B4: STOP`

## 29. Próximo bloque gobernado

`MASTER PLAN — D:\Roby EXPLICIT OWNER DEVELOPMENT HISTORY CONSULTATION`
`— CONTRACT RED`

El próximo bloque debe crear únicamente el contrato RED de reachability y hacer
STOP antes de GREEN.
