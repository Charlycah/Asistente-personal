# M388.5.5 — Suite de Certificación Funcional Ejecutable

## Propósito

Convertir la certificación funcional M388.5 en pruebas ejecutables y transversales, sin agregar capacidades, reemplazar autoridades ni modificar el comportamiento productivo.

## Alcance

La suite certifica:

1. recorrido cognitivo oficial y expediente por turno;
2. unicidad de autoridades y núcleo canónico;
3. matriz de evidencia funcional;
4. degradación explícita y segura;
5. copropiedad igual de Carlos y Cristina;
6. aprendizaje gobernado sin autoactivación;
7. diagnóstico consolidado, privado y no autoritativo.

## Archivos

- `tests/architecture/test_m388_5_5_certified_cognitive_route.py`
- `tests/architecture/test_m388_5_5_certified_authorities.py`
- `tests/architecture/test_m388_5_5_functional_evidence_matrix.py`
- `tests/architecture/test_m388_5_5_safe_functional_degradation.py`
- `tests/architecture/test_m388_5_5_equal_coownership.py`
- `tests/architecture/test_m388_5_5_governed_learning_evidence.py`
- `tests/architecture/test_m388_5_5_consolidated_brain_diagnostic.py`

## Condición de aprobación

M389 queda habilitado solamente cuando:

- Ruff permanece limpio;
- estos tests y la suite completa pasan sin regresiones;
- `CanonicalCognitiveCore(` permanece en la línea 52 de `app/official_conversation_gateway.py`;
- no aparece una autoridad paralela;
- la evidencia distingue estructura, observación, participación, degradación y ausencia;
- ningún aprendizaje se activa sin confirmación;
- `.roby/credentials.json` no se modifica ni se incluye en el ZIP de entrega.

## Decisión de implementación

M388.5.5 agrega únicamente pruebas y documentación. No modifica producción porque las capacidades requeridas ya poseen contratos y evidencia específica entre M382 y M388. La suite consolida y cruza esa evidencia.
