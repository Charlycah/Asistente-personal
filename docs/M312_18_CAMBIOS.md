# M312.18 — Presentador de respuestas

Se incorpora una capa de presentación tipada y reversible para separar los datos
completos de una capacidad de su salida conversacional.

## Alcance

- `ResponsePresentation` conserva cuerpo, fuente y enlace.
- `ResponsePresenter` ofrece modos conversación, solo fuente y solo enlace.
- El modo conversación elimina URLs y metadatos técnicos conocidos.
- Noticias y noticias proactivas reutilizan el presentador sin cambiar su
  comportamiento validado en M312.17.
- No se modifica el router general ni otras capacidades.
