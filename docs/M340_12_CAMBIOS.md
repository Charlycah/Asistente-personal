# M340.12 - Agenda Inteligente de Medicación

- Extiende el registro seguro M340.11 con una agenda diaria por persona.
- Muestra cada toma activa con horario, medicamento, dosis informada, estado e ID.
- Registra estados `tomado`, `omitido` y `postergado` para una ocurrencia fechada.
- Permite postergar el aviso entre 1 y 180 minutos sin cambiar el horario indicado.
- Conserva un historial diario separado para Carlos y Cristina.
- Permite consultar el estado de una toma concreta.
- Excluye medicamentos pausados, finalizados, archivados o fuera de vigencia.
- Rechaza horarios que no estén presentes en el registro confirmado.
- Evita duplicar una misma ocurrencia diaria: el último estado reemplaza al anterior.
- Mantiene persistencia atómica y compatibilidad con los archivos de M340.11.
- No interpreta omisiones, no recomienda duplicar dosis y no modifica prescripciones.
- Agrega 9 pruebas específicas; suite completa: 7972 tests OK.
