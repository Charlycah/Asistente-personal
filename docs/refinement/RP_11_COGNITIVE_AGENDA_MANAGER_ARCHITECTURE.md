# RP.11 — Cognitive Agenda Manager

## 1. Propósito

RP.11 incorpora una agenda cognitiva ejecutiva que representa, durante un horizonte temporal corto, aquello que merece permanecer activo en la memoria de trabajo de ROBY.

No es un gestor de tareas, no almacena la verdad de objetivos, proyectos, recordatorios, memoria personal, conversaciones, ambiente o presencia, y no ejecuta acciones. Su responsabilidad es leer señales de esos subsistemas, normalizarlas, deduplicarlas, priorizarlas y publicar un snapshot ejecutivo inmutable para que RP.10 seleccione el foco cognitivo actual.

## 2. Límites arquitectónicos

### RP.11 sí hace

- construir una representación ejecutiva temporal;
- mantener preocupaciones inmediatas activas entre ciclos;
- combinar señales heterogéneas sin apropiarse de ellas;
- deduplicar señales que describen la misma preocupación;
- calcular urgencia, importancia, continuidad y relevancia contextual;
- limitar la agenda a una capacidad explícita;
- explicar por qué cada elemento está activo y por qué uno ocupa el foco;
- degradar o retirar elementos cuando dejan de ser relevantes;
- ofrecer snapshots inmutables y observables a RP.10.

### RP.11 no hace

- crear, completar, editar ni persistir tareas;
- reemplazar Household Goals Runtime, Projects Runtime o Reminder Runtime;
- escribir en Personal Memory Runtime;
- ejecutar proactividad, notificaciones o acciones;
- decidir permisos, consentimiento o gobernanza;
- conservar historial indefinido;
- duplicar el contenido completo de las fuentes;
- inferir compromisos duraderos sin evidencia de una fuente.

## 3. Modelo de dominio propuesto

Archivo principal nuevo: `app/cognitive_agenda_manager.py`.

### Enumeraciones

`CognitiveAgendaKind`

- `COMMITMENT`
- `PENDING_CONVERSATION`
- `ACTIVE_PROJECT`
- `PRIORITY_GOAL`
- `DETECTED_OPPORTUNITY`
- `FOLLOW_UP`
- `AMBIENT_CONCERN`
- `PRESENCE_CONCERN`

`CognitiveAgendaStatus`

- `ACTIVE`
- `WAITING`
- `SNOOZED`
- `RESOLVED`
- `EXPIRED`

`CognitiveAgendaSource`

- `HOUSEHOLD_GOALS`
- `PROJECTS`
- `REMINDERS`
- `PERSONAL_MEMORY`
- `CONVERSATION`
- `AMBIENT`
- `PRESENCE`
- `COGNITIVE_LOOP`

### Objetos inmutables

`CognitiveAgendaSignal`

Representación mínima emitida por un adaptador de lectura:

- `signal_id`
- `source`
- `source_reference`
- `kind`
- `title`
- `summary`
- `observed_at`
- `due_at`
- `importance`
- `urgency`
- `continuity`
- `context_relevance`
- `status`
- `deduplication_key`
- `metadata`

`CognitiveAgendaItem`

Representación ejecutiva normalizada y activa:

- `item_id`
- `kind`
- `title`
- `summary`
- `status`
- `source_references`
- `first_observed_at`
- `last_observed_at`
- `due_at`
- `priority_score`
- `salience_score`
- `continuity_score`
- `reasons`
- `expires_at`

`CognitiveAgendaSnapshot`

- `revision`
- `generated_at`
- `items`
- `primary_focus`
- `secondary_focus`
- `source_failures`
- `discarded_signals`

`CognitiveAgendaPolicy`

- `capacity` (propuesta inicial: 12)
- `primary_focus_limit` (1)
- `secondary_focus_limit` (3)
- `default_ttl`
- TTL específicos por tipo
- pesos de prioridad
- umbral de activación
- penalización por antigüedad
- bono por continuidad
- bono por coincidencia con contexto conversacional

La política debe validar todos sus límites en `__post_init__`.

## 4. Contratos de lectura

Archivo nuevo: `app/cognitive_agenda_sources.py`.

Protocolo pequeño:

```python
class CognitiveAgendaSourceAdapter(Protocol):
    def collect(self, *, now: datetime) -> tuple[CognitiveAgendaSignal, ...]: ...
```

Adaptadores propuestos:

- `HouseholdGoalsAgendaSource`
- `ProjectsAgendaSource`
- `ReminderAgendaSource`
- `PersonalMemoryAgendaSource`
- `ConversationAgendaSource`
- `AmbientAgendaSource`
- `PresenceAgendaSource`
- `CognitiveLoopAgendaSource`

Cada adaptador conoce únicamente la API pública o snapshot de su runtime. Nunca accede a tablas ajenas directamente si ya existe un manager o servicio oficial. Los adaptadores deben ser reemplazables por lambdas o fakes en tests.

