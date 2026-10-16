# ROBY XI.2 — M327.9

## Objetivos persistentes

M327.9 incorpora una capa durable para metas de largo plazo sin modificar las
políticas ni la ejecución autónoma existente.

### Componentes

- `PersistentGoal`: contrato inmutable de objetivo.
- `GoalStatus`: active, blocked, completed y cancelled.
- `JsonPersistentGoalStore`: persistencia JSON atómica y versionada.
- `PersistentGoalSnapshot`: ordena objetivos vencidos para revisión y expone
  contadores de estado.

### Integración

`RuntimeExecutiveIntegration` expone operaciones explícitas para crear,
actualizar y consultar objetivos. El snapshot incorpora:

- `persistent_goal_count`
- `active_persistent_goal_count`
- `due_persistent_goal_count`

Ruta predeterminada:

`.roby/autonomy/persistent_goals.json`

### Límites

- Un objetivo vencido no ejecuta acciones por sí mismo.
- No cambia políticas, permisos ni niveles de autonomía.
- No altera la priorización de acciones autónomas de M327.8.
- Toda creación o transición de estado es explícita y persistente.

### Validación

- 5 pruebas nuevas.
- 7696 pruebas aprobadas.
- `compileall` aprobado.
