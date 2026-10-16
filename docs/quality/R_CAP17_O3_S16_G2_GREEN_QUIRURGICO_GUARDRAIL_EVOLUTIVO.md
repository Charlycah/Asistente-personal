# R-CAP17-O3-S16-G2 — GREEN quirúrgico — Guardrail evolutivo

## Base y evidencia

RED Windows certificado: Ruff integral PASS; 2 pruebas PASS, 1 fallo RED intencional.

## Cambio único de contrato heredado

En `tests/architecture/test_r_doc_master_consolidation_s1_contract_red.py`, la prueba `test_s1_preserves_unchanged_evolvable_masters` verifica la presencia del registro maestro vigente, pero ya no compara su contenido contra el digest histórico S1.

La constante `EVOLVABLE_UNCHANGED` y su SHA-256 S1 original se conservan literalmente como evidencia histórica, protegida por el nuevo contrato G2. Los 8 maestros estáticos, el manifiesto de traslado y la prueba de cardinalidad no se modifican. R-DOC-ROOT-1 declara el registro evolutivo sin congelación histórica de SHA.

No se modifican el registro maestro, Current Truth, Cognitive Inventory, código productivo, runtime ni tests M377.

## Estado

GREEN preparado, pendiente de certificación Windows. No promover baseline global antes de los gates completos. M377 47 RED intencionales HOLD.

## G2 final owner certification and S16-CLOSE handoff

Windows focal G2/R-DOC-S1/R-DOC-ROOT-1: **16 passed, 0 failed (1.70 s)**; Ruff PASS. Subsequent integral Windows gate: **13,724 passed, 47 M377 intentional RED, zero unexpected failures (323.80 s)**. G2 contractual guardrail is certified GREEN; M377 remains HOLD. See `docs/quality/R_CAP17_O3_S16_CIERRE_RECONCILIACION_PROMOCION_CONTROLADA.md` for the exact nine-file failure identity distribution and bounded baseline promotion.
