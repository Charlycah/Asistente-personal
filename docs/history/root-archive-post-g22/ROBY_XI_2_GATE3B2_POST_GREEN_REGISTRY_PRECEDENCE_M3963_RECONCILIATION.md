# ROBY XI.2 — GATE 3.B.2 POST-GREEN REGISTRY PRECEDENCE + M396.3 RECONCILIATION

## Estado
SURGICAL RECONCILIATION — pendiente de certificación local integral.

## Baseline material
Último ZIP completo corregido entregado por el usuario el 2026-09-02.

## Residual reproducido
La base mantenía cuatro fallos focales después del GREEN de GATE 3.B.2:

1. La capability `vision.stored_images.read_analyze` se registraba antes de todas las capabilities históricas, alterando la precedencia contractual del registro oficial.
2. La interfaz desktop heredaba ese cambio de precedencia.
3. `presence.continuity` dejaba de ocupar su posición histórica contractual.
4. El manifest M396.3 todavía contenía el hash anterior de `app/runtime_root_factory.py`.

## Reconciliación quirúrgica

- Se conserva una única construcción de `build_vision_gateway_from_environment()`.
- Se conserva una única construcción de `build_governed_stored_image_runtime(...)`.
- Se mueve únicamente el momento de registro de `vision.stored_images.read_analyze` al final del registro productivo existente, después de `capability.governed_routing_runtime`.
- Así se preserva íntegramente la precedencia histórica de todas las capabilities ya existentes.
- Se actualiza el contrato M247 para reconocer la nueva capability como extensión final del registro, sin reordenar ninguna autoridad previa.
- Se reconcilia `docs/quality/M396_3_AUTHORITY_PRESERVATION_BASELINE.json` con el hash efectivo de `app/runtime_root_factory.py`.
- Se regenera M361.

## Autoridades preservadas

No se crea ningún segundo Vision Core, Vision Gateway, Image Repository, capability registry ni runtime root.

## STOP

Continúan fuera de alcance biometría, exploración automática de galerías, selección automática, análisis automático, Memory, Learning, Planning N+1 y Reasoning automático desde imágenes.

## Validación focal del entorno de integración

- Gate 3.B.2 contract
- M247 runtime capability registry
- M248 operational capability interface integration
- M252 presence runtime
- M396.3 authority preservation
- M361 quality baseline

Resultado: `46 passed`.

No se reclama Ruff ni suite integral desde este entorno; requieren certificación local del usuario.

## Residual M264 detectado en certificación local

La certificación local posterior dejó un único fallo externo residual en `tests/test_m264_end_to_end_conversation_runtime.py`: el contrato histórico inspeccionaba exclusivamente las últimas cuatro capabilities del registro. La nueva capability visual, añadida de forma deliberada como extensión final para preservar toda la precedencia existente, desplazó esa ventana sin alterar la instancia ni el orden relativo del bloque M264.

Reconciliación mínima:

- No se modifica producción.
- No se reordena ninguna capability productiva.
- Se actualiza únicamente la expectativa contractual M264 para reconocer el nuevo tail de cinco capabilities, preservando exactamente el orden histórico de las cuatro anteriores y añadiendo `vision.stored_images.read_analyze` como extensión final.
- Se regenera M361.

Validación focal posterior: `38 passed` sobre M264 + M247 + M248 + M252 + M396.3 + M361.
