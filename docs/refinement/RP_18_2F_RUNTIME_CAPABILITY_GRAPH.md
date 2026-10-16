# RP.18.2F — Runtime Capability Graph

## Objetivo

Convertir los requisitos operativos de capacidades en un grafo declarativo,
inmutable y validado, consumido por el servicio oficial de health y readiness.

## Diseño

`RuntimeCapabilityNode` asocia una capacidad con sus residentes y con otras
capacidades requeridas u opcionales. `RuntimeCapabilityGraph` valida identidad,
referencias, superposición y ausencia de ciclos; además ofrece orden topológico,
dependientes e impacto transitivo por residente.

El grafo no contiene estado vivo. `RuntimeHealthReadinessService.evaluate_graph()`
lo interpreta siempre contra un `RuntimeOperationalSnapshot` puntual.

## Semántica

- Una capacidad requerida indisponible bloquea a su dependiente.
- Una capacidad requerida degradada degrada a su dependiente.
- Una capacidad opcional indisponible o degradada solo genera degradación.
- La salud global del runtime no se reemplaza ni se recalcula desde el grafo.

## Límites

Esta etapa no reinicia componentes, no repara fallos, no autoriza acciones y no
crea una segunda fuente de estado operativo.
