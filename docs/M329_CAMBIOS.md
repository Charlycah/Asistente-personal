# M329 — Modelo de capacidades

M329 incorpora un modelo persistente y descriptivo de capacidades para ROBY XI.2.

## Alcance

- catálogo explícito de capacidades registradas;
- riesgo y reversibilidad declarados;
- necesidad de autorización;
- dependencias entre capacidades;
- estado habilitado o deshabilitado;
- evaluación determinista de disponibilidad;
- persistencia en `.roby/autonomy/capability_model.json`;
- integración con propuestas de próximos pasos;
- contadores en el snapshot ejecutivo.

## Garantías

El modelo no ejecuta capacidades, no concede autorizaciones, no modifica objetivos,
no cambia planes y no inicia ciclos autónomos.
