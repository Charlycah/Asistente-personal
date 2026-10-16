# M389.3 — Motor de Análisis Histórico

## Objetivo

Analizar secuencias de reflexiones conversacionales ya certificadas para detectar
recurrencias, preguntas abiertas, distribución epistemológica y coexistencias
potencialmente contradictorias, sin leer texto privado ni modificar el sistema.

## Autoridad

`HistoricalAnalysisAuthority` es la única autoridad de esta capacidad. Su salida
es diagnóstica, inmutable, determinista y de solo lectura.

## Límites

- No modifica memoria.
- No crea aprendizaje.
- No cambia respuestas, permisos ni planificación.
- No resuelve contradicciones.
- No interpreta emociones ni formula diagnósticos psicológicos.
- No contiene contenido conversacional privado.

## Entrada y salida

Entrada: secuencia de `ConversationReflectionReport` de M389.2.

Salida: `HistoricalAnalysisReport`, con frecuencias codificadas, preguntas
abiertas, distribución epistemológica, riesgos y contradicciones codificadas.

## Degradación segura

Un fallo produce un informe degradado sin autoridad y sin afectar el turno ni
las reflexiones fuente.

## Certificación

La suite M389.3 verifica autoridad única, recurrencia, integridad epistemológica,
repetibilidad, inmutabilidad, ausencia de efectos secundarios y degradación
segura.
