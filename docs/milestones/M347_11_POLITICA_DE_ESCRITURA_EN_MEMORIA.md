# M347.11 — Política de escritura en memoria

## Objetivo

Definir una autorización explícita, estructurada y trazable antes de que el flujo cognitivo existente escriba un candidato en la memoria persistente.

## Autoridad canónica

M347.11 no introduce un servicio nuevo. Extiende `CognitiveLearningPolicy`, que ya clasifica candidatos de aprendizaje, y mantiene `CognitiveMemoryIntegration` como punto único de orquestación con `CognitiveMemoryStore`.

## Modelo incorporado

- `MemoryWriteDisposition`: `write`, `review` o `skip`.
- `MemoryWriteReason`: motivo observable de la decisión.
- `MemoryWriteDecision`: autorización inmutable y serialización segura.
- `LearningPolicyResult.write_decision`: decisión producida junto al candidato existente.

## Política

- Preferencias estables y convenciones de proyecto aprobadas pueden autorizar escritura.
- El contexto temporal requiere revisión y no se persiste automáticamente.
- El ruido o contenido vacío se omite.
- Una corrección exige reconciliación con el recuerdo anterior y no se anexa como una segunda verdad.
- La integración solo persiste cuando la decisión declara `persistence_allowed`.

## Integración con contexto

La política consume la misma `ConversationStrategy` y, a través de ella, la misma instancia de `ConversationContext` usada por el planificador. El contexto solo informa si había continuidad previa; no decide, persiste ni reconstruye historial.

## Límites

M347.11 no implementa deduplicación, búsqueda del recuerdo corregido, actualización, eliminación, consolidación ni resolución de referencias. Tampoco mueve la autoridad de planificación al subsistema de memoria.

## Privacidad y trazabilidad

`MemoryWriteDecision.as_dict()` expone únicamente disposición, motivo, categoría, confianza y banderas operativas. No incluye el contenido candidato, prompts, historial, credenciales ni razonamiento privado.

## Validación

Las pruebas específicas verifican escritura durable, revisión temporal, correcciones, ruido, contenido vacío, serialización segura, uso del contexto canónico y persistencia condicionada.
