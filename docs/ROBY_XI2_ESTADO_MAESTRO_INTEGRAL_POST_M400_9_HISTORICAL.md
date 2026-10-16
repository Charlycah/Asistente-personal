# ROBY XI.2 — ESTADO MAESTRO INTEGRAL POST-M400.9

**Documento rector de continuidad del proyecto**  
**Corte arquitectónico:** M400.9 — Governed External Intelligence Stabilization & Closure  
**Estado de certificación:** 11.027 tests aprobados · Ruff limpio · baseline M361 sincronizada · regresiones 0  
**Fecha de corte:** 11 de agosto de 2026

---

## 0. Propósito de este documento

Este documento actualiza —sin sustituir su función rectora— el **Estado Maestro Integral Post-M395.5** y consolida el estado real de ROBY XI.2 después de incorporar:

- la Constitución permanente del proyecto;
- la auditoría integral M394.A;
- la consolidación arquitectónica M395.1–M395.5;
- M396 — Distributed Residence Foundation;
- M397 — Governed Residence Connectivity;
- M398 — Governed Physical Transport;
- M399 — Governed Current Location + Governed Self-Diagnostics & Self-Maintenance;
- M400 — Governed External Intelligence;
- M401.1 — Governed Cognitive External Evidence Audit, cerrada documentalmente y sin cambios de código;
- el código y documentación de la baseline M400.9;
- la visión estratégica futura M500.0.

Su propósito sigue siendo responder de forma estable a seis preguntas:

1. **¿Qué es ROBY hoy?**
2. **¿Qué está realmente terminado?**
3. **¿Qué está parcialmente implementado o sólo preparado?**
4. **¿Qué está aislado, congelado o es legado?**
5. **¿Qué deuda y qué pendientes del Plan Maestro siguen abiertos?**
6. **¿Qué conviene hacer a continuación sin generar nuevos desfases?**

A partir de este corte, este documento pasa a ser el **Estado Maestro de referencia Post-M400.9**.

Los documentos anteriores no se eliminan. Conservan valor histórico, contractual o probatorio, pero no deben competir entre sí para describir el estado actual.

---

# 1. Dictamen ejecutivo

ROBY XI.2 sigue siendo un **sistema cognitivo personal, privado y gobernado**, con arquitectura operacional consolidada y un núcleo cognitivo ampliamente desarrollado.

La evolución M396–M400 no creó un segundo cerebro ni sustituyó las autoridades consolidadas por M395. Extendió el sistema hacia cuatro nuevas fronteras gobernadas:

1. residencia distribuida declarativa;
2. conectividad lógica entre residencias;
3. transporte físico gobernado;
4. observación técnica e inteligencia externa gobernada.

El proyecto **no necesita una reescritura del cerebro**.

Su situación real Post-M400.9 es:

### Núcleo cognitivo y gobernanza
**MUY AVANZADOS / CERTIFICADOS.**

### Runtime y composición operacional
**CONSOLIDADOS DESDE M395.**

No se ha autorizado una nueva refactorización general.

### Residencia distribuida
**FUNDACIÓN Y CONECTIVIDAD AVANZADAS; RESIDENCIA OPERACIONAL COMPLETA TODAVÍA PENDIENTE.**

M396 cerró el vocabulario y los invariantes de un único ROBY lógico presente en múltiples residencias autorizadas.

### Conectividad entre residencias
**CERRADA ARQUITECTÓNICAMENTE.**

M397 cerró identidad de peer, autenticación, admisión, sesión, health/readiness, revocación y comunicación auditable sin otorgar autoridad operacional.

### Transporte físico
**CERRADO COMO CAPACIDAD REUTILIZABLE, NO ACTIVADO COMO RUNTIME DISTRIBUIDO GENERAL.**

M398 cerró framing, TCP local, lifecycle, recuperación acotada, canal end-to-end y guardrails anti-abuso.

### Autodiagnóstico
**CERRADO / HUMANO-EN-EL-BUCLE.**

M399 observa, formula hipótesis, produce evidencia reproducible, sandbox, tests, diff y revisión humana. No aplica reparaciones automáticamente.

### Inteligencia externa
**CERRADA COMO FRONTERA DE EVIDENCIA.**

M400 gobierna resultados externos mediante boundary, provenance, verification, assessment y corroboration. No ejecuta providers/fuentes ni adquiere autoridad cognitiva.

### Uso cognitivo de evidencia externa
**AUDITADO, NO IMPLEMENTADO.**

M401.1 demostró que no existe todavía una ruta canónica cerrada para introducir evidencia estructurada M400 en cognición pre-inferencia. La auditoría no autoriza todavía cambios del runtime.

### Organización, memoria y conocimiento interno
**AVANZADOS.**

### Percepción física
**MIXTA.** Existen canales locales reales y contratos read-only; la percepción residencial distribuida original del roadmap sigue pendiente.

### Presencia física distribuida
**PARCIAL.** Existen foundation, conectividad y transporte; falta cerrar nodo residencial productivo, sincronización y percepción residencial.

### Legado
**AISLADO Y CONGELADO.**

### Documentación
**DEBE RECUPERAR UNA ÚNICA LÍNEA MAESTRA.**

La principal corrección metodológica de este corte es que futuras auditorías deben contrastarse contra este Estado Maestro antes de generar nuevos milestones o cambios de arquitectura.

---

# 2. Naturaleza y propósito permanente

ROBY XI.2 continúa siendo un proyecto:

- personal;
- privado;
- no comercial;
- no destinado a distribución pública;
- orientado a Carlos y Cristina;
- diseñado para acompañar, informar, organizar, recordar, ayudar y convivir dentro de límites seguros.

La arquitectura no debe evolucionar por novedad tecnológica. Toda capacidad nueva debe justificar qué problema real resuelve y qué autoridad existente la gobierna.

