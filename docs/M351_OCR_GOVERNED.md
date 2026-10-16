# M351 — OCR gobernado

M351 incorpora extracción óptica de texto local como una capacidad del único
`OfficialVisionCore`.

## Alcance

- Captura una sola imagen después de validar permiso, consentimiento y solicitud.
- Usa el contrato `TextExtractor`, independiente del proveedor concreto.
- Devuelve texto, confianza, idioma y regiones geométricas.
- Incluye un adaptador local opcional basado en Tesseract y OpenCV.
- Descarta el frame después del procesamiento y no expone sus bytes.

## Límites

No interpreta documentos, facturas ni formularios. Tampoco clasifica contenido,
extrae entidades, almacena imágenes, crea memoria visual ni activa la cámara de
forma continua. La comprensión semántica de documentos pertenece a una versión
posterior y deberá tener gobernanza propia.

El OCR puede contener errores. ROBY debe presentar el texto como extracción y no
como una transcripción infalible, especialmente ante importes, fechas o datos
sensibles.
