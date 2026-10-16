# RP.20.22 — Consultas de snapshot canónicas

Se retiraron de `CognitiveCoreRuntime` dos propiedades públicas sin consumidores:

- `is_running`, equivalente a `snapshot.running`.
- `is_healthy`, equivalente a comprobar `snapshot.status`.

El runtime conserva una única superficie de lectura, `snapshot`, junto con las operaciones de ciclo de vida `start()` y `stop()`.
