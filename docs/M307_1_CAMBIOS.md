# M307.1 - Recuperación del lector de Gmail

## Corrección

- El lector conversacional de correo ya no depende de `config.example.json` para inicializar Gmail.
- Toma `GMAIL_ADDRESS` y `GMAIL_APP_PASSWORD` directamente del almacén canónico de credenciales (`.roby/credentials.json`) mediante `SecretsLoader`.
- Se conserva el lector IMAP en modo solo lectura y no se modifica la voz, el clima ni el resto del runtime.

## Prueba de regresión

- Se agregó `tests/test_m307_1_gmail_credentials_wiring.py`.
- Verifica que Gmail se construye con las credenciales canónicas aunque no exista el archivo base de configuración anterior.

## Validación

- Compilación Python completa: correcta.
- Suite completa: `6988 passed`.
