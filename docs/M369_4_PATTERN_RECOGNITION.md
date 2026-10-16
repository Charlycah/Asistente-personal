# M369.4 — Pattern Recognition

## Objetivo

Incorporar una autoridad gobernada y de solo lectura que estructure patrones
candidatos a partir de relaciones explícitas, consistentes y trazables entre
hábitos previamente revisables.

## Autoridad

`pattern_recognition` depende únicamente de `habit_detection`.

## Contrato

La autoridad recibe evidencia explícita con sujeto, contexto y valor observado.
Una única evidencia permanece como `insufficient_evidence`. Dos o más evidencias
consistentes, procedentes de hábitos distintos, pasan a `review_required`.

La identidad del candidato es determinista y toda evidencia conserva la
trazabilidad hacia el hábito de origen.

## Límites

M369.4:

- no acepta patrones automáticamente;
- no infiere relaciones no declaradas;
- no adapta el razonamiento;
- no autoriza persistencia;
- no modifica el runtime.

La adaptación basada en patrones queda reservada para M369.5.
