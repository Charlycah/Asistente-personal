# ROBY XI.2 — POST-G21 CONTRACT DESIGN — EXECUTION AUTHORIZATION BOUNDARY

## Estado

**CONTRACT DESIGN — PRE-RED — SIN CAMBIO PRODUCTIVO — NO ABRE G22**

Base de referencia:

`ROBY_XI.2_INTEL-G21_CERTIFIED_PLUS_SAFE_CACHE_CLEANER.zip`

Baseline certificado:

**14.177 PASS · 0 FAIL · Ruff clean**

Este documento congela el contrato arquitectónico entre el cierre inerte de G21/G16 y la ejecución durable existente G18/G17.

---

## 1. Problema exacto

G21 ya produce productivamente:

`ApprovedKnowledgeRevisionEvidence`
+ `owner`
→ existing G15
→ existing G16
→ `GovernedKnowledgeRevisionRequest`
→ STOP.

El `GovernedKnowledgeRevisionRequest` certificado sigue siendo inerte y no concede autoridad de ejecución.

Hoy G18 puede ejecutar un G16 ya certificado cuando ese request llega por `OfficialConversationGateway`, sin una evidencia adicional y explícita de permiso de ejecución.

Por lo tanto, falta una condición gobernada entre:

`CERTIFIED REQUEST`

y:

`DURABLE MEMORY MUTATION`.

---

## 2. Regla rectora congelada

**HUMAN APPROVAL MAY PREPARE/CERTIFY; ONLY AN EXACT, EXPLICIT EXECUTION AUTHORIZATION MAY CROSS INTO DURABLE MEMORY MUTATION.**

Distinciones obligatorias:

- `G14 CONTENT APPROVAL != EXECUTION AUTHORIZATION`
- `APPROVED REVISION != PREPARED REVISION`
- `PREPARED REVISION != CERTIFIED REQUEST`
- `CERTIFIED REQUEST != AUTHORIZED EXECUTION`
- `AUTHORIZED EXECUTION != SUCCESSFUL MEMORY MUTATION`
- `REQUEST PRESENT != PERMISSION TO APPLY`
- `SESSION CONTINUITY != EXECUTION PERMISSION`
- `G16 grants_authority=False` conserva su significado.

---

## 3. Arquitectura objetivo

```text
exact G16 GovernedKnowledgeRevisionRequest
+ explicit human execution response
        ↓
existing human approval authority
        ↓
AuthorizedKnowledgeRevisionExecutionEvidence | None
        ↓
STOP
        ↓
exact G16 request
+ exact execution authorization evidence
        ↓
existing ProductiveGovernedLearningWiring
        ↓
existing G18 productive execution seam
        ↓
existing G17 / OfficialMemoryGateway
        ↓
atomic durable revision
```

No se crea:

- una segunda autoridad humana;
- un segundo Memory gateway;
- un segundo productive wiring;
- un nuevo revision executor;
- un nuevo writer.

---

## 4. Autoridad humana

La evaluación de la respuesta humana debe permanecer bajo la autoridad humana existente:

`M369ExplicitHumanLearningApprovalEvidenceFoundation`

La foundation existente puede evolucionar con una operación adicional específica para ejecución, pero **no se crea una nueva autoridad paralela**.

La operación de ejecución debe ser semánticamente distinta de G14.

G14 responde a:

> “¿Apruebo esta corrección propuesta?”

La nueva operación responde a:

> “¿Autorizo aplicar ahora este request G16 exacto?”

Por lo tanto:

`CONTENT APPROVAL != APPLY-NOW AUTHORIZATION`

---

## 5. Input humano explícito

Debe existir un input explícito de autorización de ejecución, conceptualmente:

`ExplicitHumanKnowledgeRevisionExecutionAuthorizationResponse`

Nombre no congelado, semántica sí.

Debe contener como mínimo:

- identificador propio de la respuesta;
- `revision_request_id`;
- referencia humana explícita;
- texto de respuesta;
- `approver`;
- `exact_linkage=True` por defecto sólo si el contrato actual mantiene esa convención.

La respuesta debe enlazar directamente con el G16 exacto.

No debe enlazar sólo por:

