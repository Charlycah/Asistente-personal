# ADR-073 - Integracion de Scope Guard en codigo real

## Estado
Aceptado para M71.

## Contexto
La Fase VII introduce ROBY Personal Operations. Antes de incorporar memoria domestica, documentos, agenda, tareas o autonomia supervisada, ROBY necesita un limite operativo formal que impida que nuevas capacidades crucen dominios excluidos.

El usuario definio explicitamente que quedan fuera de alcance cuentas, bancos, billeteras, pagos y compras. El sistema tambien debe tratar decisiones medicas, legales y acciones externas como dominios de revision humana.

## Decision
Se incorpora `core.scope_guard` como modulo de nucleo y se integra de forma opcional en `CognitivePipeline`.

El modulo expone:

- `ScopeGuardPolicy`
- `ScopeGuardManager`
- `ScopeGuardSnapshot`
- `ScopeGuardDecision`
- `ScopeDomain`
- `ScopeGuardStatus`
- `ScopeGuardSignal`

`CognitivePipeline` acepta un `scope_guard` opcional, lo ejecuta durante `process_turn()` y agrega sus reglas al `system_prompt`.

## Reglas normativas

- ROBY MUST NOT operar bancos, cuentas, billeteras, pagos, inversiones ni compras.
- ROBY MAY organizar memoria domestica, documentos, agenda, conocimiento y tareas.
- ROBY SHOULD derivar acciones externas o decisiones sensibles a revision humana.
- Si una solicitud mezcla dominios permitidos y prohibidos, MUST prevalecer la interpretacion mas restrictiva.

## Consecuencias

- La Fase VII inicia con un limite arquitectonico verificable.
- Los bloques posteriores deberan consultar o respetar `ScopeGuardManager` antes de proponer ejecucion.
- El sistema preserva autonomia supervisada sin convertirse en un agente con capacidad de operar dominios sensibles.

## Verificacion

- `pytest -q tests/test_m71_scope_guard.py`: 11 passed.
- `pytest -q`: 756 passed.
- Ruff no pudo ejecutarse en este entorno porque el paquete no esta instalado.
