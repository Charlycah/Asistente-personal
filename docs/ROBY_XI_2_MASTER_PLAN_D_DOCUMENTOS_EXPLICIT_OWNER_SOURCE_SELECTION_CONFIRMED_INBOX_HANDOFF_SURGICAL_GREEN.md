# ROBY XI.2 — D:\Documentos explicit Owner source selection

## Confirmed Inbox handoff — SURGICAL GREEN

## Gate de entrada

Este GREEN parte del CONTRACT RED Owner-certified:

- 9 fallos contractuales esperados;
- 13.390 tests restantes en PASS;
- Ruff clean;
- todos los fallos contractuales debidos exclusivamente a la ausencia de
  `app.personal_document_ingestion_runtime`.

El test corregido entregado por Owner, sin el import `pytest` no utilizado, es la
base contractual canónica.

## Micro-reconciliación del harness descubierta en GREEN

La existencia del módulo permitió alcanzar por primera vez APIs que el RED no
podía ejecutar. Se detectaron tres incompatibilidades del harness con las APIs
canónicas existentes:

1. `GovernedConversationPipelineRequest` requiere `owner` explícito;
2. `DocumentInboxManager` recibe un `DocumentRepository`, no una ruta, y la
   inspección de pruebas corresponde a `repository.list_all()`;
3. `OfficialRuntimeCapabilityRegistry` expone `capability_names`, no
   `registered_names()`.

El test GREEN conserva todas las expectativas semánticas del RED y sólo adapta
su harness a esas autoridades existentes. No se modificó producto para fabricar
APIs de conveniencia destinadas al test.

## Delta productivo

Se añade:

- `app/personal_document_ingestion_runtime.py`.

Se modifica quirúrgicamente:

- `app/runtime_root_factory.py`.

No se modifican:

- `app/personal_document_source.py`;
- `core/document_inbox.py`;
- el admission adapter de Reasoning;
- Knowledge;
- Memory;
- Learning;
- self-improvement.

## Autoridades preservadas

`PersonalDocumentRootDiscoveryAdapter` continúa siendo la autoridad subordinada
para discovery, revalidación y handoff de la fuente seleccionada.

`DocumentInboxManager` continúa siendo la única autoridad de ingestión y
persistencia documental.

`OfficialRuntimeCapabilityRegistry` continúa siendo la autoridad de registro e
intercepción de la capability.

El runtime root reutiliza exactamente la instancia canónica `document_inbox`
que ya construía antes de crear el registry.

## Capability

Nombre:

`personal_documents.ingest_selected`

Descriptor:

- kind: FILES;
- risk: MEDIUM;
- permission scope: WRITE;
- requires confirmation: true;
- initiation policy: HUMAN_APPROVAL;
- effect class: STATE_CHANGING;
- interaction scope: HUMAN.

## Máquina de interacción

La ruta productiva queda:

Owner explícito
→ discovery gobernado existente
→ filtrado metadata-only
→ presentación relativa segura
→ selección explícita
→ confirmación explícita
→ `PersonalDocumentRootDiscoveryAdapter.ingest_selected()`
→ `DocumentInboxManager`
→ presentación de resultado
→ STOP.

Discovery y selección no producen ingestión.

La confirmación es session-scoped, expira a los cinco minutos y se consume antes
del intento de ingestión, por lo que no puede reutilizarse como confirmación
repetida.

La cancelación elimina el estado efímero pendiente.

## Privacidad y boundedness

La presentación de candidatos contiene únicamente metadata relativa segura:

- relative path;
- suffix;
- size.

No presenta:

- root absoluto;
- `source_reference` interno;
- contenido del documento;
- candidate ID interno.

La selección sólo admite ordinal presentado o relative path presentado.

## Runtime composition

`build_runtime_root()` registra el runtime mediante:

`build_personal_document_ingestion_runtime_from_environment(...)`

inyectando:

`document_inbox=document_inbox`

La capability no se registra si falta `ROBY_PERSONAL_DOCUMENTS_ROOT`, si el root
no es válido o si el Inbox canónico está deshabilitado.

No se crea un segundo Inbox ni un segundo registry.

## STOP posterior a ingestión

El resultado de la ingestión no dispara automáticamente:

- Reasoning;
- Knowledge admission;
- Memory;
- Learning;
- self-improvement;
- code mutation;
- source mutation;
- background scan o watcher.

El `document_id` puede presentarse al Owner. Cualquier admisión posterior a
Reasoning continúa requiriendo el mecanismo explícito ya existente.

## Certificación local

Contrato corregido GREEN:

- 12/12 PASS.

Regresión conjunta source foundation + nuevo contrato:

- 24/24 PASS.

Calidad estructural:

- `app/personal_document_ingestion_runtime.py`: 243 líneas, 0 >88;
- test contractual: 222 líneas, 0 >88;
- `app/runtime_root_factory.py`: 0 >88;
- `py_compile`: PASS.

Ruff no está disponible en el entorno de construcción del asistente.

La suite global fue iniciada pero alcanzó el límite temporal del contenedor
antes de completar. No se declara certificación global local a partir de una
ejecución incompleta.

## Gate Owner esperado

Desde el RED Owner-certified de 13.390 PASS + 9 RED, el cierre esperado es:

- 13.399 PASS;
- 0 FAIL;
- Ruff clean.

Ese conteo y Ruff deben ser confirmados por el Owner gate antes de declarar el
bloque OWNER-CERTIFIED.

## Estado

`SURGICAL_GREEN: LOCAL GREEN`

`EXPECTED_RED_CLOSURE: 9/9`

`PRODUCTIVE_RUNTIME_REACHABILITY: IMPLEMENTED`

`CANONICAL_DOCUMENT_INBOX: REUSED`

`NEW_PERSISTENCE_AUTHORITY: NONE`

`NEW_COGNITIVE_AUTHORITY: NONE`

`AUTO_REASONING_AFTER_INGESTION: FORBIDDEN`

`OWNER_GLOBAL_CERTIFICATION: PENDING`
