# M355 — Document Classification gobernado

M355 clasifica evidencia documental obtenida desde una única captura autorizada.
Reutiliza OCR y, cuando están disponibles, señales auxiliares de objetos y códigos
visuales. No retiene la imagen original.

## Categorías iniciales

- factura;
- recibo;
- ticket o entrada;
- formulario;
- carta;
- etiqueta;
- documento de identidad;
- desconocido.

La clasificación es explicable: devuelve confianza, señales coincidentes,
alternativas y procedencia del clasificador. Una evidencia insuficiente produce
`unknown` en lugar de inventar una categoría.

## Gobernanza y límites

Cada operación requiere permiso de cámara, consentimiento explícito, solicitud
directa y la capacidad `document_understanding`.

M355 no consulta la web, no abre enlaces, no paga facturas, no almacena imágenes
y no ejecuta acciones. No extrae campos contables estructurados como total,
fecha de vencimiento, emisor o número de factura; esa extracción corresponde a
un milestone posterior.
