# ROBY XI.2 M304.10

Corrección de pruebas heredadas después de consolidar `.roby/` como almacenamiento canónico.

## Cambios

- `tests/test_config_loader_manual.py` ahora usa configuración temporal autocontenida.
- `tests/test_m304_9_canonical_roby_storage.py` ya no falla por la presencia física
  de una carpeta `.hal/` residual en una instalación actualizada sobre una carpeta vieja.
- La prueba sigue verificando que no existan archivos de configuración o credenciales
  heredados en la raíz del proyecto.

## Validación

- `pytest -q`: 6962 passed.
