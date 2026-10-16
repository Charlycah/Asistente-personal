# ROBY XI.2 — GATE 3.B
## Personal Visual Collection / "Pinacoteca" → Existing Governed Vision — Contract Boundary Reconciliation

**Base certificada:** GATE 3.A.1 SURGICAL GREEN + M396.3 reconciliado, **13.937 PASS + Ruff limpio + 0 FAIL**.
**Movimiento:** reconciliación contractual/documental; **sin cambios productivos**.
**STOP:** no CAP-18 productivo, no Memory, no Learning, no Planning N+1, no exploración automática de galerías, no biometría.

## 1. Veredicto ejecutivo

La capacidad visual no está ausente. ROBY ya posee autoridades canónicas maduras para persistencia privada voluntaria, gobierno visual y análisis local:

- `core.governed_image_repository.ImageRepository` es el puerto canónico de persistencia visual.
- `infrastructure.vision.file_image_repository.FileImageRepository` es el adaptador privado local ya existente.
- `app.vision_gateway.GovernedVisionGateway` es la frontera oficial de aplicación para visión y retención.
- `app.vision_core.OfficialVisionCore` es el motor canónico de análisis visual.
- `core.intelligent_vision.IntelligentVisionService` conserva política, consentimiento y prohibiciones.
- las familias visuales ya existentes cubren escena, objetos, personas, rostros sin identidad, OCR, códigos e inteligencia documental.
- `core.cognitive_runtime_orchestration.visual_context.GovernedVisualCognitiveContextBridge` ya demuestra que contexto visual previamente integrado puede proyectarse a cognición transitoria como evidencia subordinada, sin autoridad de Memory/Learning/Execution.

Por tanto, **no corresponde crear `PinacotecaManager`, otro Vision Core, otro Vision Gateway, otro ImageRepository ni un catálogo cognitivo paralelo**.

El gap real es estrecho y doble:

1. `FileImageRepository`/`GovernedVisionGateway` no están provisionados productivamente como colección visual personal durable compartida.
2. la colección puede listar metadatos, pero el contrato `ImageRepository` no expone lectura gobernada del asset seleccionado; y `OfficialVisionCore` sólo posee entradas públicas que capturan desde `CameraProvider`. Hoy no existe un seam explícito **stored image seleccionada → bytes transitorios → análisis por la autoridad visual existente**.

**Clasificación:** `EXISTING CANONICAL STORAGE/VISION AUTHORITIES — MINIMAL PROVISIONING + EXPLICIT SELECTION/ANALYSIS-INPUT SEAM REQUIRED`.

## 2. Nomenclatura cerrada para este tramo

Para ROBY XI.2:

- **Personal Visual Collection / "Pinacoteca" (nombre provisional)** = fotografías, imágenes y arte personales.
- **Música/audio** = familia distinta; no forma parte de CAP-18 visual.

El uso histórico de “Pinacoteca” como catálogo/reproductor musical queda superseded. Ningún diseño visual debe heredar semántica de playback de audio.

## 3. Autoridades canónicas exactas

### 3.1 Persistence/source port

`ImageRepository` ya define la autoridad de persistencia visual a nivel de puerto:

- `store(...)`;
- `get(image_id)`;
- `list(owner=...)`;
- `delete(image_id)`.

`StoredImage` conserva identidad/provenance mínima durable:

- `image_id`;
- `owner`;
- `label`;
- `category`;
- `tags`;
- `mime_type`;
- `size_bytes`;
- `sha256`;
- `stored_at` timezone-aware.

`image_id` debe seguir siendo la identidad canónica de la pieza almacenada; `sha256` prueba contenido. El path físico del asset es detalle del adaptador y no debe convertirse en identidad de dominio.

### 3.2 Durable local adapter

`FileImageRepository` ya persiste JPEG/PNG/WebP bajo un root privado, separando `assets/` y `metadata/`. Exige simultáneamente:

- `user_requested=True`;
- `explicit_user_consent=True`;
- bytes no vacíos;
- MIME permitido.

Además elimina asset y metadata juntos y valida `image_id` antes de resolver paths.

No se necesita una segunda base de datos ni un nuevo repositorio para crear la colección personal inicial.

### 3.3 Application boundary

`GovernedVisionGateway` ya es, por M362, la frontera oficial de aplicación. Actualmente delega captura al `OfficialVisionCore` y las operaciones de store/get/list/delete al `ImageRepository` configurado.

La colección/selección futura debe ampliarlo o componerse **a través de él**, no rodearlo accediendo directamente desde UI/runtime al filesystem privado.

### 3.4 Analysis authority

`OfficialVisionCore` es el motor canónico. Sus operaciones públicas conservan gobierno y consentimiento, pero todas adquieren el frame mediante `camera_provider.capture(...)`.

