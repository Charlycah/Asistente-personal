# M407.2 — Residential Node Productive Connectivity — Residential Process Wiring & Lifecycle Integration

**Baseline de partida:** M407.1 certificada · 11.209 tests · Ruff limpio · M361 sincronizada.

## Objetivo

Alojar la composición M407.1 dentro del proceso residencial M402.3 existente como una
tarea opcional del `ResidentRuntimeService`, sin crear otro runtime, authority, registry,
transporte, sincronización ni mecanismo de deployment del sistema operativo.

## Implementación

`app/residential_connectivity_wiring.py` añade únicamente wiring de borde:

- `ResidentialConnectivityProcessSettings`: configuración explícita de endpoint, peer,
  transport id, intervalo y retry policy;
- `ResidentialConnectivityWiringDependencies`: inyección obligatoria del
  `PeerAuthenticationBoundary` M397 y de la fuente canónica de
  `ResidenceContextSnapshot` M396;
- `ResidentialConnectivityResidentWiring`: adapta M407.1 a un único `ResidentTask`;
- `ConnectivityAwareResidentialLifecycle`: garantiza que la composition cierre el
  carrier/recovery antes de liberar el lease del proceso residencial.

`build_residential_node_service()` conserva `tasks=()` cuando no existe wiring y sólo
agrega `residential-connectivity` cuando el wiring está presente.

## Configuración opt-in

La conectividad residencial permanece deshabilitada cuando no se declara configuración.
Una configuración parcial falla cerrado. La activación usa
`ROBY_RESIDENT_CONNECTIVITY_ENABLED=true` y exige peer ResidenceId, host, port, label y
transport id explícitos. Endpoint y ResidenceId permanecen conceptos separados.

La mera configuración de entorno no constituye autenticación. Si la conectividad está
habilitada, el proceso exige que el host suministre un `PeerAuthenticationBoundary`
gobernado y una fuente de contexto residencial. M407.2 no implementa un autenticador
"always verified" ni inventa una autoridad M396/M397.

## Lifecycle y fallos

Un fallo de conexión degrada la task, no el proceso residencial. Lease y heartbeat
continúan representando presencia del proceso, no health de red.

La task puede consumir un `TransportFailureObservation` M398 explícito y delegar recovery
a M407.1. No existe todavía en la baseline un monitor productivo que detecte por sí solo
la caída de un carrier ya establecido; M407.2 no infiere ni fabrica ese hecho.

En shutdown, la composition se detiene antes del lifecycle residencial para que no quede
carrier/recovery activo después de liberar el lease.

## Ownership preservado

- M396: ResidenceId, admisión y contexto residencial canónico.
- M397: authentication, admission verification, session y readiness.
- M398: carrier TCP, transport failure facts y bounded recovery.
- M402: lifecycle e integrated Residential Node status.
- M407.1: composition connect/reconnect y facts para M402.
- M407.2: wiring de proceso y lifecycle solamente.

## Límites pendientes demostrados

M407.2 no declara deployment físico completo porque la baseline todavía no aporta:

1. una implementación productiva concreta de `PeerAuthenticationBoundary`;
2. una fuente productiva de `ResidenceContextSnapshot` dentro del entrypoint standalone;
3. un monitor físico que convierta una caída de carrier vivo en
   `TransportFailureObservation`.

Estos límites son dependencias explícitas, no permisos para degradar los contratos M397
ni M398.

## Fuera de alcance

No incluye M403, perception M404, discovery, credential provisioning, TLS/PKI, installer,
Docker, systemd/Task Scheduler, autostart, actualización remota ni hardware real.
