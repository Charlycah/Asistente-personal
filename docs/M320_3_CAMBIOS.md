# M320.3 — Saludo con pedido activo

## Objetivo

Mejorar el criterio conversacional del Brain cuando un turno combina una cortesía inicial con un pedido real.

## Cambio incremental

`ConversationalCriterion` ahora distingue entre:

- un saludo puro, que conserva el saludo visible de ROBY;
- un saludo seguido por una pregunta o instrucción directa, que se considera un pedido activo.

Ejemplos:

- `Hola Roby, ¿cómo estás?` → saludo;
- `Hola Roby, decime el clima` → pedido directo;
- `Buenos días: ¿qué reuniones tengo hoy?` → pedido directo.

## Límites arquitectónicos

- No se modifican motores.
- No se modifica Memoria ni Contexto.
- No se alteran contratos públicos.
- La integración continúa en `UnifiedExperienceLayer`.
- El flujo se mantiene: Brain → Motores → Presentation Layer.

## Pruebas

Se agregan cuatro pruebas específicas para clasificación y presentación, además de conservar las pruebas de M320.1 y M320.2.
