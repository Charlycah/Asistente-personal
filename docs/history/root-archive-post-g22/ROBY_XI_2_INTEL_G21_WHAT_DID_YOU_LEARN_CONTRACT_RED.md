# ROBY XI.2 — INTEL-G2.1 — “WHAT DID YOU LEARN?” — CONTRACT RED

**Baseline de partida:** 14.068 PASS · Ruff clean · 0 FAIL, certificada por el usuario.

## Alcance contractual

Este RED congela exclusivamente el seam reconciliado en INTEL-G2.1:

1. la configuración canónica proyecta explícitamente el timezone household;
2. `OfficialMemoryGateway` acepta ese timezone de forma explícita;
3. “qué aprendiste hoy” resuelve el día civil household y consume exclusivamente la introspección temporal certificada por INTEL-G2;
4. “qué aprendiste ayer” usa el día civil household anterior, no una ventana móvil de 24 horas;
5. un intervalo sin aprendizaje durable produce una respuesta conversacional honesta sin inventar actividad, conversación o retrieval como aprendizaje.

## Semántica temporal

Para `America/Argentina/Buenos_Aires`, con `now=2026-09-05T01:30:00+00:00`, “hoy” corresponde al día civil local 2026-09-04 y por tanto al intervalo UTC half-open:

`[2026-09-04T03:00:00+00:00, 2026-09-05T03:00:00+00:00)`

“Ayer” corresponde a:

`[2026-09-03T03:00:00+00:00, 2026-09-04T03:00:00+00:00)`

## STOP

El RED no abre períodos naturales complejos, Analysis Mode, Biblioteca/Internet, Learning admission, revisión longitudinal, curiosidad, investigación, autonomía, nuevo ledger/store/registry/runtime ni nueva autoridad.

No modifica código productivo.

## Resultado dirigido esperado

El contrato contiene **5 fallos intencionales**, correspondientes exactamente a los cinco puntos todavía ausentes. La suite completa y Ruff deben ser certificados localmente por el usuario antes de abrir SURGICAL GREEN.
