# M312.17 — Presentación conversacional de noticias

- Las respuestas normales de noticias ya no muestran ni mencionan enlaces.
- Las noticias proactivas conservan título, fecha y fuente, pero ocultan la URL.
- Pedir la fuente devuelve únicamente el nombre de la fuente.
- Pedir explícitamente enlace, link o URL devuelve únicamente la URL.
- La URL sigue conservándose internamente en `CurrentAffairsItem`.
- No se modifican la búsqueda, frescura, selección ni persistencia de noticias.
