# M395.2 — Bootstrap y Composición

## Objetivo

Consolidar el bootstrap y la composición operacional sin introducir capacidades,
autoridades ni composition roots adicionales.

## Cambios

1. `app.runtime_bootstrap_contract` concentra los identificadores estables de
   bootstrap sin importar implementaciones de runtime.
2. `roby_config` y `hal_config` dejan de importar `runtime_root_factory` sólo para
   leer el identificador de factory.
3. El SCC histórico entre `roby_config`, `runtime_root_factory`,
   `runtime_environment_wiring`, `unified_runtime_integration` y `voice_input`
   queda roto.
4. `RuntimeCompositionRoot.compose()` conserva la autoridad única de composición,
   pero delega el wiring de contributors cognitivos a una función privada
   subordinada. No se crea otro root.
5. `OFFICIAL_RUNTIME_FACTORY` continúa reexportado desde
   `app.runtime_root_factory` para compatibilidad.

## Invariantes

- Una sola `RuntimeCompositionRoot`.
- Una sola factory oficial: `app.runtime_root_factory:build_runtime_root`.
- Configuración no depende de la implementación de la factory.
- Wiring privado no adquiere autoridad cognitiva.
- Sin capacidades funcionales nuevas.
