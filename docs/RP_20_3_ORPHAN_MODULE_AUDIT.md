# RP.20.3 — Auditoría y eliminación de módulos huérfanos

## Criterio

Un archivo se retiró únicamente cuando se cumplieron simultáneamente estas condiciones:

1. no era importado por el runtime oficial, la composición, scripts ni pruebas;
2. no registraba capabilities, lifecycles, schedulers, memoria ni persistencia;
3. era un esqueleto vacío, un placeholder histórico o una fachada duplicada;
4. existía una implementación oficial vigente cuando el nombre sugería una función real.

## Resultado

Se retiraron 33 archivos sin consumidores. La poda incluye el `core.orchestrator`
histórico, motores y handlers placeholder, repositorios vacíos, interfaces sin
implementación y módulos de compatibilidad meteorológica sin referencias.

No se eliminaron `m3`–`m7` de forma global. Parte de esos paquetes todavía sostiene
contratos consumidos por adaptadores oficiales, pruebas de API pública y el dominio de
recordatorios. Su eventual consolidación requiere migración explícita y queda fuera de
esta poda conservadora.

## Invariantes preservadas

- un runtime y una composición oficiales;
- una ruta conversacional gobernada;
- un registro oficial de capabilities;
- una autoridad de memoria;
- una agenda cognitiva persistente;
- configuración doméstica compatible.
