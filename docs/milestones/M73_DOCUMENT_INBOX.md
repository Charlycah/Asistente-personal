# M73 — Document Inbox

## Objetivo

Incorporar documentos a ROBY como registros estructurados, consultables y auditables,
protegidos por Scope Guard e integrables con Household Memory.

## Componentes

- `DocumentMetadata`: título, origen, tipo de medio, autor, fechas y etiquetas.
- `DocumentRecord`: contenido, categoría, estado, hash y enlace doméstico.
- `DocumentRepository`: contrato de persistencia.
- `InMemoryDocumentRepository`: implementación determinista inicial.
- `DocumentClassifier`: clasificación por reglas reemplazables.
- `DocumentInboxManager`: ingreso, búsqueda, archivado y vinculación.
- `DocumentInboxSnapshot`: resumen operativo para el pipeline cognitivo.

## Capacidades

- Ingreso de texto normalizado.
- Lectura UTF-8 de TXT, Markdown, CSV y JSON.
- Clasificación documental determinista.
- Deduplicación por SHA-256.
- Búsqueda por contenido, metadatos, categoría y estado.
- Marcado de documentos sensibles para revisión humana.
- Bloqueo de dominios financieros y compras mediante Scope Guard.
- Archivado sin pérdida de identidad.
- Vinculación opcional con Household Memory.
- Integración de contexto con `CognitivePipeline`.

## Fuera de alcance de M73

- Extracción directa de PDF o DOCX.
- OCR de imágenes.
- Índice vectorial o embeddings.
- Sincronización con nubes documentales.
- Ejecución automática de obligaciones detectadas.

Estos puntos se incorporarán mediante adaptadores y milestones posteriores.

## Quality Gate

- Ruff: limpio.
- Tests M71–M73: 37 aprobados.
- Suite completa: 782 aprobados.
- `compileall`: correcto.
