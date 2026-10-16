# ADR-080 — Registro gobernado de claims

## Estado
Aceptado para M78.

## Contexto
M77 normaliza las fuentes de Personal Operations como evidencia trazable, pero una
evidencia no equivale por sí misma a una afirmación evaluable. La FASE VIII necesita
representar qué se afirma, quién o qué originó la afirmación, qué evidencia la apoya o
contradice y cuál es su estado, sin introducir todavía reglas de inferencia ni resolver
conflictos.

## Decisión
Crear `core/governed_reasoning/claims.py` con un modelo explícito de claims y un
registro desacoplado mediante repositorio.

M78 introduce:

- `Claim`, afirmación inmutable con sujeto, predicado y valor;
- `ClaimType`, que separa hechos, observaciones, hipótesis, supuestos, resultados de
  reglas, ausencia de evidencia y declaraciones de conflicto;
- `ClaimOrigin`, separado del tipo y del estado de verdad;
- `ClaimStatus`, que conserva propuesta, soporte, corroboración, disputa, refutación,
  obsolescencia, supersesión y revisión requerida;
- `ClaimEvidenceLink`, enlace a una versión concreta de `EvidenceReference` con rol
  explícito de soporte, contradicción o contexto;
- `ClaimConfidence`, confianza declarada simple con justificación, sin sustituir el
  modelo multifactorial previsto para M81;
- `ClaimRepository` e `InMemoryClaimRepository`;
- `ClaimRegistryManager`, responsable de registrar, consultar, versionar y superseder
  claims sin ejecutar inferencias.

Los claims son inmutables. Los cambios de estado crean revisiones secuenciales y el
repositorio conserva el historial completo. La supersesión no elimina el claim previo:
crea un claim nuevo enlazado y una nueva revisión del anterior marcada como
`SUPERSEDED`.

Los hechos y observaciones requieren evidencia de soporte. Un claim corroborado exige
al menos dos evidencias de soporte. La ausencia de evidencia no puede utilizar
evidencia de soporte como prueba de ausencia. Los resultados de reglas quedan
reservados para M80 y requieren origen y referencia de regla explícitos.

## Alternativas descartadas

### Usar directamente `KnowledgeItem` como claim
Se descartó porque el conocimiento aprobado de M74 tiene un ciclo de vida diferente.
Un claim puede estar propuesto, disputado o refutado y no debe incorporarse
silenciosamente a la Personal Knowledge Base.

### Guardar solo texto libre
Se descartó porque impediría comparar claims, aplicar reglas tipadas y detectar
conflictos de manera determinista en milestones posteriores.

### Mutar el estado del claim existente
Se descartó porque rompería la auditabilidad. Las revisiones inmutables permiten
reconstruir cómo cambió la evaluación sin reescribir el pasado.

### Calcular confianza compleja en M78
Se descartó porque la confianza multifactorial depende de contexto, conflictos y
políticas que pertenecen a M81. M78 solo conserva una declaración validada y su
justificación.

## Consecuencias

- M79 podrá seleccionar claims y evidencia sin confundir sus identidades.
- M80 podrá producir `RULE_RESULT` mediante reglas versionadas sin presentarlo como
  hecho.
- M81 podrá evaluar disputa y corroboración sobre estados ya definidos.
- Los repositorios futuros deberán preservar revisiones secuenciales y deduplicación
  semántica.
- M78 no infiere, no resuelve conflictos, no promueve claims a conocimiento y no
  ejecuta acciones externas.
