# M20 — Tool System

## Objetivo

Introducir una abstracción mínima para herramientas ejecutables sin acoplar todavía
`ROBY.process()` ni `ExecutionEngine` a una implementación concreta de tools.

Este milestone prepara el terreno para incorporar herramientas futuras de forma
incremental, testeable y desacoplada.

## Alcance

M20 agrega:

- `Tool`: contrato mínimo de herramienta ejecutable.
- `CallableTool`: adaptador para funciones Python simples.
- `ToolRequest`: entrada normalizada para pedir la ejecución de una herramienta.
- `ToolResult`: salida normalizada del despacho.
- `ToolRegistry`: registro y resolución de herramientas por nombre.
- `ToolDispatcher`: despacho seguro de herramientas registradas.

## Contrato arquitectónico

Una herramienta debe:

- tener un nombre no vacío;
- exponer una operación `execute(**parameters)`;
- poder registrarse y resolverse por nombre;
- ejecutarse mediante `ToolDispatcher` sin exponer excepciones al llamador.

El dispatcher debe:

- devolver `ToolResult(success=True, output=...)` cuando la ejecución funciona;
- devolver `ToolResult(success=False, error=...)` cuando la herramienta falla;
- devolver un fallo controlado cuando la herramienta no está registrada.

## Decisiones de diseño

- El Tool System vive en `m5`, junto a la capa de ejecución.
- No se integra todavía con `ExecutionEngine` para evitar un cambio grande.
- No se modifica `ROBY.process()`.
- No se introduce descubrimiento dinámico, plugins ni persistencia.

## Fuera de alcance

Este milestone no incluye:

- plugin discovery;
- herramientas externas reales;
- integración con planes de M4;
- reemplazo de `ExecutionRegistry`;
- ejecución asíncrona;
- permisos o sandboxing.

## Tests agregados

- Registro y resolución de herramientas.
- Rechazo de nombres vacíos.
- Error controlado ante herramienta faltante.
- Ejecución exitosa vía dispatcher.
- Fallo controlado si una herramienta lanza excepción.
- Fallo controlado si se despacha una herramienta no registrada.

## Estado

Completo para M20 inicial.

El siguiente incremento natural sería integrar este sistema con la capa de
ejecución, manteniendo compatibilidad con `ExecutionRegistry`.
