# M387.8 — Reflexión posterior y aprendizaje gobernado

## Propósito

M387.8 incorpora la reflexión posterior al expediente cognitivo antes de que el
turno sea sellado. La reflexión continúa siendo observacional: mide metadatos de
la respuesta y su degradación, pero no cambia la respuesta ni reabre decisiones.

## Cierre observado

`UnifiedBrain` utiliza el cierre observado del gateway oficial. El observador
existente produce la reflexión y el gateway registra su evidencia dentro del
mismo ciclo. Los gateways históricos conservan el mecanismo anterior.

## Aprendizaje gobernado

El nodo `learning_candidate` diferencia tres situaciones:

- no existe candidato: `OMITTED`;
- existe un candidato revisable y no persistente: `PARTICIPATED`;
- intenta presentarse como aceptado o persistido automáticamente: `BLOCKED`.

M387.8 no crea candidatos a partir de conversaciones, no almacena contenido y
no activa aprendizaje automático. En el flujo productivo actual, la ausencia de
candidato queda registrada expresamente.

## Autoridad y privacidad

La evidencia no contiene texto de conversación, respuesta, propuesta ni
identificadores personales. No concede permisos, no acepta conocimiento y no
autoriza persistencia. Carlos y Cristina conservan igual autoridad de revisión.
