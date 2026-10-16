# ADR-105 — Shared Intellectual Interests

## Estado

Aceptado.

## Contexto

M93–M102 construyen la conversación viva, su oportunidad, momento, reflexión,
continuidad, contribución intelectual, realización, presencia, feedback y ritmo.
Falta una representación explícita y gobernada de los temas que muestran valor
intelectual compartido dentro de la conversación.

## Decisión

M103 incorpora `SharedIntellectualInterests`, una capa que recibe la decisión de
ritmo de M102 y evidencia conversacional tipada. La capa agrupa evidencia por
tema, calcula una puntuación conservadora, clasifica la fuerza como emergente,
establecida o central y conserva referencias de origen.

Los resultados son inmutables, deterministas, auditables y pueden quedar como
identificados, pendientes de revisión, insuficientes o no aplicables.

## Límites

M103 no escribe memoria personal, no aprende preferencias automáticamente, no
modifica personalidad o políticas, no genera texto, no decide el momento de
intervenir y no inicia conversaciones. Un ritmo pausado o de cierre puede
conservar el interés detectado, pero desaconseja su activación inmediata.

## Consecuencias

Los hitos posteriores pueden usar intereses compartidos como contexto gobernado
sin convertir inferencias conversacionales en hechos permanentes sobre el
usuario.
