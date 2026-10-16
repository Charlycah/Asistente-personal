# M312.1 — Infraestructura del Cerebro de ROBY

## Alcance

Esta versión agrega una infraestructura de memoria canónica, aislada y todavía no
conectada al comportamiento visible de ROBY.

## Componentes nuevos

- `domain/brain`: modelo auditable de recuerdos, tipos, estado y vencimiento.
- `application/brain`: `BrainService` con operaciones de recordar, recuperar,
  actualizar, olvidar y vencer.
- `infrastructure/brain`: persistencia JSON con escritura atómica.
- `tests/test_m312_1_brain_foundation.py`: pruebas de persistencia, búsqueda,
  deduplicación, vencimiento, actualización y olvido.

## Restricciones respetadas

- No se modificó el runtime.
- No se conectó el cerebro a voz, Gmail, clima, noticias ni interfaz.
- No se reemplazaron memorias históricas existentes.
- No se almacenan credenciales ni secretos.

## Próximo paso sugerido

M312.2: conectar únicamente la memoria del estado del proyecto ROBY, manteniendo
el resto de la conversación sin cambios.
