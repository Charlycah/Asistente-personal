# ROBY XI.2 — M304.5

Base: M304.4.

## Mejora incremental

- La escucha continua ahora responde `Sí, te escucho.` cuando reconoce solamente
  la palabra de activación, incluso repetida, por ejemplo `Roby, Roby`.
- Las repeticiones iniciales de los alias de activación se eliminan antes de
  enviar el comando al runtime. Ejemplo: `Roby, Roby, me das el clima` se procesa
  como `me das el clima`.
- No se modificaron Vosk, el VAD, OpenWeather ni los routers conversacionales.

## Validación

- Tests focalizados: 17 OK.
- Suite completa: 6954 OK.
- Ruff no estaba instalado en el entorno de empaquetado; ejecutar localmente:
  `ruff check .`.
