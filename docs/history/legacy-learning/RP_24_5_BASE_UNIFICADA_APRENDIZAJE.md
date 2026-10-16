# RP.24.5 — Base Unificada de Aprendizaje

RP.24.5 incorpora una base local, persistente y auditable para conocimiento
aprendido por ROBY.

## Principios

- Nunca se elimina silenciosamente un aprendizaje previo.
- Toda confirmación, corrección y archivado deja un evento de auditoría.
- Las correcciones crean un nuevo registro y marcan el anterior como superado.
- La persistencia se realiza exclusivamente en SQLite local.
- La confianza, procedencia, propietario y fechas permanecen explícitos.

## Tipos iniciales

Preferencias, hechos, hábitos, correcciones, conocimiento doméstico,
procedimientos e intereses.

## API

`UnifiedLearningBase` expone operaciones para aprender, consultar, confirmar,
corregir, archivar, buscar y revisar el historial.

RP.24.5 no reentrena modelos ni infiere hábitos automáticamente. Proporciona la
infraestructura estable sobre la que podrán integrarse esas capacidades bajo
políticas futuras.
