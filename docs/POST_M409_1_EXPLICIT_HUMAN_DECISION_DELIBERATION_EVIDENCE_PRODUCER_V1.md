# Post-M409.1 — Explicit Human Decision Deliberation Evidence Producer v1

## Estado

IMPLEMENTED — pendiente de cierre/certificación final del entorno del usuario.

## Objetivo

Añadir una proyección conversacional mínima, determinista y read-only que preserve
alternativas de decisión expresadas explícitamente por el usuario en el turno actual.

La capability termina en evidencia estructurada. No produce recomendaciones, no decide,
no crea `GovernedDecisionOption`, no llama M391.6 y no entra todavía al runtime
conversacional productivo.

## Contrato

`ExplicitHumanDecisionDeliberationEvidenceProducer.analyze(text)` devuelve
`ExplicitDecisionDeliberationEvidence` con uno de cuatro estados:

- `NOT_DELIBERATION`
- `EXPLICIT`
- `AMBIGUOUS`
- `INSUFFICIENT_OPTIONS`

Cuando el estado es `EXPLICIT`, cada alternativa conserva:

- `raw_text`
- `normalized_text`
- `start_offset`
- `end_offset`
- `ordinal`

La invariante principal es:

`source_text[start_offset:end_offset] == raw_text`

## Gramática v1 admitida

- `¿A o B?`
- `¿Conviene A o B?`
- `¿Qué me conviene: A o B?`
- `Entre A y B, ¿cuál conviene?`
- `Tengo dos opciones: A o B.`
- listas explícitamente marcadas de 2 a 5 opciones, por ejemplo
  `Tengo tres opciones: A, B o C.`

La gramática privilegia precisión sobre cobertura. No intenta interpretar discurso libre.

## Abstenciones obligatorias

v1 no genera ni completa alternativas. Se abstiene o degrada conservadoramente ante:

- preguntas sin alternativas explícitas;
- listas múltiples no marcadas;
- alternativas duplicadas;
- referencias como `el otro`, `esto`, `aquello`;
- alternativas incompletas como `qué otra cosa`;
- delimitación binaria con comas ambiguas;
- cualquier caso que requiera memoria, contexto o inferencia semántica.

## Normalización

Sólo se permite normalización superficial de whitespace. El producer no realiza:

- lematización;
- resolución de fechas;
- expansión de elipsis;
- resolución de referencias;
- traducción;
- generación con LLM;
- ranking o preferencia.

El orden de las alternativas es únicamente el orden de aparición y nunca representa
preferencia.

## Gobernanza

La capability:

- no es una authority;
- no consulta repositories ni bases de datos;
- no usa filesystem, networking, threads ni procesos de fondo;
- no consulta memoria ni contexto conversacional previo;
- no importa M391.5 ni Foundation v1;
- no importa ni llama M391.6;
- no llama Conversation Repair;
- no persiste resultados;
- no ejecuta acciones;
- no concede autoridad.

Foundation v1 permanece CLOSED / CERTIFIED / FROZEN. M409.1 y Residential permanecen
FROZEN. M410/networking permanece NO-GO.

## Validación específica

La suite arquitectónica del producer cubre casos positivos y negativos, exactitud de
spans, determinismo, fingerprint, ambigüedad, duplicados y ausencia de dependencias
prohibidas.
