# RP.18.2D — Snapshot operativo unificado del runtime

## Objetivo

Proveer una única fotografía operativa, inmutable y serializable del runtime oficial de ROBY, construida exclusivamente desde las autoridades consolidadas en RP.18.2B y RP.18.2C.

## Fuente de verdad

El snapshot combina, sin duplicar estado ni ejecutar acciones:

- `LongLivedRuntimeLifecycle` para identidad, estado y heartbeat del proceso;
- `RuntimeHeartbeatSupervisor` para conocer si la supervisión está activa;
- `ResidentComponentRegistry` para estado, salud, criticidad y errores residentes.

`OfficialROBYRuntime.snapshot()` es el acceso oficial. La propiedad `operational_snapshot` ofrece la misma lectura para consumidores que prefieran una vista inmediata.

## Modelo

`RuntimeOperationalSnapshot` expone:

- fecha de generación;
- estado y salud global;
- disponibilidad operativa;
- identidad del proceso y sesión;
- timestamps del lifecycle;
- estado del supervisor;
- residentes sin exponer sus instancias;
- conteos agregados;
- causas normalizadas de degradación.

## Reglas de salud

- `HEALTHY`: lifecycle ejecutándose, supervisor activo y residentes requeridos disponibles, sin incidencias.
- `DEGRADED`: lifecycle degradado, supervisor ausente o fallo/degradación opcional.
- `UNAVAILABLE`: lifecycle fallido o residente requerido indisponible.
- `UNKNOWN`: runtime todavía no iniciado o detenido sin una falla activa.

La disponibilidad (`available`) es más estricta que la continuidad: solo es verdadera cuando el runtime está plenamente saludable.

## Límites

Esta etapa no agrega:

- recuperación automática;
- publicación de eventos;
- métricas históricas;
- observabilidad externa;
- decisiones metacognitivas;
- mutaciones sobre lifecycle o residentes.

El snapshot es una lectura puntual y determinista.
