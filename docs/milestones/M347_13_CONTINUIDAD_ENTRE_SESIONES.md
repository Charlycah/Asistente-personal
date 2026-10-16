# M347.13 — Continuidad entre sesiones

## Objetivo

Permitir que la recuperación relevante de memoria continúe entre sesiones de
un mismo perfil sin crear otro store, otro recuperador ni un estado de sesión
paralelo.

## Integración canónica

M347.13 reutiliza `RuntimeSessionProfile`, definido por el subsistema canónico
de identidad y sesiones. `CognitiveMemoryIntegration` acepta ese mismo perfil
y registra `session_id` y `profile_id` dentro de los metadatos estructurados del
recuerdo autorizado por la política de escritura.

El recall existente usa esa procedencia para distinguir:

- recuerdos de la sesión actual;
- recuerdos de otra sesión del mismo perfil;
- recuerdos históricos sin procedencia de sesión;
- recuerdos pertenecientes a otro perfil, que quedan excluidos.

## Decisión observable

`SessionContinuityDecision` informa cantidades y procedencia sin exponer el
contenido de los recuerdos ni razonamiento interno. La decisión indica si hubo
continuidad real desde otra sesión y conserva la decisión de relevancia de
M347.12 como autoridad sobre qué recuerdos usar.

## Compatibilidad

Los recuerdos anteriores a M347.13 no contienen `session_id` ni `profile_id`.
Se clasifican como recuerdos heredados y siguen siendo recuperables. No se
requiere migración de esquema SQLite.

## Límites

M347.13 no implementa sincronización remota, handoff entre dispositivos,
resúmenes de sesión, reconstrucción completa de conversaciones ni otro motor
de identidad. Tampoco altera la política de escritura ni el umbral de
relevancia.
