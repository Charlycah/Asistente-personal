# M149 — Living Conversation Presence Policy

## Responsabilidad única
Evaluar el awareness de presencia producido por M148 y declarar si el contexto es elegible o debe quedar inhibido para etapas conversacionales posteriores.

## Entradas
- resultados gobernados de M148;
- propietario;
- política de frescura, confianza, límites y aceptación de contexto parcial.

## Salidas
- `ELIGIBLE` para awareness estable completo;
- `ELIGIBLE_PARTIAL` para awareness estable parcial permitido;
- `INHIBITED` para transición, incertidumbre o interrupción;
- `REVIEW_REQUIRED`, `BLOCKED` o `NOT_APPLICABLE` cuando corresponde.

## Reglas
- selección determinista del resultado M148 válido más reciente;
- preservación exacta del resultado y estados fuente;
- elegibilidad exclusivamente para awareness estable;
- inhibición explícita para transición, incertidumbre e interrupción;
- control de propietario, frescura, confianza, duplicados y límites;
- identificadores deterministas y repositorio inmutable mediante protocolo.

## Fuera de alcance
Decisión de iniciar conversación, activación conversacional, selección de timing, generación de prompts, realización de respuestas, identidad, actividad, intención, adaptación conductual, proveedores, automatización y mutación de plataforma.
