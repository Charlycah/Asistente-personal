# M365.6 — Android Bridge Capability Catalog Foundation

M365.6 incorpora un catálogo gobernado e inmutable de capacidades Android.

El catálogo sólo permite `list`, `find` y `contains`. Las categorías iniciales son notificaciones, archivos, cámara, micrófono, contactos, calendario, ubicación, sensores, portapapeles y estado del dispositivo.

Cada descriptor conserva `enabled=False` y `executable=False`. El registro `android.capabilities.catalog` es metadata pasiva, no tiene handler y no habilita transporte, planner ni acciones reales sobre Android.
