# ROBY XI.2 — GATE 3.A
## Personal Documents Source Authority / Durable Provenance — Contract Boundary Reconciliation

**Base:** GATE 3 Personal Sources Real Inventory, certificada en 13.928 PASS + Ruff limpio + 0 FAIL.
**Movimiento:** reconciliación contractual; sin cambios productivos.
**STOP:** no CAP-18, no Memory, no Learning, no Planning N+1, no scanner/background ingest.

## 1. Veredicto ejecutivo

La autoridad de fuente documental **ya existe** y está definida por M73:

- `core.document_inbox.DocumentInboxManager` gobierna ingreso, deduplicación, clasificación, recall, archive y Scope Guard.
- `core.document_inbox.DocumentRepository` es el contrato canónico de persistencia de esa fuente.
- `DocumentRecord` es la identidad documental primaria y trazable.

No corresponde crear `PersonalDocumentsManager`, ni convertir Personal Knowledge en almacén de documentos, ni reutilizar Biblioteca CAP-17 como catálogo de documentos personales.

El gap real es más estrecho: el contrato M73 sólo dispone hoy de `InMemoryDocumentRepository` y el runtime oficial no provisiona una instancia durable de `DocumentInboxManager`. Por ello, la fuente documental existe semánticamente pero no queda durable/reachable de forma productiva.

**Clasificación:** `EXISTING CANONICAL SOURCE AUTHORITY — MINIMAL PERSISTENCE + OFFICIAL WIRING EXTENSION REQUIRED`.

## 2. Autoridad canónica exacta

### 2.1 Source authority

`DocumentInboxManager` es la autoridad de ciclo de vida del documento personal. El ADR-075 ya fijó que:

- separa metadatos, contenido, clasificación, repositorio y ciclo de vida;
- la persistencia queda detrás de `DocumentRepository`;
- Scope Guard gobierna alcance;
- un documento informa/organiza, pero no autoriza acciones.

Por tanto, la solución no debe introducir otro catálogo documental paralelo.

### 2.2 Persistence authority

`DocumentRepository` es el puerto existente que debe recibir una implementación durable de infraestructura. En la base auditada sólo existe `InMemoryDocumentRepository`; no existe `SQLiteDocumentRepository`, `FileDocumentRepository` ni equivalente productivo.

La extensión mínima correcta es un **adaptador de infraestructura** que implemente exactamente `DocumentRepository`, preservando la autoridad de M73.

### 2.3 Reading / extraction authority

`app.document_reading.DocumentReadingService` no es catálogo ni repositorio. Es lector explícito/grounded y ya soporta TXT/MD/CSV/JSON/HTML/DOCX/PDF/EPUB con límites de seguridad.

Debe seguir siendo lector/extractor. Cuando una incorporación durable use formatos que M73 no lee por sí mismo, la capa de aplicación puede usar `DocumentReadingService.read_text(...)` y luego entregar el contenido a `DocumentInboxManager.ingest_text(...)`. No debe invertirse la dependencia haciendo que `core.document_inbox` importe `app.document_reading`.

## 3. Provenance existente y suficiente para el primer seam durable

`DocumentRecord` ya conserva:

- `document_id` estable;
- `source_name`;
- `media_type`;
- `content_hash` SHA-256;
- categoría y estado;
- `issued_at` / `expires_at` cuando existen;
- timestamps de creación/actualización;
- enlace opcional a Household Memory.

La deduplicación se realiza por hash del contenido normalizado. Para la primera persistencia durable no es necesario inventar una segunda identidad de fuente.

El identificador canónico para consumidores sigue siendo `document_id`; el hash prueba versión/contenido. `source_name` describe procedencia visible pero no debe convertirse en autoridad de identidad.

No se justifica persistir un path absoluto como identidad canónica: mover un archivo no debe cambiar la identidad documental ya registrada. Si en un futuro se necesita reabrir el archivo original, deberá reconciliarse como locator separado, no sustituyendo `document_id`/hash.

## 4. Personal Knowledge: consumidor derivado, no source authority

El ADR-076 es explícito: **los documentos son fuentes; no se confunden con el conocimiento derivado**.

`PersonalKnowledgeBaseManager.candidate_from_document(...)` ya consume un `DocumentRecord` desde `DocumentInboxManager` y crea un candidato con:

- `KnowledgeSource.DOCUMENT`;
- `source_reference="document:<document_id>"`;
- revisión humana según reglas existentes.

La base productiva actual sí provisiona `SQLitePersonalKnowledgeRepository`, pero construye `PersonalKnowledgeBaseManager(repository=repository)` **sin** `document_inbox`.

Por tanto:

- NO mover documentos a la DB de Personal Knowledge;
- NO duplicar contenido documental como forma primaria de persistencia;
- SÍ inyectar la misma instancia oficial de `DocumentInboxManager` al manager de Personal Knowledge cuando se cierre el seam de runtime.

## 5. Task Intelligence y otros consumidores

`TaskIntelligenceManager.candidate_from_document(...)` también depende opcionalmente de `DocumentInboxManager`, pero el wiring productivo actual construye Task Intelligence sin esa dependencia.

