# M338 — Confianza e incertidumbre

M338 se construye exclusivamente sobre la M337 validada.

## Alcance

Se añade `core/cognitive_confidence` con una representación explícita,
inmutable y determinista de la confianza cognitiva.

API pública:

- `ConfidenceLevel`
- `Confidence`
- `ConfidenceResolver`
- `ExplicitConfidenceResolver`
- `ConfidenceController`
- `ConfidenceManager`

Los cinco niveles se traducen a puntuaciones estables dentro del contrato
persistente existente. La incertidumbre se deriva como el complemento de la
puntuación, sin probabilidades aprendidas ni inferencia.

`ConfidenceManager` refleja cambios explícitos mediante
`CognitiveStateUpdater`, por lo que reutiliza la persistencia y el historial de
M334–M336 sin crear archivos nuevos ni modificar el runtime.

## Fuera de alcance

- inferencia automática;
- aprendizaje;
- análisis conversacional;
- confianza por foco u objetivo;
- integración con el runtime;
- cambios automáticos de confianza.
