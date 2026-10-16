# M385.5 — Propiedad canónica de la memoria

## Decisión

La memoria personal productiva de ROBY tiene un único almacén físico conjunto:
`coowners.sqlite3`. Su propietario canónico es `Carlos y Cristina`.

`Carlos` y `Cristina` son alias válidos del mismo ámbito de copropiedad. No crean
almacenes separados. Los nombres presentes en órdenes como `recordá sobre
Cristina` son atribuciones del recuerdo (`subject`), no propietarios físicos.

## Límites de seguridad

- Solo `Carlos`, `Cristina` y `Carlos y Cristina` pueden resolver el almacén
  productivo.
- Un texto libre no puede crear una base de memoria nueva.
- Los sujetos admitidos por las órdenes conversacionales son Carlos y Cristina.
- Un único almacén histórico reconocido puede copiarse al nombre canónico
  mediante una instantánea transaccional de SQLite. El original se conserva.
- Si existen simultáneamente los históricos reconocidos de Carlos y Cristina,
  ROBY se detiene y exige revisión humana. No mezcla, mueve ni elimina datos.
- Los archivos históricos desconocidos se preservan y no se interpretan.

## Alcance

La canonicalización se activa en el constructor productivo. Las instancias de
prueba o herramientas que crean directamente el runtime mantienen el modo
general anterior salvo que soliciten expresamente el modo canónico.

M385.5 no lee recuerdos personales existentes, no modifica credenciales y no
introduce aprendizaje autónomo.