La identidad de ROBY no se confunde con el proveedor de modelo, la residencia física ni el canal de transporte. ROBY sigue siendo un único sistema lógico cuya continuidad reside en arquitectura, identidad, memoria, reglas, relaciones, conocimiento y gobernanza.

---

# 3. Principios permanentes

Se mantienen como constitucionales:

1. **Un único cerebro lógico.**
2. **Una única autoridad por capacidad.**
3. **Integración antes que duplicación.**
4. **No crear gestores paralelos cuando existe una autoridad ampliable.**
5. **Separar decisión, observación, composición, ejecución y lifecycle.**
6. **Una capacidad no se considera operativa sólo porque exista código.**
7. **Cambios pequeños, verificables y reversibles.**
8. **Documentación sincronizada con el código.**
9. **Toda evolución debe conservar trazabilidad.**
10. **La ejecución externa sensible requiere gobernanza y autorización.**
11. **El aprendizaje no puede modificar silenciosamente el comportamiento productivo.**
12. **La percepción debe basarse en evidencia real del canal correspondiente.**
13. **No atribuir consciencia subjetiva, emociones humanas reales ni certeza sin evidencia.**
14. **Privacidad y minimización de datos como criterio de diseño.**
15. **Una autoridad canónica puede delegar implementación, pero no fragmentar su responsabilidad.**
16. **Una auditoría reduce incertidumbre; no crea automáticamente arquitectura.**
17. **Todo nuevo trabajo debe declarar su impacto sobre el Plan Maestro y cualquier pendiente que desplace.**
18. **Evidencia externa no equivale a conocimiento interno.**
19. **Confianza no equivale a certeza.**
20. **Corroboración no equivale a verdad.**
21. **Información externa no equivale a autoridad cognitiva.**

---

# 4. Jerarquía documental definitiva

## Nivel A — Constitución permanente

Conservan autoridad sobre principios:

- `VISION.md`;
- `architecture_rules.md`;
- decisiones constitucionales explícitas del Libro Técnico;
- invariantes certificadas M396, M397, M398, M399 y M400.

## Nivel B — Estado actual

La referencia del estado corriente pasa a ser:

> **ROBY XI.2 — Estado Maestro Integral Post-M400.9**

Este documento debe actualizarse por grandes épocas arquitectónicas, no por cada microincremento.

## Nivel C — Evidencia de arquitectura actual

- M394.A.1–M394.A.6;
- documentación M395.1–M395.5;
- documentación y cierres M396–M400;
- M401.1 Closure + Master Plan Drift Map;
- baseline M361;
- tests arquitectónicos;
- runtime compatibility registry;
- mapas de autoridad vigentes.

## Nivel D — Referencias maestras históricas

Conservar, pero no usar como descripción absoluta del presente:

- Estado Maestro Post-M395.5;
- M380.A y fases;
- M388.5 Acta de Certificación del Cerebro;
- M391.0 Atlas Cognitivo Maestro;
- LT-1.x M394.8;
- auditorías M341/M360;
- inventarios M384/M388.

## Nivel E — Historia detallada

- milestones;
- ADR;
- releases;
- changelogs;
- refinements;
- certificaciones intermedias.

## Nivel F — Visión futura

- M500.0 y documentos equivalentes.

M500.0 sigue siendo visión/roadmap, no evidencia de implementación.

---

# 5. Línea base certificada actual

## M400.9 — Governed External Intelligence Stabilization & Closure

Estado:

**CERTIFICADO / BASELINE OFICIAL ACTUAL**

Validación final declarada:

- Ruff: limpio;
- quality baseline M361: sincronizada;
- pytest: **11.027 passed**;
- regresiones conocidas: 0.

### Época M395 — Consolidación del Núcleo Operacional Unificado

Se conserva como cierre de la gran consolidación del cerebro/runtime:

- fronteras y contratos neutrales;
- bootstrap y composición;
- alineación cognitiva;
- compatibilidad/legado;
- síntesis de orquestadores.

### M396 — Distributed Residence Foundation

**FORMALMENTE CERRADO.**

Entregó contratos inmutables para identidad de residencia, roles, admisión/revocación, endpoints, locality, snapshots, capabilities y limitations.

No implementó red, sincronización, ejecución remota ni segundo cerebro.

Principio rector:

> **One house. One ROBY. Many windows.**

### M397 — Governed Residence Connectivity

**FORMALMENTE CERRADO.**

Entregó:

- peer identity;
- explicit authentication;
- admission verification contra M396;
- session lifecycle;
- health/readiness;
- failure/revocation;
- auditable message envelope;
- transport adapter boundary.

`communication_ready` nunca equivale a autorización de acción.

### M398 — Governed Physical Transport

**CERRADO.**

Entregó:

- runtime facts de transporte;
- governed binding;
- framing/serialization;
- local TCP;
- listener/dialer lifecycle;
- bounded recovery;
- end-to-end residence channel;
- transport security/abuse guardrails.

M397 conserva autoridad lógica. M398 no activa cognición distribuida, ejecución remota ni replicación de memoria.

### M399 — Governed Self-Diagnostics & Self-Maintenance

**CERRADO.**

Cadena cerrada:

**Observación → tendencia → anomalía → hipótesis → confianza → evidencia → prueba reproducible → propuesta aislada → sandbox → tests → diff → explicación → decisión humana**

La cadena termina en decisión humana. No existe aplicación automática de reparación.

M399.1 añadió además Governed Current Location como prerequisito auditado de etapa.

### M400 — Governed External Intelligence

**CERRADO.**

Cadena cerrada:

**explicit external need → governed route/query → existing execution authority → M400 boundary → external evidence → provenance → verification → assessment → corroboration → ROBY interpretation and decision**

M400 no ejecuta providers/fuentes, no certifica verdad y no otorga autoridad cognitiva.

### M401.1 — Governed Cognitive External Evidence Audit

**CERRADA DOCUMENTALMENTE / SIN CAMBIOS DE CÓDIGO.**

