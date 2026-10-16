# M41 - ROBY Identity

## Estado

Ready for local validation.

## Objetivo

Iniciar **FASE IV.1 - Identidad** incorporando una identidad cognitiva estable,
determinista y testeable para ROBY.

ROBY deja de ser tratado solo como pipeline o runtime y comienza a tener un
contrato explícito de identidad:

- quién es;
- para quién existe;
- cuál es su propósito;
- qué principios no debe traicionar;
- quiénes son Carlos y Cristina dentro del hogar;
- qué responsabilidades permanentes tiene.

## Alcance

M41 no introduce autonomía, acciones proactivas, persistencia nueva ni cambios
invasivos en Arquitectura 1.0. La identidad es una capa leída por los módulos
cognitivos, no una capa ejecutora.

## Decisiones

- Se crea `core.identity` como contrato estable de identidad.
- La identidad no depende de LLM ni de Internet.
- Carlos y Cristina quedan modelados como miembros del hogar.
- El Cognitive Pipeline puede recibir una identidad opcional e inyectarla en el
  `system_prompt`.
- La compatibilidad hacia atrás se mantiene: si no se pasa identidad, M40 sigue
  funcionando como antes.

## Principio arquitectónico

ROBY no es el modelo externo. ROBY es la entidad persistente. Los modelos externos
son herramientas consultables cuando ROBY necesita conocimiento, explicación o
razonamiento adicional.

## Validación esperada

```bash
pytest tests/test_m41_roby_identity.py
pytest tests/test_m40_cognitive_pipeline.py
pytest
```

El cierre requiere que M41 pase y que la suite existente no retroceda.
