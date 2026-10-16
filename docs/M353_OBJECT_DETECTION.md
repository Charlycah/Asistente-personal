# M353 — Object Detection gobernado

M353 extiende el único `OfficialVisionCore` con detección local de objetos sobre
una captura explícitamente autorizada.

## Alcance

La capacidad devuelve etiquetas, confianza y regiones geométricas. El frame es
transitorio y no forma parte del resultado. El detector es un contrato
intercambiable; se incluye un adaptador opcional OpenCV DNN para modelos ONNX
locales suministrados por el usuario.

## Gobernanza

La operación exige permiso de cámara, consentimiento explícito, solicitud
directa y la capacidad `OBJECT_DETECTION`. El resultado no ejecuta acciones,
no abre enlaces, no compra productos y no modifica el entorno.

## Límites

M353 no incorpora seguimiento, memoria visual, comprensión de escenas,
identidad, atributos personales, captura continua ni inferencia remota. Una
etiqueta es una estimación del modelo y debe presentarse con su confianza.
