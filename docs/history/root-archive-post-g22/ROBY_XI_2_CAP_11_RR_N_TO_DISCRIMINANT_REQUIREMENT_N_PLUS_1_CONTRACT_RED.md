# CAP-11 — RR(N) → R(N+1) — Contract RED

Estado: RED contractual ejecutado y observado antes del GREEN.

Frontera congelada:

- RR2 → R3 con budget 4;
- RR3 → R4 con budget 4;
- cero requirements → cierre `NO_NEW_REQUIREMENT`;
- RR4 terminal → no R5;
- preservación del owner existente;
- STOP absoluto antes de Planning.

Resultado RED observado: `4 failed`.

Los cuatro fallos se produjeron en el mismo punto arquitectónico esperado: `GovernedLongHorizonInvestigationReassessmentRequirementAdmissionV1` recibía el `GovernedInvestigationReasoningClosureResult` N-step pero intentaba consumirlo como `GovernedInvestigationReasoningReentryRecordingResult`, accediendo a lineage histórico no presente (`originating_reasoning_id` directo en el wrapper).

El RED confirma que el residual era el handoff entre dos resultados canónicos existentes y no una ausencia de autoridad de discriminación, Episode o Reasoning.