Demostró una limitación contractual real para el uso pre-inferencia de evidencia M400, pero no autorizó cambios en:

- `CognitiveRuntimeOrchestrator`;
- `GovernedRuntimePreparation`;
- `CognitivePipeline`;
- `RuntimeCompositionRoot`;
- `OfficialConversationGateway`.

---

# 6. Dimensión actual del código

Las cifras exactas de archivos/líneas del corte M400.9 no se recalculan en este documento.

El último inventario maestro cuantitativo consolidado Post-M395.5 registró aproximadamente 1.840 archivos Python y ~312.212 líneas en las seis áreas principales. Ese dato se conserva como referencia histórica, no como medición exacta de M400.9.

Regla:

> El crecimiento del repositorio no justifica por sí mismo dividir módulos ni crear nuevas autoridades.

---

# 7. Arquitectura real actual

## Frontera de aplicación — `UnifiedBrain`

- entrada de aplicación;
- delegación;
- no autoridad cognitiva global.

## Frontera conversacional — `OfficialConversationGateway`

- única frontera conversacional productiva;
- coordina el turno;
- conserva las autoridades de dominio.

## Núcleo cognitivo canónico — `CanonicalCognitiveCore`

- representación canónica;
- observabilidad;
- snapshots;
- mapa de dominios;
- `observational=True`;
- `execution_authority=False`.

No es un segundo executor.

## Composición — `RuntimeCompositionRoot`

- composición;
- wiring;
- no decisión cognitiva;
- permanece único.

## Lifecycle — `OfficialROBYRuntime`

- inicio/parada;
- residentes;
- estado operacional;
- no autoridad cognitiva.

## Herramientas — `ToolGatewayManager`

- frontera de ejecución gobernada;
- permisos/policy;
- capabilities externas.

## Residencia distribuida — `core.residence_domain`

- representación declarativa de residencias autorizadas;
- no segundo ROBY;
- no replicación implícita;
- no runtime distribuido autónomo.

## Conectividad — `core.connectivity_domain`

- identidad lógica de peer;
- autenticación/admisión/sesión/readiness/revocación;
- no acción autorizada por conectividad.

## Transporte físico — `core.physical_transport`

- canal físico subordinado a M397;
- framing y carrier;
- no identidad, no autoridad cognitiva, no ejecución remota.

## Recursos externos — `ExternalResourceRegistryAuthority`

- registro declarativo;
- identidad/estado/autorización/conectividad declarativa;
- no I/O.

## Inteligencia externa — `core.governed_external_intelligence`

- boundary canónico de admisión de evidencia externa;
- provenance;
- verification;
- assessment;
- corroboration;
- no ejecución externa;
- no autoridad cognitiva.

---

# 8. Estado operacional: qué está realmente vivo

## Por turno

- `UnifiedBrain`;
- `OfficialConversationGateway`;
- runtime conversacional;
- pipeline;
- capability routing;
- observabilidad del turno.

## Condicional

- memoria;
- planificación;
- decisión/coordinación;
- reasoning;
- retrieval;
- Calendar;
- Gmail;
- mapas;
- clima;
- cámara;
- voz;
- capacidades externas configuradas.

## Consultivo

- planning;
- reasoning;
- reflection contributors;
- cognitive maturity;
- análisis gobernado.

## Residentes

- cognitive core resident;
- battery awareness;
- reminders;
- proactividad gobernada;
- otros residentes configurados.

## Contractual/diagnóstico

- residence domain M396;
- connectivity M397;
- physical transport M398 cuando no está activado por aplicación;
- self-diagnostics artifacts M399;
- governed external intelligence M400;
- inventories;
- readiness;
- certifications;
- stabilization;
- evidence modules;
- mapas de autoridad.

No participar en todos los turnos no significa estar muerto.

---

# 9. Inventario funcional maestro

La clasificación sigue usando:

- **COMPLETO**: terminado para el alcance declarado;
- **AVANZADO/PARCIAL**: capacidad real sin cubrir toda la visión;
- **FUNDACIONAL**: contrato/modelo preparado sin operación integral;
- **FUTURO/PENDIENTE**: capacidad integral no cerrada.

## 9.1 Cerebro y cognición

### Núcleo cognitivo
**COMPLETO / CERTIFICADO para su arquitectura actual.**

### Memoria
**AVANZADA.**

### Modelo mental / world model
**AVANZADO / CERTIFICADO.**

### Planificación
**AVANZADA / CERTIFICADA.**

### Aprendizaje
**ALTO CONTROLADO.**

### Reflexión
**AVANZADA / ALINEADA.**

### Cognitive maturity
**AVANZADA.**

### Uso cognitivo directo de evidencia M400
**NO CERRADO OPERACIONALMENTE.**

Existe auditoría M401.1, no implementación certificada.

## 9.2 Conversación y compañía

Se mantienen los estados Post-M395.5: conversación contextual, largo plazo, personalidad, explicaciones, identidad conversacional y convivencia permanecen avanzadas, sin atribución de consciencia o emoción humana real.

## 9.3 Organización personal

Objetivos, proyectos, tareas, recordatorios y agenda continúan avanzados/operativos según su contrato. Calendar externo sigue siendo una capability diferente y condicional.

---

# 10. Conocimiento del mundo

ROBY mantiene una representación interna gobernada de personas, hogar, lugares, objetos, eventos, relaciones y contexto.

La incorporación de M400 no altera esta regla:

> **evidencia externa ≠ conocimiento interno.**

La admisión/verification/assessment/corroboration de una pieza externa no la convierte automáticamente en memoria ni world-model persistente.

---

# 11. Percepción

## Texto
**REAL / OPERATIVO.**

## Voz
**REAL CONDICIONADA POR HARDWARE Y CONFIGURACIÓN.**

## Cámara local
**REAL CONDICIONAL.**