- session id;
- target memory id;
- revision proposal id;
- texto similar;
- owner;
- última revisión pendiente.

---

## 6. Evidencia de autorización

La evaluación positiva produce un artefacto inerte conceptualmente denominado:

`AuthorizedKnowledgeRevisionExecutionEvidence`

Nombre no congelado; semántica y propiedades sí.

Debe preservar como mínimo:

- `authorization_id`;
- `revision_request_id`;
- `application_proposal_id`;
- `revision_approval_id`;
- `revision_proposal_id`;
- `target_memory_id`;
- `target_owner`;
- `expected_target_fingerprint`;
- `replacement_idempotency_key`;
- explicit human response reference;
- `approver`;
- deterministic `execution_authorization_fingerprint`.

Debe ser **exact-linked** al G16 request.

---

## 7. Propiedades obligatorias de la evidencia

`AuthorizedKnowledgeRevisionExecutionEvidence` es evidencia de permiso, no ejecución.

Debe permanecer inerte:

- `read_only = True`
- `write_performed = False`
- `replacement_persisted = False`
- `supersession_applied = False`
- `memory_modified = False`
- `executes_actions = False`

Puede expresar que **autoriza ese request exacto**, pero no debe convertirse en autoridad general ni reutilizable para otro request.

Su alcance debe ser:

`ONE EXACT AUTHORIZATION → ONE EXACT CERTIFIED REQUEST LINEAGE`

---

## 8. Exact linkage

La autorización sólo es válida si coincide exactamente con el request G16 evaluado.

Como mínimo deben coincidir:

- `revision_request_id`;
- `application_proposal_id`;
- `revision_approval_id`;
- `revision_proposal_id`;
- `target_memory_id`;
- `target_owner`;
- `expected_target_fingerprint`;
- `replacement_idempotency_key`.

No basta coincidencia parcial.

Congelado:

`PARTIAL LINKAGE != EXECUTION AUTHORIZATION`

`SAME MEMORY != SAME REQUEST`

`SAME REVISION PROPOSAL != SAME CERTIFIED REQUEST`

---

## 9. Evaluación humana

La autoridad humana existente debe devolver:

`AuthorizedKnowledgeRevisionExecutionEvidence | None`

Debe abstenerse si:

- no existe respuesta explícita;
- la respuesta no autoriza aplicar ahora;
- `exact_linkage=False`;
- el `revision_request_id` no coincide;
- cualquier lineage material no coincide;
- el request no es G16 certificado;
- el request no es inerte;
- el request declara autoridad o ejecución previa incompatible;
- el approver/respuesta no cumple el vocabulario humano gobernado existente.

No reconstruir requests.

No buscar “el último request”.

No inferir consentimiento.

---

## 10. Vocabulario humano

Debe distinguirse inequívocamente entre aprobar contenido y autorizar ejecución.

Ejemplos conceptuales positivos:

- “Sí, aplicar ahora.”
- “Autorizo aplicar esta revisión.”
- “Proceder con este request.”
- “Sí, ejecutar esta revisión.”

Ejemplos que **no** deben bastar:

- “Sí, la corrección está bien.”
- “Apruebo la revisión.”
- “De acuerdo.”
- “Perfecto.”
- silencio;
- mera continuidad conversacional.

La implementación concreta debe reutilizar, extender o parametrizar el vocabulario humano gobernado existente sin crear una nueva autoridad semántica paralela.

---

## 11. HARD EXECUTION BOUNDARY

Después de producir:

`AuthorizedKnowledgeRevisionExecutionEvidence | None`

debe existir un STOP.

La evaluación humana no puede:

- llamar a G17;
- llamar a `apply_governed_knowledge_revision(...)`;
- llamar a `execute_certified_revision_request(...)`;
- almacenar;
- archivar;
- superseder;
- mutar Memory.

Congelado:

`AUTHORIZATION EVIDENCE != EXECUTION`

---

## 12. Entrada endurecida a G18

G18 debe conservarse como única productive reachability hacia G17.

Su precondición evoluciona conceptualmente de:

```text
G16 request
→ G18
→ G17
```

a:

