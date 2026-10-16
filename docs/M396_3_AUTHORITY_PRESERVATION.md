# M396.3 — Authority Preservation Guardrails

## Estado

Incremento de endurecimiento arquitectónico de M396 dedicado al invariante
**M396-I03 — Authority Preservation**.

M396.3 no incorpora una nueva capacidad productiva. Convierte la regla constitucional
«M396 no absorbe responsabilidades pertenecientes a autoridades existentes» en una
barrera verificable y auditable.

## Línea base

Parte de M396.2 certificada con Ruff limpio, baseline M361 sincronizada,
10.358 tests aprobados y cero regresiones.

## Principio protegido

> **Residence describe dónde está ROBY y desde dónde interactúa; no decide qué está
> autorizado a hacer, qué dispositivo debe operar, qué capacidad ejecutar, qué
> contexto transferir, qué presencia conversacional inferir ni qué componente del
> runtime gobernar.**

## Mapa de propiedad preservado

M396.3 congela como fronteras externas al dominio Residence, sin reasignarlas:

- `ExternalResourceRegistryAuthority`: registro, identidad, estado y autorización
  declarativa de recursos externos.
- `OfficialDeviceGateway`: frontera oficial para dispositivos y solicitudes de
  capacidad de dispositivo.
- `OfficialPresenceRuntimeGateway`: presencia conversacional oficial.
- `OfficialContextContinuityRuntimeGateway`: continuidad contextual oficial por
  propietario y sesión.
- `CognitiveAuthorityMap`: asignación canónica de una autoridad primaria por
  responsabilidad cognitiva.
- `OfficialCapabilityGateway`: acceso gobernado a capacidades registradas.
- `OfficialGovernedCapabilityRoutingRuntimeGateway`: políticas y enrutamiento
  gobernado de capacidades.
- `ResidentComponentRegistry`: ciclo de vida de componentes internos del runtime
  residente; continúa siendo un dominio distinto de Residence.
- `runtime_root_factory`: composition root oficial; M396.3 no añade wiring de
  residencia.

## Regla de dependencia

`core.residence_domain` permanece como modelo declarativo puro:

- puede depender de biblioteca estándar;
- no depende de `app`;
- no importa autoridades, gateways, managers, runtimes o registries existentes;
- no contiene llamadas de autorización, ejecución, routing, discovery, transporte,
  persistencia o mutación remota.

La dependencia futura permitida deberá orientarse desde una frontera gobernada hacia
el contexto de residencia, nunca al revés de forma que Residence se convierta en
propietario de la capacidad.

## Manifiesto de preservación

`docs/quality/M396_3_AUTHORITY_PRESERVATION_BASELINE.json` registra SHA-256 de las
fronteras críticas anteriores tal como existen en la baseline M396.2. Los tests de
M396.3 fallan si cualquiera de esas piezas cambia dentro de este incremento.

Este manifiesto no pretende congelarlas para siempre. Un incremento futuro puede
cambiarlas mediante decisión arquitectónica explícita, nueva baseline y pruebas
actualizadas. Su función es impedir absorciones accidentales durante Distributed
Residence.

## Prohibiciones específicas de I03

Residence no puede:

- registrar o autorizar recursos externos;
- conceder permisos o consentimientos;
- operar dispositivos;
- ejecutar capacidades;
- seleccionar/rutear herramientas;
- transferir o enriquecer contexto conversacional por autoridad propia;
- modificar memoria, aprendizaje, personalidad o planificación;
- gobernar presencia conversacional;
- iniciar/parar componentes residentes;
- convertirse en composition root;
- introducir `ResidenceAuthority`, `ResidenceManager`, `ResidenceGateway` o
  `ResidenceOrchestrator` como atajo arquitectónico.

## Relación con otros invariantes

I03 refuerza especialmente:

- M396-I02 — Unique Cognitive Authority;
- M396-I08 — Capability Is Not Authority;
- M396-I09 — No Implicit Replication;
- M396-I10 — Credential Isolation;
- M396-I13 — Transport Independence;
- M396-I15 — Governed Evolution;
- M396-I18 — Experiential Continuity subordinada a autoridades cognitivas existentes.

## Criterio de cierre

M396.3 queda apto para certificación cuando:

1. las fronteras críticas conservan exactamente su contenido respecto de M396.2;
2. `core.residence_domain` no depende de autoridades ni runtime productivo;
3. Residence carece de API productiva de autorización, ejecución o routing;
4. `runtime_root_factory` permanece sin wiring de Residence;
5. Ruff queda limpio;
6. baseline M361 se regenera correctamente;
7. la suite completa finaliza sin regresiones.
