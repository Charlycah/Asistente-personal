# RP.12 — Cognitive Agenda Reasoning

## Propósito

RP.12 convierte la agenda cognitiva de RP.11 en una memoria de trabajo
interpretada. El runtime residente puede evaluar el foco ejecutivo y producir
una deliberación trazable sin ejecutar acciones externas ni irreversibles.

## Contrato

`CognitiveAgendaReasoner` recibe un `CognitiveAgendaSnapshot` y devuelve una
`CognitiveAgendaDeliberation` inmutable para el foco primario.

La deliberación contiene:

- clave del elemento de agenda;
- disposición ejecutiva;
- resumen legible;
- rationale técnico;
- confianza acotada;
- indicador explícito de autorización del usuario.

## Disposiciones

- `observe`: mantener observación pasiva;
- `continue`: conservar el asunto en foco;
- `prepare_follow_up`: preparar un seguimiento interno;
- `propose_action`: formular una acción para autorización, sin ejecutarla;
- `wait_for_unblocking`: esperar que desaparezca el bloqueo.

## Gobernanza

RP.12 no llama herramientas, no modifica persistencia y no ejecuta acciones.
Una disposición `propose_action` siempre marca
`requires_user_authorization=True`. La ejecución continúa perteneciendo a las
capas oficiales de planificación, permisos y routing gobernado.

## Integración

RP.10 sigue siendo dueño del ciclo residente. En cada tick:

1. RP.11 refresca la agenda.
2. RP.12 delibera sobre el foco primario.
3. El estado continuo publica agenda y deliberación.
4. El rationale compatible `agenda:<key>` permanece sin cambios.
5. Si la agenda está vacía, se conserva el selector legado de RP.10.