```text
exact G16 request
+ exact AuthorizedKnowledgeRevisionExecutionEvidence
→ G18
→ G17
```

G18 no debe:

- reconstruir G16;
- recertificar G16;
- repetir G14;
- repetir la autorización;
- interpretar texto humano;
- fabricar evidencia faltante.

Sólo verifica correspondencia exacta y ejecuta mediante el camino productivo existente.

---

## 13. ProductiveGovernedLearningWiring

`ProductiveGovernedLearningWiring` sigue siendo el único coordinador productivo.

Puede recibir una operación mínima conceptualmente similar a:

`execute_authorized_revision_request(request, authorization)`

Nombre no congelado.

Debe:

1. validar que ambos objetos existan;
2. comprobar exact linkage;
3. comprobar que la evidencia autoriza ese request exacto;
4. delegar al mecanismo G18/G17 existente;
5. no crear nueva autoridad;
6. no recertificar;
7. no reconstruir.

No debe aceptar sólo `request`.

---

## 14. OfficialConversationGateway

Si la autorización se hace reachable desde conversación, `OfficialConversationGateway.submit(...)` debe recibir de forma explícita el material correspondiente.

No debe ejecutar simplemente porque:

`governed_knowledge_revision_request is not None`.

Debe requerir el par gobernado:

`request + authorization evidence`

o una respuesta humana explícita que sea evaluada primero por la autoridad existente y cuyo resultado sea luego usado en un paso separado.

La conversación debe diferenciar estados:

Antes de ejecución:

> “La revisión está certificada y pendiente de autorización de aplicación.”

Con autorización pero antes de resultado:

> “La ejecución quedó autorizada para este request exacto.”

Sólo después de G17 exitoso:

> “La revisión fue aplicada en la memoria oficial.”

Nunca reportar “aplicada” cuando sólo exista autorización.

---

## 15. Owner y session

`session_id` puede ayudar a localizar continuidad conversacional, pero no concede permiso de ejecución.

`target_owner` proviene del G16 exacto y no debe inferirse desde session.

Congelado:

- `SESSION ID != MEMORY OWNER`
- `SESSION ID != EXECUTION AUTHORIZATION`
- `CURRENT SESSION != PERMISSION TO APPLY`

---

## 16. Idempotencia y replay

La autorización debe estar ligada al `replacement_idempotency_key` del G16.

Un replay del mismo par exacto:

`same G16 request + same execution authorization`

puede apoyarse en la idempotencia existente de G17.

Pero la autorización no puede reutilizarse para:

- otro request id;
- otro target fingerprint;
- otro replacement idempotency key;
- otra revisión;
- otro owner;
- otra Memory target.

Congelado:

`AUTHORIZATION REPLAY != AUTHORIZATION TRANSFER`

---

## 17. Resultado de ejecución

La autorización no garantiza que G17 vaya a ejecutar con éxito.

G17 puede todavía rechazar por:

- target stale;
- target inactive;
- fingerprint mismatch;
- category mismatch;
- owner mismatch;
- invalid lineage;
- idempotency conflict;
- cualquier contrato ya gobernado por G17.

Por tanto:

`AUTHORIZED EXECUTION != SUCCESSFUL EXECUTION`

La autoridad humana no debe saltarse validaciones técnicas de Memory.

---

## 18. Failure / abstention

Debe resultar en no ejecución cuando:

- no hay autorización;
- autorización rechazada;
- linkage incorrecto;
- request distinto;
- owner distinto;
- fingerprint distinto;
- idempotency key distinta;
- autorización ya pertenece a otro request;
- evidencia reconstruida o incompleta;
- request no certificado;
- request no inerte.

Congelado:

`NO AUTHORIZATION != PERMISSION TO INFER ONE`

`MISSING EVIDENCE != PERMISSION TO RECONSTRUCT IT`

---

## 19. Componentes prohibidos

No introducir:

- `RevisionExecutionApprovalManager`
- `KnowledgeRevisionExecutionAuthority`
- `RevisionExecutionManager`
- `KnowledgeRevisionManager`
- `ProductiveKnowledgeRevisionWiring`
- `AuthorizedRevisionInbox`
- segundo `OfficialMemoryGateway`
- segunda autoridad humana
- segundo productive wiring
- nueva Memory authority

