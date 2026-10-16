# M22 — Cache

## Objetivo

Introducir una abstracción de cache reutilizable para ROBY, sin acoplarla todavía a `ROBY.process()` ni al sistema de herramientas.

## Decisión arquitectónica

La cache se define en `core.cache` como contrato de núcleo:

```text
core.cache.CacheStore
        ↑
        │
core.cache.InMemoryCacheStore
```

`ROBY` puede recibir una cache inyectada, pero no la usa todavía durante `process()`.

## Alcance incluido

- `CacheEntry`
- `CacheStore`
- `InMemoryCacheStore`
- Operaciones básicas:
  - `get(key)`
  - `set(key, entry)`
  - `delete(key)`
  - `clear()`
- Integración opcional en `ROBY.__init__`
- Garantía de que `ROBY.process()` no lee ni escribe cache todavía

## Alcance excluido

- TTL / expiración
- Cache persistente
- Cache distribuida
- Políticas LRU/LFU
- Integración con tools
- Integración con memoria semántica
- Invalidación automática

## Contrato

### `get(key)`

Devuelve `CacheEntry` si existe la clave, o `None` si no existe.

### `set(key, entry)`

Guarda o reemplaza la entrada asociada a la clave.

### `delete(key)`

Elimina la clave si existe. No falla si la clave no existe.

### `clear()`

Elimina todas las entradas.

## Tests agregados

- `CacheEntry` conserva valor y metadata por defecto.
- `InMemoryCacheStore` devuelve `None` para claves inexistentes.
- Guarda y recupera entradas.
- Sobrescribe claves existentes.
- Elimina entradas individuales.
- Limpia todas las entradas.
- `ROBY` usa `InMemoryCacheStore` por defecto.
- `ROBY` acepta cache inyectada.
- `ROBY.process()` no lee ni escribe cache.

## Estado

Completo.
