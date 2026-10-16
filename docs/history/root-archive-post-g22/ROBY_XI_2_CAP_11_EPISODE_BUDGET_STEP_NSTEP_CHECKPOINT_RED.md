# ROBY XI.2 — CAP-11 Episode budget/step N-step + checkpoint continuity — RED

Estado: **RED contractual preparado** sobre baseline 13.669 PASS + Ruff limpio.

Este bloque congela la primera generalización constitucional de CAP-11 sin abrir step 3 productivo. El hard-cap gobernado queda explícito en **4 adquisiciones**, con default histórico **2**.

La producción debe permanecer sin modificar durante RED. El contrato exige que el único Episode owner pueda representar step N dentro de `1..4`, que `start(...)` admita budget explícito sin romper la identidad histórica de budget 2, que `record_reentry(...)` y `evaluate_continuation(...)` dejen de depender de la semántica fija “segundo paso”, y que el checkpoint conserve `current_step` explícito y lo incluya en su fingerprint.

Resume permanece consultativo: un checkpoint N-step no agotado puede ser candidato; uno agotado exige review. Ningún budget concede Planning/Authorization/Execution por sí mismo.

No se generalizan todavía Productive Continuation, Planning Reentry, Authorization Reentry, Execution Reentry, RR2 Closure ni bridges P2/A2/E2/RR2.
