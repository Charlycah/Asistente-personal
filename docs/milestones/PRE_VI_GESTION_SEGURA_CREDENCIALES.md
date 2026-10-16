# Pre-Fase VI — Gestión segura de credenciales

## Objetivo

Preparar ROBY para la Fase VI sin introducir secretos en el repositorio.

Este ajuste no agrega una capacidad cognitiva nueva. Endurece la infraestructura
para que futuras herramientas externas puedan consumir claves, tokens y parámetros
locales desde variables de entorno mediante una única ruta autorizada.

## Principio

Ningún secreto debe vivir en código fuente, JSON versionado, tests reales o ZIPs de
entrega. El contrato público queda en `.env`; los valores reales viven en
`.env`, que queda ignorado por Git.

## Archivos agregados o modificados

- `.env`: plantilla sin secretos reales.
- `.gitignore`: ignora `.env`, `.env.local` y variantes, preservando `.env`.
- `infrastructure/config/config_schema.py`: amplía `SecretsConfig`.
- `infrastructure/config/settings_loader.py`: centraliza lectura de secretos.
- `tests/test_config.py`: cubre carga de nuevas variables y validación de cámara.

## Variables contempladas

- `OPENWEATHER_API_KEY`
- `WEATHERAPI_KEY`
- `GOOGLE_CLIENT_SECRET_FILE`
- `GOOGLE_TOKEN_FILE`
- `GMAIL_ADDRESS`
- `GMAIL_APP_PASSWORD`
- `GEMINI_API_KEY`
- `OPENROUTER_API_KEY`
- `MISTRAL_API_KEY`
- `OPENAI_API_KEY`
- `CAMERA_INDEX`

## Uso local

```bash
cp .env .env
```

Luego completar únicamente las claves necesarias en `.env`.

## Nota de seguridad

Si alguna clave fue compartida accidentalmente en archivos previos, debe considerarse
expuesta y conviene revocarla/regenerarla antes de usarla en producción.
