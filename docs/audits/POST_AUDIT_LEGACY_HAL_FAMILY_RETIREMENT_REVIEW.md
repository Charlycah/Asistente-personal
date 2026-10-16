# ROBY XI.2 — LEGACY HAL FAMILY RETIREMENT REVIEW

## Baseline
POST-G22 + CURRENT TRUTH CONSOLIDATION + ROOT CLEANUP + FASE 5.H  
14.191 PASS · 0 FAIL · Ruff clean.

## Decisión
RETIREMENT APPROVED AS A GOVERNED, COORDINATED SURGERY.

La familia HAL histórica revisada no presenta consumidores productivos actuales y
puede retirarse sin eliminar la compatibilidad de configuración `.hal`, porque
esa migración ya está implementada en `app.roby_config`.

## Familia candidata
- `app/hal_config.py`
- `core/hal.py`
- `core/hal_console_application/`
- `core/hal_voice_style_policy/`
- `interfaces/cli/hal_console.py`

Superficie aproximada: 1.382 líneas Python.

## Evidencia de aislamiento

### `core.hal`
- No tiene imports productivos externos detectados.
- Sólo aparece como target histórico en `app.runtime_compatibility`.
- `runtime_compatibility` lo declara `LEGACY_ISOLATED`, `executable=False`.
- No es Composition Root oficial.
- El contrato M395.4 permite únicamente `core/hal.py` y `core/roby.py` como
  importadores de M3→M7.

### `app.hal_config`
- No tiene consumidor productivo.
- Un test arquitectónico sólo inspecciona que no importe directamente
  `runtime_root_factory`.
- `app.roby_config` ya contiene `LEGACY_CONFIG_PATH = Path(".hal/config.json")`
  y ejecuta la migración/normalización correspondiente.
- Por tanto retirar `app.hal_config` NO elimina la capacidad de migrar una
  configuración histórica `.hal`.

### `core/hal_console_application`
- Sin consumidores externos detectados.
- Sólo consume internamente `core.hal_voice_style_policy`.
- La superficie vigente equivalente es `core.roby_console_application`.

### `core/hal_voice_style_policy`
- Sin consumidores salvo la console HAL histórica.
- Los tests históricos M165 ya ejercitan `core.roby_voice_style_policy`.

### `interfaces/cli/hal_console.py`
- Sin consumidores detectados.
- Los tests M172 usan `interfaces.cli.roby_console`.

## Contratos que deben cambiar en la cirugía

### `app/runtime_compatibility.py`
`legacy_hal_runtime` debe dejar de figurar como una superficie viva
`LEGACY_ISOLATED`.

Recomendación:
- conservar el registro por trazabilidad;
- cambiar disposition a `RETIRED`;
- executable=False;
- delegates_to=None;
- nota explícita de que la implementación fue retirada después de M395.4.

No crear alias hacia ROBY: eso reviviría un nombre histórico innecesario.

### `tests/architecture/test_m395_4_compatibility_legacy.py`
Actualizar el contrato:
- `legacy_hal_runtime` esperado como `RETIRED`;
- `legacy_roby_runtime` sigue `LEGACY_ISOLATED`;
- `ALLOWED_CORE_LEGACY_IMPORTERS` pasa de
  `{"core/hal.py", "core/roby.py"}` a `{"core/roby.py"}`.

### `tests/architecture/test_m395_2_bootstrap_composition_boundaries.py`
Eliminar la aserción que intenta analizar `app.hal_config`, dado que el módulo
dejará de existir.
No reemplazarla por otro módulo: `app.roby_config` ya está cubierto.

## Documentación
Actualizar sólo documentación canónica/actual relevante para dejar explícito:
- HAL family RETIRED;
- `core.roby` continúa LEGACY_ISOLATED;
- M3→M7 continúan FROZEN;
- la migración `.hal/config.json` permanece en `app.roby_config`.

La documentación histórica M395.4 NO debe reescribirse como si HAL nunca hubiese
existido. Debe mantenerse como historia y, si hace falta, recibir una nota de
supersession posterior.

Los manifiestos históricos con SHA-256 no deben borrarse ni recalcularse para
reescribir el pasado.

## Fuera de alcance
NO retirar:
- `core.roby`
- `m3`, `m4`, `m5`, `m6`, `m7`
- `app.roby_config`
- migración `.hal/config.json`
- `m6.response.models` shim
- runtime compatibility registry
- Composition Root

NO tocar:
- `runtime_root_factory.py`
- authorities
- stores
- persistence productiva
- Cognitive/Planning runtime

## Riesgo
BAJO-MEDIO.

Bajo desde runtime productivo porque no hay reachability moderna.
Medio desde contratos históricos porque M395.2/M395.4 codifican expresamente la
presencia de HAL y deben evolucionarse en sincronía.

## Cirugía recomendada
1. Eliminar los 9 archivos Python de la familia HAL.
2. Marcar `legacy_hal_runtime` como RETIRED.
3. Ajustar M395.2 y M395.4 para reflejar el retiro.
4. Actualizar Current Truth / documentación actual.
5. No modificar historia congelada salvo nota de supersession.
6. Ejecutar validación dirigida de compatibility/bootstrap.
7. Ejecutar certificación completa:
   - `python scripts/clean_project_caches.py`
   - `python scripts/generate_quality_baseline.py`
   - `ruff check .`
   - `pytest -q`

## Criterios de aceptación
- cero imports a módulos HAL retirados;
- `core.roby` es el único importador histórico core permitido de M3→M7;
- `.hal/config.json` sigue migrando por `app.roby_config`;
- ninguna nueva authority/alias/runtime;
- Ruff clean;
- full pytest clean.

## Conclusión
La compatibilidad HAL ya no aporta comportamiento productivo ni migración
exclusiva. Su existencia actual es principalmente evidencia histórica y contrato
de compatibilidad.

El retiro coordinado está arquitectónicamente justificado y reduce superficie
muerta sin tocar el cerebro unificado ni las islas históricas M3→M7.

NEXT CANDIDATE:
LEGACY HAL FAMILY RETIREMENT — IMPLEMENTATION.
