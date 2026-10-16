# ROBY XI.2 — GATE 3.A.1 — SURGICAL GREEN

## Existing Document Inbox → Durable Repository → Official Shared Runtime Provisioning

### Estado

SURGICAL GREEN implementado; pendiente de certificación local completa del usuario.

### Autoridad preservada

- `core.document_inbox.DocumentInboxManager` continúa siendo la única autoridad del ciclo de vida documental.
- `core.document_inbox.DocumentRepository` continúa siendo el puerto canónico de persistencia.
- No se introduce `PersonalDocumentsManager`, `DocumentSourceManager` ni autoridad paralela.

### Extensión mínima implementada

1. `infrastructure/repositories/sqlite_document_repository.py`
   - `SQLiteDocumentRepository` implementa el contrato existente `DocumentRepository`.
   - Persiste `DocumentRecord` completo, incluyendo `document_id`, SHA-256 efectivo, metadata, contenido, clasificación, estado y timestamps.
   - Conserva deduplicación por hash después de reiniciar el proceso.

2. `app/runtime_environment_wiring.py`
   - `build_document_inbox_from_environment()` provisiona el `DocumentInboxManager` canónico con repositorio SQLite durable.
   - `build_personal_knowledge_from_environment(document_inbox=...)` acepta la autoridad documental existente.
   - `build_task_intelligence_from_environment(document_inbox=...)` acepta la misma autoridad documental existente.

3. `app/runtime_root_factory.py`
   - El composition root construye una sola instancia de Document Inbox y la inyecta en Personal Knowledge y Task Intelligence.
   - No se crea una segunda instancia por consumidor.

4. Contrato RED
   - Se integra la versión corregida por el usuario del test Gate 3.A.1, sin las tres incidencias E501 originales.

### Límites preservados

Este GREEN no introduce:

- ingestión documental automática;
- Reasoning automático desde documentos;
- Memory o Learning automáticos;
- Planning N+1;
- autoridad de Biblioteca/CAP-17 sobre Documentos Personales;
- CAP-18 / Pinacoteca;
- cambio de `.roby/config.json`.

### Validación en entorno de integración

- Contrato Gate 3.A.1: `9 passed`.
- M73 + M74 + M75 + contrato: `57 passed`.
- Runtime composition slice + contrato: `29 passed`.
- M361 + contrato: `14 passed`.
- `python -m compileall -q core app infrastructure`: limpio.
- La suite completa fue iniciada, pero el entorno de integración agotó su timeout antes de completarla; no se reclama certificación integral desde este entorno.
- Ruff no está instalado en el entorno de integración; la certificación Ruff corresponde al entorno local del usuario.

### Certificación requerida

Ejecutar localmente:

```text
python scripts/generate_quality_baseline.py
ruff check .
pytest -q
```

El GREEN sólo se considerará oficialmente cerrado después de esa certificación completa.

### Reconciliación M396.3 posterior a validación local

La validación local del usuario detectó un único fallo residual en
`tests/architecture/test_m396_3_authority_preservation.py`: el manifest histórico
`docs/quality/M396_3_AUTHORITY_PRESERVATION_BASELINE.json` conservaba el hash
anterior de `app/runtime_root_factory.py`, archivo modificado legítimamente por
este Gate para compartir una sola instancia de `DocumentInboxManager`.

Se actualizó exclusivamente la entrada SHA-256 de `app/runtime_root_factory.py`
en dicho manifest, desde
`9db380c472b3988a68dccb8887fddf69ac97ef07a3775eef8c1a8816d9f1d1b0` a
`1ea91b31c393125233ddfc6b90d0a0f926687b1667586952d1e3315f3840cf28`.

No se volvió a modificar `app/runtime_root_factory.py` ni ningún código de
producción durante esta reconciliación. El contrato Gate 3.A.1 corregido por el
usuario permanece idéntico byte a byte.

Validación focal posterior:

- M396.3 + Gate 3.A.1 contract: `21 passed`.
- M361 quality baseline: `5 passed` después de regenerar el snapshot.
- La suite completa fue iniciada nuevamente, pero el entorno de integración
  agotó el timeout antes de completarla; no se reclama certificación integral.
- Ruff continúa no disponible en este entorno de integración.
