# RP.18.2A — Inventario de ejecutables y roots

## Propósito

Esta etapa inicia la depuración operativa previa a la metacognición. Su alcance es
identificar, clasificar y certificar todos los puntos que pueden construir, adaptar
o iniciar una ejecución de ROBY. No modifica todavía el lifecycle ni retira código.

## Cadena oficial encontrada

```text
main:main
  -> app.local_conversation_factory:build_local_conversation_from_environment
  -> app.local_runtime_entrypoint:build_local_runtime_from_environment
  -> app.runtime_root_factory:build_runtime_root
  -> core.runtime_composition_root:RuntimeCompositionRoot
```

El modo escritorio entra también por `main:main` y delega en
`app.desktop_bootstrap:build_unified_desktop_app`.

## Clasificación

| Clave | Target | Rol | Decisión RP.18.2 |
|---|---|---|---|
| roby_process_entrypoint | `main:main` | entrada canónica de proceso | conservar como autoridad |
| desktop_runtime | `app.desktop_bootstrap:build_unified_desktop_app` | entrada UI canónica | conservar |
| desktop_compatibility_alias | `app.desktop_bootstrap:build_desktop_app` | alias compatible | conservar delegación |
| local_conversation | `app.local_conversation_factory:build_local_conversation_from_environment` | fábrica conversacional | conservar |
| local_runtime_bootstrap_factory | `app.local_runtime_entrypoint:build_local_runtime_from_environment` | bootstrap local | conservar como autoridad |
| official_runtime_factory | `app.runtime_root_factory:build_runtime_root` | fábrica canónica | conservar como autoridad |
| runtime_composition_root | `core.runtime_composition_root:RuntimeCompositionRoot` | raíz canónica | conservar como autoridad |
| long_lived_lifecycle | `app.long_lived_runtime_entrypoint:build_long_lived_lifecycle_from_environment` | adaptador lifecycle | conservar |
| desktop_operational_adapter | `app.desktop_bootstrap:build_operational_desktop_app` | adaptador gobernado | conservar |
| household_provisioning | `app.household_always_on_bootstrap:bootstrap_household` | aprovisionamiento | conservar fuera del lifecycle |
| legacy_application_composition | `app.bootstrap:build_app` | composition root histórico | delegar en una etapa posterior |
| artifact_cleaner | `scripts.clean_project_artifacts:main` | mantenimiento | conservar fuera de ROBY runtime |

## Robylazgos

1. Solo `main.py` inicia actualmente el proceso de ROBY. El otro guard
   `__main__` pertenece a una herramienta de limpieza.
2. `RuntimeCompositionRoot` ya declara ser el constructor oficial y memoiza su
   composición; es la base correcta para el Paso 2.
3. `app.bootstrap:build_app` construye un grafo histórico distinto. No se elimina
   en esta etapa porque primero deben mapearse sus consumidores y contratos.
4. `bootstrap_household` inicializa perfiles y almacenamiento doméstico, pero no
   representa una ejecución residente.
5. El escritorio delega lifecycle y supervisor en la composición oficial. La
   consola histórica fue retirada después de migrar sus contratos verificables.

## Contrato incorporado

`app.runtime_execution_inventory` ofrece un inventario inmutable y consultable,
con targets importables, roles y decisiones explícitas. Esto evita que el mapa
arquitectónico dependa solo de documentación manual.

## Límites de esta entrega

- No se redirigen builders.
- No se fusionan runtimes.
- No se elimina `app.bootstrap`.
- No se cambia el orden de arranque o apagado.
- No se modifica ninguna ruta conversacional ni de capacidades.

El siguiente paso es **RP.18.2A.2 / Paso 2 — Raíz oficial de composición**, donde
los adaptadores deberán comenzar a depender de una composición canónica única sin
romper compatibilidad.
