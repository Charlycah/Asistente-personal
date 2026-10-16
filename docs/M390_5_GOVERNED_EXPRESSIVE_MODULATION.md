# M390.5 — Modulación Expresiva Gobernada

## Objetivo

Permitir que el estado interior simulado de M390 aporte una señal expresiva limitada a la autoridad adaptativa M377, sin crear un segundo motor de personalidad, respuesta o estilo.

## Decisión arquitectónica

`AdaptivePersonalityAuthority` continúa siendo la única autoridad de modulación expresiva. M390.5 incorpora `GovernedExpressiveModulation` como adaptador puro y subordinado: recibe un `SimulatedInnerStateSnapshot` explícito y produce un `AdaptivePersonalityRequest` compatible con M377.

El adaptador no construye perfiles, no modifica texto, no ensambla respuestas y no posee `authority_id`.

## Señales admitidas

La modulación afectiva sólo puede proponer estos tonos de entrega:

- `neutral`
- `warm`
- `careful`

No puede solicitar `direct` ni `repairing`. Esos estados continúan gobernados por la personalidad y el contexto explícito de M377.

## Precedencias

1. Una expresión estable `repairing` conserva prioridad.
2. Un contexto explícitamente sensible o una expresión estable `careful` conserva prioridad.
3. La señal afectiva simulada puede modular el tono dentro de los límites M390.5.
4. Sin señal afectiva válida se aplica la lógica previa de M377.
5. Las preferencias explícitas de detalle y estructura no son modificadas por M390.5.

## Degradación segura

Un snapshot ausente, insuficiente o degradado no produce modulación afectiva. El adaptador tampoco infiere una emoción desde ausencia de información.

## Límites

M390.5 no incorpora:

- persistencia;
- aprendizaje;
- modificación de identidad o rasgos;
- edición directa de texto;
- ensamblado de respuesta;
- LLM;
- runtime;
- acciones;
- permisos;
- objetivos propios.

## Invariante principal

El mundo interior simulado puede aportar contexto expresivo, pero nunca reemplaza a `AdaptivePersonalityAuthority` ni se convierte en una autoridad de respuesta.
