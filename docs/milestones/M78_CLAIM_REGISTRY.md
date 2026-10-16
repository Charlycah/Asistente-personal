# M78 — Claim Registry

## Objetivo

Representar afirmaciones evaluables de forma inmutable, trazable y separada de la
evidencia normalizada en M77, sin introducir todavía contexto de razonamiento,
inferencias ni resolución de conflictos.

## Alcance implementado

### Modelo de claim

`Claim` conserva:

- sujeto, predicado y valor;
- tipo de afirmación;
- origen de creación;
- estado de evaluación;
- propietario;
- enlaces a versiones concretas de evidencia;
- confianza declarada y justificada opcional;
- referencia de regla reservada para M80;
- vigencia opcional;
- enlace de supersesión;
- timestamp, identificador, revisión y huella semántica.

### Tipos y estados

Los tipos distinguen:

- hechos;
- observaciones;
- resultados de reglas;
- supuestos;
- hipótesis;
- ausencia de evidencia;
- declaraciones de conflicto.

Los estados distinguen:

- propuesto;
- soportado;
- corroborado;
- disputado;
- refutado;
- obsoleto;
- supersedido;
- revisión requerida.

### Enlaces de evidencia

`ClaimEvidenceLink` conserva el identificador, procedencia y huella de la versión de
M77 utilizada. El rol es explícito:

- `SUPPORTS`;
- `CONTRADICTS`;
- `CONTEXT`.

El enlace no copia ni modifica la fuente original.

### Repositorio y registro

`ClaimRepository` define el contrato de persistencia. La implementación inicial
`InMemoryClaimRepository` ofrece:

- almacenamiento de la revisión vigente;
- historial completo por claim;
- búsqueda por huella semántica;
- rechazo de duplicados;
- orden determinista;
- validación de revisiones secuenciales.

`ClaimRegistryManager` permite:

- registrar claims explícitos;
- crear claims respaldados por evidencia M77;
- marcar automáticamente soporte o corroboración según la cantidad de fuentes;
- heredar `REVIEW_REQUIRED` desde evidencia pendiente de revisión;
- revisar estados sin mutar el historial;
- superseder claims conservando ambos registros;
- filtrar por propietario, estado y tipo.

## Invariantes cubiertas

- hechos y observaciones requieren evidencia de soporte;
- un claim corroborado requiere al menos dos evidencias;
- ausencia de evidencia no equivale a evidencia de ausencia;
- un resultado de regla requiere origen y referencia de regla;
- los claims y enlaces son inmutables;
- no se repite una misma evidencia dentro de un claim;
- las revisiones avanzan exactamente de una en una;
- los duplicados semánticos se rechazan;
- la supersesión conserva el historial;
- una inferencia no se registra como hecho;
- no se modifica M72–M77;
- no se ejecutan acciones externas.

## Archivos principales

```text
core/governed_reasoning/claims.py
core/governed_reasoning/__init__.py
tests/test_m78_claim_registry.py
docs/adr/ADR_080_claim_registry.md
docs/milestones/M78_CLAIM_REGISTRY.md
docs/milestones/M78_verification.txt
docs/milestones/M78_commit_message.txt
```

## Pruebas específicas

M78 añade 23 pruebas focalizadas para:

- confianza declarada;
- trazabilidad de evidencia;
- invariantes por tipo y estado;
- distinción entre ausencia de evidencia y prueba de ausencia;
- inmutabilidad;
- estabilidad de huellas;
- deduplicación;
- revisiones secuenciales;
- soporte y corroboración;
- propagación de revisión requerida;
- historial y supersesión;
- filtros deterministas;
- serialización completa.

## Fuera de alcance

- ensamblado de contexto;
- reglas y ejecución de inferencias;
- detección o resolución automática de conflictos;
- cálculo multifactorial de confianza;
- Decision Records;
- Explainable Answers;
- integración con Cognitive Pipeline;
- persistencia SQL;
- promoción automática a Personal Knowledge Base;
- acciones externas.

## Próximo milestone

M79 — Context Assembly.
