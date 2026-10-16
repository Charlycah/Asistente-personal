# M367.1 — Internal World Model Foundation

## Objetivo

Declarar una representación interna gobernada del mundo de ROBY reutilizando las
capacidades existentes. Esta etapa inventaría autoridades; no crea otro cerebro,
otro almacén ni otro runtime.

## Componentes existentes reconciliados

- `MentalModel`: modelos revisables de personas, proyectos, tareas, sistema,
  entorno, conceptos y self.
- `PersonalIdentityProfile`: identidad y perfil del usuario.
- `TaskIntelligenceManager`: trabajo estructurado y tareas.
- `CognitiveGoalManager`: objetivos cognitivos.
- `UnifiedCognitiveBlackboard`: contexto activo por sesión.
- `RelationshipMemoryManager`: relaciones conocidas.
- `CanonicalMemoryFacade`: memoria gobernada.
- `CapabilityRegistry`: capacidades disponibles sin autorización implícita.
- `AmbientContextFoundation`: señales ambientales.
- `ScopeGuard`: restricciones y dominios autorizados.

## Autoridad

La autoridad descriptiva única es `internal_world_model`. Cada dominio conserva
su implementación especializada y no se duplica.

## Límites

M367.1 es de solo lectura, no agrega inferencia, no añade persistencia, no cambia
el runtime y no afirma consciencia. Representar una capacidad no autoriza su uso,
y representar un estado no lo convierte en un hecho confirmado.
