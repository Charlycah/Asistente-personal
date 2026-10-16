# Certificación RP.19.2 — Activación inteligente de la agenda

## Alcance certificado

RP.19.2 extiende el `CognitiveAgendaManager` canónico con selección ejecutiva de foco, sin crear schedulers, residentes, memorias ni lifecycles paralelos.

## Comportamiento

- `primary_focus` conserva compatibilidad como cabeza informativa de la agenda.
- `activated_focus` identifica el único asunto habilitado para el ciclo cognitivo.
- Los asuntos `blocked` permanecen visibles pero no se activan.
- Los asuntos `watching` sólo se activan con urgencia material.
- La selección combina score, envejecimiento y penalización temporal por repetición.
- `last_activated_at` y `activation_count` persisten en la misma base SQLite de RP.19.1.
- La migración de esquema es incremental y compatible con bases RP.19.1 existentes.
- Razonamiento, reflexión, thought stream, world model, memoria episódica y self model reciben únicamente el foco efectivo.

## Integración

La activación ocurre dentro del `ContinuousInternalCognitiveLoop` oficial. Recordatorios, metas, proyectos, compromisos, conversación y actividad ambiental continúan entrando mediante las fuentes autoritativas existentes. No se ejecutan acciones externas ni irreversibles.

## Pruebas nuevas

`tests/test_rp_19_2_intelligent_cognitive_agenda_activation.py`

Cobertura: bloqueo, observación urgente, rotación anti-repetición, restauración del historial, integración con el ciclo y trazabilidad de la decisión.

## Validación final

- `ruff check .`: limpio.
- `pytest -q`: 6495 pruebas aprobadas.
- Baseline RP.19.1: 6489 pruebas.
- Incremento RP.19.2: 6 pruebas.
