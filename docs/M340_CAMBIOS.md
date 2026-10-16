# M340 — Priorización cognitiva

M340 cierra la primera serie cognitiva iniciada en M333 mediante una política
explícita, determinista y explicable para seleccionar un objetivo cognitivo
prioritario.

## Incorporado

Nuevo paquete `core/cognitive_priority` con:

- `PriorityDecision`
- `PriorityReason`
- `PriorityPolicy`
- `DeterministicPriorityPolicy`
- `PriorityResolver`
- `PriorityManager`

## Reglas

1. Solo participan objetivos activos.
2. Siempre prevalece la prioridad explícita más alta del objetivo.
3. Entre objetivos con igual prioridad, se favorece la coincidencia con el foco.
4. Si continúa el empate, se selecciona el objetivo más antiguo.
5. El identificador alfabéticamente menor es el desempate final estable.
6. La confianza se incluye en la decisión para trazabilidad, pero no altera la
   selección en M340.

## Garantías

- mismas entradas, misma decisión;
- sin mutaciones de objetivos, foco o estado cognitivo;
- sin persistencia adicional;
- sin ejecución automática;
- sin aprendizaje, probabilidades ni inferencia;
- sin integración con el runtime.

## Pruebas

Se añaden 22 pruebas específicas en
`tests/test_m340_cognitive_priority.py`.
