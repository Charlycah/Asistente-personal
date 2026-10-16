# M347.9 — Diagnóstico de decisiones fallidas

## Objetivo

Permitir que ROBY identifique de forma estructurada cuándo una decisión cognitiva quedó degradada por una clasificación desconocida o por confianza insuficiente, reutilizando la traza canónica de M347.7.

## Implementación

Se incorporaron `DecisionFailureReason` y `DecisionFailureDiagnostic` en `core/conversation_strategy.py`. `ConversationStrategyPlanner` deriva los diagnósticos al adjuntar `CognitiveDecisionTrace`; no se agregó un segundo analizador, planificador ni sistema de observabilidad.

Los motivos observables son:

- intención cognitiva desconocida;
- confianza cognitiva inferior al mínimo;
- intención interactiva desconocida;
- confianza interactiva inferior al mínimo.

Cada diagnóstico registra componente, confianza observada, mínimo esperado, acción seleccionada, necesidad de aclaración y aplicación de fallback.

## Fuente de verdad

Los diagnósticos viven dentro de `CognitiveDecisionTrace.failure_diagnostics`. `ConversationStrategy.diagnose_failed_decision()` solo expone esa información. No existe almacenamiento paralelo ni se reconstruyen causas fuera de la traza.

## Seguridad

El diagnóstico contiene hechos determinísticos de clasificación. No almacena prompts, texto del usuario, credenciales, cadenas de razonamiento, hipótesis descartadas ni excepciones de runtime.

## Compatibilidad

Una decisión satisfactoria mantiene una tupla vacía. Las estrategias históricas sin traza también devuelven una tupla vacía. No cambian la igualdad histórica, los metadatos, la acción seleccionada, la explicación de M347.8, las respuestas ni el runtime.

## Alcance excluido

No se diagnosticaron fallos de red, proveedores, herramientas, voz o persistencia. Tampoco se agregaron reintentos, ejecución, selección de herramientas ni recuperación automática. `.roby/credentials.json` permanece intacto.

## Validación

Se añadieron pruebas para decisiones satisfactorias, intenciones desconocidas, confianza cognitiva baja, confianza interactiva baja, serialización segura, compatibilidad con M347.8 y estrategias históricas.
