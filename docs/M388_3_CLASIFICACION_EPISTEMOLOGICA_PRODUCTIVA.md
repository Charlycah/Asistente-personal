# M388.3 — Clasificación epistemológica productiva

## Objetivo

Integrar la clasificación `hecho`, `inferencia`, `hipótesis` y
`desconocido` en el razonamiento productivo sin otorgar autoridad factual al
texto conversacional ni modificar decisiones.

## Punto de integración confirmado

El observador recibe solamente los `claims` que el
`GovernedContextAssembler` ya seleccionó. Se ejecuta después del armado del
contexto y antes del motor de inferencia.

## Reglas de seguridad

- Una afirmación de Carlos o Cristina no se convierte automáticamente en hecho.
- Solo un claim factual respaldado o corroborado se registra como hecho.
- Un resultado de regla permanece inferencia.
- Una suposición o hipótesis nunca se promociona automáticamente.
- La incertidumbre produce diagnóstico degradado y explícito.
- La ausencia de claims produce omisión; ROBY no inventa conocimiento.
- La evidencia del ciclo contiene niveles, no contenido privado de los claims.
- Un fallo del observador diagnóstico no cambia el razonamiento productivo.

## Alcance

M388.3 vuelve observable la calidad epistemológica del contexto realmente
usado. No modifica claims, memoria, conocimiento, inferencias, decisiones,
respuestas ni acciones externas.
