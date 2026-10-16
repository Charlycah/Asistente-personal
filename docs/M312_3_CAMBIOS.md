# ROBY M312.3 — Adaptador de memoria oficial

## Objetivo

Incorporar el primer acceso histórico de solo lectura al BRAIN sin modificar
el runtime visible ni el escritor de memoria oficial.

## Cambios

- Nuevo `OfficialMemoryBrainAdapter`.
- `BrainService` acepta lectores externos optativos.
- Traducción de `MemoryItem` a `BrainMemory` con procedencia y modo de solo
  lectura explícitos.
- Cuatro pruebas de regresión específicas.
- Documentación técnica en `docs/brain/M312_3_OFFICIAL_MEMORY_ADAPTER.md`.

## Garantías

- No se migran datos.
- No se escribe en `OfficialMemoryGateway`.
- No se conecta el adaptador al runtime raíz.
- Un `BrainService` creado como antes mantiene exactamente el comportamiento
  desconectado de M312.1.

## Validación de construcción

- `pytest -q`: 7009 passed.
- Compilación Python: correcta.
- Ruff no disponible en el entorno de construcción; se requiere validación en
  el entorno local del proyecto.
