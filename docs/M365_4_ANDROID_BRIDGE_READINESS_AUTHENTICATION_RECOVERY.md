# M365.4 — Android Bridge Readiness, Authentication & Recovery

## Objetivo

Extender la frontera Android con una evaluación pura de readiness, autenticación declarativa y recuperación controlada, conservando la ejecución real deshabilitada.

## Readiness

`AndroidBridgeReadinessPolicy` combina la activación M365.2 y la disponibilidad de transporte M365.3. Sus estados son `DISABLED`, `BLOCKED`, `UNAVAILABLE`, `AUTHENTICATION_REQUIRED` y `READY`.

`READY` significa únicamente que las declaraciones son coherentes. Siempre conserva `executable=False`.

## Autenticación declarativa

`AndroidBridgeAuthenticationDeclaration` registra esquema, `key_id`, presencia de prueba y vigencia temporal. La frontera no almacena secretos, tokens, claves ni el valor de la prueba. No realiza criptografía ni consulta `.roby/credentials.json`.

## Recuperación controlada

`AndroidBridgeRecoveryPolicy` produce metadata determinista con estado, intento máximo y demora sugerida. No inicia timers, no duerme, no ejecuta retry loops y no abre transportes.

## Límites

M365.4 no añade conexión Android, intercambio de mensajes, autenticación criptográfica, descubrimiento, planner, herramientas o acciones. Toda ejecución futura continúa reservada a `ToolGatewayManager`.
