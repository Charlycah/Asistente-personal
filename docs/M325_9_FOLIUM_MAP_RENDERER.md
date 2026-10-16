# M325.9 — Folium Map Renderer

M325.9 incorpora el adaptador concreto de `MapDocumentRenderer` para producir documentos HTML interactivos a partir de un `MapDisplayRequest` y un `MapDisplayTarget` ya resuelto.

## Componentes

- `FoliumMapRendererConfig`
- `FoliumMapRenderer`
- `FoliumMapRendererError`
- `FoliumUnavailableError`
- `FoliumRenderError`

## Garantías

- No realiza geocodificación ni llamadas de red propias.
- No abre ventanas ni navegadores.
- Genera cada documento con nombre único.
- Usa un directorio temporal por defecto o uno configurable.
- Mantiene la atribución del proveedor de mosaicos de Folium.
- Escapa etiquetas antes de incorporarlas al HTML.
- Elimina archivos parciales cuando falla el renderizado.
- Devuelve un `MapDocument` con URI `file://` y tipo `text/html`.

## Dependencia opcional

```powershell
pip install -r requirements-maps.txt
```

## Validación

- Pruebas específicas: 22 passed.
- Suite completa en el entorno de construcción: 7284 passed.
