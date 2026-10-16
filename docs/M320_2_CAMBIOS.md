# M320.2 — Cierre conversacional contextual

## Objetivo

Mejorar el criterio del Brain para reconocer cierres naturales sin confundir
una fórmula de cortesía con el final de la conversación.

## Cambios

- Se amplía el reconocimiento de agradecimientos finales.
- Se incorporan despedidas breves y deterministas.
- Un agradecimiento o pedido cortés seguido de una consulta activa conserva
  la categoría `DIRECT_REQUEST` y continúa hacia los motores.
- No se modifican motores, contexto, memoria ni contratos públicos.

## Pruebas

Se agregan cuatro pruebas específicas en
`tests/test_m320_2_contextual_closure.py`.
