# ROBY XI.2 — Personal Cognitive Integration — Unified Source Wave

## Estado

Implementación consolidada del BLOQUE II para proyectar relevancia personal hacia el único
`CognitiveAgendaManager` residente.

## Fuentes integradas

- Tasks → `resident_tasks`
- Reminders → `resident_reminders`
- Calendar → `calendar_read`
- Notes → `personal_knowledge_notes`

Goals y Projects permanecen integrados desde Lote A.

## Authorities preservadas

La integración no transfiere autoridad. Tasks sigue perteneciendo a `TaskIntelligenceManager`;
Reminders a su dominio/application service; Calendar al runtime/provider; Notes a
`PersonalKnowledgeBaseManager`. Cognitive Agenda recibe únicamente proyecciones read-only y
transitorias de relevancia.

No se crea manager, store, scheduler, thread, lifecycle, planner, persistence o Cognitive Agenda
adicional.

## APIs read-only

Se consolidan las siguientes superficies de lectura:

- `TaskIntelligenceManager.list_tasks()`
- `PersonalKnowledgeBaseManager.list_items()`
- `ReminderConversationService.list_pending()`
- Calendar provider-neutral `list_events(CalendarTimeRange)` mediante el runtime oficial READY.

## Admission policies

### Tasks

Se admiten sólo tareas `pending`, `in_progress` o `blocked` cuando además existe relevancia
objetiva: bloqueo, importancia >= 8, urgencia >= 8 o deadline dentro de siete días.

Tasks terminales o tareas activas de baja relevancia no ocupan Cognitive Agenda.

### Reminders

Sólo reminders `pending` vencidos o con vencimiento dentro de las próximas 48 horas producen
awareness cognitivo. La lectura no completa, cancela ni snoozea el reminder.

### Calendar

Desktop consulta únicamente una ventana de 48 horas mediante `calendar.read` cuando el runtime
está READY. Cada evento se proyecta de forma efímera y expira al finalizar su `time_range`.
Calendar conserva íntegramente la verdad y persistencia del evento.

### Notes

Sólo `KnowledgeKind.NOTE` con estado `ACTIVE` y una marca explícita de seguimiento puede llegar a
Cognitive Agenda. Tags admitidos en esta primera ola:

- `actionable`
- `agenda`
- `follow_up`
- `pendiente`
- `seguimiento`

Una nota ordinaria nunca se convierte en foco ni commitment sólo por existir.

## Semántica de Cognitive Agenda

Las cuatro fuentes usan `CognitiveAgendaKind.FOLLOW_UP`; no se añade un nuevo enum sólo para
representar el origen de la señal. La identidad/provenance se conserva mediante claves estables:

- `task:<task_id>`
- `reminder:<uuid>`
- `calendar:<event_id>`
- `note:<item_id>`

La fuente permanece separada en `source`.

## Degradación

Cada source es aislable. Un fallo de Reminders, Calendar, Tasks o Notes se registra como fallo de
source y no bloquea las demás fuentes ni Goals/Projects.

Las ausencias terminales se resuelven mediante el mecanismo existente de `absence_status` del
Cognitive Agenda, sin mutar la authority fuente.

## Validación en este entorno

- RED inicial: 7 fallos esperados por ausencia de los cuatro contratos en el builder.
- Tests propios post-integración: **9 PASS**.
- Matriz focal/transversal de Tasks, Notes, Reminders, Calendar, Cognitive Agenda, Lote A,
  Personal Organization y Whole Personal System: **172 PASS**.
- `py_compile` de archivos modificados: PASS.
- chequeo manual de longitud >88 en archivos modificados: 0 líneas.
- Ruff no está instalado en este runtime; gate local pendiente.
- suite completa `pytest -q` pendiente de validación local.

## Gates de promoción

Antes de promover como nueva baseline:

```text
python scripts/generate_quality_baseline.py
ruff check .
pytest -q
```

## Resultado arquitectónico

El BLOQUE II avanza sin ampliar el número de cerebros o autoridades. El mismo estado cognitivo
residente puede ahora recibir señales selectivas de Tasks, Reminders, Calendar y Notes, además de
Goals y Projects, mientras cada dominio conserva su verdad canónica.
