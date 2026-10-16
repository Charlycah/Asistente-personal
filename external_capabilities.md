> **CURRENT SNAPSHOT — laptop-only residency:** Current certified baseline: **12,534 PASS · 0 FAIL · Ruff clean**. Android is **RETIRED / HISTORICAL — CLOSED / CERTIFIED** at **13,746 PASS · 0 FAIL · Ruff clean**. Mobile/Hands-Free/Driving is **RETIRED / HISTORICAL — CLOSED / CERTIFIED** at **13,209 PASS · 0 FAIL · Ruff clean**. Residential/MINI-PC/distributed-residence is **RETIRED / HISTORICAL — CLOSED / CERTIFIED** at **12,534 PASS · 0 FAIL · Ruff clean** after governed reachability review and de-wiring of `residential.remote_presence`. `OfficialDeviceRuntimeGateway`, neutral device capabilities/continuity, Presence, ResidentComponentRegistry, local Web Panel, InformationClassification, Camera/Vision and multimodal laptop infrastructure are preserved. Historical milestone sections below are traceability only and do not authorize reintroduction of retired capability families.

## M399.2 — Governed Self-Diagnostics Foundation

M399.2 no añade capacidades externas. `self_diagnostics` consume únicamente observaciones explícitas ya entregadas por autoridades internas; no descubre recursos, no consulta red, no activa providers, no inspecciona dispositivos y no realiza polling.

## M394.1 — Registro Gobernado de Recursos Externos

M394.1 inaugura la infraestructura externa sólo a nivel registral. ROBY puede conocer de forma explícita que existe un recurso externo, su tipo y su autoridad de procedencia, pero no realiza descubrimiento, conexión, autorización, activación, lectura de red, polling ni ejecución. El único estado nuevo es `known`; los estados operacionales posteriores permanecen fuera de alcance.

## M393.8 — Estabilización Relacional

M393.8 no incorpora conectores ni capacidades externas. Cierra únicamente contratos internos ya existentes de `relationship_memory` y no accede a red, dispositivos, sensores, servicios o credenciales.

## M393.7 — Auditoría Relacional Gobernada

M393.7 no añade una capacidad externa ni un nuevo conector. Expone únicamente una auditoría de sólo lectura sobre trazabilidad relacional ya gobernada bajo `relationship_memory`.

## M393.6 — Trazabilidad Relacional Gobernada

M393.6 no añade capacidades externas. Sólo enlaza estados internos ya gobernados de memoria relacional; no consulta red, sensores, contactos, servicios, credenciales ni dispositivos.

## M393.1 — Memoria Relacional Enriquecida Gobernada

M393.1 no añade capacidades externas. Sólo relaciona registros internos existentes con referencias explícitas de evidencia ya gobernada; no consulta red, contactos, sensores, servicios externos ni credenciales.

## M392.8 — Estabilización Integral del Modelo del Mundo

M392.8 no añade capacidades externas. Sólo audita representaciones internas ya gobernadas y no habilita sensores, seguimiento, automatización, red ni ejecución.

## M392.7 — Integración del Mundo Gobernada

La integración del mundo no añade capacidades externas. Sólo compone representaciones internas ya gobernadas y no habilita sensores, seguimiento, automatización ni ejecución.

## M392.4 — Objetos Gobernados

M392.4 no añade capacidad externa: no detecta, rastrea, compra, busca productos ni controla objetos. Sólo representa conocimiento ya gobernado.

## M392.2 — Personas Gobernadas

M392.2 no añade capacidades externas. No usa cámara, reconocimiento facial, contactos, GPS ni servicios externos para identificar personas; sólo representa evidencia gobernada ya suministrada por autoridades internas.

## M392.1 — Representación del Hogar Gobernada

M392.1 no añade capacidades externas. La representación doméstica es interna, de solo lectura y construida únicamente desde evidencia ya persistida por autoridades gobernadas. No consulta sensores, GPS, Android ni servicios externos.

## M391.7 — Predicción Gobernada

No añade una capacidad externa ni acceso nuevo a servicios. Formaliza evaluación predictiva interna sobre resultados M391.4 explícitos bajo `governed_reasoning`, sin reloj residente, persistencia, probabilidad inventada ni ejecución.

