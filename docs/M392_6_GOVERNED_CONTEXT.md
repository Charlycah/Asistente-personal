# M392.6 — Contexto Gobernado

M392.6 amplía el modelo persistente del mundo con una representación contextual
explícita, inmutable y de solo lectura bajo `internal_world_model`.

La proyección admite únicamente evidencia ya gobernada procedente de
`UnifiedCognitiveBlackboard` y de contextos `READY` emitidos por
`AmbientContextFoundation`. Las entradas del blackboard deben ser de tipo
`CONTEXT`; otras clases de señal no se promueven silenciosamente.

M392.6 no crea una autoridad paralela, no persiste contexto adicional, no
modifica las fuentes y no resuelve contradicciones ocultándolas. Un contexto
ambiental no listo permanece como evidencia que requiere revisión.

M392.6 no infiere estados personales, actividad, presencia o ubicación. No
realiza tracking, no lee sensores, no consulta proveedores, no usa reloj de
pared y no activa automatizaciones. Tampoco habilita ejecución ni cambia el
runtime.

El objetivo es permitir que hogar, personas, lugares, objetos y línea temporal
puedan ser interpretados posteriormente dentro de un marco contextual explícito
sin degradar procedencia, autoridad ni nivel epistemológico.
