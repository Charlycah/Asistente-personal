# M326.1 — Controlled Autonomy Contracts

Base: M325.12 estable.

## Objetivo

Iniciar Executive Decision & Controlled Autonomy con contratos puros y
explícitos. Esta versión no ejecuta acciones ni modifica el runtime.

## Incorporado

- `DecisionSituation`: situación normalizada, evidencia, urgencia y origen.
- `ActionCandidate`: opción posible sin capacidad de ejecución.
- `RiskAssessment`: riesgo, confianza, impacto y reversibilidad.
- `DecisionPolicy`: límites de autonomía y modo simulación seguro por defecto.
- `AutonomyDecision`: observar, recomendar, confirmar, autorizar, bloquear o
  simular.
- `DecisionOutcome`: resultado verificable vinculado a una decisión.
- `DecisionJournalEntry`: registro inmutable y consistente de extremo a extremo.
- `DecisionEngine` y `DecisionJournal`: puertos estructurales para incrementos
  posteriores.

## Reglas de seguridad

- M326.1 no contiene ejecutores ni invoca herramientas.
- Solo una política `autonomous_low_risk` puede representar autorización.
- Una autorización solo puede ser de riesgo bajo.
- El riesgo prohibido siempre exige una decisión bloqueada.
- El modo simulación está activado por defecto.
- Todas las referencias entre situación, candidatos, evaluaciones, decisión y
  resultado se validan al construir el journal.

## Fuera de alcance

- evaluación automática de situaciones;
- generación automática de candidatos;
- motor de políticas;
- ejecución de acciones;
- recuperación autónoma del audio;
- integración conversacional.
