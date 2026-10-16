# RP.15 — Cognitive Hypothesis Workspace

## Propósito

RP.15 incorpora un espacio cognitivo gobernado para mantener interpretaciones
alternativas sobre el hilo activo de RP.14.

La capa no ejecuta acciones, no modifica la agenda y no almacena cadenas privadas
de razonamiento. Conserva solamente proposiciones resumidas, confianza, evidencia,
estado y revisiones auditables.

## Flujo

```text
RP.11 Cognitive Agenda Manager
              ↓
RP.12 Cognitive Agenda Reasoning
              ↓
RP.13 Cognitive Reflection Engine
              ↓
RP.14 Cognitive Thought Stream
              ↓
RP.15 Cognitive Hypothesis Workspace
              ↓
Continuous Cognitive State
```

## Contratos

El workspace puede:

- crear una hipótesis de continuidad para el hilo activo;
- abrir una alternativa de reevaluación cuando RP.13 lo recomienda;
- fortalecer o debilitar confianza con cambios acotados;
- ordenar hipótesis y seleccionar una interpretación líder;
- suspender hipótesis pertenecientes a focos anteriores;
- acumular fuentes de evidencia sin duplicarlas.

El resultado queda disponible como:

```python
state.hypothesis_workspace
```

Se preserva el contrato histórico:

```python
state.rationale == "agenda:<key>"
```

## Gobernanza

RP.15:

- no ejecuta capacidades;
- no crea planes operativos;
- no solicita autorización;
- no reemplaza RP.12 ni RP.13;
- no modifica RP.11 ni RP.14;
- no conserva cadenas privadas de razonamiento.
