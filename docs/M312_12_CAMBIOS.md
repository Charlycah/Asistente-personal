# M312.12 — Preparación de contexto para conversación

## Objetivo

Convertir el contexto personal seguro de M312.10 en un paquete breve,
estructurado y limitado, apto para una futura integración conversacional.

## Incorporado

- `ConversationContextItem`
- `ConversationContextPackage`
- `ConversationContextPreparer`
- límites configurables de cantidad y caracteres
- normalización de texto
- conteo de elementos omitidos
- proyección mínima sin metadatos internos
- exposición controlada desde `IdentityMemoryBrainComposition`

## Seguridad

- mantiene el filtrado por identidad de M312.10
- desconocido y conflicto reciben solamente contexto compartido
- no modifica memorias ni perfiles
- no se conecta a `main.py`
- no se conecta a `runtime_root_factory.py`
- no altera respuestas visibles

## Validación interna

- 4 pruebas nuevas
- 7045 pruebas aprobadas
- compilación Python correcta
