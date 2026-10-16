# M365.1 — Android Bridge Contract Foundation

## Propósito

M365.1 define el contrato neutral y gobernado entre ROBY XI.2 y un futuro agente Android autorizado. El incremento describe identidad, versión de protocolo, capacidades, permisos y diagnóstico sin implementar transporte ni ejecución.

La base de entrada es M364, validada con 8706 pruebas aprobadas y Ruff limpio.

## Autoridad reutilizada

`AndroidBridgeContract` está subordinado a `OfficialDeviceGateway`. No crea un segundo registro de dispositivos ni una ruta paralela de ejecución.

El teléfono Android se registra como:

- categoría `mobile`;
- transporte lógico declarado `local_api`;
- identidad estable de dispositivo y agente;
- versión del protocolo del bridge;
- capacidades independientes del transporte;
- permisos Android declarativos.

## Contrato del agente

`AndroidBridgeIdentity` declara:

- `device_id` estable dentro de ROBY;
- `agent_id` de la aplicación autorizada;
- versión del protocolo;
- versiones opcionales de aplicación y Android;
- fabricante y modelo opcionales.

`AndroidBridgeDeclaration` incorpora capacidades y estados de permisos. Declarar un permiso como concedido no autoriza a ROBY a utilizarlo.

## Evaluación

`AndroidBridgeContract.assess()` comprueba:

1. que el dispositivo esté registrado en `OfficialDeviceGateway`;
2. que la versión del protocolo sea compatible;
3. que las capacidades estén declaradas;
4. que permisos y diagnósticos sigan siendo descriptivos.

El resultado siempre conserva `executable=False`.

## Límites de M365.1

M365.1:

- no abre sockets;
- no descubre teléfonos;
- no empareja dispositivos;
- no implementa HTTP, WebSocket, Bluetooth, USB, ADB ni nube;
- no solicita permisos Android;
- no lee notificaciones, ubicación, cámara, micrófono, contactos o archivos;
- no conecta el bridge al planner;
- no registra herramientas ejecutables;
- no crea trabajo en segundo plano;
- no modifica `.roby/credentials.json`.

Toda ejecución futura deberá registrarse y pasar exclusivamente por `ToolGatewayManager`, con permisos mínimos, consentimiento y trazabilidad.

## Próximo incremento

M365.2 podrá incorporar configuración y activación local controlada, manteniendo el transporte reemplazable y deshabilitado por defecto.

## Quality gates

- modelos inmutables y validados;
- composición exclusiva mediante `OfficialDeviceGateway`;
- incompatibilidad de protocolo degradada explícitamente;
- dispositivo desconocido bloqueado;
- permisos sin autoridad implícita;
- ninguna red, ejecución o integración con planner;
- Ruff limpio y suite completa sin regresiones.
