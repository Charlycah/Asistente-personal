# M365.7 — Android Bridge Capability Selection & Stabilization

M365.7 cierra la serie Android Bridge con una selección gobernada de candidatos.

Los candidatos iniciales son estado del dispositivo, notificaciones y portapapeles.
La selección sólo expresa prioridad futura: no activa handlers, permisos, transporte ni
operaciones sobre Android. Todo resultado conserva `executable=False`.

La política consulta el catálogo canónico, no lo muta y bloquea identificadores no
declarados. La readiness del bridge es una precondición descriptiva, no una autorización
de ejecución. Cualquier capacidad real requerirá un milestone posterior y su registro
explícito detrás de `ToolGatewayManager`.
