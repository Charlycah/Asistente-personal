# M68 — Camera Adapter

## Objetivo

M68 incorpora la primera capacidad de percepción local de ROBY: captura controlada de cámara.
La cámara no se conecta al `CognitivePipeline` ni al core cognitivo de forma directa; entra como adapter externo detrás de la arquitectura de Fase VI.

## Principio

ROBY no abre la cámara directamente.
ROBY solicita una capacidad visual y el sistema decide si puede ejecutarla.

```text
Usuario
  → comprensión semántica
  → Capability Registry
  → Permissions & Consent
  → Tool Gateway
  → Camera Adapter
  → proveedor local de cámara
```

## Componentes

- `infrastructure/camera/camera_client.py`
  - `CameraFrame`
  - `CameraProvider`
  - `CameraProviderError`
  - `OpenCVCameraClient`

- `infrastructure/camera/camera_adapter.py`
  - `CameraAdapter`
  - `CameraAdapterPolicy`
  - `build_camera_adapter_from_config`

- `tests/test_m68_camera_adapter.py`

## Capacidades

M68 implementa:

- `camera.capture`

La capacidad ya existía semánticamente desde M63B y ahora recibe su adapter real.

## Seguridad y permisos

La cámara usa:

- `PermissionScope.DEVICE`
- `requires_confirmation=True`
- consentimiento explícito antes de capturar

Sin permiso activo, el `ToolGateway` bloquea la ejecución con:

```text
consent_required:device
```

## Diseño del frame

`CameraFrame` normaliza:

- índice de cámara
- mime type
- tamaño en bytes
- ancho y alto si están disponibles
- timestamp
- id de frame

Por defecto, el resultado **no expone los bytes de imagen**. Esto evita que una captura grande o sensible circule innecesariamente por el pipeline. La política `include_image_bytes_in_output=True` permite habilitarlo en contextos controlados.

## OpenCV opcional

`OpenCVCameraClient` importa `cv2` solo en tiempo de ejecución.
Si OpenCV no está instalado o la cámara no está disponible, el error se normaliza mediante `CameraProviderError`.

Esto permite que los tests usen mocks y no dependan de hardware real.

## Contrato preservado

M68 no modifica contratos de:

- M50–M60
- M61 Tool Gateway
- M62 Capability Registry
- M63 Permissions & Consent
- M63B Semantic Capability Descriptors
- M65 Weather Adapter
- M66 Mail Reader Adapter
- M67 Mail Action Adapter

## Resultado

ROBY queda preparado para entender expresiones como:

- “ROBY, mirá esto.”
- “ROBY, qué ves?”
- “ROBY, podés leer este papel?”
- “ROBY, sacá una foto.”

sin convertir la cámara en una dependencia del núcleo cognitivo.
