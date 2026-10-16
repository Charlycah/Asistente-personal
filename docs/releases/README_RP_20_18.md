# RP.20.18 — Retiro de constructor trivial sin consumidores

Se retiró `app.desktop_ui.create_desktop_app()`. La función no tenía consumidores y sólo devolvía `ROBYDesktopApp(adapter=ROBYUIAdapter(roby or ROBY()))`.

Se conservaron `build_desktop_app()` y `build_unified_desktop_app()` porque forman parte del inventario de entrypoints y de la compatibilidad operacional. También se conservaron los builders que interpretan entorno o ensamblan varios colaboradores.

Validación esperada:

```powershell
ruff check .
pytest -q
```