Esto confirma que M73 fue diseñado como fuente compartida para consumidores posteriores. La instancia durable debe ser **única y compartida** por los consumidores que necesiten documento, no recreada por subsistema.

`DailyBriefing` y el Cognitive Pipeline también aceptan Document Inbox como superficie opcional/histórica, pero no deben usarse para justificar una nueva autoridad. Son consumidores/proyecciones.

## 6. Reasoning / Evidence boundary

M77 ya contiene `DocumentEvidenceAdapter` dentro del `EvidenceRegistry` canónico. Convierte `DocumentRecord` en `EvidenceReference` con:

- `EvidenceSourceType.DOCUMENT`;
- `source_id=document_id`;
- fingerprint = `DocumentRecord.effective_hash`;
- categoría, source_name y media_type como metadata;
- sensibilidad conservadora.

Esto demuestra que **no falta un nuevo modelo de evidencia documental**.

El gap de GATE 3.A termina antes de Reasoning automático: hacer durable/reachable el `DocumentRecord` no autoriza registrarlo automáticamente como evidencia ni iniciar Reasoning. Cualquier handoff productivo a Knowledge/Reasoning debe ser explícito y reutilizar M77/las authorities existentes.

## 7. Frontera con Biblioteca CAP-17

Biblioteca CAP-17 y Documentos Personales pueden reutilizar `DocumentReadingService`, pero poseen identidades y gobierno distintos:

- Biblioteca: root/catalogue/selection propios y flujo de adquisición gobernada CAP-17.
- Documentos Personales: `DocumentInboxManager` + `DocumentRepository` + `DocumentRecord`.

No se debe introducir un root de Biblioteca dentro de Document Inbox ni convertir Document Inbox en una segunda Biblioteca. Tampoco debe utilizarse el catálogo CAP-17 como persistencia documental personal.

## 8. Runtime gap exacto

La base oficial construye:

- Personal Knowledge con SQLite durable;
- Task Intelligence con SQLite durable;
- pero no construye una fuente documental durable compartida.

El seam mínimo de runtime que queda por contratar es:

1. una implementación durable de `DocumentRepository` en infraestructura;
2. un único builder/provisioning oficial de `DocumentInboxManager` sobre esa implementación;
3. una única instancia compartida inyectada en Personal Knowledge y Task Intelligence donde corresponda;
4. sin ingestión automática, sin scanner, sin Memory/Learning;
5. lectura/importación sólo por solicitud explícita;
6. ningún nuevo manager de dominio.

## 9. Qué NO debe formar parte del primer RED

No incluir en el contrato inicial:

- búsqueda semántica/vectorial;
- embeddings;
- watcher de carpetas;
- sincronización cloud;
- OCR nuevo;
- reanálisis automático;
- obligaciones/tareas automáticas derivadas;
- Memory/Learning;
- Planning;
- Reasoning automático;
- fusión con Biblioteca;
- CAP-18 visual.

## 10. Contract boundary recomendado

El siguiente RED está justificado y debe probar sólo el seam durable/productivo de M73.

Nombre recomendado:

**GATE 3.A.1 — Existing Document Inbox → Durable Repository → Official Shared Runtime Provisioning — CONTRACT RED**

Contratos mínimos esperados:

1. Existe exactamente un adaptador durable que implementa `DocumentRepository` sin crear nueva autoridad de dominio.
2. Conserva round-trip de `DocumentRecord` completo, incluido hash, metadata, estado e identidad.
3. Deduplicación por hash continúa perteneciendo a `DocumentInboxManager`.
4. El runtime oficial provisiona un único `DocumentInboxManager` durable.
5. Personal Knowledge recibe esa misma instancia; no copia la fuente ni cambia su autoridad.
6. Task Intelligence, si se conecta en este mismo seam, recibe la misma instancia, no otra.
7. `DocumentReadingService` permanece lector/extractor y no se convierte en repositorio.
8. No hay ingestión automática/background.
9. No se llama Memory, Learning, Planning ni Reasoning como consecuencia de registrar un documento.
10. `.roby/config.json` y `credencial.json` permanecen intactos.

## 11. Decisión final de GATE 3.A

**SOURCE AUTHORITY:** `DocumentInboxManager`.

**PERSISTENCE PORT:** `DocumentRepository`.

**PRIMARY SOURCE ENTITY:** `DocumentRecord` (`document_id` + content hash).

**READER/EXTRACTOR:** `DocumentReadingService`.

**DERIVED KNOWLEDGE CONSUMER:** `PersonalKnowledgeBaseManager`.

**EVIDENCE NORMALIZATION:** existing M77 `DocumentEvidenceAdapter` / `EvidenceRegistry`.

**RESULT:** `MINIMAL CANONICAL EXTENSION REQUIRED` limitada a persistencia durable y provisioning compartido del authority ya existente.

**NEXT:** GATE 3.A.1 CONTRACT RED.

**STOP:** no producción hasta RED contractual; no CAP-18, Memory, Learning ni Planning N+1.
