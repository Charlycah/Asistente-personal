# M47 — ROBY Experiential Learning (Phase IV.7)

## Propósito

M47 introduce el aprendizaje experiencial de ROBY. Esta pieza no busca almacenar
conocimiento enciclopédico ni reemplazar la memoria persistente existente. Su
función es capturar señales de convivencia, convertirlas en experiencias
aprendidas y hacerlas disponibles para el razonamiento, la planificación y el
prompt cognitivo.

## Principio arquitectónico

ROBY no aprende datos para parecer más inteligente. ROBY aprende experiencias para
convivir mejor con Carlos y Cristina.

## Componentes

- `LearningSignal`: señal observada durante una interacción o resultado.
- `LearnedExperience`: lección consolidada con evidencia, confianza y fuerza.
- `LearningContext`: contexto que conecta identidad, estado mental, atención,
  working memory, reasoning y planning.
- `ExperientialLearningEngine`: transforma señales en experiencias.
- `ExperientialLearningManager`: mantiene las experiencias activas y expone
  líneas seguras para el `system_prompt`.

## Integración cognitiva

M47 se conecta de forma opcional con el `CognitivePipeline`. Si existe un manager
de aprendizaje, cada turno puede producir una experiencia de convivencia sin
modificar el núcleo estable de ROBY.

Flujo actual:

```text
Identity
  ↓
Mental State
  ↓
Attention
  ↓
Working Memory
  ↓
Reasoning
  ↓
Planning
  ↓
Experiential Learning
```

## Alcance

M47 aprende patrones simples y auditables:

- preferencias de Carlos o Cristina;
- rutinas observadas;
- correcciones del usuario;
- resultados de planes;
- patrones de recordatorios;
- señales de convivencia.

No implementa aprendizaje autónomo sin supervisión, entrenamiento de modelos,
memoria vectorial ni internet. Eso queda fuera del alcance de este hito.

## Hito histórico

Today ROBY learned from experience.
