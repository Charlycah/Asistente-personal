# M394.5 — Conectividad Gobernada de Recursos Externos

## Propósito

M394.5 amplía la infraestructura externa gobernada para representar cómo podría conectarse un recurso externo ya registrado, sin establecer ninguna conexión real. La conectividad es conocimiento declarativo y permanece separada del registro, la identidad, el estado y la autorización.

## Autoridad

La única autoridad continúa siendo `ExternalResourceRegistryAuthority`. No se crean `ConnectivityManager`, `ConnectionManager`, gestores de red ni autoridades paralelas.

## Modelo

`ExternalResourceConnectivityState` admite únicamente:

- `unknown`: no existe declaración de conectividad.
- `configured`: existe un perfil declarativo con transporte y referencia de endpoint.
- `unavailable`: existe evidencia explícita de que la conectividad declarada no está disponible.

Cada declaración explícita se conserva como `ExternalResourceConnectivityDeclaration`, con estado, `transport_type`, `endpoint_reference`, fuente, instante declarado y revisión consecutiva. Un registro heredado de M394.1–M394.4 comienza en `unknown` sin migración destructiva.

## Operaciones gobernadas

`declare_connectivity()` registra evidencia descriptiva recibida del llamador. `connectivity_state()` y `connectivity_history()` exponen el estado e historial. `connection_profile()` devuelve el último perfil sólo cuando el estado vigente es `configured`.

Ninguna de estas operaciones abre sockets, redes, Wi-Fi, Bluetooth, USB, HTTP, APIs, procesos o dispositivos. No existe `connect()` en esta autoridad.

## Separación de dimensiones

Declarar conectividad no modifica `identity`, `state`, `authorization_state` ni `authorization_history`. Un recurso puede estar `available` y `authorized` sin tener conectividad configurada, o tener un perfil `configured` sin que ello signifique conexión activa.

## Invariantes preservados

- Una única autoridad por capacidad.
- Sin gestores paralelos.
- `OfficialDeviceGateway` permanece intacto.
- `CanonicalCognitiveCore(` conserva su posición contractual.
- No se modifica `.roby/credentials.json`.
- No se añade persistencia, descubrimiento, autenticación, activación ni ejecución externa.

## Fuera de alcance

M394.5 no conecta cámaras, sensores, nodos, servicios o dispositivos; no escanea la red; no resuelve endpoints; no comprueba disponibilidad; no autentica; no activa; no transmite datos. La ejecución de conectividad real queda fuera de este incremento.
