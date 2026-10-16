# M364 — Device Capability Foundation

## Propósito

M364 establece una fundación común y gobernada para describir dispositivos físicos o virtuales sin depender de un transporte, fabricante o protocolo específico.

La base validada de entrada es M363, con 8698 pruebas aprobadas y Ruff limpio.

## Autoridades reutilizadas

M364 no crea una arquitectura paralela. Reutiliza:

- `DeviceIdentity` para la identidad estable del dispositivo;
- `DeviceCapabilityDescriptor` y `DeviceCapabilityRegistry` para capacidades declaradas;
- `ToolGatewayManager` como única vía futura de ejecución externa.

La nueva frontera de aplicación es `OfficialDeviceGateway`.

## Modelo neutral

Un dispositivo queda representado por:

- identidad y propietario;
- categoría funcional;
- uno o varios transportes;
- fabricante, modelo y firmware opcionales;
- capacidades declaradas;
- observación de estado y diagnóstico.

Transportes iniciales:

- Bluetooth;
- USB;
- Wi-Fi;
- LAN;
- nube;
- API local;
- serial;
- virtual.

La capacidad es independiente del transporte. Una impresora puede exponer `print` por USB o Wi-Fi; una aspiradora robot puede exponer `battery`, `clean_room` y `return_to_base` mediante Wi-Fi o API local.

## Categorías iniciales

- computadora;
- móvil;
- wearable;
- audio;
- video;
- impresora;
- electrodoméstico;
- sensor;
- controlador;
- desconocido.

Estas categorías son descriptivas y no habilitan acciones por sí mismas.

## Estado y diagnóstico

`DeviceObservation` registra de manera uniforme:

- estado operativo;
- transporte activo;
- batería cuando existe;
- fecha de observación;
- diagnósticos no sensibles.

Una observación no ejecuta conexión, emparejamiento ni comandos.

## Gobierno de acciones

`OfficialDeviceGateway.prepare_action()` valida:

1. que el dispositivo sea conocido;
2. que la capacidad esté declarada;
3. que exista solicitud explícita del usuario;
4. consentimiento para acciones sensibles o destructivas;
5. confirmación adicional para acciones destructivas.

Toda acción de M364 produce un plan con `executable=False`.

M364 no conecta, desconecta, imprime, limpia, mueve, enciende ni controla hardware. La ejecución futura deberá pasar por ToolGateway y por un adaptador específico validado.

## Ejemplo: aspiradora robot

Una aspiradora robot puede registrarse como `HOME_APPLIANCE`, utilizar Wi-Fi y API local, y declarar:

- `battery`;
- `clean_room`;
- `return_to_base`.

La frase «Roby, limpiá el living» podrá convertirse en una acción gobernada sólo cuando exista un adaptador futuro. En M364 únicamente se reconoce el dispositivo, se valida la capacidad y se prepara el plan.

## Límites

M364 no incorpora:

- descubrimiento automático de Bluetooth o USB;
- emparejamiento;
- drivers;
- ejecución de comandos;
- telemetría continua;
- vigilancia de dispositivos;
- adaptadores de fabricantes;
- Home Assistant ni MCP.

## Quality gates

Toda integración futura deberá:

- usar `OfficialDeviceGateway` como frontera;
- registrar identidad, transportes y capacidades;
- mantener capacidades independientes del transporte;
- ofrecer diagnóstico y degradación explícitos;
- pasar por ToolGateway para ejecutar;
- incluir pruebas unitarias, negativas, de composición y de hardware cuando corresponda;
- documentar permisos, desactivación y privacidad.
