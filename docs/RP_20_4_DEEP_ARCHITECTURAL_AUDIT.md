# RP.20.4 — Auditoría arquitectónica profunda

## Resultado

La auditoría estática del runtime oficial confirmó:

- un único grafo de composición y ningún ciclo de imports en producción;
- alta concentración de responsabilidades en `app/runtime_root_factory.py`;
- contratos de entorno e interceptores operacionales mezclados con el ensamblado;
- ausencia de una segunda ruta de runtime, scheduler, memoria o conversación.

## Refactor aplicado

Los puertos de readiness, observación de proveedores, descripción de carga,
construcción de inferencia e interceptores domésticos fueron trasladados a
`app/runtime_environment_ports.py`.

`app/runtime_root_factory.py` mantiene reexportados los nombres anteriores para
preservar compatibilidad, pero queda enfocado en construir el runtime oficial.
No se modificó la conducta ni se agregó una composición alternativa.

## Decisiones conservadoras

No se fusionaron todavía los subsistemas `m3`–`m7`, ni las familias cognitivas
del directorio `core`, porque siguen sosteniendo contratos funcionales y pruebas.
Su simplificación futura requiere migración por responsabilidad, no eliminación
masiva.

## Invariantes nuevas

- los puertos auxiliares no vuelven a definirse dentro del factory;
- las importaciones públicas históricas siguen resolviendo al objeto oficial;
- el grafo de imports de producción debe permanecer acíclico.
