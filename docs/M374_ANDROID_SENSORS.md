# M374 — Android Sensors

## Objetivo

Cerrar la Fase II incorporando una representación canónica, inmutable y de solo lectura de observaciones de sensores Android.

## Autoridad

`OfficialDeviceGateway` continúa siendo la única autoridad de dispositivos. M374 no introduce un gateway paralelo ni una implementación física de sensores.

## Modelos

- `AndroidSensorKind`
- `AndroidSensorAccuracy`
- `AndroidSensorReading`
- `AndroidSensorSnapshot`

Las lecturas pueden representar disponibilidad, valores normalizados, unidad, precisión, instante, fuente, sensibilidad y evidencia. Todos los modelos conservan `read_only=True` y `executable=False`.

## Gobierno

Una observación sólo puede admitirse cuando el dispositivo está registrado, es móvil y declara la capacidad `android.sensors`. Las lecturas de un snapshot deben pertenecer al mismo dispositivo y no pueden repetir un tipo de sensor.

## Fuera de alcance

M374 no incorpora `SensorManager`, listeners, polling, GPS, ubicación, cámara, micrófono, Bluetooth scanning, Wi-Fi scanning, transporte Android real, tareas en segundo plano, persistencia, automatización ni integración cognitiva automática.

## Cierre de la Fase II

Con M374 quedan establecidas las fronteras gobernadas de Device State, Notifications, Clipboard, Files y Sensors. Todas permanecen pasivas, trazables y subordinadas a una única autoridad.
