# M373 — Android Files

## Propósito

M373 incorpora la representación canónica y gobernada de observaciones del sistema de archivos Android. `OfficialDeviceGateway` continúa siendo la única autoridad de dispositivos.

## Alcance

- `AndroidFileEntry` representa metadatos observados de un archivo o directorio.
- `AndroidFileSnapshot` representa una observación inmutable de una ruta raíz.
- Toda observación permanece en **solo lectura**, no ejecutable y sensible por defecto.
- La admisión exige un dispositivo móvil registrado que declare `android.files`.
- Las rutas deben ser absolutas, pertenecer al dispositivo observado y no repetirse dentro del snapshot.

## Fuera de alcance

M373 no abre, lee, copia, mueve, renombra, elimina ni escribe archivos. Tampoco incorpora ADB, Storage Access Framework, MediaStore, exploración recursiva, indexación, búsqueda, sincronización, persistencia, polling, background ni integración cognitiva automática.

## Gobierno

Los modelos describen evidencia externa; no autorizan acciones. Cualquier capacidad futura deberá atravesar `ToolGatewayManager`, políticas explícitas, consentimiento y trazabilidad.