## Vision Core
Detección de personas, rostro como detección, OCR, QR/códigos, objetos y comprensión de escena permanecen implementados según sus contratos.

## Android State / Notifications / Clipboard / Files / Sensors
**COMPLETOS COMO CONTRATOS GOBERNADOS READ-ONLY.**

## Current Location M399.1
**CAPACIDAD GOBERNADA INCORPORADA**, sin reinterpretarla como GPS residencial completo o sincronización distribuida.

## Percepción residencial distribuida
**PENDIENTE.**

El M400 real cerró inteligencia externa, no la Residential Perception Foundation prevista originalmente.

Siguen pendientes, como rama del Plan Maestro:

- cámaras IP residenciales;
- sensores domésticos;
- fuentes físicas del hogar;
- integración read-only inicial sobre residencia/nodo gobernado.

---

# 12. Servicios externos e inteligentes

### Weather
**OPERATIVO/GOBERNADO.**

### Gmail
**OPERATIVO/GOBERNADO si configurado.**

### Calendar
**OPERATIVO/GOBERNADO si configurado.**

### Maps
**EXISTENTE/GOBERNADO.**

### Retrieval / información externa histórica
**AVANZADO/GOBERNADO / CONDICIONAL.**

### Governed External Intelligence M400
**CERRADO ARQUITECTÓNICAMENTE COMO FRONTERA DE EVIDENCIA.**

M400 añade:

- mapa de autoridad multiprovider/source;
- boundary común de evidencia;
- integración de resultados ya ejecutados;
- provenance;
- verification;
- execution trace;
- assessment;
- corroboration/contradiction handling.

No añade:

- polling;
- background fetching;
- nueva autoridad cognitiva;
- truth certification;
- ejecución de provider/source dentro de M400;
- research goals autónomos.

### Programación como servicio formal propio
**NO CONSOLIDADA COMO CAPABILITY ESPECÍFICA.**

### Diagramas/gráficos/comparación técnica
Mantienen el estado histórico salvo que una fase futura los formalice explícitamente.

---

# 13. Infraestructura física

## Laptop
**NODO OPERATIVO ACTUAL / PRIMARY HOME práctico.**

M396 exige preservar el comportamiento local como referencia cuando no existen residencias extendidas activas.

## Residencias autorizadas
**MODELADAS CONTRACTUALMENTE.**

M396 soporta identidad, roles, admisión/revocación, endpoints y locality.

## Conectividad lógica
**CERRADA ARQUITECTÓNICAMENTE.**

## Transporte físico
**CERRADO COMO CAPACIDAD REUTILIZABLE.**

Existe local TCP y canal físico gobernado, pero M398 no activa por sí solo un runtime distribuido integral.

## Mini-PC residencial / Residential Node
**PENDIENTE COMO OBJETIVO DEL PLAN MAESTRO.**

La existencia de M396–M398 no equivale todavía a un nodo residencial productivo certificado con lifecycle y responsabilidades concretas.

## Red doméstica
**AVANZADA EN CONTRATOS / PARCIAL EN OPERACIÓN INTEGRAL.**

## Acceso remoto público/cloud relay
**NO CERRADO.**

M398 explícitamente no abre exposición pública, cloud relay ni PKI integral.

## Panel web
**FUTURO.**

---

# 14. Arquitectura distribuida

La visión constitucional sigue siendo:

> **Un ROBY lógico, múltiples residencias/nodos autorizados.**

Estado Post-M400.9:

### Distributed Residence Foundation
**CERRADA — M396.**

### Governed Connectivity
**CERRADA — M397.**

### Governed Physical Transport
**CERRADA — M398.**

### Residential Node productivo
**PENDIENTE.**

### Governed Synchronization
**PENDIENTE.**

El roadmap original esperaba que M399 definiera qué estado se comparte/no comparte, memoria, conocimiento, configuración, conflictos, versionado y recuperación. Esa capacidad fue desplazada por la rama M399 de location/self-diagnostics y debe recuperarse como pendiente, no considerarse resuelta.

### Identidad única distribuida
**FUERTEMENTE FUNDAMENTADA, NO CERRADA COMO EXPERIENCIA DISTRIBUIDA COMPLETA.**

### Seguridad distribuida
**AVANZADA EN AUTH/ADMISSION/SESSION/TRANSPORT GUARDRAILS; AÚN NO ES TOPOLOGÍA DISTRIBUIDA TOTAL.**

### Memoria/knowledge replication
**NO IMPLEMENTADA POR M396–M398.**

M396 prohíbe replicación implícita y M398 explícitamente no implementa memory replication.

---

# 15. Hogar inteligente

ROBY todavía no debe considerarse un sistema integral de hogar inteligente operativo.

Ahora existe una base más fuerte que en M395.5:

- modelo del hogar;
- residencia distribuida M396;
- conectividad M397;
- transporte M398;
- dispositivos/recursos;
- permisos;
- Tool Gateway;
- external resource registry;
- capacidades de percepción local.

Pero siguen faltando como cierre integral:

- Residential Node;
- Governed Synchronization;
- cámaras IP residenciales;
- sensores domésticos;
- discovery gobernado;
- control físico específico del hogar;
- política operacional doméstica integral.

Las automatizaciones físicas generales permanecen fuera de alcance hasta cerrar esa infraestructura.

---

# 16. Identidad

La identidad declarada/perfiles permanece avanzada.

M396/M397 agregan identidad de residencia y peer sin confundirla con identidad cognitiva de ROBY.

Reglas adicionales:

- `ResidenceId` no equivale a dirección de transporte;
- peer autenticado no equivale a peer admitido;
- admisión no equivale a autorización de acción;
- carrier/TCP no equivale a identidad;
- ninguna residencia crea otro ROBY.

La biometría por voz/rostro/escritura continúa sin cerrarse como identidad biométrica general.

---

# 17. Estado afectivo, empatía y consciencia

Sin cambios de autoridad respecto del Estado Maestro Post-M395.5.

