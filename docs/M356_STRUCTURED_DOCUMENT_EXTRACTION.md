# M356 — Structured Document Extraction gobernado

M356 transforma OCR ya autorizado en campos documentales estructurados y
explicables. Reutiliza una única captura, clasifica el documento y extrae solo
campos respaldados por evidencia visible.

## Campos iniciales

- emisor estimado;
- número de factura o comprobante;
- fecha de emisión;
- vencimiento;
- identificador fiscal;
- importe total;
- moneda;
- código de pago o referencia proveniente de QR/código de barras.

Cada campo incluye nombre, valor, confianza y evidencia textual. Los campos que
no aparecen no se inventan.

## Gobernanza y privacidad

La operación exige permiso de cámara, consentimiento explícito, solicitud del
usuario y `DOCUMENT_UNDERSTANDING`. El frame es transitorio y nunca forma parte
del resultado ni del snapshot.

M356 no consulta la web, no verifica fiscalmente el documento, no abre enlaces,
no realiza pagos, no crea recordatorios y no guarda imágenes. Un código visual
se trata únicamente como dato extraído. Toda validación o acción posterior debe
pasar por otra capacidad gobernada y una autorización independiente.
