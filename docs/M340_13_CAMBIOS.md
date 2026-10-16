# M340.13 - Health Orchestrator

- Agrega una capa coordinadora de salud sin reemplazar los servicios existentes.
- Incorpora los comandos `resumen de salud de Carlos/Cristina` y `estado de salud de Carlos/Cristina`.
- Reúne en una sola respuesta la medicación activa del día y los tres chequeos activos más recientes.
- Muestra el estado confirmado de cada toma, incluidas las postergaciones registradas.
- Mantiene completamente separados los datos de Carlos y Cristina.
- Excluye medicamentos pausados, finalizados, archivados o fuera de vigencia y chequeos archivados.
- Trabaja solamente con datos locales ya confirmados; no diagnostica, no interpreta síntomas y no modifica prescripciones.
- Integra el flujo tanto para entrada escrita como por voz.
- Agrega 7 pruebas específicas de orquestación.
- Validación funcional completa: 7979 tests OK.