## M390.8 — Estabilización y Evidencia Integral

M390.8 no agrega capacidades externas. Sólo incorpora evidencia diagnóstica interna, explícita y de solo lectura para estabilizar y cerrar la serie M390.

## M379 — Personal Organization Foundation

M379 no agrega capacidades externas. Inventaría capacidades internas ya existentes y define una única fachada de organización personal, sin proveedores, red, herramientas, ejecución ni persistencia nueva.

## M378 — Explicaciones Inteligentes

M378 no agrega capacidades externas. Define una frontera cognitiva interna para explicar decisiones y límites ya producidos por el cerebro unificado, sin proveedores, red, herramientas, ejecución, persistencia ni llamadas a LLM.

## M377 — Personalidad Adaptativa

M377 no agrega capacidades externas. Define una frontera cognitiva interna que modula la expresión del único ROBY a partir de su personalidad estable. No incorpora proveedores, red, herramientas, persistencia, aprendizaje de preferencias ni agentes secundarios.

## M376 — Conversaciones de Largo Plazo

M376 no agrega capacidades externas. Define una frontera cognitiva interna para archivos conversacionales resumidos, sin proveedores, red, herramientas ni persistencia de producción.

## M375 — Conversación Contextual

M375 no agrega una capacidad externa. Formaliza una capacidad cognitiva interna gobernada sobre `ConversationContext`, sin proveedores, transporte, persistencia ni herramientas nuevas.

## M367.3 — Project Knowledge Model

No incorpora capacidades externas. La documentación local se trata como evidencia explícita y no como autoridad automática.

# ROBY XI.2 — external_capabilities.md

> **Inventario canónico de capacidades externas**

**Milestone de origen:** M348.0  
**Última revisión documental:** M360.0.d  
**Base canónica:** M378

## 1. Propósito

Este documento constituye el inventario oficial de las capacidades externas de
ROBY XI.2.

Su objetivo es evitar duplicaciones, identificar autoridades y contratos
existentes, distinguir capacidades completas de brechas reales y servir como
punto de partida obligatorio para nuevos desarrollos.

## 2. Documentos canónicos

Antes de incorporar una capacidad externa deberán leerse:

1. `VISION.md`
2. `README.md`
3. `architecture_rules.md`
4. `external_capabilities.md`
5. `integration_decision.md`
6. `CHANGELOG_ARCHITECTURE.md`

## 3. Checklist obligatorio

- ¿La capacidad ya existe total o parcialmente?
- ¿Existe una autoridad canónica responsable?
- ¿Puede extenderse un contrato existente?
- ¿Se evita una segunda fuente de verdad?
- ¿Se integra mediante `ToolGatewayManager`?
- ¿Respeta la gobernanza de credenciales?
- ¿Tiene activación explícita y readiness?
- ¿Existe trazabilidad completa?
- ¿Se definieron pruebas automáticas y manuales?
- ¿Aporta valor personal a Carlos y Cristina?

## 4. Arquitectura de integración

Usuario → Intención → ConversationContext → ConversationStrategyPlanner →
CognitiveAction → ToolGatewayManager → Adaptador → Proveedor externo →
Resultado → DecisionTrace → CognitiveLearningPolicy → Persistencia →
CognitiveMemoryRecall → Respuesta

Nunca se conectará el planner directamente con un proveedor externo.

## 5. Inventario canónico revisado

| Capacidad | Estado M348.1 | Autoridad / patrón | Observación |
|---|---|---|---|
| Clima | Implementada | ToolGatewayManager + proveedor gobernado | Operativa |
| Noticias e información gobernada | Implementada | Fuentes gobernadas + normalización + relevancia | Operativa |
| Gmail / correo | Implementada y gobernada | Integración Gmail, OAuth, transporte, readiness y pruebas | No es brecha |
| LLM local / Ollama | Implementada y gobernada | Proveedor local compatible con OpenAI + routing | No es brecha |
| Calendario | Contrato mínimo definido | Capacidad reconocida + `CalendarProvider` neutral | Adaptador real pendiente |
| Home Assistant | Pendiente | Por diseñar mediante autoridades existentes | Brecha futura |
| MCP | Pendiente | Protocolo transversal, no una capacidad única | Brecha futura |

