# M325.10 — Desktop Map Presenter

## Objetivo

Presentar documentos HTML de mapas en superficies de escritorio sin acoplar el
renderizador Folium a una biblioteca gráfica concreta.

## Cambios

- Se añadió `DesktopMapPresenter` como implementación de `MapPresenter`.
- El modo `system_browser` utiliza `webbrowser` y admite inyección para pruebas.
- El modo `embedded_window` requiere un adaptador explícito, evitando nuevas
  dependencias de interfaz en esta versión.
- Se gobiernan los esquemas URI permitidos (`file`, `http`, `https`).
- Los errores de la superficie se contienen en `MapPresentationResult`.
- Se añadieron pruebas unitarias para configuración, navegador, ventana
  embebida, rechazo, excepciones y validación de URI.

## Fuera de alcance

- Integración conversacional.
- Implementación concreta de una ventana web embebida.
- Geocodificación, renderizado y cálculo de rutas.