## 5. CognitiveAgendaManager

Responsabilidades:

1. recolectar señales de todas las fuentes;
2. aislar fallos por fuente;
3. normalizar valores y timestamps;
4. deduplicar por `deduplication_key` y referencias fuente;
5. fusionar señales relacionadas;
6. reconciliar el snapshot anterior con las señales actuales;
7. aplicar continuidad temporal sin transformar la agenda en persistencia;
8. expirar elementos según política;
9. calcular prioridad de forma determinista;
10. ordenar y limitar capacidad;
11. publicar un snapshot inmutable y monotónico.

API propuesta:

```python
class CognitiveAgendaManager:
    @property
    def snapshot(self) -> CognitiveAgendaSnapshot: ...

    def refresh(self, *, now: datetime | None = None) -> CognitiveAgendaSnapshot: ...

    def clear(self) -> None: ...
```

No necesita hilo propio en la primera iteración. RP.10 ya posee el ciclo residente y será quien invoque `refresh()` en cada `tick()`. Esto evita dos schedulers, carreras y deuda de lifecycle.

## 6. Priorización

La puntuación debe ser explícita, acotada y trazable. Propuesta inicial:

`priority = urgency + importance + continuity + context + temporal_pressure - staleness`

Orden de desempate determinista:

1. mayor `priority_score`;
2. vencimiento más cercano;
3. mayor continuidad;
4. observación más reciente;
5. `item_id` lexicográfico.

Reglas cualitativas iniciales:

- reparación conversacional o compromiso explícito inmediato: máxima atención;
- recordatorio vencido o próximo: urgencia alta;
- objetivo prioritario con próximo paso actual: importancia alta;
- proyecto activo sin próximo paso: seguimiento, no urgencia automática;
- oportunidad ambiental: activa sólo mientras conserve actualidad y consentimiento;
- presencia: modifica relevancia, no crea por sí sola una obligación;
- memoria personal: aporta contexto y continuidad, no debe fabricar compromisos;
- una señal repetida aumenta continuidad, no multiplica elementos.

## 7. Integración con RP.10

RP.10 conserva la propiedad del ciclo temporal y del lifecycle. Se modifica mediante composición:

```python
ContinuousInternalCognitiveLoop(
    cognitive_agenda=agenda_manager,
    latest_self_analysis=...,
    open_commitments=...,      # compatibilidad temporal
    ambient_activity=...,      # compatibilidad temporal
)
```

En `tick()`:

1. RP.10 solicita `agenda_manager.refresh(now=timestamp)`;
2. obtiene `primary_focus`;
3. traduce el tipo de agenda a `CognitiveFocus`;
4. conserva la reparación conversacional como regla de seguridad prioritaria durante la migración;
5. publica en `ContinuousCognitiveState` la referencia del elemento focal y el snapshot de agenda;
6. si RP.11 falla, RP.10 incrementa fallos y usa el selector legado, sin detenerse.

Extensión compatible de `CognitiveFocus`:

- mantener valores existentes;
- agregar `PRIORITY_GOAL`, `ACTIVE_PROJECT`, `REMINDER`, `FOLLOW_UP`, `OPPORTUNITY`, `PRESENCE` sólo cuando exista un caso probado;
- no eliminar `OPEN_COMMITMENTS` ni `AMBIENT_AWARENESS`.

Extensión compatible de `ContinuousCognitiveState` mediante campos opcionales con default:

- `agenda_item_id: str | None = None`
- `agenda_kind: CognitiveAgendaKind | None = None`
- `agenda_revision: int | None = None`

## 8. Composición Desktop Runtime

Archivo a ampliar: `app/always_on_personal_runtime_wiring.py`.

Nueva fábrica:

```python
def build_cognitive_agenda_manager_from_environment(...): ...
```

Configuración sugerida:

- `ROBY_COGNITIVE_AGENDA_ENABLED=true`
- `ROBY_COGNITIVE_AGENDA_CAPACITY=12`
- `ROBY_COGNITIVE_AGENDA_DEFAULT_TTL_SECONDS=1800`

En `app/desktop_bootstrap.py`:

1. construir adaptadores desde los runtimes ya compuestos;
2. construir `CognitiveAgendaManager`;
3. inyectarlo en `build_continuous_cognitive_loop_from_environment`;
4. no agregar otro componente al lifecycle porque RP.11 no tiene hilo;
5. exponer snapshot sólo por observabilidad, sin acoplar UI.

## 9. Persistencia

RP.11 v1 debe ser exclusivamente in-memory.

Justificación:

- la verdad ya vive en los runtimes fuente;
- la agenda es memoria de trabajo, no memoria episódica ni base de tareas;
- reconstruirla al iniciar es correcto;
- evita estados ejecutivos obsoletos después de un reinicio;
- simplifica compatibilidad y recuperación ante fallos.

Una persistencia futura sólo podría guardar telemetría o continuidad de muy corto plazo, nunca convertirse en fuente autoritativa.

## 10. Concurrencia y seguridad

