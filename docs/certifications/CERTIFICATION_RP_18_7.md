# Certificación RP.18.7

Se certifica que ROBY XI.2 clasifica explícitamente sus superficies históricas y que
los entrypoints oficiales no construyen una segunda autoridad de lifecycle.

También se certifica que la captura ambiental de cámara ya no accede directamente
al adapter registrado y atraviesa la ruta oficial de capacidades.

Compatibilidad conservada:

- `build_desktop_app()` como alias fino;
- `DesktopPersonalRuntime` para consumidores históricos;
- `build_operational_desktop_app()` como adapter especializado;
- `app.bootstrap:build_app` como composición legada aislada y no oficial.

La única autoridad operacional continúa siendo `OfficialROBYRuntime`.
