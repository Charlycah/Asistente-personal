# M352 — QR y códigos de barras gobernados

M352 extiende el único `OfficialVisionCore` con decodificación local y explícita
de QR y códigos de barras. La cámara se utiliza una sola vez por solicitud y el
frame se descarta después del procesamiento.

El resultado contiene únicamente contenido decodificado, tipo, confianza,
región geométrica y procedencia del adaptador. **No abre enlaces, no ejecuta
comandos, no consulta Internet y no persiste imágenes ni contenidos de forma
automática.**

El adaptador opcional `PyzbarVisualCodeDecoder` usa OpenCV y pyzbar. El contrato
`VisualCodeDecoder` mantiene el núcleo desacoplado de esa implementación.
