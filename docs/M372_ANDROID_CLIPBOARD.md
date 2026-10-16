# M372 — Android Clipboard

## Objetivo

Incorporar la representación canónica del portapapeles Android como una observación sensible, inmutable, de solo lectura y no ejecutable.

## Autoridad

`OfficialDeviceGateway` continúa siendo la única autoridad de dispositivos. M372 no crea un gateway de portapapeles ni un almacén paralelo.

## Modelos

- `AndroidClipboardContentKind` normaliza el tipo declarado del contenido.
- `AndroidClipboardItem` representa el único elemento observado sin inferir acciones.
- `AndroidClipboardSnapshot` representa un portapapeles vacío o un elemento observado para un dispositivo.

## Admisión

Un snapshot sólo puede admitirse cuando el dispositivo:

1. está registrado;
2. pertenece a la categoría móvil;
3. declara `android.clipboard`.

## Privacidad y límites

El contenido se marca como sensible por defecto. Observarlo no autoriza escribir, limpiar, sincronizar, compartir, abrir una URI, ejecutar un intent, persistirlo ni incorporarlo automáticamente a memoria, modelo mental, planificación o aprendizaje.

M372 no implementa lector Android real, ADB, transporte, polling, procesos en segundo plano ni automatizaciones.

## Verificación

La cobertura exige inmutabilidad, timestamps conscientes de zona horaria, MIME types únicos, pertenencia al dispositivo, capacidad declarada, autoridad única, ausencia de métodos de acción y documentación sincronizada.
