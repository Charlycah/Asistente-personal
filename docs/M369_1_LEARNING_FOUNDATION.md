# M369.1 — Learning Foundation

## Propósito

M369.1 abre la Serie M369 mediante una frontera canónica, gobernada y de solo
lectura para el aprendizaje futuro de ROBY XI.2.

La versión no agrega aprendizaje automático. Reúne las superficies históricas
de observación, experiencia, evidencia y política bajo una sola
autoridad descriptiva:

```text
learning_foundation
└── cognitive_memory
```

## Autoridad y dominios

`learning_foundation` reconcilia, sin reemplazar, estas autoridades existentes:

- `core.learning:LearningSignal` para observaciones explícitas;
- `core.learning:LearnedExperience` para experiencias ya representadas;
- `OperationalLearning` para evidencia operacional trazable;
- `CognitiveLearningPolicy` para gobierno previo a cualquier admisión.

Los dominios declarados son observaciones, experiencias, evidencia y política. Todos conservan su responsabilidad original.

## Candidato de aprendizaje

M369.1 puede estructurar un candidato inmutable desde:

- un sujeto explícito;
- un valor propuesto explícito;
- una o más observaciones identificadas y trazables;
- una confianza explícita entre cero y uno.

Todo candidato queda obligatoriamente en estado `review_required`.

La fundación no acepta candidatos como conocimiento, no autoriza persistencia y
no considera una observación aislada como preferencia, hábito o patrón.

## Límites

M369.1 no incorpora:

- aprendizaje automático;
- aprendizaje de preferencias;
- detección de hábitos;
- reconocimiento de patrones;
- razonamiento adaptativo;
- promoción automática a memoria;
- persistencia nueva;
- cambios de runtime.

Estas capacidades quedan reservadas para incrementos posteriores de M369.

## Invariantes

- Existe una única autoridad `learning_foundation`.
- Cada dominio se declara una sola vez.
- Todo candidato requiere evidencia explícita y única.
- La identidad del candidato es determinista para entradas idénticas.
- Todo candidato requiere revisión.
- Ningún candidato queda aceptado ni autorizado para persistencia.

## Criterio de aceptación

M369.1 se considera válida con Ruff limpio, suite completa sin regresiones,
documentación sincronizada y baseline M361 actualizado.
