# CAP-11 — Execution step N → existing Reasoning re-entry — RED

El contrato RED está materializado en:

`tests/architecture/test_cap11_execution_step_n_to_existing_reasoning_reentry_contract_red.py`

Fallos deliberados esperados sobre la producción actual:
- RR3 intermedio todavía es rechazado por el supuesto fijo step 2;
- RR4 terminal todavía es rechazado por el supuesto fijo step 2;
- el STOP intermedio todavía no puede llegar a `AWAITING_REQUIREMENT`;
- el source contract todavía detecta guards RR2 terminales.

La preservación histórica RR2/budget 2 debe permanecer verde durante RED.
