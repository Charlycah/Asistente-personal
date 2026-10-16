# ROBY XI.2 — M327.7

## Memoria de experiencia

- Se agregó `JsonExperienceMemory`, una memoria persistente y versionada.
- Agrupa experiencias por tipo de situación y acción autónoma.
- Conserva ocurrencias y resultados exitosos, degradados, fallidos o desconocidos.
- Registra el último resultado y su marca temporal.
- Usa escritura JSON atómica en `.roby/autonomy/experience_memory.json`.
- El runtime expone cantidad total de experiencias y patrones conocidos.
- La memoria es descriptiva: no modifica decisiones, políticas ni permisos.
- Un archivo corrupto o con esquema desconocido se rechaza explícitamente.

## Validación

- 3 pruebas nuevas para persistencia, agregación y corrupción.
- 7687 pruebas aprobadas.
- `compileall` aprobado.
- Ruff debe confirmarse en el entorno local del proyecto.
