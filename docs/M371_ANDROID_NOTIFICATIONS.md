# M371 — Android Notifications

## Objetivo

M371 incorpora la representación canónica de notificaciones Android como una
capacidad estrictamente de solo lectura. El incremento no conecta todavía un
dispositivo real ni incorpora listeners, polling o procesos en segundo plano.

## Autoridad única

`OfficialDeviceGateway` continúa siendo la única autoridad de dispositivos. No
se crea un gateway paralelo de notificaciones. El gateway admite únicamente
snapshots de un dispositivo móvil previamente registrado que declare
`android.notifications`.

## Modelo canónico

`AndroidNotification` representa identidad, aplicación de origen, título,
texto, categoría, visibilidad, marcas descriptivas y evidencia. El modelo es
inmutable, exige timestamps con zona horaria y conserva siempre
`read_only=True` y `executable=False`.

`AndroidNotificationSnapshot` agrupa una observación coherente de un único
dispositivo, impide identificadores duplicados y mantiene trazabilidad de la
fuente y la evidencia.

## Límites

M371 no permite:

- abrir una notificación;
- responderla;
- descartarla o marcarla como leída;
- activar listeners reales;
- consultar Android mediante ADB, red o transporte físico;
- ejecutar automatizaciones;
- persistir contenido sensible;
- inyectar notificaciones automáticamente en memoria, planificación,
  aprendizaje o conversación.

Las capacidades cognitivas podrán consumir estas observaciones únicamente en
incrementos posteriores, bajo políticas explícitas de privacidad, relevancia y
trazabilidad.
