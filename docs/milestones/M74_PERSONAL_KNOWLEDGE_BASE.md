# M74 — Personal Knowledge Base

## Objetivo

Convertir información manual y documental en conocimiento personal estructurado, trazable, consultable y relacionado.

## Componentes

- `KnowledgeCandidate`: propuesta pendiente de validación.
- `KnowledgeItem`: unidad persistible de conocimiento.
- `KnowledgeRelation`: vínculo explícito entre elementos.
- `PersonalKnowledgeRepository`: contrato de persistencia.
- `InMemoryPersonalKnowledgeRepository`: implementación determinista inicial.
- `PersonalKnowledgeBaseManager`: servicio de aplicación y dominio.
- `PersonalKnowledgeSnapshot`: contexto resumido para observabilidad y prompt.

## Capacidades

- Creación manual de conocimiento.
- Candidatos derivados de Document Inbox.
- Revisión humana para baja confianza o generación automática.
- Clasificación por tipo, propietario, fuente y estado.
- Búsqueda por texto y etiquetas.
- Deduplicación mediante huella SHA-256.
- Relaciones explícitas entre conocimientos.
- Reemplazo preservando historia.
- Archivado.
- Integración con Scope Guard y Cognitive Pipeline.

## Límites

M74 no implementa embeddings, base vectorial, inferencia autónoma permanente, sincronización externa ni modificación automática de conocimiento aprobado.

## Quality Gate

- Ruff: limpio.
- Pytest: 798 pruebas aprobadas.
- Pruebas específicas M74: 16 aprobadas.
- Compileall: correcto.
