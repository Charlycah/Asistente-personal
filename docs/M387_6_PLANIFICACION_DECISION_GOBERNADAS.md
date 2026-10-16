# M387.6 — Planificación y decisión gobernadas

## Propósito

M387.6 incorpora evidencia separada para planificación, permisos y decisión.
Ningún plan se considera permiso y ninguna decisión se considera ejecución.

## Recorridos observados

ROBY conserva dos recorridos productivos:

1. El plan conversacional directo coordina capacidades oficiales de riesgo
   permitido. El expediente registra el plan y, por separado, la comprobación de
   seguridad aplicada a sus pasos.
2. El runtime cognitivo aporta planificación ejecutiva y coordinación como
   contexto consultivo para la respuesta. En este caso, permisos registra
   explícitamente `advisory_only`.

El `UnifiedCognitiveCoordinator` continúa siendo la autoridad de decisión para
escenarios coordinados. Si detecta el escenario pero no encuentra resultados
seguros, la decisión queda degradada y permisos queda bloqueado.

## Estados seguros

- Un aporte aplicado participa.
- Un aporte no necesario se omite.
- Un contribuidor fallido se degrada.
- Un plan sin capacidad segura mantiene permisos bloqueado.
- Una coordinación sin resultado seguro nunca se presenta como decisión final.

## Privacidad y autoridad

La evidencia contiene sólo códigos técnicos. No contiene texto, títulos de plan,
directivas, conclusiones, referencias, nombres o sesiones.

El adaptador no planifica, no decide, no ejecuta herramientas y no cambia
permisos. Sólo observa las autoridades existentes durante el turno oficial.
