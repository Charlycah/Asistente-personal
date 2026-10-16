# M79 — Context Assembly

## Objetivo

Construir contextos mínimos, relevantes, deterministas y gobernados para futuras
consultas de razonamiento, utilizando evidencia M77 y claims M78 sin ejecutar todavía
inferencias.

## Componentes incorporados

### `ReasoningQuery`

Define:

- texto de consulta;
- propietario;
- dominios propuestos a Scope Guard;
- temas adicionales;
- claims o evidencias explícitamente solicitados;
- instante `as_of` para evaluar vigencia;
- identificador estable derivado de su contenido.

La tokenización normaliza mayúsculas y acentos para ofrecer relevancia lexical
repetible.

### `ContextSelectionPolicy`

Controla:

- máximo de claims;
- máximo de evidencias;
- relevancia mínima;
- incorporación de elementos `shared`;
- incorporación explícita de Daily Briefing;
- estados permitidos de claims y evidencias.

### `ContextSelectionDecision`

Registra por candidato:

- tipo de elemento;
- identificador;
- inclusión o exclusión;
- motivo;
- puntuación de relevancia.

### `ReasoningContextBundle`

Resultado inmutable que contiene:

- consulta;
- decisión de Scope Guard;
- estado del ensamblado;
- claims seleccionados;
- evidencia seleccionada;
- decisiones auditables;
- huella estable del contexto.

### `GovernedContextAssembler`

Flujo implementado:

1. valida la consulta y el tiempo;
2. ejecuta Scope Guard;
3. bloquea sin recuperar contexto cuando corresponde;
4. filtra claims por propietario, estado y vigencia;
5. ordena por relevancia y claves estables;
6. incorpora evidencia explícita, relevante o enlazada a claims;
7. aplica políticas de estado, propietario, vigencia y derivación;
8. registra inclusiones, exclusiones y referencias faltantes;
9. produce `READY`, `INSUFFICIENT`, `REVIEW_REQUIRED` o `BLOCKED`.

## Invariantes

- Scope Guard precede cualquier selección.
- Mismo estado y misma consulta producen la misma huella de contexto.
- El orden de inserción no cambia el resultado.
- Claims y evidencias no se duplican.
- Propietarios diferentes no se mezclan implícitamente.
- Claims obsoletos, supersedidos o refutados se excluyen por defecto.
- Evidencias archivadas, supersedidas o canceladas se excluyen por defecto.
- Vigencia futura o expirada se audita y excluye.
- Daily Briefing se excluye por defecto como resumen derivado.
- Falta de contexto es un resultado válido, no una excepción.
- M79 no modifica M77/M78 ni ejecuta acciones.

## Archivos principales

```text
core/governed_reasoning/context.py
core/governed_reasoning/__init__.py
tests/test_m79_context_assembly.py
docs/adr/ADR_081_context_assembly.md
docs/milestones/M79_CONTEXT_ASSEMBLY.md
docs/milestones/M79_verification.txt
docs/milestones/M79_commit_message.txt
```

## Pruebas focalizadas

M79 añade 26 pruebas para:

- validación e identidad de consultas;
- normalización de términos;
- políticas y decisiones inmutables;
- selección relevante y explícita;
- arrastre de evidencia enlazada;
- auditoría de evidencia faltante;
- separación de propietarios;
- filtros de estados;
- vigencia temporal;
- control de resúmenes derivados;
- bloqueo y revisión por Scope Guard;
- propagación de revisión desde claims y evidencia;
- contexto insuficiente;
- límites y ranking;
- independencia del orden de entrada;
- estabilidad de huella;
- serialización auditable.

## Fuera de alcance

- reglas de inferencia;
- producción de nuevos claims;
- resolución de conflictos;
- confianza multifactorial;
- Decision Records;
- Explainable Answers;
- integración con Cognitive Pipeline;
- recuperación semántica basada en embeddings;
- acciones externas.

## Próximo milestone

M80 — Governed Inference.
