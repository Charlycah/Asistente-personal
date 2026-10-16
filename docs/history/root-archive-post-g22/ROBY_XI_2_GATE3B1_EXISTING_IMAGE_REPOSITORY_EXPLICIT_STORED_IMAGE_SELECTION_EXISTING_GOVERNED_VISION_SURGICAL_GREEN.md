# ROBY XI.2 — GATE 3.B.1
## Existing Image Repository → Explicit Stored-Image Selection → Existing Governed Vision — SURGICAL GREEN

**RED certificado por el usuario:** 13.939 PASS + 11 RED FAIL esperados + Ruff limpio + 0 FAIL externos.  
**Estado:** SURGICAL GREEN certificado localmente por el usuario: 13.950 PASS + Ruff limpio + 0 FAIL.

## 1. Resultado

El seam contractual de GATE 3.B.1 queda implementado extendiendo exclusivamente las autoridades existentes. No se crea PinacotecaManager, VisualCollectionManager, otro Vision Core, otro Vision Gateway ni otro repositorio de imágenes.

Flujo implementado:

`image_id + owner + consentimiento explícito actual` → `ImageRepository.read_asset` → verificación owner + SHA-256 en `FileImageRepository` → bytes transitorios internos → `GovernedVisionGateway.analyze_stored_image` → `OfficialVisionCore.analyze_stored_image` → resultado seguro con provenance → STOP.

## 2. Cambios productivos quirúrgicos

1. `core/governed_image_repository.py`
   - añade `StoredImageAsset`, contenedor transitorio sin path/root;
   - amplía el puerto `ImageRepository` con `read_asset(image_id, *, owner)`.
2. `infrastructure/vision/file_image_repository.py`
   - implementa lectura por identidad almacenada;
   - valida owner;
   - resuelve internamente el path físico;
   - recalcula y verifica SHA-256 antes de devolver bytes transitorios.
3. `app/vision_gateway.py`
   - añade `StoredImageAnalysisRequest` con selección explícita y consentimiento fresco;
   - añade `StoredImageAnalysisResult` sin raw bytes;
   - añade `analyze_stored_image`, preservando `image_id`, owner, SHA-256, MIME y `source_ref`.
4. `app/vision_core.py`
   - añade boundary no-camera `StoredVisualInput`;
   - añade `OfficialVisionCore.analyze_stored_image` sin invocar `CameraProvider` ni alterar contadores de captura.
5. `app/runtime_environment_wiring.py`
   - añade `build_vision_gateway_from_environment`;
   - reutiliza `GovernedVisionGateway`, `OfficialVisionCore` y `FileImageRepository` existentes;
   - root privado configurable mediante `ROBY_VISUAL_COLLECTION_ROOT`, default `.roby/visual_collection`.

## 3. Autoridades preservadas

- `ImageRepository`: puerto canónico de persistencia visual.
- `FileImageRepository`: adapter privado existente.
- `GovernedVisionGateway`: única frontera oficial de aplicación.
- `OfficialVisionCore`: única autoridad visual canónica.
- No se modifica la semántica de captura de cámara existente.

## 4. Privacidad y provenance

- El almacenamiento histórico no autoriza un análisis posterior.
- Cada análisis exige `explicit_user_consent=True` y `user_requested=True`.
- El owner solicitado debe coincidir con el owner persistido.
- Los bytes sólo viven en el handoff transitorio interno y no aparecen en el resultado.
- El path/root físico no cruza el contrato del repositorio.
- `image_id` preserva identidad y SHA-256 prueba integridad de contenido.
- `source_ref` es `stored_image:<image_id>`.

## 5. Límites / STOP

Este GREEN no habilita:

- identificación biométrica;
- embeddings/vector store;
- búsqueda semántica de imágenes;
- scanner/watchers/importación automática de galerías;
- almacenamiento automático de capturas;
- Memory;
- Learning;
- Planning / Planning N+1;
- Reasoning automático;
- ejecución automática;
- edición de imágenes;
- música/audio;
- una nueva autoridad cognitiva CAP-18.

`.roby/config.json` permanece fuera de alcance. `credencial.json` debe preservarse si existe.

## 6. Validación del paquete antes de entrega

- contrato GATE 3.B.1: **13 PASS**;
- slice visual existente + contrato: **96 PASS**;
- M361 + M396.3 + contrato: **30 PASS**;
- `compileall core app infrastructure domain`: limpio;
- line-length manual de archivos Python modificados: limpio.

Certificación local posterior: `python scripts/generate_quality_baseline.py`, `ruff check .` y `pytest -q` cerraron con 13.950 PASS + Ruff limpio + 0 FAIL. Las dos correcciones de orden/formato de imports suministradas por el usuario para `app/runtime_environment_wiring.py` y `app/vision_gateway.py` quedan incorporadas en la siguiente entrega ZIP.
