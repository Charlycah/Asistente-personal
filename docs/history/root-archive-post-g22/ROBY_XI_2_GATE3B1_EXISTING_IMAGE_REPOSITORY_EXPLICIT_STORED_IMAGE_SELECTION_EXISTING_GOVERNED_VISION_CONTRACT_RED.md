# ROBY XI.2 — GATE 3.B.1
## Existing Image Repository → Explicit Stored-Image Selection → Existing Governed Vision — CONTRACT RED

**Base certificada:** GATE 3.A.1 SURGICAL GREEN, 13.937 PASS + Ruff limpio + 0 FAIL.  
**Reconciliación previa:** GATE 3.B Contract Boundary Reconciliation.  
**Estado de este paquete:** CONTRACT RED intencional.  
**Producción:** sin cambios productivos en este gate.

## 1. Objeto

Convertir los gaps demostrados en GATE 3.B en un contrato ejecutable antes de tocar producción. El RED no crea una Pinacoteca cognitiva ni una autoridad visual nueva. Fija únicamente el seam mínimo entre el repositorio de imágenes existente, una selección explícita de una imagen ya almacenada y las autoridades visuales existentes.

## 2. Autoridades preservadas

- `core.governed_image_repository.ImageRepository`: puerto de persistencia.
- `infrastructure.vision.file_image_repository.FileImageRepository`: adaptador durable privado.
- `app.vision_gateway.GovernedVisionGateway`: frontera oficial de aplicación.
- `app.vision_core.OfficialVisionCore`: autoridad visual canónica.
- `core.intelligent_vision.IntelligentVisionService`: política/gobierno.

No se autoriza `PinacotecaManager`, `VisualCollectionManager`, otro Vision Core, otro Vision Gateway ni otro ImageRepository.

## 3. Contrato RED

El test `tests/architecture/test_gate3b1_stored_image_selection_existing_governed_vision_contract_red.py` exige:

1. `ImageRepository` debe ampliar su boundary con lectura controlada del asset seleccionado, owner-scoped y por `image_id`.
2. `FileImageRepository` debe resolver internamente el asset; consumidores no conocen root/path físico.
3. La lectura debe rechazar owner incorrecto.
4. La lectura debe verificar SHA-256 antes de entregar bytes transitorios.
5. `GovernedVisionGateway` debe exponer una operación explícita para analizar una stored image seleccionada.
6. El consentimiento histórico de almacenamiento no basta: la operación de análisis necesita consentimiento/solicitud explícitos actuales.
7. El resultado debe conservar `image_id`, owner, SHA-256, MIME y `source_ref=stored_image:<image_id>` sin exponer bytes crudos.
8. `OfficialVisionCore` debe aceptar una entrada visual ya adquirida sin obligar a una nueva captura de cámara.
9. Ese análisis no debe usar `CameraProvider` ni incrementar semántica de captura.
10. El runtime debe poder provisionar un `GovernedVisionGateway` oficial con el `FileImageRepository` existente y un root privado explícito (`ROBY_VISUAL_COLLECTION_ROOT`).
11. No se introducen autoridades visuales paralelas.
12. `StoredImage.sha256` continúa siendo prueba de contenido y `image_id` la identidad de la pieza almacenada.

## 4. Límites explícitos

Fuera de alcance:

- reconocimiento/identificación biométrica;
- embeddings o vector store;
- búsqueda semántica de imágenes;
- watchers/scanners/importación automática de galerías;
- re-retención implícita de bytes;
- Memory;
- Learning;
- Planning / Planning N+1;
- Reasoning automático;
- ejecución automática;
- edición de imágenes;
- música/audio;
- CAP-18 como autoridad cognitiva nueva.

`.roby/config.json` no debe modificarse. `credencial.json` debe preservarse si existe.

## 5. Semántica esperada del RED

En la base reconciliada, los tests funcionales nuevos deben fallar exclusivamente porque todavía faltan los seams productivos descritos. Las invariantes que ya existen —una sola autoridad visual y provenance SHA-256 de `StoredImage`— deben permanecer verdes.

El RED correcto habilita después, y sólo después de certificación local, un SURGICAL GREEN de alcance mínimo.

**STOP:** no implementar producción dentro de este paquete RED.
