# ROBY XI.2 — ESTADO MAESTRO INTEGRAL POST-M405

**Documento rector de continuidad del proyecto**  
**Corte arquitectónico:** M405.1 — Information Classification Foundation  
**Estado de certificación:** **11,161 tests aprobados · Ruff limpio · baseline M361 sincronizada · regresiones 0**  
**Fecha de corte:** 11 de agosto de 2026

---

## 0. Propósito y autoridad documental

Este archivo es la referencia canónica del **estado actual Post-M405**. Sustituye como descripción corriente al antiguo Estado Maestro Post-M400.9, que se conserva como evidencia histórica en `docs/ROBY_XI2_ESTADO_MAESTRO_INTEGRAL_POST_M400_9_HISTORICAL.md`.

Los documentos históricos no se eliminan y mantienen valor probatorio. Cuando exista una diferencia entre un estado histórico y este documento sobre qué está abierto/cerrado hoy, prevalece este Estado Maestro Post-M405.

---

# 1. Dictamen ejecutivo

ROBY XI.2 continúa siendo un único sistema cognitivo personal, privado y gobernado. Desde el corte Post-M400.9 se recuperó el tronco físico/distribuido sin crear segundo cerebro, segundo `RuntimeCompositionRoot` ni autoridades paralelas.

Estado actual del tronco recuperado:

- **M401 — Governed Cognitive Use of External Evidence:** CLOSED.
- **M402 — Residential Node:** CLOSED arquitectónica y operacionalmente; certificación de despliegue físico separada.
- **M403 — Governed Synchronization:** CLOSED arquitectónica y mínimamente operacional.
- **M404 — Residential Perception:** FORMAL INTERIM CLOSED arquitectónicamente y para la ruta operacional mínima local; hardware doméstico distribuido pendiente de certificación física.

La baseline oficial Post-M405.1 está validada con **11,161 tests, Ruff limpio, M361 sincronizada y 0 regresiones**.

- **M405 — Information Classification:** CLOSED como foundation neutral con primer consumer M403 outbound; receiver-side enforcement diferido por falta de consumidor real.

No existe un bloqueo arquitectónico que justifique M404.3 ni M405.2 por continuidad automática.

---

# 2. Principios permanentes

Permanecen rectores:

1. un único ROBY / un único cerebro lógico;
2. un único `RuntimeCompositionRoot`;
3. una autoridad por capacidad;
4. integración antes que duplicación;
5. no crear managers/registries paralelos cuando ya existe owner canónico;
6. no implicit replication;
7. observación != autoridad;
8. evidencia != conocimiento;
9. percepción != interpretación;
10. interpretación != memoria;
11. comunicación/readiness != permiso de acción;
12. cambios pequeños, verificables y reversibles;
13. documentación y código deben permanecer sincronizados;
14. un hueco de auditoría no abre automáticamente un milestone;
15. una dependencia física externa no debe transformarse en abstracción especulativa.
16. classification != authorization;
17. classification != synchronization shareability;
18. classification puede restringir una frontera, nunca ampliar permisos existentes;
19. `UNCLASSIFIED` nunca equivale a `PUBLIC`.

---

# 3. Jerarquía documental actual

## Nivel A — Constitución permanente

- `VISION.md`;
- `architecture_rules.md`;
- decisiones constitucionales y ADR vigentes.

## Nivel B — Estado actual

- **`ESTADO_MAESTRO_INTEGRAL.md` — Post-M405** (este documento).

## Nivel C — Cierres recientes del tronco

- `docs/M401_GOVERNED_COGNITIVE_USE_OF_EXTERNAL_EVIDENCE_CLOSURE_AUDIT.md`;
- `docs/M402_RESIDENTIAL_NODE_FORMAL_CLOSURE.md`;
- `docs/M403_GOVERNED_SYNCHRONIZATION_FORMAL_CLOSURE.md`;
- `docs/M404_RESIDENTIAL_PERCEPTION_FORMAL_INTERIM_CLOSURE.md`;
- `docs/M405_INFORMATION_CLASSIFICATION_FORMAL_CLOSURE.md`.

Estados maestros de cortes anteriores permanecen históricos y no compiten con este documento para describir el presente.

---

# 4. Estado del núcleo y cognición

El núcleo cognitivo, memoria, conocimiento, planificación, aprendizaje, conversación y personalidad permanecen consolidados bajo las autoridades existentes. M401 cerró el uso cognitivo gobernado de evidencia externa mediante un handoff mínimo y explícito, sin acquisition manager, provider authority, segundo orchestrator ni promoción automática a memoria/knowledge.

