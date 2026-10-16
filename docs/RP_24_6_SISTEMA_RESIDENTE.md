# RP.24.6 — Sistema Residente

ROBY incorpora un supervisor local liviano que mantiene activas sus tareas de
agenda, noticias, salud operativa y otros servicios autorizados sin mantener un
modelo de lenguaje cargado permanentemente.

## Garantías

- una sola instancia mediante el lease existente;
- heartbeat periódico y recuperable;
- tareas independientes y configurables;
- fallos aislados por tarea;
- backoff exponencial limitado;
- detención limpia y liberación del lease;
- métricas de ejecución sin contenido conversacional;
- ninguna activación automática de micrófono, cámara o servicios remotos.

El supervisor reutiliza `LongLivedRuntimeLifecycle` y añade únicamente la
planificación de trabajo residente.
