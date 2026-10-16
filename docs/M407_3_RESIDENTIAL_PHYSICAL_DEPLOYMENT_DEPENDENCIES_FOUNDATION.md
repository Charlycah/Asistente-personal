# M407.3 — Residential Node Physical Deployment Dependencies Foundation

**Baseline de partida:** M407.2 certificada · 11.219 tests · Ruff limpio · M361 sincronizada.

## Objetivo

Cerrar las dependencias software productivas restantes antes de una certificación física
real del Residential Node, sin crear nuevas authorities ni reabrir M396/M397/M398/M402.

El incremento queda limitado a tres adapters:

1. provisioning explícito de `ResidenceContextSnapshot` M396;
2. implementación productiva mínima de `PeerAuthenticationBoundary` M397 mediante
   credential provisionada y proof HMAC SHA-256;
3. traducción de fallos I/O observados por M398 a `TransportFailureObservation`.

## Productive residence context

`ProductiveResidenceContextSource` materializa exclusivamente tipos canónicos M396. Para
el proceso residencial inicial, Primary Home permanece `PRIMARY_HOME` y el nodo físico
permanece `EXTENDED` con `admission_id` explícito. `ResidenceId` no deriva de hostname, IP,
MAC, PID ni transport endpoint.

El provisioning de entorno exige etiquetas no secretas y admission provenance explícita.
No introduce DB, registry distribuido ni nueva autoridad de identidad.

## Productive peer authentication

`ProvisionedPeerAuthenticationBoundary` implementa el boundary M397 existente. No concede
admission, session, readiness ni action authority.

El mecanismo inicial es `psk-hmac-sha256`: el secreto del peer se obtiene mediante un
`PeerCredentialSource`; la presentación transporta sólo un HMAC proof derivado para el
`ResidenceId`. La comparación usa `hmac.compare_digest`. El resultado M397 expone sólo una
referencia opaca (`provisioned:<residence_id>`), nunca el proof ni el secreto.

`SecretsLoaderPeerCredentialSource` reutiliza el secret store privado existente de ROBY a
través de una key de configuración no secreta. El credential puede rotar sin cambiar
`ResidenceId`.

Este mecanismo está diseñado sólo para el primer deployment doméstico controlado. No
constituye PKI, TLS mutuo ni seguridad para exposición pública/remota.

## Transport failure observation

`TransportFailureObservationAdapter` convierte únicamente hechos físicos observados en
M398 a los tipos ya existentes:

- `ConnectionRefusedError` → `CONNECTION_REFUSED`;
- `TimeoutError` → `TIMEOUT`;
- `ConnectionResetError` → `CONNECTION_RESET`;
- `OSError` → `OS_ERROR`;
- EOF explícito → `PREMATURE_EOF`;
- framing inválido → `INVALID_FRAME`.

El adapter no reintenta, no autentica y no decide readiness. M407.1 continúa delegando el
recovery acotado a M398 y revalida M397 después de recuperar transporte.

## Integración con M407.1/M407.2

El entrypoint M402.3 conserva dependency injection explícita. Cuando conectividad está
habilitada y no se suministran dependencies manuales, M407.3 puede construirlas desde:

- provisioning M396 explícito;
- referencia de credential en el secret store;
- evidence proof `psk-hmac-sha256` configurado para el peer.

Configuración incompleta o scheme distinto falla cerrado. Sin conectividad configurada,
el comportamiento histórico `tasks=()` permanece intacto.

`ResidentialConnectivityConfig` no incluye la presentación del peer en `repr`, evitando
que un proof de autenticación aparezca accidentalmente en diagnóstico textual.

## Ownership preservado

- M396: ResidenceId, roles, contexto y admission provenance.
- M397: authentication, admission verification, session y communication readiness.
- M398: TCP/carrier, failure kinds y bounded recovery.
- M402: lifecycle e integrated Residential Node status.
- M407.1: connect/reconnect composition.
- M407.2: process wiring.
- M407.3: deployment-edge provisioning/adapters solamente.

## Fuera de alcance

No incluye Governed Synchronization M403, Residential Perception M404, discovery, PKI,
TLS, VPN, cloud relay, background polling, socket watchdog, installer, Docker, systemd,
Task Scheduler, autostart, instalación de Python/dependencias ni hardware real.

## Criterio de terminación

M407.3 queda software-completo cuando el proceso puede materializar contexto M396, evaluar
un proof productivo mediante M397 y convertir fallos físicos observables de M398 al modelo
canónico sin test doubles semánticos ni defaults permisivos. La certificación física sigue
siendo un gate posterior y separado.
