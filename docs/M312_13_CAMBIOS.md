# M312.13 — Diagnóstico del paquete de contexto conversacional

## Objetivo

Observar y validar el paquete preparado por M312.12 antes de cualquier conexión
con el runtime conversacional visible.

## Incorporado

- `ConversationContextDiagnostic`
- `ConversationContextDiagnosticReport`
- `ConversationContextDiagnosticFinding`
- inspección de límites de elementos y caracteres
- recálculo independiente del conteo de caracteres
- detección de identificadores duplicados
- detección de sujetos fuera del alcance permitido
- detección de textos vacíos y conteos inválidos
- salida JSON manual mediante `scripts/conversation_context_diagnostic.py`

## Garantías

- diagnóstico de solo lectura
- no modifica el paquete inspeccionado
- no escribe memorias ni perfiles
- no se conecta a `main.py`
- no se conecta a `runtime_root_factory.py`
- no altera respuestas visibles
- conserva sin cambios la preparación de M312.12

## Validación

- pruebas específicas de integridad, límites, alcance y no mutación
- Ruff limpio
- suite completa requerida antes de entrega