No se autoriza una nueva refactorización general del cerebro como consecuencia de M404.

---

# 5. Estado físico/distribuido Post-M405

## M396 — Distributed Residence

**CLOSED.**

Posee `ResidenceId`, admission/revocation y capabilities declaradas. Una residencia no equivale a address, transporte ni autoridad cognitiva.

## M397 — Governed Connectivity

**CLOSED.**

Posee autenticación, peer/session/readiness y comunicación auditable. Readiness no autoriza acción.

## M398 — Governed Physical Transport

**CLOSED.**

Posee framing/delivery y recovery acotado. Transporte disponible no equivale a identidad, persistence ni cognitive acceptance.

## M402 — Residential Node

**CLOSED arquitectónica y operacionalmente.**

Existe binding/snapshot/lifecycle/bootstrap residencial mínimo sin segundo cerebro ni segundo root. La prueba sobre un mini-PC concreto sigue como **Physical Deployment Certification** separada y no constituye deuda M402.

## M403 — Governed Synchronization

**CLOSED arquitectónica y mínimamente operacionalmente.**

M403 define shareability, envelope/admission, wiring sobre M397/M398, revision/fingerprint/freshness/conflict y transient mirror semantics. No añade durable replication, automatic replay, merge ni memory/knowledge replication.

## M404 — Residential Perception

**FORMAL INTERIM CLOSED.**

### Arquitectura

CLOSED mediante M404.1:

- source/residence binding;
- physical observation;
- provenance;
- fail-closed admission;
- read-only semantics;
- reuse de M396 `ResidenceId` y External Resource Registry `resource_id`;
- Vision Core preservado como interpreter.

### Operación mínima

CLOSED mediante M404.2:

- una captura física local real;
- un `CameraAdapter.capture()` por adquisición;
- metadata segura del frame;
- `ResidentialPhysicalObservation`;
- admission M404;
- sin raw media, streaming, persistence, synchronization o device control.

### Certificación física residencial distribuida

**PENDING EXTERNAL HARDWARE.**

No existe todavía una fuente doméstica concreta certificada en un Residential Node que demuestre:

`household physical source → M404 → M403 → Primary Home`.

Eso es dependencia física, no hueco contractual.

---

# 6. Ownership canónico de Residential Perception

- **M396:** residence identity/admission/capabilities.
- **External Resource Registry:** physical/external `resource_id`, registration and authorization facts.
- **M404:** perceptual source binding, physical observation representation and admission.
- **Physical adapter:** source-specific acquisition only.
- **Vision Core:** visual interpretation.
- **M403:** cross-residence synchronization when explicitly required.
- **Cognition:** later interpretation/use under existing cognitive governance.

Prohibiciones:

- no `ResidentialSourceRegistry` paralelo;
- no `ResidentialVisionCore`;
- no source-as-cognitive-authority;
- no automatic memory/knowledge/action from perception.

---

# 7. Estado de fuentes físicas

## Cámara local

**REAL / OPERACIONAL PARA CAPTURA PUNTUAL M404.2.**

No implica percepción continua ni recording.

## Sensores Android M374

**CERRADOS COMO CONTRATOS READ-ONLY, NO COMO ADQUISICIÓN FÍSICA RESIDENCIAL CERTIFICADA.**

No deben utilizarse como evidencia de sensor doméstico productivo sin I/O real.

## Sensor doméstico residencial

**PENDING EXTERNAL HARDWARE / SOURCE-SPECIFIC INTEGRATION.**

M404 binding/admission ya es suficiente. No se autoriza framework genérico antes de existir una fuente concreta.

## Cámara IP residencial

**PENDING EXTERNAL HARDWARE + SOURCE-SPECIFIC ACQUISITION.**

Además requerirá una decisión separada de media/reference para garantizar que Vision interprete el mismo artifact adquirido, sin recapture ni persistence implícita.

## Node telemetry

Battery/host telemetry puede ser I/O físico real, pero no debe reinterpretarse como percepción ambiental del hogar.

---

# 8. Governed Synchronization después de M404

M403 está preparado para transportar explícitamente una futura observación M404 cross-residence. Sin embargo:

- M404 admission != synchronization;
- synchronization != persistence;
- synchronization != interpretation;
- synchronization != cognitive acceptance;
- una observación local Primary Home no se sincroniza consigo misma sólo para ejercitar infraestructura.

M404 → M403 debe abrirse productivamente cuando exista una fuente remota real que lo requiera.

---

# 9. Information Classification Post-M405

## M405 — Canonical Information Classification

**CLOSED — M405.1.**

