# M365.3 — Android Bridge Transport Abstraction

M365.3 incorpora una frontera de transporte reemplazable y simulable sobre la activación controlada de M365.2.

## Diseño

- `AndroidBridgeTransport` es un protocolo estructural que sólo expone metadata mediante `describe()`.
- `AndroidBridgeTransportDescriptor` declara identidad, tipo, protocolos soportados y disponibilidad.
- `NullAndroidBridgeTransport` es el valor seguro por defecto y siempre está indisponible.
- `StaticAndroidBridgeTransport` permite pruebas deterministas sin red ni hardware.
- `AndroidBridgeTransportPolicy` combina la activación gobernada con el descriptor sin producir efectos secundarios.

## Estados

- `DISABLED`: el bridge está deshabilitado por configuración.
- `BLOCKED`: la activación no está lista o el protocolo no es compatible.
- `UNAVAILABLE`: la activación está lista, pero el transporte declarado no está disponible.
- `AVAILABLE`: activación lista, transporte disponible y protocolo soportado.

`AVAILABLE` sólo describe preparación contractual. Todo resultado conserva `executable=False`.

## Límites

La abstracción no abre conexiones y no define `connect`, `send` ni `receive`. No incorpora HTTP, WebSocket, Bluetooth, USB, ADB, sockets, descubrimiento, reintentos, credenciales, planner ni ejecución. Los futuros adaptadores de I/O deberán quedar gobernados y cualquier acción seguirá reservada a `ToolGatewayManager`.