ROBY dispone de relación, personalidad, regulación funcional simulada, estados cognitivos, reflexión y adaptación expresiva.

Se mantiene la frontera:

- empatía funcional: avanzada como modelado/respuesta contextual;
- estado afectivo simulado: existe;
- emociones humanas reales: no afirmables;
- consciencia subjetiva: no demostrada/no clasificable.

M396–M400 no modifican esta frontera.

---

# 18. Recursos externos e inteligencia externa

## External Resource Registry

**IMPLEMENTADO Y AISLADO POR DISEÑO.**

Sigue representando recursos conocidos, estados, permisos/autorización, conectividad declarativa y auditoría sin I/O.

## M400 Governed External Intelligence

**IMPLEMENTADO Y CERRADO COMO FRONTERA DE EVIDENCIA.**

M400 no reemplaza External Resource Registry, Tool Gateway, provider routing, source execution, M397 connectivity ni M398 transport.

Su ownership es diferente:

> gobernar cómo resultados externos ya producidos son admitidos, trazados, verificados, evaluados y corroborados como evidencia subordinada.

Reglas permanentes M400:

- ROBY conserva autoridad cognitiva;
- providers y sources permanecen distintos;
- provenance precede verification;
- verification no certifica verdad;
- assessment no certifica verdad;
- confidence no es certeza;
- corroboration no es verdad;
- mayoría no es verdad;
- actor diversity no garantiza independencia epistemológica;
- no adquisición externa silenciosa.

---

# 19. Legado y compatibilidad

Sin cambios sustanciales respecto de M395.4:

- `core.hal`: `LEGACY_ISOLATED`;
- `core.roby`: `LEGACY_ISOLATED`;
- M3–M7: congelados;
- `m6.response.models`: shim de compatibilidad;
- evidencia, ADR, migration utilities y tests históricos se preservan.

Regla:

> El legado puede sostener compatibilidad, pero no recuperar autoridad productiva principal.

---

# 20. Piezas aisladas: diagnóstico actualizado

## Aisladas correctamente

- External Resource Registry;
- certificaciones;
- inventories;
- stabilization modules;
- migration utilities;
- legado congelado;
- foundations cuyo aislamiento forma parte de su contrato.

## Cerradas pero no activadas como runtime general

- parte de la residencia distribuida M396;
- physical transport M398;
- governed external intelligence M400.

Su no activación global no equivale a código muerto.

## Pendientes reales de integración/etapa

- Residential Node;
- Governed Synchronization;
- Residential Perception;
- decisión Go/No-Go para uso cognitivo M400 después de M401.1.

---

# 21. Deuda técnica y arquitectónica restante

La deuda Post-M400.9 debe distinguirse de los pendientes funcionales del Plan Maestro.

## 21.1 No reabrir M395 sin necesidad demostrada

`OfficialConversationGateway`, `CognitivePipeline`, `GovernedRuntimePreparation`, `CognitiveRuntimeOrchestrator` y `RuntimeCompositionRoot` permanecen zonas sensibles.

M401.1 detectó una posible limitación contractual pre-inferencia, pero **no autoriza aún una refactorización**.

## 21.2 Deuda distribuida pendiente

- nodo residencial productivo;
- sincronización gobernada;
- política de conflictos/versionado/recuperación;
- integración de percepción residencial.

## 21.3 Deuda documental

La documentación raíz debe reflejar M400.9 y recuperar una única línea maestra.

## 21.4 Tamaño de módulos

Se mantiene la regla Post-M395:

> no dividir por longitud; sólo intervenir cuando exista una razón funcional, contractual o de dependencias demostrada.

---

# 22. Deuda documental

Después de M396–M400 reaparece el riesgo que el Estado Maestro Post-M395.5 intentó resolver: múltiples documentos de cierre pueden describir correctamente su etapa pero no el estado global.

## Regla actualizada

1. Este Estado Maestro Post-M400.9 describe el presente.
2. Los cierres M396–M400 prueban sus dominios.
3. M401.1 describe una auditoría, no una nueva arquitectura productiva.
4. README, `architecture_rules.md`, `CHANGELOG_ARCHITECTURE.md` y documentos de instalación canónica deben señalar el corte M400.9.
5. No crear otro “Estado Maestro” en cada incremento.
6. El próximo Estado Maestro sólo debe emitirse cuando cambie nuevamente una época arquitectónica.

---

# 23. Qué conservar sin tocar

No iniciar limpieza indiscriminada.

Conservar:

- Constitution/VISION;
- architecture rules;
- tests históricos;
- ADR;
- milestones;
- certifications;
- M361 baseline;
- Atlas;
- M394/A;
- M395 docs;
- M396–M400 closure docs;
- M401.1 audit closure;
- External Resource Registry;
- Residence Domain;
- Connectivity Domain;
- Physical Transport;
- Self-Diagnostics;
- Governed External Intelligence;
- Device foundation;
- legacy shims;
- relationship memory;
- vision core;
- capability registry.

La simplificación futura debe seguir siendo quirúrgica.

---

# 24. Visión futura consolidada

M500.0 continúa siendo una visión estratégica válida, pero el estado M400.9 obliga a distinguir lo ya avanzado de lo todavía pendiente.

### Ya avanzado respecto de la visión

- identidad/residencia distribuida declarativa;
- conectividad lógica;
- transporte físico gobernado;
- autodiagnóstico gobernado;
- inteligencia externa gobernada.

### Pendiente prioritario del tronco físico/distribuido

1. Residential Node.
2. Governed Synchronization.
3. Residential Perception.

### Pendiente posterior

- panel web gobernado;
- cámaras residenciales operativas;
- GPS/movilidad integral;
- wearables;
- identidad multimodal;
- herramientas inteligentes adicionales;
- hogar inteligente operacional.

---

# 25. Roadmap recomendado desde M400.9

