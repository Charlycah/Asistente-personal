# M77 — Evidence Model

## Objetivo

Normalizar registros de M72–M76 como evidencia trazable, inmutable y gobernada,
sin modificar las fuentes ni introducir todavía claims o inferencias.

## Alcance implementado

### Paquete de FASE VIII

Se creó `core/governed_reasoning/` para separar la nueva capa de
`core/reasoning.py` y mantener una frontera arquitectónica explícita.

### Modelo común

`EvidenceReference` conserva:

- tipo e identificador de fuente;
- naturaleza de la evidencia;
- propietario;
- estado normalizado;
- sensibilidad;
- instante observado;
- vigencia opcional;
- huella SHA-256;
- resumen limitado;
- metadatos estructurados;
- identificador estable derivado de procedencia y huella.

`EvidenceBundle` proporciona orden determinista, deduplicación y una huella de
colección reproducible para el mismo tiempo inyectado y las mismas referencias.

### Adaptadores

Se incorporaron adaptadores para:

- M72 `HouseholdMemoryEntry`;
- M73 `DocumentRecord`;
- M74 `KnowledgeItem`;
- M75 `Task`;
- M76 `DailyBriefing`.

Los estados se traducen sin ocultar archivo, supersesión, cancelación, finalización o
necesidad de revisión. Los documentos médicos, de seguros y contratos se clasifican
como sensibles. Household Memory conserva sensibilidad doméstica. El Daily Briefing
se identifica expresamente como resumen derivado.

### Registro

`EvidenceRegistry`:

1. selecciona exactamente un adaptador compatible;
2. valida el dominio mediante Scope Guard;
3. normaliza la fuente;
4. deduplica por identidad de evidencia;
5. conserva una referencia de solo lectura al objeto original;
6. permite resolver la fuente mientras exista en el registro local.

## Invariantes cubiertas

- toda evidencia tiene fuente e identificador;
- todos los timestamps son conscientes de zona horaria;
- toda huella es SHA-256;
- el identificador coincide con procedencia y huella;
- no hay metadatos vacíos;
- la vigencia final no precede a la inicial;
- un bundle no contiene duplicados;
- los adaptadores tienen tipos de fuente únicos;
- una fuente no soportada se rechaza explícitamente;
- la normalización no modifica el objeto fuente;
- no se crean claims, inferencias ni acciones.

## Archivos principales

```text
core/governed_reasoning/__init__.py
core/governed_reasoning/evidence.py
tests/test_m77_evidence_model.py
docs/adr/ADR_079_evidence_model.md
docs/milestones/M77_EVIDENCE_MODEL.md
docs/milestones/M77_verification.txt
docs/milestones/M77_commit_message.txt
```

## Pruebas específicas

M77 añade 21 pruebas focalizadas para:

- validación de entidades;
- estabilidad de identificadores;
- orden y deduplicación;
- adaptación de M72–M76;
- sensibilidad documental;
- conservación de estados;
- resolución de la fuente original;
- serialización de procedencia;
- rechazo de fuentes y configuraciones inválidas.

## Fuera de alcance

- Claim Registry;
- ensamblado de contexto;
- reglas de inferencia;
- resolución de conflictos;
- Decision Records;
- integración con Cognitive Pipeline;
- persistencia SQL;
- acciones externas.

## Próximo milestone

M78 — Claim Registry.
