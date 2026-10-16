# ROBY XI.2 — GATE 3.A.1 — CONTRACT RED

## Existing Document Inbox → Durable Repository → Official Shared Runtime Provisioning

### Base certificada

Gate 3.A certificado sobre 13.928 PASS, Ruff limpio y 0 FAIL.

### Autoridad preservada

- `DocumentInboxManager` sigue siendo la única autoridad del ciclo de vida documental.
- `DocumentRepository` sigue siendo el puerto canónico de persistencia.
- `DocumentReadingService` no se convierte en repositorio.
- Personal Knowledge y Task Intelligence siguen siendo consumidores derivados.
- No se crea un segundo manager, planner, agent, runtime cognitivo ni autoridad documental.

### Carencia contractual que este RED debe demostrar

La implementación vigente sólo ofrece `InMemoryDocumentRepository` y el wiring oficial construye Personal Knowledge y Task Intelligence sin una instancia documental compartida. El contrato exige la mínima extensión canónica necesaria para:

1. proveer un adapter durable detrás del `DocumentRepository` existente;
2. preservar `document_id`, SHA-256, metadata, contenido y timestamps tras reinicio;
3. preservar deduplicación por hash tras reinicio;
4. provisionar `DocumentInboxManager` desde el wiring oficial mediante persistencia durable;
5. inyectar la MISMA instancia ya construida de `DocumentInboxManager` en Personal Knowledge y Task Intelligence;
6. mantener a esos consumidores sin autoridad sobre el catálogo documental.

### Frontera de diseño

El RED acepta `SQLiteDocumentRepository` como adapter infraestructural coherente con los repositorios SQLite ya existentes. No cambia el contrato `DocumentRepository` ni la entidad `DocumentRecord`.

La composición debe recibir/reutilizar una instancia explícita de `DocumentInboxManager`; los builders consumidores no deben crear silenciosamente otro inbox.

### STOP

Fuera de alcance de este contrato:

- ingestión automática de carpetas;
- watchers de filesystem;
- sincronización cloud;
- adquisición automática por CAP-17;
- Reasoning automático;
- Memory;
- Learning;
- Planning N+1;
- CAP-18;
- Visual Collection / Pinacoteca.

### Criterio RED

El test contractual debe fallar exclusivamente porque todavía no existen el adapter durable y el provisioning/wiring compartido exigidos. Los invariantes de autoridad existente deben permanecer verdes.
