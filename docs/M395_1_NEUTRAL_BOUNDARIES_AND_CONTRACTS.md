# M395.1 — Fronteras y contratos neutrales

## Objetivo

Eliminar inversiones de capa detectadas por M394.A sin añadir capacidades, autoridades, gateways ni comportamiento nuevo.

## Migraciones certificables

1. `CameraFrame` pasa a `domain.vision.camera_frame`.
   `infrastructure.camera.camera_client` conserva un reexport compatible.
2. Los modelos y protocolos de Cognitive Agenda pasan a `domain.cognitive_agenda`.
   `app.cognitive_agenda_manager` conserva reexports compatibles.
3. Priority Reasoning pasa a `domain.priority_reasoning`.
   `app.priority_reasoning` y `core.priority_reasoning` quedan como superficies compatibles.
4. Android activation depende del contrato mínimo `domain.device_gateway_contract.RegisteredDeviceLookup`, no de `app.device_gateway`.
   `OfficialDeviceGateway` conserva su autoridad y ubicación.
5. El contrato moderno de respuesta pasa a `domain.response`.
   `m6.response.models` queda como shim histórico; sólo HAL/ROBY/M7 históricos deben depender de él.

## Invariantes

- No cambia el comportamiento observable.
- No se crea una segunda autoridad.
- No se activa I/O físico.
- No se retira legado histórico.
- Los imports históricos soportados preservan identidad de tipos.
- Ningún cambio de M395.1 autoriza nuevas acciones.
