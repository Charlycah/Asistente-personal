# M365.2 — Android Bridge Configuration & Controlled Activation

M365.2 añade configuración canónica y evaluación de activación controlada al contrato Android creado en M365.1.

## Autoridades reutilizadas

- La configuración procede del árbol oficial ya cargado desde `.roby/config.json`; el proveedor no lee archivos ni crea otra fuente de verdad.
- `OfficialDeviceGateway` continúa siendo el único registro de dispositivos.
- La futura ejecución continúa reservada a `ToolGatewayManager`.

## Estados

- `DISABLED`: la configuración no habilita el bridge.
- `CONFIGURED`: existe configuración válida, pero no hay activación automática o falta una declaración.
- `READY`: configuración habilitada, modo por declaración, dispositivo conocido, agente permitido y protocolo compatible.
- `BLOCKED`: falla identidad, registro o compatibilidad.

`READY` significa únicamente preparación contractual. Todo resultado conserva `executable=False`.

## Límites

Este milestone no abre transportes, sockets, HTTP, WebSocket, Bluetooth, USB ni ADB. Tampoco registra herramientas, llama al planner, solicita permisos Android o ejecuta capacidades del teléfono. El modo diagnóstico sólo agrega razones explicativas.
