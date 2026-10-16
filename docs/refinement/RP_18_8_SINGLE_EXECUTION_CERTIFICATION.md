# RP.18.8 — Single Execution Certification

ROBY Desktop entra por `main:main` y delega construcción conversacional en
`app.local_conversation_factory:build_local_conversation_from_environment`.
`OfficialROBYRuntime` conserva la autoridad única de lifecycle, supervisor y
residentes.

La consola histórica, su composición y sus interruptores de lifecycle fueron
retirados después de migrar sus contratos de entrada, diagnóstico, cierre y
presentación hacia autoridades independientes.

La certificación ejecutable vive en `app.runtime_execution_certification` y
valida:

1. un solo entrypoint de proceso;
2. una sola autoridad de lifecycle;
3. compatibilidad no ejecutable;
4. identidad compartida de conversation/bootstrap/root;
5. ausencia física de los adaptadores de consola retirados.
