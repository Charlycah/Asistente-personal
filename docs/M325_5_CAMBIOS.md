# M325.5 — Recovery & Health Coordinator

M325.5 incorpora una autoridad transversal e independiente para observar la
salud de componentes, degradarlos de forma determinista, abrir circuitos y
coordinar intentos de recuperación acotados.

## Nuevo paquete

- `core/executive_recovery_health/models.py`
- `core/executive_recovery_health/coordinator.py`
- `core/executive_recovery_health/__init__.py`

## Capacidades

- Registro explícito de componentes y políticas de salud.
- Estados `UNKNOWN`, `HEALTHY`, `DEGRADED`, `UNHEALTHY`, `RECOVERING` y
  `DISABLED`.
- Circuitos `CLOSED`, `OPEN` y `HALF_OPEN`.
- Conteo de fallos consecutivos, fallos totales y éxitos.
- Apertura del circuito al alcanzar el umbral configurado.
- Cooldown configurable antes de probar ejecución o recuperación.
- Máximo configurable de intentos de recuperación.
- Callbacks de recuperación ejecutados fuera del lock interno.
- Contención de excepciones producidas por callbacks de recuperación.
- Activación y desactivación explícita de componentes.
- Snapshot agregado e inmutable del estado operativo.

## Compatibilidad

La incorporación es aditiva. No modifica residentes, desktop, consola, voz,
presentación, sensores ni el canal `Queue[str]`. Tampoco reinicia procesos ni
conecta todavía los componentes existentes con el coordinador.

## Fuera de alcance

- Persistencia de salud entre reinicios.
- Reinicio real de procesos o threads.
- Registro automático de residentes.
- Políticas de backoff exponencial.
- Emisión de eventos ejecutivos de salud.
- Integración con doctor, heartbeat o lease.

## Validación

- Pruebas M325.1–M325.5: 58 aprobadas.
- Suite completa: 7197 aprobadas.
