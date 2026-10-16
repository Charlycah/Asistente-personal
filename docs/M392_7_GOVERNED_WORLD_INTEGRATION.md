# M392.7 — Integración del Mundo Gobernada

## Objetivo

M392.7 integra las seis representaciones gobernadas certificadas de M392 sin
crear una nueva memoria, autoridad, persistencia o motor operativo.

La autoridad canónica continúa siendo `internal_world_model`.

## Dominios integrados

- M392.1 — hogar;
- M392.2 — personas;
- M392.3 — lugares;
- M392.4 — objetos;
- M392.5 — línea temporal;
- M392.6 — contexto.

`GovernedWorldIntegrationView` recibe directamente las seis representaciones ya
gobernadas. No vuelve a leer sus fuentes, no reinterpreta su evidencia y no
reescribe sus estados.

## Contrato

`GovernedWorldIntegrationSnapshot` es inmutable y de sólo lectura. Conserva
cada sub-representación intacta, su procedencia y su autoridad. Si un dominio
requiere revisión, el snapshot integrado también requiere revisión.

M392.7 no crea hechos, inferencias, persistencia, gestores, automatizaciones,
procesos en segundo plano ni permisos de ejecución. Tampoco modifica los datos
de origen.

## Límites

La integración es composición, no consolidación destructiva. Las autoridades de
origen siguen siendo responsables de sus propios datos y M392.7 no resuelve
contradicciones silenciosamente.
