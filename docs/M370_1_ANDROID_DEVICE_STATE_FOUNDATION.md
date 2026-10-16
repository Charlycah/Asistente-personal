# M370.1 — Android Device State Foundation

M370.1 inicia la Fase II de capacidades Android con una representación canónica,
inmutable y de solo lectura del estado de un dispositivo Android.

## Decisión arquitectónica

`OfficialDeviceGateway` continúa siendo la única autoridad de dispositivos. Este
milestone no crea `AndroidDeviceStateGateway`, repositorios paralelos ni una ruta
alternativa de integración. El contrato Android ya existente aporta identidad y
capacidades declaradas; M370.1 únicamente incorpora el modelo normalizado
`AndroidDeviceState` y permite que la autoridad oficial conserve la observación más
reciente en memoria.

## Estado representado

El agregado puede describir:

- identidad visible del dispositivo y versión de Android;
- batería y estado de alimentación;
- conectividad general, Wi-Fi y Bluetooth;
- pantalla encendida o apagada;
- almacenamiento y memoria disponibles;
- instante, fuente y evidencia de la observación.

Los campos que una futura fuente no pueda conocer permanecen explícitamente
opcionales o en estado `unknown`; no se inventan valores.

## Límites obligatorios

- La capacidad es de **solo lectura** respecto del dispositivo.
- Todo estado conserva `read_only=True` y `executable=False`.
- El dispositivo debe estar registrado en `OfficialDeviceGateway`.
- Debe declarar expresamente la capacidad `android.device_state`.
- No se abre transporte, no se consulta ADB y no se incorpora I/O real.
- No hay automatizaciones, comandos, acciones ni modificación del teléfono.
- No se conecta todavía con runtime, planner, memoria, modelo mental o aprendizaje.
- La futura adquisición real deberá permanecer subordinada al Android Bridge y a
  las políticas de Tool Gateway que correspondan.

## Fuera de alcance

Notificaciones, portapapeles, archivos, sensores, ubicación, cámara, ejecución en
segundo plano, emparejamiento y control del dispositivo pertenecen a hitos
posteriores.