Los detectores/analyzers internos ya consumen `CameraFrame`, por lo que el problema no es ausencia de visión; es ausencia de una entrada oficial para media visual ya seleccionada y no proveniente de una captura de cámara en ese turno.

No debe fingirse que una fotografía almacenada es una nueva captura de cámara sólo para reutilizar el API actual. El futuro seam debe preservar la provenance `stored_image:<image_id>` de forma explícita.

## 4. Gap contractual exacto del repositorio de imágenes

`ImageRepository.get(image_id)` devuelve únicamente `StoredImage` (metadata). `FileImageRepository` sí conserva los bytes en `assets/`, pero no existe un método público del puerto para recuperar el contenido seleccionado.

Por ello, una UI podría hoy listar y elegir metadata, pero no puede entregar el asset al pipeline visual sin conocer detalles privados del adaptador (`assets/`, extensión y root), lo que rompería la frontera arquitectónica.

La extensión mínima debe proveer **lectura gobernada del contenido de un image_id explícitamente seleccionado**, con estas propiedades:

- la selección es explícita y owner-scoped;
- la resolución del archivo permanece dentro del repositorio/adaptador;
- el hash del contenido leído se verifica contra `StoredImage.sha256`;
- los bytes son transitorios y no aparecen en resultados, logs ni contexto cognitivo;
- no existe enumeración/background scanning fuera de `list(...)` explícito;
- la lectura no autoriza análisis por sí sola.

No se prescribe aún el nombre final del método/record; eso pertenece al CONTRACT RED y al GREEN posterior. Sí queda fijado que **no puede requerir a consumidores conocer el path físico del asset**.

## 5. Gap contractual exacto hacia Existing Governed Vision

El segundo seam faltante es transformar la selección autorizada en una observación visual que use las autoridades ya existentes.

Estado actual:

**ImageRepository metadata → STOP**

Estado objetivo mínimo:

**owner-scoped list → explicit image_id selection → governed asset read → transient visual input → GovernedVisionGateway → OfficialVisionCore/existing analyzers → governed visual result → STOP**

Requisitos de arquitectura:

1. `GovernedVisionGateway` continúa como frontera de aplicación.
2. `OfficialVisionCore` continúa como autoridad de análisis.
3. La entrada desde colección debe conservar `image_id`, `sha256`, owner y origen almacenado como lineage/provenance.
4. La política de `IntelligentVisionService` continúa gobernando capabilities, consentimiento y prohibiciones.
5. Los bytes crudos existen sólo durante el análisis y no son retenidos nuevamente de forma implícita.
6. Un análisis de fotografía almacenada no debe incrementar semánticamente una “captura de cámara” ni inventar `camera_index` como provenance si el seam puede evitarlo.
7. Ningún resultado debe exponer bytes crudos.

Esto puede requerir una extensión instrumental mínima para “visual input already acquired”, pero **no una nueva autoridad visual**.

## 6. Productive provisioning gap

No se encontró un builder/runtime global que construya `FileImageRepository` y `GovernedVisionGateway` como colección visual personal durable oficial.

Las pruebas M362/M363 los construyen manualmente y `OfficialWindowsWorkspaceGateway.store_screenshot(...)` puede entregar una captura al gateway para persistencia, pero eso no constituye provisioning global de una colección personal.

El seam productivo futuro debe:

- provisionar un único `FileImageRepository` privado;
- inyectarlo en el `GovernedVisionGateway` oficial;
- definir un root privado canónico bajo `.roby/` o un override explícito, sin modificar automáticamente `.roby/config.json`;
- reutilizar la misma instancia para list/select/read/store/delete;
- no crear watchers ni indexadores background.

## 7. Privacy, consent y provenance

Las barreras M362 permanecen obligatorias:

- guardar una imagen requiere solicitud y consentimiento explícitos;
- una referencia de persona es una imagen etiquetada, no una plantilla biométrica;
- identificación biométrica está prohibida;
- no se exploran galerías automáticamente;
- no se almacena automáticamente una captura transitoria;
- `VisionPolicy.retain_raw_media` permanece `False` por defecto;
- la cognición recibe semántica visual estructurada, no bytes.

Para una imagen ya almacenada, el consentimiento de **almacenamiento** histórico no debe interpretarse automáticamente como consentimiento ilimitado para todo análisis futuro. El CONTRACT RED debe exigir una solicitud explícita de selección/análisis para el turno/operación correspondiente.

## 8. Frontera con Visual Cognitive Context

`GovernedVisualCognitiveContextBridge` ya establece una frontera correcta para cognición:

