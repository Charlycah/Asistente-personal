# RP.18.2E — Runtime Health & Readiness Service

## Objetivo

Traducir el snapshot operativo unificado de ROBY en una evaluación explícita,
inmutable y explicable de salud y readiness global, además de readiness por
capacidad.

El servicio no administra lifecycle, no inicia componentes, no recupera fallos
y no duplica estado. Su única fuente es `RuntimeOperationalSnapshot`.

## Autoridad

`app.runtime_health_readiness.RuntimeHealthReadinessService` consume el snapshot
oficial y produce `RuntimeHealthReadinessReport`.

`OfficialROBYRuntime` expone:

- `health_readiness`
- `readiness(*capabilities, now=None)`

## Niveles globales

- `unknown`
- `not_ready`
- `ready`
- `degraded`
- `blocked`

Un lifecycle creado o iniciando todavía no está listo, pero tampoco se considera
fallado. Un lifecycle fallido o un residente requerido indisponible bloquea el
runtime. Incidencias opcionales degradan el readiness sin bloquearlo.

## Readiness por capacidad

`RuntimeCapabilityRequirement` declara:

- identidad de capacidad;
- residentes requeridos;
- residentes opcionales;
- necesidad de runtime activo;
- necesidad de supervisor activo;
- descripción.

El resultado por capacidad puede ser:

- `unknown`;
- `available`;
- `degraded`;
- `unavailable`.

La evaluación por capacidad es independiente del resultado global. Por ejemplo,
ROBY puede estar globalmente listo mientras una capacidad no configurada queda
indisponible. Del mismo modo, una dependencia opcional ausente puede degradar
una capacidad sin bloquear su uso.

## Compatibilidad con M162

El paquete histórico `core.runtime_readiness_gate` conserva su función cognitiva
y advisory. RP.18.2E no lo reemplaza ni le concede autoridad operativa. El nuevo
servicio vive en `app`, se basa en el runtime real y tampoco autoriza acciones.

## Garantías

- vista inmutable;
- serialización segura con `to_dict()`;
- sin exposición de instancias residentes;
- findings separados en `blockers` y `warnings`;
- búsquedas de capacidad sin sensibilidad a mayúsculas;
- validación de identidades duplicadas y dependencias contradictorias;
- evaluación determinista sobre un snapshot dado.
