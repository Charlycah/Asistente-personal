# ADR-075 — Document Inbox

## Estado

Aceptado para M73.

## Contexto

ROBY necesita incorporar documentos personales y domésticos como conocimiento
estructurado sin convertir el núcleo cognitivo en un lector dependiente de formatos,
proveedores u OCR. La solución debe respetar Scope Guard, integrarse opcionalmente
con Household Memory y conservar trazabilidad documental.

## Decisión

Se introduce `DocumentInboxManager` como servicio de aplicación del núcleo. El
subsistema separa metadatos, contenido, clasificación, repositorio y ciclo de vida.
La primera implementación admite texto directo y archivos UTF-8 `.txt`, `.md`,
`.csv` y `.json`. Los formatos binarios requieren extractores dedicados futuros.

Los documentos se deduplican mediante SHA-256. Scope Guard bloquea contenido fuera
de alcance y marca para revisión humana los documentos sensibles. La vinculación con
Household Memory es explícita y opcional.

## Consecuencias

- La persistencia queda detrás de `DocumentRepository`.
- La clasificación inicial es determinista y reemplazable.
- PDF, DOCX, imágenes y OCR no se simulan; se incorporarán mediante adaptadores.
- Un documento informa y organiza, pero no autoriza acciones externas o sensibles.
- El pipeline cognitivo puede exponer un resumen documental sin acoplarse al formato.