La numeración M398–M400 del roadmap Post-M395.5 fue ocupada por trabajo real intercalado. No se recomienda renumerar retrospectivamente.

## Tronco maestro recuperado

### Pendiente A — Residential Node

Objetivo:

materializar una residencia/nodo real sobre M396–M398 sin crear otro cerebro, memoria o autoridad cognitiva.

Debe definir al menos:

- qué runtime mínimo vive en el nodo;
- qué capabilities puede alojar;
- cómo se registra su lifecycle;
- qué permanece en el primary home;
- qué ocurre ante pérdida de conectividad;
- qué acciones siguen requiriendo autoridad central.

### Pendiente B — Governed Synchronization

Debe responder explícitamente:

- qué estado se comparte;
- qué estado nunca se comparte;
- memoria;
- knowledge;
- configuración;
- conflictos;
- versionado;
- recuperación;
- aislamiento de credenciales;
- revocación.

M396-I09 `No Implicit Replication` permanece rector.

### Pendiente C — Residential Perception Foundation

Sólo después de residencia/synchronization suficientemente cerradas:

- cámaras IP;
- sensores;
- fuentes físicas del hogar;
- inicialmente read-only;
- provenance del canal;
- permisos;
- observabilidad/fallo seguro.

## Rama M401 — Governed Cognitive Use of External Evidence

### Estado

**M401.1 AUDITORÍA CERRADA.**

### Siguiente gate

Realizar un **Go/No-Go técnico**.

**GO** sólo si puede demostrarse que el objetivo cognitivo de M401 requiere un cambio mínimo y controlado que preserve M395.

**NO-GO / DIFERIR** si para lograrlo se necesita reabrir ampliamente el pipeline/runtime sin necesidad operacional demostrada.

### Regla de prioridad

M401 no debe convertirse en una secuencia indefinida de perfeccionamiento cognitivo que vuelva a desplazar Residential Node, Synchronization y Residential Perception.

---

# 26. Por qué recuperar el tronco distribuido

La lógica Post-M395.5 sigue siendo válida:

> **¿Dónde vive físicamente una capacidad cuando la laptop no está presente?**

M396–M398 avanzaron mucho la respuesta, pero todavía falta convertir contracts/conectividad/transporte en una residencia productiva y definir cómo se comparte estado.

Por eso la secuencia conceptual recuperada es:

**residencia declarativa → conectividad → transporte → nodo residencial → sincronización → percepción residencial**

M399 y M400 se preservan como ramas intercaladas legítimas, no como sustitutos de los pasos desplazados.

---

# 27. Qué NO recomiendo como siguiente fase

No abrir todavía, salvo necesidad explícita demostrada:

- autonomía física general;
- Home Assistant operativo integral;
- reconocimiento biométrico general;
- GPS continuo;
- wearables médicos;
- polling masivo;
- cámaras remotas generalizadas antes de cerrar Residential Perception;
- control Wi-Fi arbitrario;
- compras autónomas;
- entrenamiento neuronal propio;
- self-repair automático;
- external research loops autónomos;
- segundo orchestrator cognitivo;
- segundo composition root;
- nueva autoridad cognitiva para evidencia externa.

---

# 28. Clasificación de datos recomendada

Se conserva la clasificación mínima:

### Pública
Información sin sensibilidad personal especial.

### Personal
Agenda, proyectos, preferencias.

### Privada
Contactos, conversaciones, archivos personales.

### Sensible
Ubicación, biometría, cámaras, salud, credenciales.

M396–M400 refuerzan la necesidad de que transporte, synchronization y evidencia externa preserven clasificación, provenance, credenciales aisladas y permisos explícitos.

---

# 29. Criterio definitivo para nuevas capacidades

Antes de crear o modificar una capacidad, responder:

1. ¿Qué problema real resuelve?
2. ¿Qué autoridad existente lo gobierna?
3. Si no existe autoridad, ¿por qué hace falta una nueva?
4. ¿Es representación, decisión, ejecución o infraestructura?
5. ¿Participa por turno, bajo condición, como residente o sólo como diagnóstico?
6. ¿Qué datos maneja y qué sensibilidad tienen?
7. ¿Qué puede fallar?
8. ¿Cómo falla seguro?
9. ¿Qué pruebas demostrarán que está realmente operativo?
10. ¿Cómo se revierte?
11. ¿Qué documento maestro cambia?
12. ¿Introduce un ciclo o inversión de capa?
13. **¿Qué línea del Plan Maestro avanza?**
14. **¿Qué pendiente anterior desplaza?**
15. **¿El hueco descubierto bloquea el objetivo actual o puede diferirse?**

Si estas preguntas no pueden responderse, la capacidad todavía no está lista para código.

Todo incremento futuro deberá declarar además:

**IMPACTO EN PLAN MAESTRO**  
**DECISIÓN PREVIA QUE PRESERVA**  
**PENDIENTE QUE RESUELVE**  
**NUEVO HUECO CREADO**  
**NIVEL DE TERMINACIÓN**  
**GO/NO-GO**

---

# 30. Estado global por dominio

