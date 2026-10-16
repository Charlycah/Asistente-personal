# ROBY XI.2 — GATE 3 — Personal Sources Real Inventory
## Documentos Personales + Visual Collection / "Pinacoteca" — Surgical Reconciliation

**Base auditada:** 13.928 PASS + Ruff limpio + 0 FAIL (certificación local del usuario).
**Tipo de movimiento:** reconciliación/inventario; sin cambios productivos.
**STOP:** no diseñar CAP-18, no abrir Planning N+1, Memory ni Learning.

## 1. Veredicto ejecutivo

GATE 3 encuentra dos realidades distintas:

1. **Documentos Personales no está ausente.** Existe una familia documental amplia, pero fragmentada entre lectura explícita productiva, un `DocumentInboxManager` histórico integrado al Cognitive Pipeline, capacidades visuales de OCR/clasificación/extracción/inteligencia documental y `PersonalKnowledgeBase`. No existe todavía una única fuente privada durable y gobernada que unifique lectura, ingreso, provenance y consulta de documentos personales sin confundirse con Biblioteca.
2. **La colección visual tampoco parte de cero.** Ya existe la autoridad visual canónica (`GovernedVisionGateway` + `OfficialVisionCore`), un contrato de persistencia (`ImageRepository`) y un adaptador privado local (`FileImageRepository`), además del bridge visual→cognición transitorio. Lo ausente es una **capacidad de colección personal** productivamente provisionada/catalogable: no una nueva autoridad de visión.

**Clasificación global:** `EXISTING AUTHORITIES + MINIMAL SOURCE-LAYER SEAMS REQUIRED`; no se justifica crear nuevos cerebros, managers cognitivos, vision runtimes ni repositorios paralelos.

## 2. Documentos Personales — inventario real

### Autoridades y superficies existentes

- `app/document_reading.py::DocumentReadingService`: lector productivo explícito de archivos locales. Admite TXT/MD/CSV/JSON/HTML/DOCX/PDF/EPUB con límites de tamaño y prompt grounded. Ya es usado por Desktop y por el runtime de Biblioteca.
- `core/document_inbox.py::DocumentInboxManager`: ingreso, clasificación, recall, archive, deduplicación SHA-256 y Scope Guard. Su repositorio por defecto es **in-memory**; sólo ingiere paths textuales TXT/MD/CSV/JSON y declara extractores dedicados para binarios.
- `core/document_extraction`, `core/document_classification`, `core/document_intelligence`: capacidades estructuradas existentes, hoy consumidas principalmente por `OfficialVisionCore` para documentos observados visualmente.
- `core/document_actions::GovernedDocumentActionService`: acciones documentales separadas y gobernadas por Tool Gateway/consentimiento; no debe convertirse en autoridad de fuente.
- `core/personal_knowledge_base.py`: puede crear conocimiento trazable desde `DocumentInboxManager`, pero la construcción productiva observada de Personal Knowledge usa SQLite sin conectar Document Inbox.
- `core/cognitive_pipeline.py`: acepta `DocumentInboxManager` opcionalmente; esto demuestra integración cognitiva histórica, no una fuente personal durable provisionada por el runtime actual.

### Persistencia / provenance

- `DocumentRecord` conserva `document_id`, `source_name`, `media_type`, hash SHA-256, categoría, estado y timestamps.
- El `DocumentRepository` documental no tiene en esta base un adaptador SQLite/file productivo equivalente al de Personal Knowledge.
- `DocumentReadingService` lee el path solicitado pero no registra por sí mismo un `DocumentRecord` durable.
- Biblioteca CAP-17 tiene root/catalogue/selection y su propio gobierno de source/evidence; **no debe absorber Documentos Personales**.

### Gap exacto

Falta reconciliar un seam de **fuente privada documental** que reutilice `DocumentReadingService` para lectura y las estructuras documentales existentes para provenance/registro, con root/selección/consentimiento explícitos y persistencia definida, sin convertir `DocumentInboxManager` en segundo Knowledge/Reasoning authority.

**Clasificación:** `MINIMAL CANONICAL SOURCE-LAYER EXTENSION REQUIRED`, pero todavía no RED: antes debe fijarse qué componente existente será la autoridad de catálogo/registro durable y cómo se provisiona desde runtime sin mezclar Biblioteca.

## 3. Visual Collection / "Pinacoteca" — inventario real

### Autoridades canónicas existentes