## 6. Primera brecha seleccionada

M348.1 selecciona **Google Calendar** como primera integración externa de la
serie M348.

La brecha no consiste en crear una nueva capacidad cognitiva. Consiste en
completar una capacidad ya reconocida mediante un proveedor real, gobernado,
configurable y trazable.

## 7. Gobernanza de credenciales

Toda nueva API deberá integrarse con el sistema canónico de credenciales.

`.roby/credentials.json` debe preservarse. No se crearán archivos paralelos para
tokens, claves o secretos salvo que un proveedor exija técnicamente un artefacto
externo y exista una decisión arquitectónica explícita que lo gobierne.

Los secretos reales nunca se documentarán ni se incluirán en ejemplos.

## 8. Orden obligatorio para nuevas integraciones

1. Inventario y diagnóstico.
2. Selección de brecha real.
3. Contrato o extensión mínima.
4. Adaptador del proveedor.
5. Configuración y activación controlada.
6. Errores, readiness y recuperación.
7. Trazabilidad cognitiva.
8. Pruebas end-to-end.
9. Validación manual real.
10. Estabilización y patrón reutilizable.

## 9. Regla de actualización

Este inventario deberá actualizarse cuando:

- una capacidad pase de pendiente a parcial;
- se incorpore un proveedor;
- cambie la autoridad canónica;
- aparezca una nueva brecha;
- se estabilice una integración;
- se retire una capacidad por decisión formal.


## 10. Estado M348.2

Se definió el contrato neutral de Calendar sin incorporar proveedor ni red.
El contrato establece modelos timezone-aware y operaciones mínimas de lectura,
disponibilidad y creación gobernada.

No se modificó `.roby/credentials.json` ni se creó almacenamiento paralelo.

## 10. Estado M348.3

Google Calendar dispone ahora de un adaptador concreto detrás del contrato
neutral de M348.2. La capacidad todavía no se considera operativa porque faltan:

- configuración canónica;
- activación OAuth controlada;
- composición de runtime;
- readiness y recuperación;
- integración gobernada con ToolGatewayManager;
- validación manual con una cuenta real.

## 10. Estado posterior a M348.4

Google Calendar dispone ahora de:

- contrato neutral;
- adaptador Google Calendar API v3;
- configuración desde la autoridad canónica de credenciales;
- activación por feature flag;
- estados de disponibilidad controlados;
- autorización interactiva bloqueada por defecto;
- integración pasiva en el único runtime composition root.

La capacidad continúa en estado **parcial** porque todavía no está expuesta a la
conversación ni al `ToolGatewayManager` y no cuenta con validación de cuenta real.

## 11. Estado posterior a M348.5

Google Calendar dispone ahora de:

- contrato neutral;
- adaptador Google Calendar API v3;
- activación controlada mediante la autoridad canónica;
- readiness explícito y libre de secretos;
- clasificación estable de fallos;
- planes deterministas de recuperación;
- recuperación OAuth únicamente bajo invocación explícita.

La capacidad continúa en estado **parcial** porque todavía no está conectada al
`ToolGatewayManager`, no posee trazabilidad cognitiva integral y no fue validada
contra una cuenta real.


## M348.6 — ToolGateway y planner

Calendar queda registrado detrás del gateway oficial con lectura controlada de eventos y disponibilidad. La escritura se declara para preservar el contrato futuro, pero permanece deshabilitada y requiere confirmación. El planner sólo recibe una capacidad `calendar` de lectura cuando el runtime está listo.

## 12. Estado posterior a M348.7

Google Calendar ofrece consulta conversacional completa de agenda y disponibilidad
para intervalos relativos, días de semana, fechas explícitas y franjas horarias.
Los eventos se ordenan y los bloques ocupados se presentan con precisión. La
capacidad continúa siendo de solo lectura: crear, modificar o eliminar eventos
permanece bloqueado y requiere un milestone posterior de gobierno y confirmación.

## Calendar — creación gobernada (M348.8)

