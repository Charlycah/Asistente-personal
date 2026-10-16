# Credenciales locales de ROBY

ROBY no utiliza `.env`. Las credenciales privadas se cargan desde:

```text
.roby/credentials.json
```

Este archivo está ignorado por Git y no debe compartirse ni publicarse.

Por compatibilidad, ROBY también reconoce `.roby/credencial.json` y las dos
variantes anteriores dentro de `.hal/`. Al iniciar, las migra automáticamente
a la ruta canónica `.roby/credentials.json`.

## OpenWeather

Pegá la clave en:

```json
"OPENWEATHER_API_KEY": "tu_clave"
```

La capacidad meteorológica ya está habilitada en `.roby/config.json`. Al reiniciar
ROBY, preguntas como `¿Cómo está el clima en Buenos Aires?` se enrutan antes que
el modelo general hacia OpenWeather.

## Gemini y Mistral

Pegá las claves en `GEMINI_API_KEY` y `MISTRAL_API_KEY`. Después habilitá el
proveedor correspondiente dentro de `.roby/config.json`.

## Gmail

Para Gmail se recomienda OAuth. Guardá el archivo descargado de Google Cloud en
`.roby/google-client-secret.json`; ROBY podrá conservar el token local en
`.roby/google-token.json`. No uses tu contraseña normal de Gmail.

## Seguridad

- No subas `.roby/credentials.json` a Git.
- No envíes ese archivo por correo o mensajería.
- Revocá y reemplazá una clave si fue expuesta.
- Conservá `credentials.example.json` solamente como plantilla vacía.
