# ROBY XI.2 — P7-C2-LOCAL-S2C-A — GREEN QUIRÚRGICO

## Estado

GREEN quirúrgico construido sobre el RED Owner-certified de 12,878 PASS / 3 expected RED FAIL / Ruff clean.

## Cirugía

Única modificación productiva: `app/official_runtime_composition.py`.

`build_official_runtime_from_environment(...)` ahora:

1. construye el `OfficialConversationGateway` existente;
2. invoca `build_foursquare_governed_source_from_environment()`;
3. si el resultado es `None`, continúa fail-closed sin registrar provider;
4. si existe adapter, lo registra mediante `register_governed_source_query_adapter(...)` usando `FoursquareGovernedSourceAdapter.SOURCE_ID`;
5. no ejecuta consultas ni autoriza acceso externo durante startup.

## Frontera preservada

`PROVIDER AVAILABLE AT STARTUP != PER-TURN NETWORK AUTHORIZATION`.

No se modifica `OfficialConversationGateway`. No se abre S2C-B. No se agrega network execution, ubicación persistente, Memory, Learning, Planning, Execution, booking o navigation.

## Validación local disponible

- contrato S2C-A: 7 PASS;
- regresión focal S1 + S2A + S2B-A + S2B-B + S2C-A: 56 PASS;
- `py_compile`: PASS;
- M361 regenerado;
- máximo de línea del archivo productivo modificado: 88;
- SHA-256 del gateway protegido preservado: `05626c7376b1ebe36b82b6c7c4503b88f6a101e2ba585947493044c8238d36f8`;
- Ruff no está instalado en el entorno de construcción;
- un intento de suite completa excedió el límite local de ejecución y no se usa como evidencia de certificación.

## Gate Owner requerido

```text
python scripts/clean_project_caches.py
python scripts/generate_quality_baseline.py
ruff check .
pytest -q
```

Resultado contractual esperado: 12,881 PASS / 0 FAIL / Ruff clean.

## STOP

GREEN BUILT → OWNER CERTIFICATION PENDING → STOP BEFORE S2C-A CLOSURE / S2C-B.