ROBY dispone de un vocabulario neutral canónico de sensibilidad:

- `UNCLASSIFIED`;
- `PUBLIC`;
- `PERSONAL`;
- `PRIVATE`;
- `SENSITIVE`.

La taxonomía es nominal, no ordinal, y no concede acceso, permiso, routing, persistencia, memoria, conocimiento ni acción. Los dominios conservan la semántica de sus propios datos y declaran clasificación cuando una frontera classification-aware lo requiere.

## Primer consumer productivo

M403 consume classification de forma subordinada mediante `SynchronizationClassificationPolicy` durante outbound admission. `SyncShareabilityClass` conserva ownership de elegibilidad de sincronización; classification sólo puede agregar restricciones. Los flows legacy M403 permanecen compatibles cuando no activan policy classification-aware.

## Receiver-side enforcement

**DEFERRED / NO ARCHITECTURAL DEBT.**

Classification no forma parte actualmente de `GovernedSyncEnvelope` ni del carrier M397. El receptor conserva toda su admission estructural M403 existente, pero no revalida sensibilidad de forma independiente. No se autoriza una modificación de envelope/codec por simetría teórica.

Receiver-side enforcement sólo se reabre cuando exista un producer/consumer cross-residence real que necesite conservar classification después del transporte. Ese trabajo requerirá un gate específico de schema, codec y compatibilidad.

## Límites permanentes

- no `InformationClassificationAuthority`;
- no Privacy Manager global;
- no classifier universal;
- no registry global de classification;
- no migración masiva de modelos legacy;
- no inferencia de classification desde `state_domain`;
- no weakening de prohibiciones de dominio;
- outbound guard != end-to-end enforcement.

---

# 10. Dependencias físicas separadas de arquitectura

## Residential Node Physical Deployment Certification

Pendiente ejecutar el nodo en hardware residencial concreto y certificar la ruta física real. No reabre M402.

## M404 Residential Sensor Physical Certification

Pendiente seleccionar hardware real que sea read-only, one-shot capable y produzca payload autocontenido. Una fuente concreta puede justificar un adapter pequeño y source-specific.

## M404 Residential IP Camera Physical Certification

Pendiente dispositivo/protocolo real y media/reference governance. No justifica hoy un `CameraManager`, `MediaRepository` o platform framework.

---

# 11. Qué NO debe abrirse por continuidad

Sin necesidad concreta demostrada, NO abrir:

- M404.3 genérico;
- generic sensor framework;
- MQTT/Home Assistant integral;
- polling/streaming masivo;
- media archive/repository;
- automatic M403 synchronization;
- automatic Vision inference;
- memory/knowledge replication;
- device actuation;
- second orchestrator/root/brain.

---

# 12. Nivel real de terminación

| Capability | Arquitectura | Operación mínima | Física residencial | Experiencia |
|---|---|---|---|---|
| Residential Node M402 | CLOSED | CLOSED | Certification pending | Pending deployment |
| Governed Synchronization M403 | CLOSED | CLOSED minimal | Depends on real peer/source | Partial |
| Residential Perception M404 | CLOSED | CLOSED local one-shot | Household certification pending | Partial |
| Information Classification M405 | CLOSED | CLOSED outbound foundation | N/A | Receiver-side enforcement deferred |

La palabra “cerrado” debe conservar siempre estos calificadores cuando la evidencia física real todavía dependa de hardware/configuración externos.

---

# 13. Tronco maestro recuperado

La secuencia estratégica que había quedado desplazada está ahora arquitectónicamente recuperada:

**Distributed Residence → Governed Connectivity → Physical Transport → Residential Node → Governed Synchronization → Residential Perception**

No queda un hueco arquitectónico interno en este tronco que deba llenarse con código especulativo.

Quedan **certificaciones físicas** y futuras expansiones concretas de fuentes.

---

# 14. Regla para el siguiente trabajo

Antes de abrir otro milestone:

1. contrastar el objetivo contra este Estado Maestro Post-M405;
2. demostrar un consumidor, hardware o necesidad funcional real;
3. identificar el owner canónico existente;
4. preferir reutilización o extensión mínima;
5. separar certificación física de arquitectura;
6. evitar convertir dependencias externas en frameworks prematuros;
7. mantener Ruff limpio, M361 sincronizada, suite completa limpia y 0 regresiones.

---

# 15. Baseline oficial

**M405.1 — Information Classification Foundation**  
**11,161 tests passed**  
**Ruff clean**  
**M361 synchronized**  
**0 regressions**

**M405 Formal Closure & Canonical Documentation Sync Post-M405:** checkpoint documental actual.
