# ROBY XI.2 — GATE 3.B.2
## Official Runtime Root → Explicit User-Initiated Stored-Image Access — CONTRACT BOUNDARY RECONCILIATION

**Baseline de entrada certificada por el usuario:** 13.950 PASS + Ruff limpio + 0 FAIL.

**Naturaleza del gate:** reconciliación arquitectónica / contractual. No abre una nueva autoridad visual ni cognitiva.

## 1. Objeto

Determinar el seam mínimo que falta después de GATE 3.B.1 para que la colección visual privada ya gobernada sea alcanzable desde el runtime oficial de ROBY por petición explícita del usuario, reutilizando exclusivamente las autoridades existentes.

GATE 3.B.1 ya cerró el tramo interno:

`image_id + owner + consentimiento explícito` → `ImageRepository.read_asset` → `FileImageRepository` owner/hash check → `GovernedVisionGateway.analyze_stored_image` → `OfficialVisionCore.analyze_stored_image` → resultado estructurado seguro → STOP.

Este gate estudia únicamente la reachability productiva anterior a ese tramo:

`Official Runtime Root` → `explicit user request` → `existing GovernedVisionGateway`.

## 2. Evidencia real del repositorio

### 2.1 El builder visual ya existe

`app/runtime_environment_wiring.py` contiene `build_vision_gateway_from_environment()`.

Ese builder:

- crea el adapter existente `FileImageRepository`;
- usa `ROBY_VISUAL_COLLECTION_ROOT` con default `.roby/visual_collection`;
- construye el `GovernedVisionGateway` existente;
- usa el `OfficialVisionCore` existente.

No crea un segundo Vision Gateway, Vision Core o Image Repository.

### 2.2 El runtime root todavía no lo provisiona

`app/runtime_root_factory.py` no importa ni invoca `build_vision_gateway_from_environment()`.

Por tanto, el builder existe pero todavía no es productivamente alcanzable desde `build_runtime_root()`.

### 2.3 El capability registry oficial todavía no expone la colección almacenada

El runtime root registra actualmente capacidades operativas como cámara, correo, calendario y Biblioteca, pero no existe una capability productiva para:

- listar metadata de imágenes privadas por owner;
- seleccionar explícitamente un `image_id`;
- solicitar análisis de esa imagen almacenada por el `GovernedVisionGateway` ya existente.

La cámara no es sustituto válido: GATE 3.B.1 separó expresamente análisis de stored image de semántica de captura.

### 2.4 La authority visual ya tiene operaciones suficientes

`GovernedVisionGateway` ya ofrece:

- `list_stored_images(owner=...)`;
- `get_stored_image(image_id)`;
- `analyze_stored_image(StoredImageAnalysisRequest)`;
- store/delete gobernados ya existentes.

No se justifica crear un `PinacotecaManager`, `VisualCollectionManager`, segundo repositorio, segundo gateway ni segundo core.

### 2.5 Existe un patrón productivo canónico reutilizable

Biblioteca ya demuestra el patrón correcto de reachability:

`runtime root` → wiring existente → interceptor de conversación subordinado → capability registry oficial → authority existente.

Para colección visual debe reutilizarse ese patrón de composición, sin copiar la authority de Biblioteca ni crear una authority cognitiva nueva.

## 3. Dictamen

Clasificación:

**EXISTING GOVERNED VISUAL AUTHORITIES + MINIMAL OFFICIAL RUNTIME REACHABILITY SEAM REQUIRED**

El residual no está en visión, persistencia ni análisis. Está exclusivamente en la exposición productiva, explícita y user-initiated desde el composition root oficial.

## 4. Seam canónico permitido

El seam mínimo admitido para el próximo CONTRACT RED es:

`build_runtime_root()`
→ construye **una sola vez** `build_vision_gateway_from_environment()`
→ expone un **interceptor/port de conversación subordinado**
→ registra una capability read/analyze de colección visual en el `OfficialRuntimeCapabilityRegistry`
→ usuario pide listar o analizar
→ listado owner-scoped devuelve sólo metadata/provenance
→ análisis exige `image_id` explícito + consentimiento actual
→ mismo `GovernedVisionGateway.analyze_stored_image()`
→ mismo `OfficialVisionCore`
→ resultado estructurado seguro
→ STOP.

## 5. Semántica de selección

La selección productiva debe permanecer deliberadamente estrecha:

1. listar puede devolver metadata owner-scoped;
2. listar no analiza imágenes;
3. ninguna imagen se selecciona automáticamente;
4. análisis requiere `image_id` exacto ya elegido por el usuario;
5. owner del request debe propagarse sin reemplazo implícito;
6. el consentimiento debe ser fresco para el análisis;
7. un nombre de archivo ambiguo no debe convertirse silenciosamente en un `image_id`;
8. no se introduce búsqueda semántica/vectorial ni embeddings.

## 6. Provenance y privacidad

El boundary productivo sólo puede exponer metadata segura ya existente:

- `image_id`;
- owner;
- MIME;
- SHA-256;
- timestamps/metadata ya persistidos cuando correspondan;
- `source_ref=stored_image:<image_id>` en resultados de análisis.

No debe exponer:

- path físico;
- root privado;
- bytes crudos;
- hashes como mecanismo de búsqueda global;
- contenido de otro owner.

## 7. Qué NO debe hacer el próximo RED/GREEN

Queda fuera de alcance:

- crear CAP-18 como autoridad paralela;
- crear `PinacotecaManager` o `VisualCollectionManager`;
- escanear carpetas o galería automáticamente;
- watcher/background indexing;
- importar imágenes automáticamente;
- analizar automáticamente después de listar;
- usar CameraProvider para stored images;
- identificación biométrica;
- face recognition/identity;
- embeddings/vector store;
- Memory;
- Learning;
- Planning / Planning N+1;
- Reasoning automático;
- edición de imágenes;
- música/audio.

`.roby/config.json` permanece fuera de alcance y `credencial.json` debe preservarse si existe.

## 8. Forma recomendada del próximo CONTRACT RED

El siguiente RED debe probar únicamente estas invariantes:

1. `runtime_root_factory` importa el builder visual existente;
2. `build_runtime_root()` construye exactamente un `GovernedVisionGateway` de colección privada;
3. el mismo gateway se entrega al interceptor/port productivo, sin reconstrucción;
4. capability registry registra exactamente una superficie read/analyze para stored images;
5. listado es owner-scoped y metadata-only;
6. listado no llama `analyze_stored_image`;
7. análisis exige `image_id` exacto;
8. análisis exige consentimiento explícito/fresco;
9. análisis delega una sola vez al mismo `GovernedVisionGateway`;
10. el resultado no expone raw bytes ni filesystem path;
11. no se usa camera capture para stored-image access;
12. no aparece una segunda authority visual;
13. no hay Memory/Learning/Planning/Reasoning automático.

## 9. Decisión de arquitectura

**GO para CONTRACT RED**, pero sólo sobre reachability oficial user-initiated.

No hay justificación para ampliar visión, persistencia o cognición en este gate.

## 10. Estado

**GATE 3.B.2 — CONTRACT BOUNDARY RECONCILIATION — COMPLETADO.**

**NEXT:** GATE 3.B.2 — Official Runtime Root → Explicit User-Initiated Stored-Image Access — CONTRACT RED.

**STOP:** no producción adicional antes del RED contractual y su certificación local.