`calendar.event.create` está registrado detrás de ToolGateway con riesgo alto,
`permission_scope=write` y confirmación obligatoria. No forma parte de las
capacidades de escritura implícita del planner. La conversación crea primero un
borrador, muestra fecha y horario, verifica conflictos y exige `sí, crear` antes
de cualquier mutación externa.

## Vision M362

La frontera vigente es `GovernedVisionGateway`, con análisis delegado al núcleo existente y retención local opcional, explícita y no biométrica.

## Windows Workspace — M363

- Estado: fundación gobernada.
- Gateway: `OfficialWindowsWorkspaceGateway`.
- Lectura: ventanas, procesos y screenshots mediante proveedor.
- Mutaciones: declaradas pero no ejecutables en M363.
- Screenshot retention: delegada a M362 con consentimiento explícito.

## M364 — Fundación común de dispositivos

Existe una frontera descriptiva y gobernada para registrar dispositivos, transportes, capacidades y diagnóstico. Bluetooth, USB, Android, Samsung Watch, impresoras, cámaras IP, aspiradoras robot y Home Assistant todavía no poseen ejecución operativa por esta sola fundación.


## M365.1 — Android Bridge Contract Foundation

Existe un contrato neutral para registrar un futuro agente Android y evaluar identidad, versión, capacidades y permisos declarativos. No existe transporte activo, lectura del teléfono, planner ni ejecución.

## M365.2 — Android Bridge Configuration & Controlled Activation

- Estado: fundacional, pasivo y deshabilitado por defecto.
- Configuración: sección `services.android_bridge` de la configuración canónica.
- Autoridad de dispositivos: `OfficialDeviceGateway`.
- Activación: evaluación pura; `READY` no implica ejecución.
- Transporte y acciones Android: no implementados.

## M365.3 — Android Bridge Transport Abstraction

- Autoridad: `AndroidBridgeContract`, subordinado a `OfficialDeviceGateway`.
- Frontera: `AndroidBridgeTransport`, exclusivamente descriptiva en este milestone.
- Adaptadores disponibles: nulo seguro y descriptor estático para pruebas.
- Estado: fundacional, simulable y no operativo.
- Ejecución: prohibida; cualquier acción futura deberá atravesar `ToolGatewayManager`.
- Transportes reales, descubrimiento, credenciales e I/O: pendientes y fuera de alcance.


## M365.4 — Android Bridge Readiness, Authentication & Recovery

La readiness combina exclusivamente las evaluaciones gobernadas existentes. La autenticación es declarativa y no conserva secretos ni pruebas. La recuperación es un plan determinista, no un mecanismo operativo; no abre conexiones, no duerme y no reintenta.


## M365.6
El catálogo Android es declarativo, pasivo y no ejecutable. Su registro usa exclusivamente ToolGatewayManager.

## M365.7 — Android Bridge Capability Selection & Stabilization

La selección es descriptiva, no ejecutable y permanece detrás de las autoridades canónicas.

## M367.7

Mental Model Stabilization no incorpora capacidades externas.

## M370.1 — Android Device State Foundation

- Autoridad: `OfficialDeviceGateway`.
- Modelo: `AndroidDeviceState`, inmutable, de solo lectura y no ejecutable.
- Admisión: dispositivo móvil registrado con `android.device_state` declarado.
- Fuente real: no implementada; no existe ADB, red, polling ni background.
- Integración cognitiva: reservada para incrementos posteriores.



## M371 — Android Notifications

- Autoridad: `OfficialDeviceGateway`.
- Modelos: `AndroidNotification` y `AndroidNotificationSnapshot`.
- Estado: fundacional, pasivo, de solo lectura y no ejecutable.
- Fuente real: no implementada; no existen listener, ADB, red, polling o background.
- Acciones: abrir, responder, descartar y marcar permanecen fuera de alcance.
- Integración cognitiva: reservada para hitos posteriores con privacidad explícita.


## M372 — Android Clipboard

