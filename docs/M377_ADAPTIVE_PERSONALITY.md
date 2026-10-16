# M377 — Personalidad Adaptativa

## Propósito

M377 permite que ROBY adapte la forma de una respuesta sin alterar quién es. La adaptación ocurre dentro del único núcleo cognitivo y consume la personalidad estable ya existente.

## Autoridades canónicas

`StablePersonalityEngine` continúa produciendo el snapshot de identidad expresiva estable. `AdaptivePersonalityAuthority` es la única autoridad para derivar un perfil de entrega a partir de ese snapshot. No existe una segunda personalidad ni un segundo cerebro.

## Perfil adaptativo

`AdaptivePersonalityProfile` conserva el identificador del snapshot estable, sus rasgos y su expresión. Sólo deriva:

- tono de entrega;
- nivel de detalle;
- estructura de respuesta;
- razones auditables de la adaptación.

Los indicadores `identity_changed` y `creates_parallel_brain` permanecen obligatoriamente falsos.

## Señales admitidas

M377 admite únicamente señales explícitas y normalizadas: complejidad de la tarea, urgencia, sensibilidad y preferencias explícitas de detalle o estructura. No deduce perfiles psicológicos ni preferencias permanentes.

## Límites

M377 no incorpora aprendizaje de personalidad, persistencia, inferencia emocional, manipulación afectiva, perfiles ocultos, agentes, identidades alternativas, LLM, cambios de memoria, cambios de planificación ni integración al runtime.

## Invariantes

1. ROBY conserva un único núcleo, cerebro e identidad.
2. Los rasgos estables nunca son modificados por la adaptación.
3. La personalidad adaptativa sólo gobierna la expresión.
4. Toda decisión es determinista y trazable.
5. Las preferencias persistentes requieren una autoridad y un hito posteriores.
