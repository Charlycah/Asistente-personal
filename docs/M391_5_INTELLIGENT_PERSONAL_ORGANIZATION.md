# M391.5 — Organización Personal Inteligente Gobernada

## Objetivo

Continuar la Época IV — Inteligencia Continua coordinando de forma explicable
agenda, tareas, recordatorios, objetivos, proyectos, notas y priorización sin
crear otra autoridad, repositorio, planificador, agente o runtime.

## Autoridad

`PersonalOrganizationAuthority` continúa siendo la única fachada canónica del
dominio de organización personal, tal como fue establecido en M379.
`IntelligentPersonalOrganizationView` es una vista pura y subordinada: no posee
autoridad independiente y no reemplaza ninguna implementación especializada.

M391.5 reutiliza además `PriorityReasoning` como autoridad existente para
clasificar candidatos. No implementa un algoritmo paralelo de prioridad.

## Entradas explícitas

La vista recibe únicamente `PersonalOrganizationItem` ya admitidos por las
autoridades originales. Cada ítem conserva su capacidad de procedencia:
agenda, tareas, recordatorios, objetivos, proyectos, notas o priorización.

Las señales de urgencia, importancia, alineación con objetivos, relevancia de
contexto, proximidad de plazo, riesgo, bloqueo, conflicto y declaración del
usuario deben llegar explícitamente. M391.5 no consulta repositorios ni inventa
esas señales por su cuenta.

## Coordinación inteligente

La inteligencia añadida consiste en combinar de forma determinista las señales
explícitas y reutilizar `PriorityReasoning` para emitir recomendaciones
explicables. Los resultados posibles son priorizar, diferir, mantener bloqueado
o exigir revisión.

Una recomendación no constituye una orden. Priorizar no autoriza ejecutar.
Bloqueos y conflictos permanecen visibles y no se resuelven silenciosamente.

## Fronteras

M391.5 no crea, modifica ni elimina tareas, objetivos, proyectos, notas,
recordatorios o eventos. No agenda reuniones, no dispara recordatorios, no
escribe notas, no persiste resultados, no modifica memoria o planificación y no
ejecuta acciones.

Tampoco inicia threads, timers o procesos residentes. La activación automática
y las mutaciones operativas permanecen bajo las autoridades ya existentes.

## Resultado

`IntelligentPersonalOrganizationReport` conserva recomendaciones, orden de
prioridad, elementos a revisión, bloqueos y un fingerprint reproducible. Es
inmutable, determinista, de sólo lectura y no concede autoridad.

## Invariantes

- Autoridad canónica: `PersonalOrganizationAuthority`.
- Prioridad: reutiliza `PriorityReasoning` / `priority_reasoning`.
- Sin `PersonalOrganizerManager`, segundo planificador o agente paralelo.
- Sin CRUD, persistencia, ejecución o cambios de runtime.
- Sin acceso a `.roby/credentials.json`.
- `CanonicalCognitiveCore(` conserva su posición contractual.
- M379 y M380 mantienen sus contratos y autoridades existentes.

## Relación con M391.1–M391.4

M391.1 consolida evidencia durante inactividad explícita. M391.2 ofrece el
modelo persistente del mundo. M391.3 evalúa escenarios y M391.4 añade análisis
causal/predictivo. M391.5 utiliza únicamente señales ya admitidas para ayudar a
ordenar la organización personal sin convertir razonamiento en acción.

## Alcance futuro

Planificación automática multietapa, reasignación autónoma de agenda,
creación automática de tareas, recordatorios proactivos, resolución automática
de conflictos y ejecución de acciones quedan fuera de M391.5.