o equivalentes semánticos.

---

## 20. Qué NO reutilizar

No utilizar:

`GovernedIndependenceAuthorizationBoundaryV1`

para este propósito.

Esa frontera pertenece a independencia/iniciación de capacidades, no a autorización de mutación durable de Memory.

Usarla aquí violaría la separación de autoridades por capacidad.

---

## 21. Alcance del futuro CONTRACT RED

El RED futuro debe demostrar la ausencia exacta del seam sin modificar producción.

Debe probar al menos:

1. existe un input explícito de autorización de ejecución enlazado a G16;
2. la autoridad humana existente es reutilizada;
3. no se crea segunda autoridad humana;
4. respuesta positiva exacta produce evidencia inerte;
5. respuesta negativa devuelve `None`;
6. linkage incorrecto devuelve `None`;
7. otro request no puede reutilizar la autorización;
8. la evidencia preserva lineage G13→G14→G15→G16;
9. la autorización no ejecuta Memory;
10. G18 exige `request + exact authorization`;
11. request solo no ejecuta;
12. autorización sola no ejecuta;
13. request + autorización incorrecta no ejecuta;
14. request + autorización exacta llega al G18/G17 existente;
15. no hay recertificación G16;
16. no hay reconstrucción de G13/G14/G15/G16;
17. no hay nuevo Memory gateway;
18. no hay nuevo productive wiring;
19. G17 conserva todas sus validaciones;
20. conversación no dice “aplicada” antes de un resultado G17 real.

---

## 22. Forma esperada del RED

El RED ideal debe tener fallos controlados concentrados en:

- ausencia del tipo de respuesta humana de ejecución;
- ausencia de evidencia de autorización exact-linked;
- ausencia del método de evaluación en la autoridad humana existente;
- ausencia de precondición de autorización en G18/productive wiring;
- eventual ausencia del seam conversacional explícito.

Los tests de anti-duplicación y preservación de G17 deben pasar desde RED.

No se busca provocar fallos amplios de Memory.

---

## 23. Criterio para numeración

Este CONTRACT DESIGN **no asigna G22**.

Sólo si el CONTRACT RED demuestra de manera reproducible que la precondición de ejecución falta en producción, el seam puede formalizarse como siguiente gate.

Si se numera, debe clasificarse como:

**execution-authorization continuity gate**

y no como:

- nueva capacidad cognitiva;
- nueva autoridad;
- nuevo sistema de Memory.

---

## 24. Validación futura

Cuando exista SURGICAL GREEN:

```text
python scripts/clean_project_caches.py
python scripts/generate_quality_baseline.py
ruff check .
pytest -q
```

No se declara certificado hasta obtener:

- cache cleanup clean;
- baseline generated;
- Ruff clean;
- full pytest 0 FAIL;
- 0 regresiones ajenas.

---

## 25. Arquitectura congelada

```text
G19 exact pending G13 proposal [session]
        ↓
G20 existing G14 content approval
        ↓
ApprovedKnowledgeRevisionEvidence
        ↓
G21 existing G15 + existing G16
        ↓
GovernedKnowledgeRevisionRequest
        ↓
HARD EXECUTION BOUNDARY
        ↓
explicit apply-now human response
        ↓
existing human approval authority
        ↓
AuthorizedKnowledgeRevisionExecutionEvidence
        ↓
STOP
        ↓
exact request + exact authorization
        ↓
existing G18 productive reachability
        ↓
existing G17 / OfficialMemoryGateway
        ↓
atomic durable revision
```

## Veredicto de diseño

El próximo seam debe autorizar **la ejecución de un request G16 exacto**, no volver a aprobar la corrección y no otorgar autoridad general.

La evidencia de autorización debe ser inerte, exact-linked, no transferible y separada del acto de mutación.

G18 permanece como único camino productivo de ejecución y G17 permanece como única implementación de mutación durable gobernada.

**CERTIFIED REQUEST MAY EXIST WITHOUT EXECUTION; DURABLE EXECUTION REQUIRES A SEPARATE, EXPLICIT, EXACT-LINKED HUMAN AUTHORIZATION.**
