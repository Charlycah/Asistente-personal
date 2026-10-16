# Configuración doméstica de ROBY

`.roby/config.json` es la única fuente persistente de configuración normal de ROBY XI.2.

## Reglas

- No se lee ni se crea `.env`.
- El archivo se valida al arrancar.
- Si falta, se crea con valores domésticos seguros.
- Las variables de proceso solo se usan como compatibilidad interna temporal del wiring certificado y no se persisten.
- Los secretos no se guardan en JSON.

## Secciones

- `household`: propietario, ciudad, zona horaria e idioma.
- `runtime`: fábrica oficial, perfil y sesión.
- `providers`: proveedor local y proveedores remotos opcionales.
- `services`: clima, Gmail, voz y cámara.
- `privacy`: consentimientos de sensores y política de contenido remoto.
- `environment`: overrides avanzados de claves `ROBY_*`; evitarlo en uso normal.

## Integraciones

OpenWeather, Gemini y Mistral permanecen desactivados hasta que exista una credencial segura. Gmail utiliza OAuth y nunca contraseña directa.
