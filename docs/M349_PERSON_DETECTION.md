# ROBY XI.2 M349 — Person Detection

## Propósito

M349 agrega al `OfficialVisionCore` la capacidad de responder si una o más
personas aparecen en un único frame solicitado y autorizado por el usuario.
La capacidad es local, no biométrica y no identifica individuos.

## Arquitectura

```text
VisionCaptureRequest
        │
OfficialVisionCore
        ├── CameraProvider
        ├── PersonDetector
        └── IntelligentVisionService
```

`OfficialVisionCore` sigue siendo la única composición oficial. La cámara
captura un frame; el detector recibe temporalmente ese frame; y el servicio de
visión existente gobierna la observación. No se crea una segunda autoridad
visual.

## Contratos

- `PersonDetector`: frontera intercambiable para detectores locales.
- `PersonRegion`: región rectangular, confianza y ninguna identidad.
- `PersonDetection`: presencia, cantidad y nombre del detector.
- `PersonDetectionResult`: resultado gobernado, sin bytes de imagen.
- `OpenCVHOGPersonDetector`: implementación CPU opcional basada en OpenCV.

## Límites de privacidad

- Requiere permiso de cámara, consentimiento y solicitud directa.
- Procesa una sola captura por invocación.
- No conserva ni devuelve los bytes del frame.
- No reconoce rostros ni identidades.
- No infiere edad, género, emociones, salud ni atributos sensibles.
- No funciona en segundo plano ni activa vigilancia continua.
- No persiste regiones, imágenes ni historial visual.

## Alcance operativo

M349 ofrece una API interna real y un adaptador OpenCV opcional. Todavía no
incorpora intención conversacional como «¿hay alguien frente a la cámara?»,
notificaciones, memoria visual, seguimiento, cámaras IP ni automatizaciones.
Esas integraciones deberán agregarse sobre este núcleo en milestones futuros.
