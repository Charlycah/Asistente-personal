# M21 — Persistent Memory

## Objetivo

Agregar una implementación persistente concreta detrás de la abstracción `MemoryStore`, sin modificar el contrato público de `ROBY.process()` ni introducir memoria semántica todavía.

## Decisión arquitectónica

La persistencia vive en infraestructura:

```text
core.memory.MemoryStore
        ↑
        │
infrastructure.repositories.SQLiteMemoryStore
```

`ROBY` sigue dependiendo de la abstracción `MemoryStore`, no de SQLite.

## Alcance incluido

- `SQLiteMemoryStore`
- Persistencia de `MemoryItem.content`
- Persistencia de `MemoryItem.metadata` como JSON
- Recuperación con `MemoryQuery`
- Filtro simple por texto en `content`
- Búsqueda case-insensitive
- Orden estable de inserción
- Integración transparente con `ROBY(memory_store=...)`

## Alcance excluido

- Memoria semántica
- Embeddings
- Ranking de relevancia
- Resumen automático
- Expiración de memorias
- Deduplicación
- Migraciones avanzadas de esquema

## Contrato

### `remember(item)`

Debe persistir el `MemoryItem` recibido.

### `recall(query)`

Debe devolver una lista de `MemoryItem`:

- si `query.text` tiene contenido, filtra por coincidencia textual en `content`;
- si `query.text` está vacío, devuelve todas las memorias;
- preserva metadata;
- respeta orden de inserción.

## Tests agregados

- Persiste items entre instancias.
- Filtra recall por texto.
- Recall es case-insensitive.
- Query vacía devuelve todo en orden de inserción.
- ROBY puede capturar un turno usando SQLite como `MemoryStore`.

## Estado

Completo.
