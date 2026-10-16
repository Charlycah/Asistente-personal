# M350 — Face Detection gobernado

M350 extiende el único `OfficialVisionCore` para localizar rostros en una captura local y explícitamente autorizada.

## Alcance

- captura única y bajo petición;
- detección local mediante un contrato `FaceDetector`;
- presencia, cantidad, regiones rectangulares y confianza;
- descarte del frame después del procesamiento;
- observabilidad sin conservar la imagen.

## Límites

Face Detection no identifica personas y no realiza reconocimiento facial. No crea plantillas biométricas ni infiere edad, género, emociones, salud, identidad u otros atributos personales. Tampoco realiza seguimiento, captura continua, vigilancia ni memoria visual.

El detector OpenCV incluido es opcional y permanece detrás del contrato de infraestructura. El núcleo cognitivo no depende directamente de OpenCV.
