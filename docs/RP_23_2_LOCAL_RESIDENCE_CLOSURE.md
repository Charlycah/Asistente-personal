# Cierre de etapa RP.23.2 — residencia local y configuración privada

## Alcance

Esta revisión certifica que ROBY continúa siendo un sistema estrictamente personal,
residente en la laptop de Carlos y Cristi, sin objetivo de publicación, venta o
distribución.

## Ajustes realizados

- Se retiró del código ejecutable la carga de archivos de variables por pares.
- Se eliminaron el asistente y la migración histórica que generaban ese formato.
- La configuración operativa queda en `.roby/config.json`.
- Las credenciales privadas quedan separadas en `.roby/credentials.json`.
- El perfil personal permanece en `.roby/profile.local.toml`.
- Se actualizaron las guías activas para reflejar el esquema local actual.
- Los antecedentes históricos pueden conservar menciones documentales, pero no forman
  parte del runtime ni de ningún módulo activo.

## Principio de residencia

ROBY está diseñado para ejecutarse localmente, crecer por incorporaciones controladas
y mantener sus datos bajo control exclusivo de Carlos y Cristi. Toda integración futura
debe ser explícita, reversible, auditable y compatible con esta residencia local.

## Corrección de pruebas heredadas

La prueba histórica `tests/test_m222_hal_setup_assistant.py` fue migrada al
contrato de configuración privada vigente. Ya no espera atributos, copias de
seguridad ni asistentes asociados al formato retirado. Las pruebas verifican
`.roby/config.json`, el directorio privado, la detección local de modelos y la
ausencia de despliegues o mutaciones del runtime.

Validación del paquete limpio: 6779 pruebas aprobadas.
