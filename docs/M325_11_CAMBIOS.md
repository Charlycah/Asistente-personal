# M325.11 — Conversational Integration

- Añade `MapConversationInterceptionPort` para detectar solicitudes explícitas de mapas.
- Extrae el lugar solicitado sin interferir con clima, noticias, deportes o conversación general.
- Orquesta geocodificación, renderizado Folium y presentación de escritorio.
- Devuelve respuestas naturales para éxito, falta de ubicación, ambigüedad, ausencia de resultados y fallos controlados.
- Añade composición opcional por entorno con `ROBY_MAPS_ENABLED` y `ROBY_NOMINATIM_USER_AGENT`.
- Registra la capacidad oficial `maps.desktop` en el runtime root.
- No añade dependencias nuevas ni modifica componentes validados de M325.8–M325.10.