- `app/vision_gateway.py::GovernedVisionGateway`: frontera oficial de aplicación para visión y retención voluntaria.
- `app/vision_core.py::OfficialVisionCore`: captura/análisis visual; conserva gobernanza y no expone raw bytes en resultados de captura.
- `core/intelligent_vision`: política visual, consentimiento, privacy levels, capabilities y eventos. `retain_raw_media=False` por defecto; identificación biométrica no puede habilitarse.
- `core/governed_image_repository.py::ImageRepository`: contrato canónico de persistencia; `ImageStoreRequest` exige owner/label y lleva category/tags/consent flags.
- `infrastructure/vision/file_image_repository.py::FileImageRepository`: persistencia privada local JPEG/PNG/WebP con metadata, SHA-256, list/get/delete.
- `core/cognitive_runtime_orchestration/visual_context.py::GovernedVisualCognitiveContextBridge`: proyecta semántica visual ya integrada a cognición **transitoria**, preservando owner/session lineage y declarando explícitamente ausencia de Memory/Learning/execution authority.

### Productive reachability observada

- `OfficialWindowsWorkspaceGateway` puede almacenar screenshots mediante el `GovernedVisionGateway` existente.
- No se encontró en el wiring de runtime una provisión global de `FileImageRepository`/`GovernedVisionGateway` que convierta el repositorio en una colección personal permanente navegable.
- Los tests M362 prueban storage/list/get/delete, consentimiento, separación de raw capture y ausencia de biometría. Los tests multimodales prueban el bridge visual→cognición, pero con `IntegratedVisualContext` ya construido.

### Privacy/provenance boundary

Ya existe una frontera fuerte: almacenamiento sólo por solicitud + consentimiento explícito; owner, label, category, tags, MIME, size, SHA-256 y timestamp; sin embeddings, template biométrico ni identity match. La captura transitoria y la retención son operaciones separadas.

### Gap exacto

Falta una **collection/source layer** productivamente provisionada para seleccionar/listar imágenes personales y, cuando corresponda, entregar una imagen seleccionada a las autoridades visuales existentes. No falta un nuevo sistema de visión ni un nuevo repositorio.

**Clasificación:** `EXISTING CANONICAL STORAGE/VISION AUTHORITIES — MINIMAL COLLECTION/SELECTION SEAM REQUIRED`.

## 4. Colisiones y fronteras

- **Biblioteca ≠ Documentos Personales.** Pueden compartir `DocumentReadingService`, pero no root, catálogo, policy ni source identity por defecto.
- **ImageRepository ≠ Vision.** El repositorio conserva; `OfficialVisionCore`/`GovernedVisionGateway` gobiernan visión/análisis.
- **Visual collection ≠ cognitive authority.** Una colección selecciona/entrega una fuente; el bridge visual existente proyecta semántica transitoria.
- **Pinacoteca ≠ música/audio.** El nombre queda reservado provisionalmente a fotografías/imágenes/arte; audio se mantiene fuera de CAP-18 hasta auditoría separada.
- **Document/visual evidence ≠ Memory/Learning.** Ninguna incorporación durable a memoria/aprendizaje queda autorizada por este Gate.

## 5. Tests representativos auditados

Slice focal ejecutado en este Gate: **326 PASS**.

Incluye M73 Document Inbox, M340.4 Document Reading, M351 OCR, M355 classification, M356 extraction, M358 intelligence, M359 actions, M362 Vision Gateway, M348.9 Vision Core, RP248 Intelligent Vision y las capas visual foundation/resolution/attention/context integration.

La suite completa no se re-certifica en este Gate porque no hubo cambios productivos.

## 6. Decisión de arquitectura

No crear:

- `PersonalDocumentsManager` paralelo;
- `PinacotecaManager` cognitivo;
- segundo Vision Core/Gateway;
- segundo ImageRepository;
- catálogo que razone;
- background scanner;
- ingestión automática a Memory/Learning;
- reconocimiento biométrico;
- CAP-18 antes de contrato.

Reutilizar:

- DocumentReading para bytes/texto documental explícito;
- estructuras documentales existentes para clasificación/inteligencia/provenance donde correspondan;
- `GovernedVisionGateway` + `OfficialVisionCore` para visión;
- `ImageRepository`/`FileImageRepository` para retención visual;
- `GovernedVisualCognitiveContextBridge` para entrada cognitiva visual transitoria.

## 7. Próximo movimiento recomendado

Dividir el siguiente Gate contractual en dos seams, sin mezclarlos:

**GATE 3.A — Personal Documents Source Authority / Durable Provenance — Contract Boundary Reconciliation**

Objetivo: decidir la autoridad existente que debe poseer catálogo/registro durable de documentos personales y definir su relación exacta con DocumentReading, Personal Knowledge y CAP-17 Knowledge/Reasoning sin mezclarla con Biblioteca.

Después, y sólo después:

**GATE 3.B — Personal Visual Collection Provisioning / Selection → Existing Governed Vision — Contract Boundary Reconciliation**

Objetivo: definir configuración privada, listado/selección explícita y handoff de una imagen almacenada hacia el `GovernedVisionGateway`/pipeline visual existente, sin crear autoridad cognitiva nueva.

**STOP actual:** no escribir RED ni producción hasta cerrar GATE 3.A.
