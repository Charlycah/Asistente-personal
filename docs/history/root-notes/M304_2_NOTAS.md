# M304.2 — Zona horaria robusta para noticias de hoy

- Conserva la corrección manual más reciente de `app/desktop_ui.py`.
- Elimina la creación de `ZoneInfo` durante la importación del router.
- Usa `America/Argentina/Buenos_Aires` cuando la base `tzdata` está disponible.
- Si `tzdata` no está instalada, usa un fallback seguro UTC-03:00 (ART).
- Mantiene el filtro estricto de noticias publicadas hoy y la prioridad del clima.
- Agrega una prueba de regresión para el entorno sin `tzdata`.
