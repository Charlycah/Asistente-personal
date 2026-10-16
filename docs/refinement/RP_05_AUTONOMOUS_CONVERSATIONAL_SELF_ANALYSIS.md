# RP.05 — Autonomous Conversational Self-Analysis

RP.05 incorpora autoanálisis conversacional autónomo y consultivo en la capa de
experiencia unificada.

## Alcance

- ROBY observa cada respuesta visible sin depender de un comando público.
- Decide ejecutar el análisis mediante umbral, señales y enfriamiento.
- Detecta correcciones del usuario, riesgo de ignorar contexto, aperturas
  repetidas y desajustes explícitos de longitud.
- Produce hallazgos y recomendaciones trazables.
- No modifica respuestas ya emitidas, configuración, memoria ni código.
- No ejecuta acciones externas y no inicia conversaciones por sí solo.

## Relación con proactividad

El autoanálisis genera una señal interna sobre calidad conversacional. La
proactividad es la capacidad separada que decide si ROBY debe iniciar una
interacción o actuar. Una integración futura puede permitir que la
proactividad consulte informes de RP.05, siempre bajo permisos, oportunidad,
frecuencia y políticas de interrupción existentes.

## Certificación local

- Pruebas focalizadas: 6 passed.
- Suite completa: 6246 passed.
- Regresiones: 0.
