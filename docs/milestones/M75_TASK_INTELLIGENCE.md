# M75 — Task Intelligence

## Objetivo

Incorporar un sistema de tareas personales seguro, priorizable, trazable e integrado
con las fuentes de contexto construidas en M72–M74.

## Componentes

- `TaskCandidate`: propuesta pendiente de aprobación.
- `Task`: unidad operativa con propietario, importancia, urgencia y plazo.
- `TaskDependency`: dependencia explícita y acíclica.
- `TaskRepository`: contrato de persistencia.
- `InMemoryTaskRepository`: implementación determinista.
- `TaskIntelligenceManager`: creación, aprobación, priorización y seguimiento.
- `TaskIntelligenceSnapshot`: contexto resumido para el pipeline cognitivo.

## Capacidades

- creación manual de tareas;
- sugerencias gobernadas y revisión humana;
- deduplicación;
- cálculo determinista de prioridad;
- dependencias y detección de ciclos;
- identificación de tareas listas;
- cambios de estado y finalización;
- candidatos desde Household Memory, Document Inbox y Personal Knowledge Base;
- conversión de una tarea y sus prerrequisitos en un `Plan` de M46;
- exposición de contexto al Cognitive Pipeline;
- bloqueo de dominios excluidos mediante Scope Guard.

## Exclusiones

M75 no ejecuta acciones externas, no agenda eventos automáticamente y no opera
cuentas, bancos, billeteras, pagos ni compras.

## Quality Gate

- Ruff: limpio.
- Tests específicos M75: 18 aprobados.
- Suite completa: 816 aprobados.
- Compilación: correcta.
