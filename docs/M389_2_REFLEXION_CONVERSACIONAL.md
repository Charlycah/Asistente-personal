# M389.2 — Reflexión Conversacional

## Propósito

M389.2 incorpora una reflexión posterior al turno, estrictamente de solo lectura,
construida a partir del expediente cognitivo certificado. No vuelve a razonar ni
modifica la respuesta emitida.

## Autoridad

`ConversationReflectionAuthority` es la única autoridad para producir el
`ConversationReflectionReport`.

## Garantías

- posterior al turno;
- determinista;
- sin contenido conversacional privado;
- sin escritura en memoria;
- sin creación de aprendizaje;
- sin decisión, ejecución ni permisos;
- degradación segura y explícita.

## Salida

El informe conserva identificadores y códigos, no texto privado. Registra nodos
participantes, nodos no resueltos, clasificación epistemológica recibida,
riesgos codificados y preguntas abiertas codificadas.

## Límites

M389.2 no implementa análisis histórico, psicología funcional, persistencia de
reflexiones, automatización ni acciones externas.
