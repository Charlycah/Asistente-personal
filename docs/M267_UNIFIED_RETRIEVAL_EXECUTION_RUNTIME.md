# ROBY M267 — Unified Retrieval Execution Runtime

M267 consolida la ejecución de recuperación histórica y M260 bajo una única autoridad operacional.

## Integración

- Preserva planificación y modelos M169–M171.
- Reutiliza `KnowledgeRetrievalExecutionGateway` para planes completos.
- Delega todas las fuentes externas exclusivamente a la misma instancia de M260.
- Mantiene fuentes internas y documentos locales mediante retrievers inyectados.
- Conserva validación de fuente, consulta, contenido y referencias HTTPS.
- No autoriza proveedores de inferencia ni mutaciones de plataforma.
- No ejecuta recuperación implícita.

## Capacidad oficial

`retrieval.unified_execution_runtime`

## Certificación

- Ruff: All checks passed.
- Pytest: 6154 passed.
- Nuevas pruebas: 5.
- Regresiones: 0.
