# M390.3 — Continuidad Interior Explícita

## Objetivo

Permitir que ROBY describa continuidad o cambio entre dos estados interiores simulados ya certificados, sin crear persistencia ni una segunda autoridad.

## Contrato

`ExplicitInnerContinuityEvaluator.compare(previous, current)` recibe dos `SimulatedInnerStateSnapshot` explícitos y devuelve un `ExplicitInnerContinuityReport` inmutable.

Compara únicamente: `affective_tone`, `activation_level`, `stability_level`, `concern_level`, `relational_openness` y `dominant_state`.

## Límites

- No construye snapshots y no reemplaza `SimulatedInnerStateAuthority`.
- No conserva historial, no lee conversación, no usa reloj ni infiere tiempo transcurrido.
- No persiste, aprende, crea memoria, modifica personalidad ni ejecuta acciones.
- Si falta cualquiera de los snapshots, la continuidad es `unavailable`.
- Si alguno está degradado, no se afirma continuidad y el informe queda degradado.

## Determinismo

Las mismas entradas producen el mismo informe y fingerprint. La continuidad existe únicamente como comparación explícita entre entradas suministradas por el llamador.
