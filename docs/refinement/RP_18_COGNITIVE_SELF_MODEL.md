# RP.18 — Cognitive Self Model

## Objetivo

Incorporar una representación ejecutiva, explícita y gobernada del estado
cognitivo actual de ROBY, sin confundir autodescripción con conciencia, identidad
humana ni capacidad operativa autónoma.

## Alcance

El modelo propio resume:

- modo cognitivo actual;
- foco activo;
- confianza e incertidumbre;
- carga cognitiva;
- estabilidad;
- necesidad de reevaluación;
- capacidades cognitivas realmente conectadas;
- procedencia de la evidencia.

## Modos

- `idle`
- `engaged`
- `reassessing`
- `suspended`

## Transiciones

- `created`
- `updated`
- `stable`
- `suspended`

## Integración

El flujo residente queda:

```text
Agenda Manager
→ Agenda Reasoning
→ Reflection Engine
→ Thought Stream
→ Hypothesis Workspace
→ World Model
→ Episodic Memory
→ Self Model
→ Continuous Cognitive State
```

La salida se publica en `ContinuousCognitiveState.self_model`.

## Gobernanza

RP.18 no ejecuta capacidades, no altera agenda, hipótesis, modelo del mundo ni
memoria episódica, no solicita autorización y no almacena cadena privada de
razonamiento. Las capacidades declaradas son únicamente las efectivamente
representadas por el pipeline cognitivo conectado.

## Compatibilidad

Se conserva el contrato histórico de racionalidad del ciclo:

```python
state.rationale == "agenda:<key>"
```

## Validación

- 11 pruebas nuevas de RP.18.
- 94 pruebas focalizadas RP.10–RP.18.
- 6366 pruebas completas aprobadas en el entorno de construcción.
