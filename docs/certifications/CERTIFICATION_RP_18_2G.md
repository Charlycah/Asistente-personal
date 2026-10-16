# Certificación RP.18.2G

Se certifica la incorporación de `RuntimeRecoveryPlanner` como planificador inmutable,
determinista y no ejecutor de recuperación operativa.

Criterios cubiertos:

- planificación por capacidad solicitada;
- propagación transitiva de dependencias;
- prioridad de lifecycle y supervisor;
- orden de residentes por `startup_order`;
- distinción entre recuperación y registro pendiente;
- blockers, warnings y serialización;
- integración con `OfficialROBYRuntime.recovery_plan`.
