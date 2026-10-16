# ADR-081 — Governed Context Assembly

## Estado

Aceptado para M79.

## Contexto

M77 normaliza evidencia y M78 registra claims, pero M80 no debe inferir sobre todos
los datos disponibles ni acceder directamente a repositorios heterogéneos. Se necesita
una frontera que seleccione un contexto mínimo, relevante, temporalmente válido,
separado por propietario y previamente evaluado por Scope Guard.

## Decisión

Se incorpora `core.governed_reasoning.context` con:

- `ReasoningQuery` para delimitar texto, propietario, dominios, temas, referencias
  explícitas y tiempo de evaluación;
- `ContextSelectionPolicy` para estados permitidos, límites, propietario compartido y
  tratamiento de resúmenes derivados;
- `ContextSelectionDecision` para registrar cada inclusión o exclusión;
- `ReasoningContextBundle` como resultado inmutable y verificable;
- `GovernedContextAssembler` para aplicar Scope Guard antes de consultar M77/M78.

La selección combina referencias explícitas y relevancia lexical determinista. Los
claims seleccionados arrastran sus evidencias enlazadas, siempre que estas sigan
siendo accesibles y cumplan las políticas. La huella del contexto depende de la
consulta, contenido seleccionado y decisiones, no del tiempo accidental de creación.

## Estados

- `READY`: existe contexto utilizable sin señales de revisión;
- `INSUFFICIENT`: no existe contexto relevante y permitido;
- `REVIEW_REQUIRED`: Scope Guard o los elementos seleccionados exigen revisión;
- `BLOCKED`: la consulta está fuera de alcance.

## Reglas de gobierno

- Scope Guard se ejecuta antes de seleccionar datos.
- El propietario de la consulta limita claims y evidencia; `shared` solo entra si la
  política lo permite.
- Claims obsoletos, supersedidos o refutados se excluyen por defecto.
- Evidencia archivada, supersedida o cancelada se excluye por defecto.
- La vigencia se evalúa contra `ReasoningQuery.as_of`.
- Daily Briefing se excluye por defecto porque es evidencia derivada; una política
  explícita puede incluirlo como orientación, nunca como sustituto silencioso de las
  fuentes primarias.
- Toda exclusión relevante queda registrada.
- M79 no crea claims, no infiere, no resuelve conflictos y no ejecuta acciones.

## Consecuencias

### Positivas

- M80 recibirá un contexto acotado y auditable.
- El resultado es repetible con el mismo estado y consulta.
- Las políticas de selección son explícitas y testeables.
- Se evita contaminación entre propietarios y fuentes obsoletas.

### Costos

- La relevancia inicial es lexical y deliberadamente limitada.
- Los registros deben estar presentes en los registros M77/M78 para poder ser
  seleccionados.
- Los futuros buscadores semánticos deberán respetar el mismo contrato de decisiones.

## Alternativas descartadas

- Entregar todos los registros al motor de inferencias: rompe minimización y
  determinismo.
- Selección exclusivamente mediante LLM: dificulta repetibilidad y auditoría.
- Usar Daily Briefing como verdad primaria: pierde procedencia y puede duplicar o
  desactualizar información.