| Dominio | Estado maestro Post-M400.9 |
|---|---|
| Gobernanza | **ALTO / CERTIFICADO** |
| Núcleo cognitivo | **ALTO / CERTIFICADO** |
| Memoria | **ALTO** |
| Modelo mental | **ALTO** |
| Planificación | **ALTO CONTROLADO** |
| Aprendizaje | **ALTO CONTROLADO** |
| Conversación | **ALTO** |
| Personalidad/explicación | **ALTO** |
| Organización personal | **ALTO, contactos generales aún parciales** |
| Mundo interno/modelo del mundo | **ALTO DESCRIPTIVO** |
| Relación | **ALTO FUNCIONAL** |
| Reflexión/madurez | **ALTO** |
| Percepción local | **MEDIO/ALTO según canal** |
| Android | **ALTO CONTRACTUAL / MEDIO FÍSICO** |
| Distributed Residence Foundation | **CERRADA ARQUITECTÓNICAMENTE** |
| Governed Connectivity | **CERRADA ARQUITECTÓNICAMENTE** |
| Physical Transport | **CERRADO / NO RUNTIME DISTRIBUIDO TOTAL** |
| Residential Node | **PENDIENTE** |
| Governed Synchronization | **PENDIENTE** |
| Self-Diagnostics | **ALTO / CERRADO / HUMANO-EN-EL-BUCLE** |
| External Resource Registry | **ALTO CONTRACTUAL / AISLADO POR DISEÑO** |
| Governed External Intelligence | **CERRADO ARQUITECTÓNICAMENTE** |
| Cognitive Use of External Evidence | **AUDITADO / NO IMPLEMENTADO** |
| Residential Perception | **PENDIENTE** |
| Hogar inteligente | **FUNDACIONAL/PARCIAL** |
| GPS/movilidad integral | **PARCIAL/FUTURO** |
| Wearables | **INEXISTENTE** |
| Identidad biométrica | **INEXISTENTE** |
| Panel web | **INEXISTENTE** |
| Autonomía física | **BAJA DELIBERADAMENTE** |
| Deep learning propio | **NO PRIORITARIO** |
| Consciencia | **NO AFIRMABLE** |

---

# 31. Qué significa “terminado” a partir de ahora

Se conserva la distinción:

### Terminado arquitectónicamente
Contrato, autoridad, invariantes y pruebas cerrados.

### Terminado operacionalmente
Existe wiring productivo y ruta real.

### Terminado físicamente
Existe hardware/transporte/configuración real y prueba física.

### Terminado como experiencia
Carlos/Cristina pueden usarlo de extremo a extremo de forma estable.

Aplicación a la nueva época:

- M396 está terminado arquitectónicamente, no significa runtime distribuido completo.
- M397 está terminado arquitectónicamente, no significa autorización de acción remota.
- M398 tiene transporte físico real/testeable, no significa cognición distribuida activa.
- M399 está terminado para autodiagnóstico/revisión, no significa auto-repair.
- M400 está terminado para gobernanza de evidencia externa, no significa uso cognitivo pre-inferencia cerrado.

---

# 32. Documento fuente vs estado actual

Después de esta actualización:

- M380 explica por qué fue necesaria la auditoría original.
- M388 explica la certificación del cerebro.
- M391 explica la arquitectura cognitiva de esa época.
- M394 explica recursos externos declarativos.
- M394.A explica la auditoría integral.
- M395 explica la consolidación del núcleo operacional.
- Estado Maestro Post-M395.5 explica el corte anterior y su roadmap.
- M396 explica Distributed Residence Foundation.
- M397 explica Governed Residence Connectivity.
- M398 explica Governed Physical Transport.
- M399 explica Current Location y Self-Diagnostics.
- M400 explica Governed External Intelligence.
- M401.1 explica la auditoría de uso cognitivo y el mapa de desfases.
- M500 conserva la visión futura.
- **Este documento explica dónde está parado ROBY en M400.9.**

---

# 33. Decisiones congeladas en este Estado Maestro

A partir del corte M400.9 quedan establecidas:

1. **M400.9 es la baseline oficial actual.**
2. **11.027 tests / Ruff limpio / M361 sincronizada / 0 regresiones** constituyen la certificación declarada de cierre.
3. No se inicia otra gran refactorización general.
4. M3–M7 permanecen congelados.
5. `CanonicalCognitiveCore` permanece observacional, no executor.
6. `RuntimeCompositionRoot` sigue siendo único.
7. `OfficialConversationGateway` sigue siendo la única frontera conversacional oficial.
8. No se crean nuevas autoridades por conveniencia organizativa.
9. M396 no autoriza segundo ROBY, replicación implícita ni autonomía de residencia.
10. M397 connectivity nunca equivale a autorización de acción.
11. M398 transport nunca equivale a identidad, trust o autoridad cognitiva.
12. M399 termina en revisión humana y no autoriza self-repair automático.
13. M400 evidencia externa no equivale a verdad, certeza, conocimiento interno ni autoridad cognitiva.
14. M401.1 queda cerrada como auditoría; no autoriza todavía cambios de runtime.
15. Residential Node, Governed Synchronization y Residential Perception permanecen pendientes del Plan Maestro.
16. Los trabajos intercalados M398–M400 se preservan; no se renumeran ni deshacen.
17. Toda auditoría futura se contrasta contra este Estado Maestro antes de abrir un nuevo milestone.
18. Un hueco detectado no abre automáticamente una nueva etapa.
19. La documentación futura debe actualizar este Estado Maestro por épocas, no crear una nueva referencia maestra en cada incremento.

---

# 34. Acción inmediata recomendada

## Checkpoint 1 — Canonical Documentation Sync Post-M400.9

Sin cambios de arquitectura productiva.

Objetivo:

- instalar este Estado Maestro Post-M400.9 como referencia actual;
- actualizar referencias de vigencia en `README.md`;
- verificar/sincronizar `architecture_rules.md`;
- actualizar `CHANGELOG_ARCHITECTURE.md` hasta M400.9;
- actualizar `ROOT_DOCUMENTATION_INSTALLATION.md`/índice canónico equivalente;
- enlazar M396–M400 como cierres certificados;
- enlazar M401.1 como auditoría cerrada, no implementación;
- marcar Estado Maestro Post-M395.5 como histórico rector del corte anterior.

## Checkpoint 2 — Go/No-Go M401

Responder únicamente:

> **¿Existe una integración cognitiva mínima M400→ROBY que pueda implementarse sin reabrir ampliamente la arquitectura consolidada por M395?**

Si **GO**:

- alcance mínimo;
- no segundo cerebro;
- no segunda autoridad;
- no persistencia automática;
- no external execution desde contributor;
- tests de invariantes;
- vuelta inmediata al Plan Maestro después del cierre.

