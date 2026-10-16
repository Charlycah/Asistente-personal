# RP.20.20 — Retiro de aliases internos de conveniencia

## Cambio

Se retiraron de `OfficialROBYRuntime` dos propiedades que duplicaban exactamente operaciones canónicas:

- `operational_snapshot` → `snapshot()`
- `health_readiness` → `readiness()`

Ambas propiedades carecían de consumidores de producción y sólo aparecían en pruebas históricas. No añadían política, transformación, coordinación, estado ni compatibilidad registrada.

## Contratos preservados

Permanecen como API canónica:

- `snapshot(now=...)`
- `readiness(requirement=None, now=...)`

También se conserva `resident_snapshot`, porque expone de forma estable la vista ordenada del registro residente y tiene consumidores reales dentro de la API del runtime.

## Aplicación

El paquete es seguro para aplicar por superposición: no elimina archivos físicos.
