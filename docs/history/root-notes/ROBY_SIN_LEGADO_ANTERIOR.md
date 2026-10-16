# Roby XI.2 RP.20.40 — identidad definitiva

Esta revisión elimina del proyecto la identidad anterior.

- Identidad única: **Roby**.
- Palabra de activación única: **Roby**.
- Directorio de datos: `.roby/`.
- Variables de entorno: prefijo `ROBY_`.
- Módulos, clases, pruebas, mensajes y documentación migrados.
- No se conserva alias nominal ni activación de compatibilidad.

## Migración local

Copiá tus archivos privados desde el directorio de datos de la versión anterior a `.roby/`, especialmente `credentials.json`. Las credenciales reales no se incluyen en el paquete.