Si **NO-GO/DIFERIR**:

- congelar M401 tras la auditoría;
- recuperar el tronco distribuido.

## Checkpoint 3 — Recuperar Plan Maestro

Orden funcional recomendado:

**Residential Node → Governed Synchronization → Residential Perception**

La numeración se asignará después de fijar el alcance; no se reutilizan M398–M400.

---

# 35. Resumen final

ROBY XI.2 llega a M400.9 con un núcleo cognitivo consolidado y nuevas fronteras gobernadas que amplían su relación con el mundo exterior sin fragmentar su autoridad.

Desde M395.5 se cerraron:

- Distributed Residence Foundation;
- Governed Residence Connectivity;
- Governed Physical Transport;
- Governed Self-Diagnostics & Self-Maintenance;
- Governed External Intelligence.

La evolución fue válida, pero desplazó tres pasos centrales del roadmap original:

- Residential Node;
- Governed Synchronization;
- Residential Perception.

M401.1 detectó un posible hueco real entre evidencia M400 y cognición pre-inferencia, pero el proyecto no debe convertir cada hallazgo de auditoría en una nueva refactorización.

La nueva disciplina de continuidad es:

> **Plan Maestro → baseline real → auditoría → necesidad demostrada → cambio mínimo → validación → sincronización documental → regreso al Plan Maestro.**

No:

> **auditoría → nueva arquitectura → nueva auditoría → nueva arquitectura.**

ROBY no necesita otro cerebro.

Necesita seguir extendiendo de forma gobernada el mismo cerebro hacia capacidades reales, sin perder de vista los pendientes estructurales ya acordados.

---

# 36. Referencia oficial de continuidad

**Estado actual:** M400.9 — Governed External Intelligence Stabilization & Closure  
**Validación:** Ruff limpio · M361 sincronizada · 11.027 tests · regresiones 0  
**M401.1:** auditoría documental cerrada · cambios de código 0 · cambio de runtime autorizado: NO  
**Documento rector actual:** ROBY XI.2 — Estado Maestro Integral Post-M400.9  
**Pendientes maestros recuperados:** Residential Node · Governed Synchronization · Residential Perception  
**Próximo checkpoint:** Canonical Documentation Sync Post-M400.9  
**Próxima decisión técnica:** Go/No-Go M401

> **Toda evolución futura debe contrastarse primero contra este Estado Maestro, la Constitución permanente, la baseline real inmediatamente anterior y las invariantes certificadas.**

# 37. M401 — Governed Cognitive Use of External Evidence — CIERRE

**Baseline certificada de cierre:** M401.3 — Minimal Productive External Evidence Handoff  
**Validación:** Ruff limpio · M361 sincronizada · 11.042 tests · regresiones 0  
**Estado:** **CERRADO / OPERACIONALMENTE INTEGRADO**

M401 resuelve el hueco identificado por M401.1 mediante una integración mínima y gobernada:

**necesidad externa → autoridad de ejecución existente → M400 → admisión cognitiva M401 → handoff explícito por turno → CognitiveRuntimeOrchestrator existente → inferencia ROBY**

M401.2 introduce la admisión cognitiva estructurada mínima necesaria para preservar lineage y
semántica M400 sin convertir evidencia en strings opacos ni conceder autoridad externa.
M401.3 completa el handoff productivo explícito por turno hasta el runtime cognitivo antes de
la inferencia, reutilizando las autoridades de adquisición/ejecución ya existentes.

Quedan preservados como invariantes de cierre:

- evidencia externa ≠ conocimiento interno;
- confianza ≠ certeza;
- corroboración ≠ verdad;
- información externa ≠ autoridad cognitiva;
- lineage M400 íntegro;
- sin promoción automática a memoria, conocimiento, learning, planning o permisos;
- evidencia rechazada permanece rechazada;
- flujo explícito por turno, sin `last_result`, cache global ni blackboard canónico;
- M401 consume evidencia ya obtenida y no reejecuta providers/fuentes;
- un único ROBY, un único cerebro, un único `RuntimeCompositionRoot`;
- `OfficialConversationGateway` conserva su rol de frontera conversacional oficial.

No se autoriza M401.4 por continuidad automática. Búsqueda autónoma, polling, background
fetching, knowledge ingestion, aprendizaje automático desde Internet y nuevas autoridades
de retrieval quedan fuera del alcance cerrado.

## 37.1 Impacto en el Plan Maestro

**IMPACTO EN PLAN MAESTRO:** cierra la rama intercalada M400→M401 sin desplazar nuevos pasos.  
**DECISIÓN PREVIA QUE PRESERVA:** una autoridad por capacidad y cerebro lógico único.  
**PENDIENTE QUE RESUELVE:** uso cognitivo gobernado, transitorio y trazable de evidencia M400.  
**NUEVO HUECO CREADO:** ninguno que bloquee el cierre.  
**NIVEL DE TERMINACIÓN:** arquitectónico y operacional para el handoff cognitivo.  
**GO/NO-GO:** M401 cerrado; NO-GO para M401.4 automático.

## 37.2 Retorno al tronco maestro

Con M401 cerrado, la prioridad vuelve al roadmap distribuido recuperado:

**Residential Node → Governed Synchronization → Residential Perception Foundation**.

---

# 38. Referencia oficial de continuidad Post-M401

**Estado actual:** M401 — Governed Cognitive Use of External Evidence — CERRADO  
**Última baseline validada:** M401.3  
**Validación:** Ruff limpio · M361 sincronizada · 11.042 tests · regresiones 0  
**Documento rector:** ROBY XI.2 — Estado Maestro Integral, actualizado Post-M401  
**Próxima dirección:** retorno al tronco maestro distribuido  
**Próximo objetivo conceptual:** Residential Node

> **M401 queda cerrado. La evidencia externa puede participar en la cognición sin convertirse en conocimiento, certeza, verdad ni autoridad.**
