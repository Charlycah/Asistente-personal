# ROBY XI.2 — M327.4

## Segunda capacidad autónoma: diagnóstico del audio

M327.4 incorpora una segunda capacidad autónoma real y de bajo riesgo:
`diagnose_audio_runtime`.

### Integración

- El evento real `AudioEngineState.ERROR` activa el ciclo autónomo desde la UI.
- El runtime consulta `diagnostic_snapshot()` sobre la misma entrada de voz activa.
- La observación `audio_runtime.error` se transforma en la situación
  `audio_runtime_requires_diagnosis`.
- La decisión se evalúa con política, compuerta de autonomía y perfil de riesgo
  bajo local a esta capacidad.
- La decisión y su resultado se conservan en el diario persistente de M327.3.

### Alcance de seguridad

- Capacidad estrictamente de solo lectura.
- No reinicia el motor de audio.
- No cambia dispositivo, umbrales ni configuración.
- No habilita ni deshabilita la escucha continua.
- Los fallos del diagnóstico no interrumpen la UI ni el runtime ejecutivo.

### Evidencia recopilada

- estado del worker;
- estado del stream;
- cantidad de frames recibidos;
- colas de audio y texto;
- dispositivo activo;
- estado y nivel del motor;
- umbrales adaptativos;
- último error informado.

### Validación

- 3 pruebas nuevas de M327.4.
- 7678 pruebas totales aprobadas.
- `compileall` aprobado.
- Ruff debe ejecutarse en el entorno local del proyecto.
