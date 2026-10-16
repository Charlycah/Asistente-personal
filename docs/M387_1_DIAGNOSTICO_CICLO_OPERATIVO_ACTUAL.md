# M387.1 — Diagnóstico del ciclo operativo actual

## Propósito

M387.1 mide qué partes del grafo cognitivo objetivo participan realmente en
cada turno. No conecta capacidades nuevas y no interpreta la mera existencia
de una clase o módulo como participación operativa.

## Resultado actual confirmado

Después de una identificación explícita y confirmada por `UnifiedBrain`, el
expediente canónico demuestra una secuencia conectada de tres nodos:

1. `conversation_ingress`;
2. `unified_coordination`;
3. `identity_and_context`.

La primera interrupción observable es `perception_and_evidence`. Los otros
catorce nodos posteriores permanecen como `not_recorded`. Esto no significa que
sus módulos no existan o no funcionen en otros recorridos; significa que todavía
no aportan evidencia al expediente cognitivo canónico del turno.

Si la identidad está pendiente, el corte aparece antes, en
`identity_and_context`, con estado `degraded`.

## Diagnóstico acumulativo

La proyección de sólo lectura informa por nodo:

- turnos participados;
- turnos omitidos, degradados o bloqueados;
- turnos sin evidencia;
- proporción de participación;
- proporción de observación.

También informa el resultado de cada ciclo, el prefijo conectado del último
turno y su primer punto de interrupción.

## Límites

El diagnóstico no contiene mensajes, respuestas, recuerdos, nombres ni
identificadores de sesión. No llama a memoria, planificación, decisión,
proveedores o acciones externas. No concede autoridad y no modifica el turno.

## Decisión para M387

Las siguientes integraciones deben añadir evidencia nodo por nodo. Un módulo
sólo podrá declararse conectado cuando el turno productivo demuestre su entrada,
salida, degradación y límites de autoridad.
