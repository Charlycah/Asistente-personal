# M340.11 - Registro Seguro de Medicación Habitual

- Agrega un registro local y estructurado de medicamentos para Carlos y Cristina.
- Exige confirmación explícita antes de guardar altas, actualizaciones, cambios de estado o archivos.
- Conserva nombre, presentación, dosis informada, horarios, momento del día, relación con comidas e instrucciones proporcionadas.
- Permite consultar medicamentos por persona sin mezclar perfiles.
- Admite estados activo, pausado y finalizado, además del archivo lógico.
- Persiste los datos mediante reemplazo JSON atómico en `.roby/medications.json`.
- Integra el registro en las entradas de texto y voz del escritorio.
- No crea recordatorios automáticos, no valida dosis y no modifica prescripciones médicas.
- Agrega 9 pruebas específicas; suite completa: 7963 tests OK.
