# M321.1 — Continuidad Conversacional

## Objetivo

Iniciar la Serie M321 — Gestión del diálogo mediante una detección conservadora
de continuidad entre turnos, sin modificar motores, memoria persistente ni
contratos públicos.

## Cambios

- Se incorpora `DialogueContinuationAnalyzer` dentro de `application.brain`.
- El resultado diferencia `NEW_TOPIC`, `CONTINUE_TOPIC` y `UNRESOLVED`.
- Sólo se reconocen señales explícitas y de bajo riesgo, como «¿Y mañana?»,
  «¿Y el otro?» o «contame más».
- `UnifiedExperienceLayer` conserva únicamente el último turno sustantivo de su
  propia instancia y expone la última decisión para diagnóstico.
- La decisión todavía no reescribe solicitudes ni altera el enrutamiento: deja
  preparada una señal estable para próximos incrementos de M321.

## Estabilidad

- Arquitectura preservada: Brain → Motores → Presentation Layer.
- Sin cambios en motores, memoria, contexto persistente o proveedores.
- Cambio pequeño y reversible.
