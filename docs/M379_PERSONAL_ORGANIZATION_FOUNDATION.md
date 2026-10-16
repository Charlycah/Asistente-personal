# M379 — Personal Organization Foundation

## Propósito

M379 inicia la Fase IV mediante un inventario gobernado de agenda, tareas,
recordatorios, objetivos, proyectos, notas y priorización.

## Autoridad

`PersonalOrganizationAuthority` es la única fachada del dominio de organización
personal. No sustituye las autoridades ya existentes: las registra y expone como
un inventario canónico para impedir nuevas implementaciones paralelas.

## Capacidades inventariadas

- agenda: `CognitiveAgendaManager`;
- tareas: `TaskIntelligenceManager`;
- recordatorios: `ReminderService`;
- objetivos: `GoalsObjectivesModel`;
- proyectos: `HouseholdProjectService`;
- notas: frontera todavía incompleta sobre `OfficialMemoryGateway`;
- priorización: `PriorityReasoning`.

## Límites

M379 no agrega CRUD, persistencia, ejecución, automatización, cambios de runtime,
LLM, otro planificador, otra memoria, otro cerebro ni otro agente. Los siguientes
incrementos deberán cerrar las brechas señaladas por el inventario reutilizando
el núcleo cognitivo unificado.
