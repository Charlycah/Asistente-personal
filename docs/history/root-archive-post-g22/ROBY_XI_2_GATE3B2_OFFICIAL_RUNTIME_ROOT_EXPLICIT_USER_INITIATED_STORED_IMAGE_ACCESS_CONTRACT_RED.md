# ROBY XI.2 — GATE 3.B.2 — CONTRACT RED
## Official Runtime Root → Explicit User-Initiated Stored-Image Access

**Baseline de entrada certificada por el usuario:** 13.950 PASS + Ruff limpio + 0 FAIL.

**Precondición:** GATE 3.B.2 Contract Boundary Reconciliation completado.

## 1. Objeto

Congelar mediante RED contractual el único seam productivo todavía ausente entre el runtime oficial y la colección visual privada ya gobernada.

El contrato no autoriza una nueva autoridad visual. Debe reutilizar:

`FileImageRepository` → `GovernedVisionGateway` → `OfficialVisionCore`.

## 2. Frontera requerida

El futuro GREEN sólo podrá cerrar:

`build_runtime_root()`
→ una única instancia creada por `build_vision_gateway_from_environment()`
→ wiring/interceptor subordinado
→ una única capability oficial para stored images
→ petición explícita del usuario
→ list metadata owner-scoped **o** análisis por `image_id` exacto
→ consentimiento fresco para análisis
→ mismo `GovernedVisionGateway.analyze_stored_image()`
→ resultado seguro
→ STOP.

## 3. Contrato RED

El archivo:

`tests/architecture/test_gate3b2_official_runtime_root_explicit_stored_image_access_contract_red.py`

fija 13 invariantes:

1. el runtime root importa el builder visual existente;
2. el runtime root lo invoca exactamente una vez;
3. `RuntimeCompositionDependencies` expone un único wiring visual gobernado;
4. existe un wiring productivo subordinado para stored-image access;
5. ese wiring recibe/reutiliza el mismo `GovernedVisionGateway` y no lo reconstruye;
6. se registra exactamente una capability canónica read/analyze;
7. listar es owner-scoped y metadata-only;
8. listar no ejecuta análisis;
9. analizar requiere `image_id` exacto y no selección fuzzy/filename/semantic;
10. analizar exige consentimiento explícito actual;
11. analizar delega una sola vez al mismo gateway existente;
12. siguen existiendo una sola `OfficialVisionCore` y una sola `GovernedVisionGateway`;
13. `.roby/config.json` permanece byte-identical.

## 4. RED esperado

La base actual debe fallar sólo porque todavía no existe la reachability productiva indicada. Los fallos esperados son contractuales, no regresiones funcionales de GATE 3.B.1.

No debe tocarse producción para convertir este RED en verde antes de la certificación local del usuario.

## 5. STOP

Fuera de alcance:

- nueva authority CAP-18;
- `PinacotecaManager` / `VisualCollectionManager`;
- scanning/watchers/background indexing;
- selección automática;
- análisis automático después de listar;
- CameraProvider para stored images;
- biometría / identificación facial;
- embeddings/vector store;
- Memory;
- Learning;
- Planning / Planning N+1;
- Reasoning automático;
- edición de imágenes;
- música/audio.

`credencial.json` debe preservarse si existe.

## 6. Estado

**GATE 3.B.2 — CONTRACT RED — PREPARADO, PENDIENTE DE CERTIFICACIÓN LOCAL.**

Siguiente movimiento permitido únicamente después de certificación:

**GATE 3.B.2 — SURGICAL GREEN.**
