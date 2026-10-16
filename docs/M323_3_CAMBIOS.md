# M323.3 — Respuestas Elípticas

Incremento mínimo sobre M323.2 para reconocer respuestas breves que dependen del
contexto conversacional, sin resolver referencias ni alterar el pedido original.

## Cambios

- Nuevo `EllipticalResponseAnalyzer` en el Brain.
- Distingue selecciones ordinales, referencias nominales, demostrativos,
  selecciones colectivas y negativas.
- Expone la decisión en `UnifiedExperienceLayer.last_elliptical_response`.
- Conserva texto, respuesta, `rationale`, motores, routing y memoria.

## Alcance deliberadamente excluido

- No elige opciones automáticamente.
- No reconstruye pedidos omitidos.
- No modifica resultados operacionales.
