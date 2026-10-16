# M399.1 — Governed Current Location Audit & Activation

## Objetivo

Cerrar el pendiente real de ubicación actual sin confundir geocodificación, mapas,
resolución de lugares o la mera declaración `android.location` con adquisición GPS.
M399.1 audita la baseline M398.10 y activa una frontera gobernada capaz de aceptar
evidencia física explícita cuando exista un proveedor Android autorizado.

## Resultado de auditoría

- `maps_foundation` ya consume `GeoPointSignal`, pero no obtiene GPS.
- `location_resolution` resuelve referencias a partir de evidencia existente, pero no
  obtiene la ubicación física actual.
- Nominatim es geocodificación: texto/lugar -> coordenadas. **Nominatim no es GPS**.
- `android.location` y el permiso Android `location` estaban declarados, pero no tenían
  un flujo operativo de observación hacia Maps.
- M397/M398 transportan mensajes y no adquieren autoridad semántica sobre ubicación.
- No se encontró una ruta de GPS físico oculta que pudiera simplemente activarse.

## Arquitectura integrada

M399.1 incorpora dos fronteras con responsabilidades distintas y no competitivas:

1. `OfficialDeviceGateway` conserva la autoridad única del dispositivo y acepta
   `AndroidLocationObservation` sólo para dispositivos móviles registrados que declaren
   `android.location`.
2. `CurrentLocationAuthority` es la única autoridad semántica de Current Location.
   Consume la última observación mediante `CurrentLocationEvidenceProvider`, aplica
   consentimiento, permiso, frescura y confianza explícita, y sólo entonces proyecta
   la evidencia existente a `GeoPointSignal` para Maps.

La cadena es:

`Android provider -> OfficialDeviceGateway -> CurrentLocationAuthority -> GeoPointSignal -> maps_foundation/location_resolution`

`GeoPointSignal` es una proyección de evidencia ya aceptada; no convierte Maps en
proveedor GPS ni duplica la autoridad del dispositivo.

## Invariantes

- Sólo lectura. No tracking, polling residente, automatización ni acciones Android.
- `CurrentLocationAuthority.AUTHORITY_ID == "current_location"` es la única autoridad
  semántica introducida para la capacidad.
- La ubicación pertenece al dispositivo observado. M399.1 no infiere que la posición
  del dispositivo sea automáticamente la posición de Carlos, Cristina u otra persona.
- Coordenadas ausentes, permiso denegado, evidencia vieja o confianza ausente no se
  completan silenciosamente.
- La confianza debe provenir explícitamente de la evidencia; M399.1 no inventa una
  probabilidad a partir de `accuracy_meters`.
- Una observación futura exige revisión y una observación stale queda no disponible.
- **predicción ≠ certeza**.
- M399.1 no modifica silenciosamente código operativo ni introduce self-maintenance.

## Alcance de la activación

La ruta gobernada queda activada a nivel de contrato e integración: ROBY puede recibir
una `AndroidLocationObservation` explícita de un dispositivo registrado, validarla y
proyectarla hacia Maps bajo una sola autoridad de Current Location.

**No existe todavía un proveedor físico Android** dentro de esta baseline que consulte
GNSS/Fused Location y produzca esas observaciones. Por lo tanto M399.1 no certifica
"GPS funcionando" ni simula coordenadas. La conexión con un proveedor físico deberá
ser un incremento posterior y permanecer detrás de esta frontera gobernada.

## Fuera de alcance

- Google Maps como fuente GPS.
- tracking continuo o historial automático de movimientos.
- asociación automática persona <-> dispositivo.
- reverse geocoding obligatorio.
- activación silenciosa de permisos Android.
- cambios en M397/M398, Nominatim o `AndroidSensorKind`.
- self-diagnostics/self-maintenance productivo de M399 principal.