- Autoridad: `OfficialDeviceGateway`.
- Modelos: `AndroidClipboardItem` y `AndroidClipboardSnapshot`.
- Estado: fundacional, sensible, pasivo, de solo lectura y no ejecutable.
- Fuente real: no implementada; no existen lector, ADB, red, polling o background.
- Acciones: escribir, limpiar, sincronizar, compartir y abrir permanecen fuera de alcance.
- Integración cognitiva: reservada para hitos posteriores con consentimiento y privacidad explícitos.


## M373 — Android Files

- **Autoridad:** `OfficialDeviceGateway`.
- **Estado:** fundamento canónico de solo lectura.
- **Contrato:** `AndroidFileEntry` y `AndroidFileSnapshot`.
- **Activación física:** no implementada.
- **Mutaciones:** prohibidas en este milestone.
- **Integración cognitiva automática:** no implementada.

## M380 — Organized Work Model

- Autoridad canónica: `PersonalOrganizationAuthority`.
- Modelos: referencias y snapshot de trabajo organizado.
- Capacidades externas nuevas: ninguna.
- Escritura, ejecución, persistencia y automatización: fuera de alcance.

## M394.2 — Identidad Gobernada de Recursos Externos

M394.2 formaliza identidad estable para los recursos ya registrables en M394.1. `ExternalResourceIdentity` separa identidad canónica (`namespace:local_id`) de etiquetas humanas y metadatos, mientras `ExternalResourceRegistryAuthority` conserva en una sola autoridad el registro, la unicidad y la resolución de identidad. Identificar no significa autenticar, conectar, autorizar, activar ni controlar.

## M394.3 — Estado Gobernado de Recursos Externos

M394.3 permite que ROBY represente si un recurso registrado es `known`, `available` o `unavailable`, siempre mediante una declaración explícita recibida por la misma `ExternalResourceRegistryAuthority`. El estado es conocimiento gobernado, no una acción: no hay sondeo, descubrimiento, conectividad, autenticación, autorización ni control. Los estados `connected`, `authorized` y `active` se reservan para etapas posteriores de M394.

## M394.4 — Autorizaciones Gobernadas de Recursos Externos

M394.4 permite que ROBY conserve una decisión explícita `unknown`, `authorized` o `denied` para un recurso registrado, con evidencia inmutable de procedencia, autor, fecha, razón y revisión. La autorización es conocimiento de política, no permiso operacional del sistema: no autentica, conecta, activa, controla ni ejecuta el recurso y permanece separada de `known`, `available` y `unavailable`.

## M394.5 — Conectividad Gobernada de Recursos Externos

M394.5 permite representar conectividad externa como conocimiento explícito: `unknown`, `configured` o `unavailable`, con transporte, referencia de endpoint, procedencia, instante y revisión. Configurar un perfil no conecta ni controla el recurso y permanece separado del estado y la autorización.


## M394.6 — Auditoría Gobernada de Recursos Externos

M394.6 incorpora evidencia inmutable y revisionada de decisiones sobre recursos externos registrados. La auditoría es descriptiva, append-only y no realiza operaciones externas.

## M394.7 — Recuperación Segura de Recursos Externos

M394.7 permite reconstruir un snapshot cognitivo inmutable de un recurso ya registrado. La recuperación se basa en el registro gobernado actual y en la auditoría disponible, distinguiendo `registered_only` de `audited`. No restaura dispositivos, no conecta, no autentica, no activa y no ejecuta recursos externos.


## M394.8 — Estabilización Integral de Recursos Externos

M394.8 cierra y estabiliza la serie M394 sin añadir operaciones externas. El modelo gobernado de recursos externos queda consolidado en registro, identidad, estado, autorización, conectividad, auditoría y recuperación segura bajo una única `ExternalResourceRegistryAuthority`.

## M396.2 — Relación con capacidades externas

Distributed Residence puede referenciar identificadores de recursos externos y
capacidades declaradas, pero M396.2 no descubre, conecta, autentica, autoriza ni ejecuta
recursos. `ExternalResourceRegistryAuthority` conserva sus competencias M394 y el
modelo de residencia no las duplica.

## M396.3 — Residence no concede capacidades

La declaración de una capacidad o recurso dentro de un `ResidenceDescriptor` es
contexto descriptivo. No sustituye registro externo, autorización, consentimiento,
routing ni ejecución. M396-I03 mantiene esas decisiones en sus fronteras oficiales.