Aunque RP.10 invoque `refresh()` desde un único hilo, `snapshot` puede ser leído desde otros componentes. El manager debe proteger reemplazo de snapshot y revisión con `threading.Lock` o `RLock`, y nunca exponer colecciones mutables.

Los errores recuperables de una fuente se registran en `source_failures`; no abortan la agenda completa. Se capturan tipos explícitos, siguiendo el patrón de RP.10, sin `except Exception` indiscriminado.

## 11. Estrategia de pruebas

### Unidad — modelo y política

- rechaza capacidad y TTL inválidos;
- normaliza puntuaciones fuera de rango;
- objetos inmutables;
- timestamps timezone-aware;
- orden determinista.

### Unidad — reconciliación

- una señal crea un elemento;
- señales duplicadas se fusionan;
- múltiples fuentes pueden respaldar un mismo elemento;
- una señal repetida conserva `first_observed_at`;
- ausencia temporal conserva continuidad hasta TTL;
- vencimiento retira el elemento;
- resuelto o expirado no ocupa capacidad;
- capacidad descarta correctamente los menos relevantes.

### Unidad — prioridad

- conversación pendiente urgente supera proyecto ordinario;
- recordatorio vencido supera oportunidad ambiental no urgente;
- objetivo prioritario puede superar proyecto sin próximo paso;
- relevancia conversacional produce bono acotado;
- antigüedad reduce saliencia;
- empates son reproducibles.

### Unidad — adaptadores

Un archivo por familia o un archivo parametrizado:

- sólo emite objetivos activos relevantes;
- sólo emite proyectos activos o bloqueados;
- recordatorios completados no aparecen;
- memoria personal aporta contexto sin compromiso ficticio;
- conversación pendiente genera follow-up;
- ambiente expira rápidamente;
- presencia ajusta relevancia sin crear tarea.

### Integración RP.10

- RP.10 consulta la agenda en cada tick;
- foco proviene del elemento principal;
- reparación conversacional conserva prioridad definida;
- fallo de agenda activa fallback legado;
- snapshot de RP.10 referencia revisión e item;
- start/stop siguen siendo idempotentes;
- no aparece un segundo hilo.

### Integración Desktop

- factory respeta feature flag;
- composición inyecta fuentes disponibles;
- fuentes ausentes degradan con seguridad;
- lifecycle inicia y detiene únicamente RP.10;
- configuración inválida falla temprano;
- compatibilidad con tests existentes.

### Regresión y certificación

En cada incremento:

1. tests nuevos del incremento;
2. tests RP.10;
3. tests Desktop Runtime afectados;
4. `ruff check .`;
5. suite completa `pytest`;
6. actualización de changelog y documento RP.11 sólo después de certificar.

## 12. Implementación incremental

### RP.11.1 — Dominio puro

- enums, señales, items, snapshot y policy;
- ranking determinista;
- sin wiring.

### RP.11.2 — Manager in-memory

- recolección, deduplicación, reconciliación, TTL y capacidad;
- fuentes fake únicamente.

### RP.11.3 — Adaptadores oficiales

- Goals, Projects y Reminders primero;
- luego Conversation, Personal Memory, Ambient y Presence;
- cada fuente se integra con tests propios.

### RP.11.4 — Integración RP.10

- agenda como proveedor principal;
- fallback legado;
- estado extendido de forma compatible.

### RP.11.5 — Desktop Runtime

- fábrica, variables de entorno y composición;
- pruebas de lifecycle y feature flags.

### RP.11.6 — Observabilidad y certificación

- snapshot diagnóstico;
- documentación;
- Ruff y suite completa.

## 13. Criterios de aceptación finales

RP.11 queda certificado cuando:

- no almacena ni modifica datos fuente;
- no posee scheduler ni hilo adicional;
- genera agenda estable, limitada, explicable e inmutable;
- deduplica señales entre fuentes;
- mantiene continuidad temporal acotada;
- RP.10 usa la agenda como fuente de foco;
- existe fallback seguro;
- Desktop Runtime conserva lifecycle idempotente;
- todos los tests previos y nuevos pasan;
- Ruff permanece sin errores.

## Implementación incremental RP.11.1

La primera implementación certificada incorpora:

- modelos inmutables de señal, ítem, política y snapshot;
- agenda ejecutiva temporal in-memory;
- deduplicación por clave cognitiva estable;
- ranking determinista por prioridad, urgencia y relevancia;
- bonificación limitada de continuidad;
- capacidad acotada de memoria de trabajo;
- aislamiento de fallos por fuente;
- adaptadores de lectura mediante composición;
- integración de RP.10 con fallback legado cuando la agenda está vacía;
- composición inicial para análisis conversacional, compromisos abiertos y
  actividad ambiental.

La agenda continúa sin ser dueña de datos y no ejecuta acciones sobre los
runtimes fuente. Goals, Projects, Reminders, Personal Memory y Presence se
incorporarán mediante adaptadores oficiales en los siguientes incrementos,
sin modificar el dominio central.
