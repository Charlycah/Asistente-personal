# M400.7 — Governed External Evidence Assessment

## Propósito

M400.7 evalúa evidencia externa ya admitida y verificada. No consulta providers,
no ejecuta fuentes y no decide verdad semántica.

**evaluación ≠ verdad certificada**

**confianza ≠ certeza**

**capacidad/evidencia externa ≠ autoridad cognitiva**

## Assessment estructural

`GovernedExternalEvidenceAssessor` toma un `ExternalIntelligenceEnvelope`, su
`ExternalIntelligenceVerification` correspondiente y un tiempo de evaluación
explícito.

Evalúa únicamente dimensiones observables:

- linaje envelope → verification;
- estado de verificación;
- antigüedad respecto del timestamp de procedencia;
- presencia de contenido utilizable;
- limitaciones heredadas de procedencia;
- estado previo de admisión.

No juzga factualidad, intención, corrección científica ni verdad del contenido.

## Política visible

La política por defecto considera fresca la evidencia hasta 24 horas y usable
hasta 7 días. Fuera de la ventana fresca degrada confianza; evidencia más antigua
recibe una penalización mayor.

La política es explícita y sustituible. La confianza no proviene de heurísticas
ocultas.

Los estados son:

- `strong`;
- `moderate`;
- `weak`;
- `rejected`.

Una evidencia rechazada nunca puede ser promovida por el assessor.

## Contenido

Para inference providers, contenido textual no vacío satisface la condición
estructural de contenido.

Para information sources, `succeeded` con items satisface la condición
estructural. `empty` se conserva como ausencia de resultados y degrada confianza;
un error de fuente degrada aún más.

Ninguna de estas comprobaciones certifica que el contenido sea verdadero.

## Autoridad y límites

El assessor expone `assessor_id`, no `authority_id`.

M400.7:

- no ejecuta providers ni fuentes;
- no selecciona provider/source;
- no cambia routing, transporte ni políticas de red;
- no escribe memoria;
- no planifica acciones;
- no modifica código operativo;
- mantiene `truth_certified=False`;
- mantiene `cognitive_authority_granted=False`.
