# ROBY XI.2 M327.6

Prevención de decisiones repetidas y bucles autónomos.

- Deduplicación temporal configurable de observaciones equivalentes.
- Bloqueo de reentrada mientras un ciclo idéntico está en ejecución.
- Las condiciones modificadas se ejecutan inmediatamente.
- El mismo diagnóstico puede reintentarse al vencer la ventana.
- Nuevo contador `autonomy_suppressed_count` en el snapshot.
- Sin cambios en políticas, permisos ni capacidades autónomas.
