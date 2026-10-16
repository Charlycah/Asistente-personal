# M389.4 — Psicología Funcional

## Objetivo

Construir una lectura funcional, no clínica y estrictamente descriptiva de
patrones cognitivos y conversacionales ya codificados por M389.1, M389.2 y
M389.3.

## Autoridad gobernada

`FunctionalPsychologyAuthority` es la única autoridad de esta capacidad. Opera
en solo lectura y produce un `FunctionalPsychologyReport` inmutable,
determinista y no autoritativo.

## Fuentes permitidas

La autoridad acepta exclusivamente:

- `EpistemicAssessment` de M389.1 — Análisis Cognitivo.
- `ConversationReflectionReport` de M389.2 — Reflexión Conversacional.
- `HistoricalAnalysisReport` de M389.3 — Análisis Histórico.

No lee texto conversacional, archivos privados, memoria, planes, permisos ni
credenciales.

## Alcance funcional

Puede describir mediante códigos:

- estilos de procesamiento epistemológico;
- patrones funcionales de objetivos, preguntas y atención a riesgos;
- estabilidad o persistencia observada históricamente;
- límites de evidencia y tensiones epistemológicas que requieren cautela.

Estos indicadores describen funcionamiento observable del sistema. No describen
la identidad esencial de una persona.

## Límites obligatorios

- No realiza diagnósticos clínicos.
- No infiere trastornos mentales.
- No prescribe tratamientos ni acciones.
- No modifica ni crea memoria.
- No modifica ni crea aprendizaje.
- No modifica planificación.
- No modifica permisos.
- No reemplaza autoridades de M389.1, M389.2 o M389.3.
- No contiene contenido conversacional privado.

## Estados

- `complete`: existe al menos una fuente codificada utilizable.
- `insufficient_evidence`: no existen fuentes suficientes; el informe permanece
  seguro y explícito.
- `degraded`: una falla interna produce un informe sin autoridad y sin efectos
  secundarios.

## Certificación

La suite M389.4 verifica autoridad única, dependencia exclusiva de fuentes
M389, ausencia de diagnóstico clínico, solo lectura, inmutabilidad,
determinismo, independencia del orden, ausencia de mutaciones, degradación
segura, exclusión de credenciales y preservación del constructor canónico en la
línea 52.