## M396.4 — Residence Explicit Admission

La detección futura de un recurso externo no lo convierte en residencia. M396.4 sólo
incorpora candidatos y proveniencia declarativa de admisión; cualquier descubrimiento,
autenticación, pairing, conectividad u operación física permanece fuera de Residence.


## M396.5 — Identidad estable de residencia

Los atributos externos observables pueden cambiar sin redefinir la identidad lógica de
la residencia. Este incremento no descubre, autentica, conecta ni opera recursos.

## Post-M404 — Residential Perception external/physical capability status

- Local camera one-shot physical acquisition into M404: **operational/validated**.
- Household sensor acquisition: **pending concrete physical source**.
- Residential IP camera acquisition: **pending concrete device/protocol and media/reference governance**.
- Android Sensors remain governed read-only contracts and do not by themselves certify physical residential sensor I/O.
- No generic MQTT/Home Assistant/sensor framework is activated by this checkpoint.

## Post-M405 — Information Classification capability status

- Canonical neutral information classification vocabulary: **operational/validated**.
- M403 outbound classification-aware admission: **operational/validated**.
- Legacy M403 flows: **preserved** when no classification policy is supplied.
- Receiver-side classification verification: **deferred; no real cross-residence consumer demonstrated yet**.
- Classification does not replace resource authorization, credential isolation, residence admission, synchronization shareability, provenance or domain policy.

## M406.1 — Governed Web Panel

Estado: **FOUNDATION OPERATIVA LOCAL / READ-ONLY**.

La primera surface Web de ROBY utiliza sólo loopback IPv4 (`127.0.0.1`) y expone un snapshot operacional minimizado por `GET /api/status`. No ofrece acciones, LAN/remoto, autenticación, cámaras/media, memoria, conversaciones, GPS ni credenciales. La surface consume owners existentes y M405 Information Classification; no adquiere autoridad propia.

## M406.2 — Minimal Human Dashboard

Estado: **EXPERIENCIA HUMANA LOCAL MÍNIMA / READ-ONLY**.

El navegador puede consumir `GET /` en el mismo servicio loopback M406.1. La página representa únicamente el snapshot clasificado ya admitido; no consulta recursos externos por sí misma, no carga CDN/JavaScript remoto, no muestra media ni credenciales y no controla dispositivos.

## Post-M406 — Governed Web Panel capability status

- Local classified read model: **operational/validated**.
- `GET /api/status` loopback JSON API: **operational/validated**.
- `GET /` minimal human dashboard: **operational/validated**.
- Optional productive `OfficialROBYRuntime` wiring: **operational/validated, disabled by default**.
- Binding: **`127.0.0.1` only**.
- LAN / authentication / TLS / remote: **future separate scope**.
- Actions/control: **not part of M406**.
- Credentials / `SENSITIVE` / `UNCLASSIFIED`: **not exposed**.

## M408.1 — Residential Remote Presence

Existe foundation para solicitar explícitamente una observación `STILL_IMAGE` fresca de una
fuente residencial M404 autorizada. La captura pasa por Tool Gateway/consent, conserva
provenance M404 y entrega media `SENSITIVE` transitoria bounded sobre un carrier M398 ya
gobernado. No existe streaming, grabación, alerta automática, exposición web pública ni
control físico de la cámara.

## Explicit Complex Decision Criteria Evidence Foundation v1

Internal read-only evidence capability only. No external provider, retrieval, network, tool, device, persistence, execution or background capability is added.

## Advanced Capability 4B — Independent Reasoning Evaluation

4B no añade capacidades externas: no consulta red, providers, herramientas, dispositivos
ni servicios. Usa únicamente datasets locales congelados y capabilities internas ya
gobernadas para producir evidencia diagnóstica reproducible.


## Current M367 external-capability note

The retirement of M367.2/.3/.4/.5/.7 is internal structural cleanup only. It adds no external capability and changes no provider, device, network, account, persistence or execution authority. M367.1 current World Model and M367.6 Priority Reasoning remain governed internal capabilities.
