# M305.2 — Activación interna del camino de voz verificado

## Diagnóstico

La prueba manual de Windows funcionaba porque definía explícitamente:

- `ROBY_CONTINUOUS_LISTENING_ENABLED=true`
- `ROBY_AUDIO_BACKEND=vosk`
- `ROBY_AUDIO_DIAGNOSTIC_MODE=true`

La corrección anterior leía el JSON directamente, pero no reproducía de forma exacta
el mismo camino de composición que había funcionado en el equipo real.

## Corrección

- `.roby/config.json` continúa siendo la única fuente persistente.
- No se agregan `.env` ni `.env.example`.
- `build_voice_input_from_environment()` activa primero la configuración canónica
  con `override_existing=True`.
- Luego construye la entrada de voz usando exactamente las mismas variables de
  proceso que la prueba manual comprobada.
- `main.py` y `desktop_bootstrap.py` también activan la configuración con
  `override_existing=True` para evitar valores antiguos en la sesión de PowerShell.

## Prueba de regresión

Se agregó una prueba que empieza con valores incorrectos (`false`, `powershell`,
`false`), activa `.roby/config.json` y verifica que se construye Vosk con diagnóstico.

## Validación

- 13 pruebas específicas de audio/configuración: aprobadas.
- La suite completa avanzó hasta 72% sin fallos, pero no finalizó dentro del límite
  de ejecución disponible; no se afirma una validación completa.
