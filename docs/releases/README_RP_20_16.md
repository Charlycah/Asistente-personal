> **HISTORICAL / APPLIED / SUPERSEDED** — Este documento conserva la evidencia del refinamiento ya aplicado. El script asociado fue archivado en `docs/history/migrations/` y no forma parte del tooling operativo actual.

# RP.20.16 — Retiro de contrato ceremonial de estado cognitivo

## Objetivo

Retirar una abstracción interna sin función arquitectónica real.

## Cambio

Se elimina `app/cognitive_state_provider.py` y su `CognitiveStateProvider`. El protocolo sólo era importado por una prueba para comprobar estructuralmente que `ContinuousInternalCognitiveLoop` exponía dos propiedades que ya son parte directa de su API concreta.

La prueba funcional ahora verifica directamente `current_state` y el avance observable de `snapshot.cycles`.

## Auditoría

Se conservaron los demás Protocols revisados cuando tipan dependencias inyectables, adaptadores externos, repositorios, transportes o múltiples dobles de prueba. Tener una sola implementación de producción no basta por sí solo para eliminar un puerto real.

## Aplicación por overlay

Este RP elimina un archivo físico. Debe ejecutarse `scripts/migrations/APPLY_RP_20_16.ps1`, que borra explícitamente el módulo obsoleto antes de validar.
