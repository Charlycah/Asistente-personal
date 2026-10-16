# M396.2 — Residence Domain Foundation

## Estado

Primer contrato productivo mínimo de la época Distributed Residence. M396.2 convierte
la constitución M396.1 en modelos de dominio inmutables y declarativos, sin introducir
red, sincronización, ejecución remota, runtime distribuido ni una nueva autoridad.

## Línea base

M396.2 parte de M396.1 certificada con Ruff limpio, baseline M361 sincronizada,
10.330 tests aprobados y cero regresiones.

## Objetivo

Permitir que el mismo ROBY represente de forma explícita y gobernable:

- su residencia primaria u hogar operacional;
- cero o más residencias extendidas;
- cero o más puntos de presencia que no necesariamente sean residencia;
- la localidad objetiva de una interacción concreta.

El incremento no conecta físicamente ningún entorno. Representa contexto; no lo
opera.

## Modelo incorporado

El paquete `core.residence_domain` incorpora exclusivamente modelos:

- `ResidenceId`: identidad lógica estable de residencia.
- `ResidenceRole`: `primary_home` o `extended`.
- `ResidenceAdministrativeState`: `registered` o `revoked`.
- `ResidencePresenceState`: `unknown`, `available` o `unavailable`.
- `ResidenceDescriptor`: descripción declarativa de una residencia, recursos
  gobernados relacionados, capacidades y limitaciones declaradas.
- `PresenceEndpoint`: punto de interacción que puede pertenecer o no a una
  residencia.
- `PresenceEndpointKind`: clasificación declarativa del endpoint.
- `InteractionLocality`: origen objetivo de una interacción concreta.
- `ResidenceContextSnapshot`: vista inmutable que exige exactamente un hogar y
  puede contener N residencias extendidas, N endpoints y una localidad activa.

## Semántica constitucional preservada

M396.2 implementa el principio:

> **Una casa. Un ROBY. Muchas ventanas.**

La localidad activa no altera el hogar. Una interacción desde el celular puede
coexistir con la laptop como `primary_home`. Una sesión Web puede ser un endpoint
sin convertirse por ello en una residencia.

El modelo tampoco representa una identidad ROBY alternativa: sólo representa
lugares y puntos de presencia pertenecientes al mismo ROBY.

## Autoridad

M396.2 no crea `DistributedResidenceAuthority`, `ResidenceManager`,
`ResidenceGateway`, `ResidenceOrchestrator` ni servicio equivalente.

Los modelos son evidencia estructurada y no toman decisiones productivas. Las
fronteras certificadas siguen vigentes:

- `ExternalResourceRegistryAuthority` conserva identidad, estado, autorización y
  conectividad declarativa de recursos externos.
- `OfficialDeviceGateway` conserva su autoridad de dispositivos.
- Presence conserva su dominio conversacional.
- `device_continuity` conserva continuidad de dispositivo y sesión.
- `context_transfer` conserva manifiestos de contexto transferible.
- `ResidentComponentRegistry` continúa registrando componentes internos del runtime
  y no residencias de ROBY.

## Separaciones obligatorias

### Identidad de residencia ≠ transporte

`ResidenceId` no contiene IP, hostname, URL, puerto, socket, token ni credenciales.

### Capacidad ≠ permiso

`capabilities` declara posibilidades del entorno. No autoriza uso, no autentica y no
ejecuta ninguna capacidad.

### Registro ≠ disponibilidad

El estado administrativo (`registered` / `revoked`) es independiente de presencia
(`unknown` / `available` / `unavailable`).

### Endpoint ≠ residencia

Un endpoint Web puede existir sin residencia asociada. Cuando un endpoint sí está
vinculado a una residencia, el snapshot exige que esa residencia exista dentro del
mismo contexto declarado.

### Interacción ≠ cambio de hogar

`InteractionLocality` identifica desde dónde ocurre una interacción. Nunca promueve
una residencia extendida a hogar.

## Invariantes materializados

M396.2 materializa de forma directa los invariantes M396-I00 a M396-I20 aplicables al
modelo de dominio, con énfasis en:

- una única continuidad ontológica de ROBY;
- exactamente un `primary_home` por snapshot;
- ningún segundo núcleo o autoridad cognitiva;
- admisión no automática;
- identidad de residencia estable;
- hogar preservado;
- capacidad separada de autoridad;
- ausencia de replicación implícita;
- aislamiento de credenciales;
- fallo de residencia extendida sin invalidar hogar;
- transporte independiente;
- ausencia de promoción automática;
- Residence Awareness como contexto objetivo;
- Interaction Locality explícita;
- continuidad experiencial subordinada a las autoridades cognitivas existentes;
- movilidad de presencia sin multiplicar ROBY.

## Caso canónico demostrado por tests

El dominio puede representar simultáneamente:

```text
ROBY
├── Laptop        -> primary_home
├── Mini-PC       -> extended / available
├── Celular       -> extended / available
├── Web           -> presence endpoint
└── interacción   -> Celular
```

El resultado conserva `Laptop` como hogar aunque la interacción activa se origine
en `Celular`.

## Fuera de alcance

M396.2 no incorpora:

- sockets, HTTP, WebSocket, Bluetooth, LAN o Internet;
- descubrimiento de nodos;
- emparejamiento;
- autenticación entre residencias;
- sincronización o replicación;
- memoria por residencia;
- personalidad por dispositivo;
- preferencias artificiales por entorno;
- ejecución remota;
- failover cognitivo;
- elección de líder;
- persistencia nueva;
- cambios en composition roots o runtime productivo.

`.roby/credentials.json` permanece fuera del contrato y no se modifica.

## Criterio de cierre

M396.2 queda apto para certificación cuando:

1. los modelos mantienen todos los invariantes declarados;
2. no existe nueva autoridad, manager, gateway u orchestrator;
3. no se introduce I/O externo ni transporte;
4. las autoridades existentes permanecen separadas;
5. Ruff queda limpio;
6. baseline M361 se regenera correctamente;
7. la suite completa queda sin regresiones.
