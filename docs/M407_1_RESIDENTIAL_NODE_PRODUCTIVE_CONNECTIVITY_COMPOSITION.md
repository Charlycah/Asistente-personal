# M407.1 — Residential Node Productive Connectivity Composition

**Baseline de partida:** Estado Maestro Post-M406 · 11.199 tests · Ruff limpio.

## Objetivo

Cerrar el cable productivo mínimo entre los contratos ya certificados M396, M397,
M398 y la observabilidad M402, sin crear otra authority, runtime, identidad,
transporte ni sincronización implícita.

## Implementación

`app/residential_connectivity_composition.py` añade una capa de composición
subordinada con tres contratos:

- `ResidentialConnectivityConfig`: ResidenceId local/peer, endpoint físico,
  presentación M397, transport id y policy M398;
- `ResidentialConnectivityComposition`: coordina dial/recovery M398 y vuelve a
  ejecutar autenticación/admisión M397 para cada carrier válido;
- `ResidentialConnectivitySnapshot`: proyección immutable de facts ya gobernados,
  sin autoridad de acción ni secretos.

La composición produce `GovernedConnectionBinding`, que puede ser consumido por
`ResidentialNodeEvaluator` M402 sin recalcular READY en M407.

## Reconnect

Ante pérdida física, M407.1 cierra el carrier previo y usa exclusivamente la
policy/recovery acotada M398. Si el transporte vuelve, crea un contexto de sesión
nuevo y repite M397 authentication + admission. Un socket recuperado nunca restaura
por sí mismo `communication_ready` ni una session anterior.

Una residencia revocada durante downtime queda no admitida y la conexión falla
cerrado. Recovery agotado permanece no ready.

## Ownership preservado

- M396: `ResidenceId` y estado canónico de residencia.
- M397: authentication, admission, session y communication readiness.
- M398: TCP, carrier, binding físico y bounded recovery.
- M402: estado integrado `REGISTERED/READY/DEGRADED/UNAVAILABLE`.
- M407.1: sólo composición productiva y observabilidad de fallo.

## Fuera de alcance

No incluye M403, replicación, percepción M404, discovery, credenciales persistidas,
installer, Docker, systemd/Task Scheduler, remote access ni hardware real.

## Invariantes

- un ROBY / un cerebro / un `RuntimeCompositionRoot`;
- endpoint físico != ResidenceId;
- transporte disponible != session lógica válida;
- recovery M398 requiere revalidación M397 antes de volver a ready;
- session previa no se reutiliza ciegamente;
- M407.1 no autoriza acciones ni sincronización;
- fallos de conectividad residencial no transfieren autoridad al nodo.
