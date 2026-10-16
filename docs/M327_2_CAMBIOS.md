# ROBY XI.2 M327.2 — Integración del primer ciclo autónomo con el runtime real

## Objetivo

Conectar la primera capacidad autónoma de M327.1 con un flujo operativo real,
sin ampliar todavía el catálogo de acciones ni introducir recuperaciones,
reinicios o mutaciones automáticas.

## Implementación

`RuntimeExecutiveIntegration` ahora:

- compone por defecto `default_first_autonomous_capability_runner()` usando el
  mismo `RecoveryHealthCoordinator` del runtime;
- utiliza una política explícita `AUTONOMOUS_LOW_RISK`, sin simulación;
- convierte cada fallo real registrado de coordinador, broker o presentación en
  una observación mediante `observation_from_component_health()`;
- ejecuta el pipeline gobernado completo de M326 y la verificación de salud de
  M327.1;
- conserva el último resultado autónomo y un contador de ciclos en el snapshot;
- evita que un error interno de autonomía oculte el error operativo original.

## Flujo integrado

```text
fallo operativo real
-> RecoveryHealthCoordinator.record_failure()
-> observation_from_component_health()
-> decisión gobernada
-> autorización de bajo riesgo
-> verify_component_health
-> supervisión del outcome
-> snapshot observable
```

## Límites de seguridad

- La única acción ejecutable sigue siendo `verify_component_health`.
- La capacidad continúa siendo de solo lectura.
- No se invocan handlers de recuperación.
- No se reinician ni habilitan componentes.
- No se modifican contadores de salud desde la capacidad autónoma.
- El camino exitoso normal no activa ningún ciclo autónomo.
- El fallo autónomo queda registrado pero no reemplaza la excepción original.

## Validación

```text
3 pruebas nuevas M327.2 OK
28 pruebas focalizadas OK
7672 pruebas totales OK
compileall OK
```

Ruff no estaba instalado en el entorno de construcción utilizado para generar
este ZIP. Debe ejecutarse localmente con `ruff check .` antes de promover la
versión como nueva base estable.