- exige owner/session lineage;
- rechaza contexto no READY o incompleto;
- proyecta escena/objetos/atención como contexto perceptivo subordinado;
- declara que la evidencia visual no certifica verdad;
- mantiene `no_memory_learning_or_execution_authority`.

Por tanto, GATE 3.B **no necesita un nuevo bridge cognitivo**. El residual está antes: lograr que una imagen personal explícitamente seleccionada pueda producir, por las authorities visuales existentes, el contexto/resultado estructurado que las capas ya existentes saben integrar.

No debe conectarse directamente `StoredImage` a Reasoning, Memory o Learning.

## 9. Fronteras con otros subsistemas

### 9.1 Windows Workspace

`OfficialWindowsWorkspaceGateway.store_screenshot(...)` ya puede persistir una screenshot mediante `GovernedVisionGateway`. Es un productor explícito de imágenes, no autoridad de colección ni análisis.

### 9.2 Multimodal Conversation Integration

`OfficialMultimodalConversationIntegrationGateway` coordina modalidades declaradas y consentimiento, pero actualmente no ejecuta cámara/hardware y no constituye la autoridad de análisis visual. No debe convertirse en Pinacoteca ni duplicar `GovernedVisionGateway`.

### 9.3 Personal Documents

Una imagen de categoría `DOCUMENT` puede ser analizada visualmente, pero no se convierte automáticamente en `DocumentRecord`. Cualquier handoff posterior hacia Document Inbox necesita su propio contrato explícito de provenance y no forma parte de GATE 3.B.

## 10. Qué NO debe formar parte del primer RED

Excluir:

- reconocimiento facial/biométrico o identity matching;
- embeddings/vector store;
- búsqueda semántica de imágenes;
- clasificación automática masiva de la colección;
- watcher/scanner de carpetas;
- importación automática de galerías del sistema;
- cloud sync;
- deduplicación global nueva más allá del hash/provenance ya disponible;
- edición/manipulación de imágenes;
- reproducción musical/audio;
- Memory/Learning;
- Planning;
- Reasoning automático;
- CAP-18 cognitivo independiente;
- nuevo Vision Core/Gateway/Repository/Manager.

## 11. Contract boundary recomendado

El siguiente RED queda justificado.

Nombre recomendado:

**GATE 3.B.1 — Existing Image Repository → Explicit Stored-Image Selection → Existing Governed Vision — CONTRACT RED**

Contratos mínimos esperados:

1. Continúa existiendo una sola `GovernedVisionGateway` y un solo `OfficialVisionCore`; no aparece `PinacotecaManager`/`VisualCollectionManager` cognitivo paralelo.
2. Existe provisioning oficial de un único `FileImageRepository` privado reutilizando el `ImageRepository` existente.
3. Listado/selección es owner-scoped y explícito; no hay scan/background.
4. El consumidor selecciona por `image_id`, nunca por path interno del adaptador.
5. El repository boundary puede entregar el asset seleccionado de forma controlada sin exponer su root/path físico.
6. El contenido recuperado conserva/verifica `StoredImage.sha256` y `mime_type`.
7. Una solicitud explícita de análisis entrega ese asset, de forma transitoria, a la autoridad visual existente.
8. El resultado conserva provenance del `image_id` seleccionado y no inventa una nueva captura de cámara como origen.
9. Los bytes crudos no aparecen en resultados ni contexto cognitivo y no se re-retienen automáticamente.
10. Consentimiento/política existentes siguen aplicándose; biometría continúa prohibida.
11. Ningún análisis dispara Memory, Learning, Planning, Reasoning o ejecución automática.
12. `.roby/config.json` y `credencial.json` permanecen intactos.

## 12. Decisión final de GATE 3.B

**PERSISTENCE PORT:** `ImageRepository`.

**DURABLE ADAPTER:** `FileImageRepository`.

**PRIMARY STORED SOURCE ENTITY:** `StoredImage` (`image_id` + SHA-256 + owner/provenance metadata).

**APPLICATION BOUNDARY:** `GovernedVisionGateway`.

**ANALYSIS AUTHORITY:** `OfficialVisionCore` + existing visual analyzers.

**POLICY AUTHORITY:** `IntelligentVisionService` / `VisionPolicy`.

**COGNITIVE PROJECTION:** existing `GovernedVisualCognitiveContextBridge`, only after upstream visual integration and never as source authority.

**RESULT:** `MINIMAL CANONICAL EXTENSION REQUIRED` limitada a provisioning privado + selección explícita + lectura controlada del asset + entrada no-camera al análisis visual existente.

**NEXT:** GATE 3.B.1 CONTRACT RED.

**STOP:** no producción hasta RED contractual; no CAP-18 paralelo, no biometría, no Memory, no Learning, no Planning N+1.
