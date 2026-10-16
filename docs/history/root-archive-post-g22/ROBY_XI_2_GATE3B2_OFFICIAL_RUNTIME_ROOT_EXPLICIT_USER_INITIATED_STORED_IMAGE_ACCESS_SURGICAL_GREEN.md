# ROBY XI.2 — GATE 3.B.2 — SURGICAL GREEN
## Official Runtime Root → Explicit User-Initiated Stored-Image Access

**Entrada certificada por el usuario:** GATE 3.B.2 CONTRACT RED — Ruff limpio, 13.952 PASS, 11 RED FAIL esperados, 0 FAIL externos.

## 1. Objeto

Cerrar exclusivamente la reachability productiva faltante entre el runtime oficial y la colección visual privada ya gobernada, sin crear una nueva autoridad visual.

Flujo resultante:

`build_runtime_root()` → una sola `build_vision_gateway_from_environment()` → `build_governed_stored_image_runtime(...)` → una capability oficial `vision.stored_images.read_analyze` → petición explícita del usuario → listado metadata owner-scoped o análisis por `image_id` exacto + consentimiento fresco → mismo `GovernedVisionGateway.analyze_stored_image()` → mismo `OfficialVisionCore` → STOP.

## 2. Cambios quirúrgicos

1. `app/governed_stored_image_runtime_wiring.py` — nuevo seam subordinado de reachability. No crea repositorio, Vision Core ni Vision Gateway.
2. `app/runtime_root_factory.py` — construye exactamente una vez el gateway visual existente y reutiliza esa misma instancia en el wiring subordinado.
3. `core/runtime_composition_root/models.py` — añade `governed_visual_collection_runtime` como dependencia observable del runtime oficial.
4. `tests/architecture/test_gate3b2_official_runtime_root_explicit_stored_image_access_contract_red.py` — se integra la corrección de imports entregada por el usuario y el último assert se transforma al estado GREEN para verificar que importar el wiring no modifica `.roby/config.json`.
5. `docs/quality/M396_3_AUTHORITY_PRESERVATION_BASELINE.json` — reconciliado únicamente por el hash legítimamente cambiado de `app/runtime_root_factory.py`.
6. `docs/quality/M361_QUALITY_BASELINE.json` — regenerado.

## 3. Invariantes preservadas

- `ImageRepository` sigue siendo el único port de persistencia visual.
- `FileImageRepository` sigue siendo el único adapter privado local.
- `GovernedVisionGateway` sigue siendo la única frontera de aplicación visual.
- `OfficialVisionCore` sigue siendo el único núcleo visual oficial.
- listado: owner-scoped, metadata-only, sin análisis.
- análisis: `image_id` exacto, petición humana explícita y consentimiento actual.
- no se exponen bytes ni paths físicos en el resultado conversacional.
- no se usa `CameraProvider` para stored images.
- `.roby/config.json` no se modifica.
- `credencial.json` no se toca.

## 4. STOP

Continúan fuera de alcance: biometría/identificación, scanning/watchers/background indexing, selección automática, análisis automático al listar, embeddings/vector store, edición de imágenes, música/audio, Memory, Learning, Planning / Planning N+1 y Reasoning automático.

## 5. Validación realizada por el asistente

- contrato GATE 3.B.2: **13 PASS**;
- GATE 3.B.2 + GATE 3.B.1 + M361 + M396.3 focal: **43 PASS**;
- `python -m compileall -q app core infrastructure domain`: **CLEAN**;
- `python scripts/generate_quality_baseline.py`: ejecutado;
- `ruff`: no disponible en el entorno del asistente;
- suite completa: intento iniciado pero el runner del entorno agotó su ventana antes de finalizar, por lo que no se reclama certificación integral local del asistente.

## 6. Estado

**GATE 3.B.2 — SURGICAL GREEN — IMPLEMENTADO, PENDIENTE DE CERTIFICACIÓN LOCAL DEL USUARIO.**
