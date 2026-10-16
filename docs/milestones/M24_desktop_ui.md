# M24 — Desktop UI

## Objetivo

Introducir una interfaz de escritorio local para interactuar con ROBY desde Windows mediante texto, sin acoplar la UI al núcleo conversacional.

## Decisión arquitectónica

M24 se implementa como **Desktop UI local**, no como Web UI.

Motivos:

- ROBY está pensado inicialmente para correr en casa/local.
- No requiere hosting ni exponer servicios en red.
- Mantiene el núcleo protegido detrás de `ROBYUIAdapter`.
- Permite agregar voz más adelante sin modificar `ROBY.process()`.

El módulo legacy `CORE_LEGACY/interface.py` se tomó como referencia conceptual: ventana, historial y cuadro de texto. No se copió directamente porque estaba acoplado a callbacks legacy y micrófono.

## Componentes agregados

Archivo:

```text
app/desktop_ui.py
```

Componentes:

- `DesktopUIConfig`
- `DesktopMessage`
- `DesktopMessagePresenter`
- `DesktopConversationController`
- `ROBYDesktopApp`
- `create_desktop_app()`

## Contrato

La UI de escritorio:

- envía texto a través de `ROBYUIAdapter`;
- recibe `UIResponse`;
- muestra mensajes del usuario y de ROBY;
- ignora mensajes vacíos;
- no conoce `ROBY.process()` directamente;
- no implementa voz todavía;
- no introduce interfaz web.

## No incluido en M24

- Voice output.
- Voice input.
- Persistencia de preferencias visuales.
- Web UI.
- Hosting remoto.
- Ejecución en segundo plano.

## Tests agregados

Archivo:

```text
tests/test_m24_desktop_ui.py
```

Cobertura:

- configuración desktop por defecto;
- formato de mensajes;
- mensajes vacíos no llaman a ROBY;
- envío de texto devuelve mensajes renderizables para la UI.

## Estado

Completo.
