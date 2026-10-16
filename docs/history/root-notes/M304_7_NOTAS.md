# ROBY XI.2 M304.7

Modo diagnóstico incremental para la escucha continua.

## Cambio

- Agrega `diagnostic_mode` a la configuración de escucha continua.
- Muestra en la interfaz RMS, umbral de voz y decisión del VAD.
- Muestra resultados parciales y finales de Vosk.
- Informa cuando Vosk cierra una frase sin producir texto.
- Permite distinguir texto parcial, texto final y ausencia de resultado.

El modo queda habilitado en `config.json` para esta versión de prueba y
deshabilitado en `config.example.json`.

No se modificaron OpenWeather, noticias, routers ni parámetros acústicos.
